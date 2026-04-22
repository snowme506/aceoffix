from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse, StoreListResponse
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/list", response_model=ResponseModel[StoreListResponse])
async def admin_list_stores(
    params: PaginationParams = Depends(),
    keyword: str = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-门店列表"""
    query = db.query(Store)
    if keyword:
        query = query.filter(Store.name.contains(keyword))
    
    total = query.count()
    stores = query.order_by(Store.sort_order).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data=StoreListResponse(
            total=total,
            items=[StoreResponse.model_validate(s) for s in stores]
        )
    )


@router.get("/detail/{store_id}", response_model=ResponseModel[StoreResponse])
async def admin_get_store(
    store_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-门店详情"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="门店不存在")
    return ResponseModel(code=200, message="success", data=StoreResponse.model_validate(store))


@router.post("/create", response_model=ResponseModel[StoreResponse])
async def admin_create_store(
    request: StoreCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-创建门店"""
    store = Store(**request.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return ResponseModel(code=200, message="创建成功", data=StoreResponse.model_validate(store))


@router.put("/update/{store_id}", response_model=ResponseModel[StoreResponse])
async def admin_update_store(
    store_id: int,
    request: StoreUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-更新门店"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="门店不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(store, field, value)
    
    db.commit()
    db.refresh(store)
    return ResponseModel(code=200, message="更新成功", data=StoreResponse.model_validate(store))


@router.delete("/delete/{store_id}", response_model=ResponseModel[dict])
async def admin_delete_store(
    store_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-删除门店"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="门店不存在")
    
    db.delete(store)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": store_id})
