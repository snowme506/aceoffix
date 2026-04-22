from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.store import Store
from app.models.banner import Banner
from app.schemas.common import ResponseModel, PaginationParams

router = APIRouter()


@router.get("/home", response_model=ResponseModel[dict])
async def get_home_data(db: Session = Depends(get_db)):
    """获取首页数据（轮播、分类、热卖商品）"""
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.sort_order).all()
    products = db.query(Product).filter(Product.status == 1).order_by(Product.id.desc()).limit(8).all()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "categories": [
                {"id": c.id, "name": c.name, "icon": c.icon}
                for c in categories
            ],
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "subtitle": p.subtitle,
                    "price": p.price,
                    "original_price": p.original_price,
                    "stock": p.stock,
                    "category_id": p.category_id,
                    "images": p.images if p.images else [],
                    "specs": p.specs if p.specs else []
                }
                for p in products
            ],
            "banners": [
                {"id": b.id, "image": b.image_url, "title": b.title, "link": b.link_url}
                for b in db.query(Banner).filter(Banner.is_active == True).order_by(Banner.sort_order).all()
            ]
        }
    )


@router.get("/products", response_model=ResponseModel[dict])
async def get_products(
    category_id: int = None,
    params: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """获取商品列表（支持分类筛选）"""
    page = params.page
    page_size = params.page_size

    query = db.query(Product).filter(Product.status == 1)

    if category_id:
        query = query.filter(Product.category_id == category_id)

    total = query.count()
    products = query.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": p.id,
                    "name": p.name,
                    "subtitle": p.subtitle,
                    "price": p.price,
                    "original_price": p.original_price,
                    "stock": p.stock,
                    "category_id": p.category_id,
                    "images": p.images if p.images else [],
                    "specs": p.specs if p.specs else []
                }
                for p in products
            ]
        }
    )


@router.get("/stores", response_model=ResponseModel[dict])
async def get_stores(db: Session = Depends(get_db)):
    """获取门店列表"""
    stores = db.query(Store).filter(Store.status == 1).order_by(Store.sort_order).all()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "items": [
                {
                    "id": s.id,
                    "name": s.name,
                    "province": s.province,
                    "city": s.city,
                    "district": s.district,
                    "address": s.address,
                    "phone": s.phone,
                    "hours": s.hours,
                    "status": s.status
                }
                for s in stores
            ]
        }
    )


@router.get("/banners", response_model=ResponseModel[dict])
async def get_banners(db: Session = Depends(get_db)):
    """获取启用的轮播图列表"""
    banners = db.query(Banner).filter(Banner.is_active == True).order_by(Banner.sort_order).all()
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={
            "items": [
                {
                    "id": b.id,
                    "image_url": b.image_url,
                    "link_url": b.link_url,
                    "title": b.title,
                    "sort_order": b.sort_order,
                    "is_active": b.is_active
                }
                for b in banners
            ]
        }
    )
