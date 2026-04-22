from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MemberLevelBase(BaseModel):
    code: str = Field(..., description="等级代码")
    name: str = Field(..., description="等级名称")
    min_points: int = Field(default=0, ge=0, description="最低积分要求")
    discount_rate: float = Field(default=1.0, ge=0, le=1, description="折扣率")
    icon: Optional[str] = Field(None, description="图标")
    color: Optional[str] = Field(None, description="颜色")
    sort_order: int = Field(default=0, description="排序")
    is_active: bool = Field(default=True, description="是否启用")


class MemberLevelCreate(MemberLevelBase):
    pass


class MemberLevelUpdate(BaseModel):
    code: Optional[str] = Field(None, description="等级代码")
    name: Optional[str] = Field(None, description="等级名称")
    min_points: Optional[int] = Field(None, ge=0, description="最低积分要求")
    discount_rate: Optional[float] = Field(None, ge=0, le=1, description="折扣率")
    icon: Optional[str] = Field(None, description="图标")
    color: Optional[str] = Field(None, description="颜色")
    sort_order: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否启用")


class MemberLevelResponse(MemberLevelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemberLevelListResponse(BaseModel):
    total: int
    items: list[MemberLevelResponse]

    class Config:
        from_attributes = True
