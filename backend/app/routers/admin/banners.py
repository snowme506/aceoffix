from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.banner import Banner
from app.schemas.banner import BannerCreate, BannerUpdate, BannerResponse, BannerListResponse
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/list", response_model=ResponseModel[BannerListResponse])
async def admin_list_banners(
    params: PaginationParams = Depends(),
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-轮播图列表"""
    total = db.query(Banner).count()
    banners = db.query(Banner).order_by(Banner.sort_order).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()

    return ResponseModel(
        code=200,
        message="success",
        data=BannerListResponse(
            total=total,
            items=[BannerResponse.model_validate(b) for b in banners]
        )
    )


@router.post("/create", response_model=ResponseModel[BannerResponse])
async def admin_create_banner(
    request: BannerCreate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-创建轮播图"""
    banner = Banner(**request.model_dump())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return ResponseModel(code=200, message="创建成功", data=BannerResponse.model_validate(banner))


@router.put("/update/{banner_id}", response_model=ResponseModel[BannerResponse])
async def admin_update_banner(
    banner_id: int,
    request: BannerUpdate,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-更新轮播图"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="轮播图不存在")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(banner, field, value)

    db.commit()
    db.refresh(banner)
    return ResponseModel(code=200, message="更新成功", data=BannerResponse.model_validate(banner))


@router.delete("/delete/{banner_id}", response_model=ResponseModel[dict])
async def admin_delete_banner(
    banner_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-删除轮播图"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="轮播图不存在")

    db.delete(banner)
    db.commit()
    return ResponseModel(code=200, message="删除成功", data={"id": banner_id})
