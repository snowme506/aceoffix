from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminUserResponse


class StatsOverview(BaseModel):
    total_users: int
    total_orders: int
    total_sales: int  # 单位：分
    total_products: int
    today_orders: int
    today_sales: int


class AdminUpdateMemberRequest(BaseModel):
    """后台更新会员信息"""
    nickname: Optional[str] = Field(None, description="昵称")
    points: Optional[int] = Field(None, ge=0, description="积分")
    member_level: Optional[str] = Field(None, description="会员等级")
    is_active: Optional[bool] = Field(None, description="是否启用")
