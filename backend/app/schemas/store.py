from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class StoreBase(BaseModel):
    name: str = Field(..., description="门店名称")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    address: Optional[str] = Field(None, description="详细地址")
    phone: Optional[str] = Field(None, description="电话")
    hours: Optional[str] = Field(None, description="营业时间")
    status: int = Field(default=1, description="状态: 1营业 0休息")
    sort_order: int = Field(default=0, description="排序")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = Field(None, description="门店名称")
    province: Optional[str] = Field(None, description="省份")
    city: Optional[str] = Field(None, description="城市")
    district: Optional[str] = Field(None, description="区县")
    address: Optional[str] = Field(None, description="详细地址")
    phone: Optional[str] = Field(None, description="电话")
    hours: Optional[str] = Field(None, description="营业时间")
    status: Optional[int] = Field(None, description="状态")
    sort_order: Optional[int] = Field(None, description="排序")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")


class StoreResponse(StoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    total: int
    items: list[StoreResponse]

    class Config:
        from_attributes = True


class NearbyStoreRequest(BaseModel):
    lat: float = Field(..., description="当前纬度")
    lng: float = Field(..., description="当前经度")
    radius: float = Field(default=10.0, description="半径（公里）")


class NearbyStoreResponse(StoreResponse):
    distance: float = Field(..., description="距离（公里）")
