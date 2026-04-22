import enum
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"           # 待支付
    PAID = "paid"                 # 已支付
    PROCESSING = "processing"     # 处理中
    SHIPPED = "shipped"           # 已发货
    COMPLETED = "completed"       # 已完成
    CANCELLED = "cancelled"       # 已取消
    REFUNDED = "refunded"         # 已退款


class PaymentStatus(str, enum.Enum):
    """支付状态"""
    UNPAID = "unpaid"             # 未支付
    PAID = "paid"                 # 已支付
    PARTIAL = "partial"           # 部分支付
    REFUNDED = "refunded"         # 已退款
    FAILED = "failed"             # 支付失败


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    
    # 用户信息
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # 金额信息（单位：分）
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)      # 商品总金额
    discount_amount: Mapped[int] = mapped_column(Integer, default=0)         # 优惠金额
    points_used: Mapped[int] = mapped_column(Integer, default=0)             # 使用积分
    points_discount: Mapped[int] = mapped_column(Integer, default=0)         # 积分抵扣金额
    final_amount: Mapped[int] = mapped_column(Integer, nullable=False)       # 应付金额
    
    # 状态
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.UNPAID, nullable=False)
    
    # 支付信息
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    payment_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 第三方支付流水号
    
    # 收货信息
    receiver_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    receiver_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    receiver_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 备注
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # 关系
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan")


class OrderItem(Base):
    """订单商品项"""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    
    # 商品信息
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 价格信息（单位：分）
    unit_price: Mapped[int] = mapped_column(Integer, nullable=False)   # 单价
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)      # 数量
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)   # 小计
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    order: Mapped["Order"] = relationship("Order", back_populates="items")
