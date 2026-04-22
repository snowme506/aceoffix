import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.store import Store
from app.schemas.store import (
    StoreCreate, StoreUpdate, StoreResponse, StoreListResponse,
    NearbyStoreRequest, NearbyStoreResponse
)
from app.schemas.common import ResponseModel, PaginationParams

router = APIRouter()


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点之间的距离（公里）"""
    R = 6371  # 地球半径（公里）
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@router.get("/list", response_model=ResponseModel[StoreListResponse])
async def get_stores(
    params: PaginationParams = Depends(),
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取门店列表"""
    query = db.query(Store).filter(Store.status == 1)
    if city:
        query = query.filter(Store.city == city)
    
    total = query.count()
    stores = query.order_by(Store.sort_order).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=StoreListResponse(
            total=total,
            items=[StoreResponse.model_validate(s) for s in stores]
        )
    )


@router.get("/detail/{store_id}", response_model=ResponseModel[StoreResponse])
async def get_store_detail(store_id: int, db: Session = Depends(get_db)):
    """获取门店详情"""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="门店不存在")
    return ResponseModel(code=200, message="获取成功", data=StoreResponse.model_validate(store))


@router.post("/nearby", response_model=ResponseModel[list[NearbyStoreResponse]])
async def get_nearby_stores(
    request: NearbyStoreRequest,
    db: Session = Depends(get_db)
):
    """获取附近门店"""
    stores = db.query(Store).filter(Store.status == 1).all()
    
    result = []
    for store in stores:
        if store.latitude is not None and store.longitude is not None:
            dist = haversine_distance(request.lat, request.lng, store.latitude, store.longitude)
            if dist <= request.radius:
                result.append({
                    **StoreResponse.model_validate(store).model_dump(),
                    "distance": round(dist, 2)
                })
    
    result.sort(key=lambda x: x["distance"])
    return ResponseModel(code=200, message="获取成功", data=result)
