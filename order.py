from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.order import OrderStatus, PaymentStatus


class OrderItemCreate(BaseModel):
    """创建订单商品项"""
    product_id: int = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    product_image: Optional[str] = Field(None, description="商品图片")
    unit_price: int = Field(..., ge=0, description="单价（分）")
    quantity: int = Field(..., ge=1, description="数量")


class OrderItemResponse(BaseModel):
    """订单商品项响应"""
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str]
    unit_price: int
    quantity: int
    total_price: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """创建订单"""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="订单商品列表")
    points_used: int = Field(default=0, ge=0, description="使用积分")
    discount_amount: int = Field(default=0, ge=0, description="优惠金额（分）")
    receiver_name: Optional[str] = Field(None, description="收货人姓名")
    receiver_phone: Optional[str] = Field(None, description="收货人电话")
    receiver_address: Optional[str] = Field(None, description="收货地址")
    remark: Optional[str] = Field(None, description="订单备注")


class OrderResponse(BaseModel):
    """订单简要响应"""
    id: int
    order_no: str
    total_amount: int
    discount_amount: int
    points_used: int
    points_discount: int
    final_amount: int
    status: OrderStatus
    payment_status: PaymentStatus
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    """订单详情响应"""
    id: int
    order_no: str
    total_amount: int
    discount_amount: int
    points_used: int
    points_discount: int
    final_amount: int
    status: OrderStatus
    payment_status: PaymentStatus
    paid_at: Optional[datetime]
    payment_method: Optional[str]
    receiver_name: Optional[str]
    receiver_phone: Optional[str]
    receiver_address: Optional[str]
    remark: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应"""
    total: int
    items: List[OrderResponse]
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """支付请求"""
    order_id: int = Field(..., description="订单ID")
    payment_method: str = Field(default="mock", description="支付方式: mock/wechat/alipay")


class PaymentResponse(BaseModel):
    """支付响应"""
    order_id: int
    order_no: str
    payment_status: PaymentStatus
    paid_at: Optional[datetime]
    message: str
    
    class Config:
        from_attributes = True
