from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse
from app.schemas.common import ResponseModel

router = APIRouter()


@router.get("/list", response_model=ResponseModel[list[CategoryResponse]])
async def get_categories(db: Session = Depends(get_db)):
    """获取分类列表"""
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.sort_order).all()
    return ResponseModel(
        code=200,
        message="获取成功",
        data=[CategoryResponse.model_validate(c) for c in categories]
    )
