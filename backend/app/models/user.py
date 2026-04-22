from datetime import datetime
from typing import Optional, List
import enum

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MemberLevel(str, enum.Enum):
    """会员等级"""
    NORMAL = "normal"      # 普通会员
    SILVER = "silver"      # 银卡
    GOLD = "gold"          # 金卡
    PLATINUM = "platinum"  # 白金


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 会员信息
    member_level: Mapped[MemberLevel] = mapped_column(
        Enum(MemberLevel), 
        default=MemberLevel.NORMAL, 
        nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 累计消费金额（分）
    
    # 推荐关系
    referrer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # 关系
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user", lazy="selectin")
    points_logs: Mapped[List["UserPointsLog"]] = relationship("UserPointsLog", back_populates="user", lazy="selectin")
    referrals: Mapped[List["User"]] = relationship("User", remote_side=[id], lazy="selectin")


class UserPointsLog(Base):
    """用户积分变动记录"""
    __tablename__ = "user_points_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # 变动信息
    change_amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 正数增加，负数减少
    current_balance: Mapped[int] = mapped_column(Integer, nullable=False)  # 变动后余额
    
    # 变动类型
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # register, order, referral, redeem, manual
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 关联信息
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"), nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="points_logs")
