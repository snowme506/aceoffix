from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductDetailResponse, ProductListResponse
from app.schemas.common import ResponseModel, PaginationParams

router = APIRouter()


@router.get("/list", response_model=ResponseModel[ProductListResponse])
async def get_products(
    params: PaginationParams = Depends(),
    category_id: Optional[int] = None,
    keyword: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取商品列表（支持分类、关键词、价格筛选）"""
    query = db.query(Product).filter(Product.status == 1)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if keyword:
        query = query.filter(Product.name.contains(keyword))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    total = query.count()
    products = query.order_by(Product.sort_order, Product.id.desc()).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=ProductListResponse(
            total=total,
            items=[ProductResponse.model_validate(p) for p in products]
        )
    )


@router.get("/detail/{product_id}", response_model=ResponseModel[ProductDetailResponse])
async def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """获取商品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    
    data = ProductResponse.model_validate(product).model_dump()
    data["category_name"] = product.category.name if product.category else None
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=ProductDetailResponse(**data)
    )
