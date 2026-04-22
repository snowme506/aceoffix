import random
import string
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserPointsLog
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.product import Product
from app.schemas.order import (
    OrderCreate, 
    OrderResponse, 
    OrderDetailResponse,
    OrderListResponse,
    PaymentRequest,
    PaymentResponse,
    OrderItemResponse
)
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.auth import get_current_user
from app.config import POINTS_CONFIG

router = APIRouter()


def generate_order_no() -> str:
    """生成订单号"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"AO{timestamp}{random_str}"


def calculate_points_discount(points: int) -> int:
    """计算积分抵扣金额（1积分=1分）"""
    return points  # 1积分抵扣1分钱


@router.post("/create", response_model=ResponseModel[OrderResponse])
async def create_order(
    request: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建订单"""
    # 验证商品价格（防止前端篡改）
    for item in request.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品ID {item.product_id} 不存在"
            )
        if item.unit_price != product.price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"商品价格已变动，请刷新后重试"
            )

    # 计算商品总金额
    total_amount = sum(item.unit_price * item.quantity for item in request.items)
    
    # 计算积分抵扣
    points_discount = calculate_points_discount(request.points_used)
    
    # 检查用户积分是否足够（重新查询确保拿到最新值）
    user_fresh = db.query(User.points).filter(User.id == current_user.id).first()
    if not user_fresh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    current_points = user_fresh[0]
    if request.points_used > current_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="积分不足"
        )

    # 验证优惠金额不超过总价
    if request.discount_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠金额不能为负"
        )
    if request.discount_amount > total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="优惠金额不能超过订单总额"
        )

    # 计算应付金额
    final_amount = total_amount - request.discount_amount - points_discount
    if final_amount < 0:
        final_amount = 0

    # 创建订单
    order = Order(
        order_no=generate_order_no(),
        user_id=current_user.id,
        total_amount=total_amount,
        discount_amount=request.discount_amount,
        points_used=request.points_used,
        points_discount=points_discount,
        final_amount=final_amount,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.UNPAID,
        receiver_name=request.receiver_name,
        receiver_phone=request.receiver_phone,
        receiver_address=request.receiver_address,
        remark=request.remark
    )
    db.add(order)
    db.flush()  # 获取order.id

    # 创建订单商品项
    for item in request.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_image=item.product_image,
            unit_price=item.unit_price,
            quantity=item.quantity,
            total_price=item.unit_price * item.quantity
        )
        db.add(order_item)

    # 扣除积分（使用新查询结果 + 内存扣减，SQLite 单写事务保证原子性）
    if request.points_used > 0:
        current_user.points = current_points - request.points_used
        points_log = UserPointsLog(
            user_id=current_user.id,
            change_amount=-request.points_used,
            current_balance=current_user.points,
            type="order",
            description=f"订单抵扣: {order.order_no}",
            order_id=order.id
        )
        db.add(points_log)

    db.commit()
    db.refresh(order)
    
    return ResponseModel(
        code=200,
        message="订单创建成功",
        data=OrderResponse.model_validate(order)
    )


@router.get("/list", response_model=ResponseModel[OrderListResponse])
async def get_order_list(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    query = db.query(Order).filter(Order.user_id == current_user.id)
    total = query.count()
    
    orders = query.order_by(Order.created_at.desc()).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data=OrderListResponse(
            total=total,
            items=[OrderResponse.model_validate(order) for order in orders]
        )
    )


@router.get("/detail/{order_id}", response_model=ResponseModel[OrderDetailResponse])
async def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取订单详情"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    return ResponseModel(
        code=200,
        message="success",
        data=OrderDetailResponse.model_validate(order)
    )


@router.post("/pay", response_model=ResponseModel[PaymentResponse])
async def pay_order(
    request: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mock支付订单"""
    order = db.query(Order).filter(
        Order.id == request.order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单状态不正确"
        )
    
    if order.payment_status == PaymentStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="订单已支付"
        )
    
    # Mock支付处理
    paid_at = datetime.utcnow()
    
    # 更新订单状态
    order.status = OrderStatus.PAID
    order.payment_status = PaymentStatus.PAID
    order.paid_at = paid_at
    order.payment_method = request.payment_method
    order.payment_no = f"MOCK{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    
    # 更新用户消费金额
    current_user.total_spent += order.final_amount
    
    # 赠送消费积分（1元=1积分）
    points_earned = int(order.final_amount / 100 * POINTS_CONFIG["order_ratio"])
    if points_earned > 0:
        current_user.points += points_earned
        points_log = UserPointsLog(
            user_id=current_user.id,
            change_amount=points_earned,
            current_balance=current_user.points,
            type="order",
            description=f"消费返积分: {order.order_no}",
            order_id=order.id
        )
        db.add(points_log)
    
    db.commit()
    db.refresh(order)
    
    return ResponseModel(
        code=200,
        message="支付成功",
        data=PaymentResponse(
            order_id=order.id,
            order_no=order.order_no,
            payment_status=order.payment_status,
            paid_at=order.paid_at,
            message="Mock支付成功"
        )
    )
