from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.security import get_password_hash


class AdminUser(Base):
    """后台管理员表"""
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


def seed_admin_user(db):
    """初始化管理员账号"""
    from sqlalchemy.orm import Session
    if not isinstance(db, Session):
        return
    
    existing = db.query(AdminUser).filter(AdminUser.username == "admin").first()
    if existing:
        return
    
    admin = AdminUser(
        username="admin",
        password_hash=get_password_hash("admin123"),
        nickname="超级管理员",
        is_active=True
    )
    db.add(admin)
    db.commit()
