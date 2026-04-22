from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MemberLevel(Base):
    """会员等级表"""
    __tablename__ = "member_levels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # normal, silver, gold, platinum
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    min_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discount_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 1.0 = 无折扣, 0.9 = 9折
    icon: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


def seed_member_levels(db):
    """初始化会员等级数据"""
    from sqlalchemy.orm import Session
    if not isinstance(db, Session):
        return
    
    existing = db.query(MemberLevel).first()
    if existing:
        return
    
    levels = [
        MemberLevel(code="normal", name="普通会员", min_points=0, discount_rate=1.0, icon="🥉", color="#999999", sort_order=1),
        MemberLevel(code="silver", name="银卡会员", min_points=500, discount_rate=0.95, icon="🥈", color="#C0C0C0", sort_order=2),
        MemberLevel(code="gold", name="金卡会员", min_points=2000, discount_rate=0.9, icon="🥇", color="#FFD700", sort_order=3),
        MemberLevel(code="platinum", name="白金会员", min_points=5000, discount_rate=0.85, icon="💎", color="#E5E4E2", sort_order=4),
    ]
    for level in levels:
        db.add(level)
    db.commit()
