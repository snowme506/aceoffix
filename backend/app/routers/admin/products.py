from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/list", response_model=ResponseModel[ProductListResponse])
async def admin_list_products(
    params: PaginationParams = Depends(),
    category_id: int = None,
    keyword: str = None,
    status: int = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-商品列表"""
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if keyword:
        query = query.filter(Product.name.contains(keyword))
    if status is not None:
        query = query.filter(Product.status == status)
    
    total = query.count()
    products = query.order_by(Product.id.desc()).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data=ProductListResponse(
            total=total,
            items=[ProductResponse.model_validate(p) for p in products]
        )
    )


@router.get("/detail/{product_id}", response_model=ResponseModel[ProductResponse])
async def admin_get_product(
    product_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-商品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    return ResponseModel(code=200, message="success", data=ProductResponse.model_validate(product))


@router.post("/create", response_model=ResponseModel[ProductResponse])
async def admin_create_product(
    request: ProductCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-创建商品"""
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return ResponseModel(code=200, message="创建成功", data=ProductResponse.model_validate(product))


@router.put("/update/{product_id}", response_model=ResponseModel[ProductResponse])
async def admin_update_product(
    product_id: int,
    request: ProductUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-更新商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return ResponseModel(code=200, message="更新成功", data=ProductResponse.model_validate(product))


@router.delete("/delete/{product_id}", response_model=ResponseModel[dict])
async def admin_delete_product(
    product_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-删除商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")
    
    db.delete(product)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": product_id})
