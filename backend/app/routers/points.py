from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.common import ResponseModel
from app.dependencies.auth import get_current_user
from app.config import POINTS_CONFIG

router = APIRouter()


@router.get("/rules", response_model=ResponseModel[dict])
async def get_points_rules():
    """获取积分规则"""
    return ResponseModel(
        code=200,
        message="success",
        data={
            "register_bonus": POINTS_CONFIG["register_bonus"],
            "order_ratio": POINTS_CONFIG["order_ratio"],
            "referral_bonus": POINTS_CONFIG["referral_bonus"],
            "exchange_rate": "1积分 = 0.01元",
            "rules": [
                {"action": "新用户注册", "points": f"+{POINTS_CONFIG['register_bonus']}"},
                {"action": "消费返积分", "points": f"消费1元返{POINTS_CONFIG['order_ratio']}积分"},
                {"action": "推荐好友", "points": f"+{POINTS_CONFIG['referral_bonus']}"},
            ]
        }
    )


@router.post("/redeem", response_model=ResponseModel[dict])
async def redeem_points(
    points: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """积分兑换（预留接口）"""
    # TODO: 实现积分兑换逻辑
    return ResponseModel(
        code=200,
        message="积分兑换功能开发中",
        data={
            "points": points,
            "available": current_user.points
        }
    )
