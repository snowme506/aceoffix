from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.common import ResponseModel, PaginationParams
from app.schemas.admin import AdminUpdateMemberRequest
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.get("/list", response_model=ResponseModel[dict])
async def admin_list_members(
    params: PaginationParams = Depends(),
    keyword: str = None,
    member_level: str = None,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-会员列表"""
    query = db.query(User)
    if keyword:
        query = query.filter(User.phone.contains(keyword) | User.nickname.contains(keyword))
    if member_level:
        query = query.filter(User.member_level == member_level)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "total": total,
            "items": [UserResponse.model_validate(u) for u in users]
        }
    )


@router.get("/detail/{user_id}", response_model=ResponseModel[UserResponse])
async def admin_get_member(
    user_id: int,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-会员详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会员不存在")
    return ResponseModel(code=200, message="success", data=UserResponse.model_validate(user))


@router.put("/update/{user_id}", response_model=ResponseModel[UserResponse])
async def admin_update_member(
    user_id: int,
    request: AdminUpdateMemberRequest,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """后台-更新会员信息（积分、等级、状态）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会员不存在")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return ResponseModel(code=200, message="更新成功", data=UserResponse.model_validate(user))
