from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/list", response_model=ResponseModel[CategoryListResponse])
async def admin_list_categories(
    params: PaginationParams = Depends(),
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-分类列表"""
    total = db.query(Category).count()
    categories = db.query(Category).order_by(Category.sort_order).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data=CategoryListResponse(
            total=total,
            items=[CategoryResponse.model_validate(c) for c in categories]
        )
    )


@router.get("/detail/{category_id}", response_model=ResponseModel[CategoryResponse])
async def admin_get_category(
    category_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-分类详情"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return ResponseModel(code=200, message="success", data=CategoryResponse.model_validate(category))


@router.post("/create", response_model=ResponseModel[CategoryResponse])
async def admin_create_category(
    request: CategoryCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-创建分类"""
    category = Category(**request.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return ResponseModel(code=200, message="创建成功", data=CategoryResponse.model_validate(category))


@router.put("/update/{category_id}", response_model=ResponseModel[CategoryResponse])
async def admin_update_category(
    category_id: int,
    request: CategoryUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-更新分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return ResponseModel(code=200, message="更新成功", data=CategoryResponse.model_validate(category))


@router.delete("/delete/{category_id}", response_model=ResponseModel[dict])
async def admin_delete_category(
    category_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-删除分类"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    
    db.delete(category)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": category_id})
