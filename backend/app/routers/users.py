from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserPointsLog
from app.schemas.user import UserProfile, PointsLogResponse, PointsLogItem
from app.schemas.common import ResponseModel, PaginationParams
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.get("/profile", response_model=ResponseModel[UserProfile])
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户个人资料"""
    return ResponseModel(
        code=200,
        message="success",
        data=UserProfile.model_validate(current_user)
    )


@router.get("/points/logs", response_model=ResponseModel[PointsLogResponse])
async def get_points_logs(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取积分明细"""
    # 查询总记录数
    total = db.query(UserPointsLog).filter(
        UserPointsLog.user_id == current_user.id
    ).count()
    
    # 查询记录
    logs = db.query(UserPointsLog).filter(
        UserPointsLog.user_id == current_user.id
    ).order_by(UserPointsLog.created_at.desc()).offset(
        (params.page - 1) * params.page_size
    ).limit(params.page_size).all()
    
    return ResponseModel(
        code=200,
        message="success",
        data=PointsLogResponse(
            total=total,
            items=[PointsLogItem.model_validate(log) for log in logs]
        )
    )


@router.get("/points/balance", response_model=ResponseModel[dict])
async def get_points_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前积分余额"""
    return ResponseModel(
        code=200,
        message="success",
        data={
            "points": current_user.points,
            "total_spent": current_user.total_spent
        }
    )
