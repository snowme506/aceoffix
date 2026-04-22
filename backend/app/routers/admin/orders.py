from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.schemas.order import OrderResponse, OrderDetailResponse
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/list", response_model=ResponseModel[dict])
async def admin_list_orders(
    params: PaginationParams = Depends(),
    order_no: Optional[str] = None,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-订单列表"""
    query = db.query(Order)
    if order_no:
        query = query.filter(Order.order_no.contains(order_no))
    if status:
        query = query.filter(Order.status == status)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "total": total,
            "items": [OrderResponse.model_validate(o) for o in orders]
        }
    )


@router.get("/detail/{order_id}", response_model=ResponseModel[OrderDetailResponse])
async def admin_get_order(
    order_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return ResponseModel(code=200, message="success", data=OrderDetailResponse.model_validate(order))


@router.put("/update-status/{order_id}", response_model=ResponseModel[OrderResponse])
async def admin_update_order_status(
    order_id: int,
    status: str,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    
    try:
        order.status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的订单状态")
    
    db.commit()
    db.refresh(order)
    return ResponseModel(code=200, message="更新成功", data=OrderResponse.model_validate(order))
