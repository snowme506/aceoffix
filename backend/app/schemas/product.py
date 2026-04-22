from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., description="商品名称")
    subtitle: Optional[str] = Field(None, description="副标题")
    description: Optional[str] = Field(None, description="商品描述")
    price: int = Field(..., ge=0, description="售价（分）")
    original_price: Optional[int] = Field(None, ge=0, description="原价（分）")
    stock: int = Field(default=0, ge=0, description="库存")
    category_id: int = Field(..., description="分类ID")
    images: Optional[List[str]] = Field(default=[], description="图片列表")
    specs: Optional[List[dict]] = Field(default=[], description="规格参数")
    status: int = Field(default=1, description="状态: 1上架 0下架")
    sort_order: int = Field(default=0, description="排序")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, description="商品名称")
    subtitle: Optional[str] = Field(None, description="副标题")
    description: Optional[str] = Field(None, description="商品描述")
    price: Optional[int] = Field(None, ge=0, description="售价（分）")
    original_price: Optional[int] = Field(None, ge=0, description="原价（分）")
    stock: Optional[int] = Field(None, ge=0, description="库存")
    category_id: Optional[int] = Field(None, description="分类ID")
    images: Optional[List[str]] = Field(None, description="图片列表")
    specs: Optional[List[Any]] = Field(None, description="规格参数")
    status: Optional[int] = Field(None, description="状态")
    sort_order: Optional[int] = Field(None, description="排序")


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    category_name: Optional[str] = Field(None, description="分类名称")

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    total: int
    items: list[ProductResponse]

    class Config:
        from_attributes = True
