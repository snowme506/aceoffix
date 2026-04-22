from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.user import MemberLevel


class UserBase(BaseModel):
    """用户基础信息"""
    phone: str = Field(..., description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")


class UserCreate(UserBase):
    """创建用户"""
    pass


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    member_level: MemberLevel
    points: int
    total_spent: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户个人资料"""
    id: int
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    member_level: MemberLevel
    points: int
    total_spent: int
    referrer_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PointsLogItem(BaseModel):
    """积分记录项"""
    id: int
    change_amount: int
    current_balance: int
    type: str
    description: str
    order_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PointsLogResponse(BaseModel):
    """积分记录响应"""
    total: int
    items: List[PointsLogItem]
    
    class Config:
        from_attributes = True
