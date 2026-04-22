from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BannerBase(BaseModel):
    image_url: str = Field(..., description="图片地址")
    link_url: Optional[str] = Field(None, description="链接地址")
    title: Optional[str] = Field(None, description="标题")
    sort_order: int = Field(default=0, description="排序")
    is_active: bool = Field(default=True, description="是否启用")


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    image_url: Optional[str] = Field(None, description="图片地址")
    link_url: Optional[str] = Field(None, description="链接地址")
    title: Optional[str] = Field(None, description="标题")
    sort_order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否启用")


class BannerResponse(BannerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BannerListResponse(BaseModel):
    total: int
    items: list[BannerResponse]

    class Config:
        from_attributes = True
