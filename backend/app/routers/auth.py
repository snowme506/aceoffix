from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User, MemberLevel, UserPointsLog
from app.schemas.user import UserResponse
from app.schemas.common import ResponseModel
from app.utils.security import create_access_token
from app.config import MOCK_SMS_CODE, SMS_CODE_EXPIRE_MINUTES, POINTS_CONFIG

router = APIRouter()

# 内存存储验证码（生产环境应使用Redis）
sms_code_storage: dict[str, datetime] = {}
# 发送记录（用于频率限制）
sms_send_times: dict[str, list[datetime]] = {}


class SendCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")


class LoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="验证码")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/send-code", response_model=ResponseModel[dict])
async def send_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    """发送验证码（Mock）"""
    now = datetime.utcnow()

    # 清理过期验证码
    expired_phones = [p for p, exp in sms_code_storage.items() if now > exp]
    for p in expired_phones:
        sms_code_storage.pop(p, None)

    # 频率限制：同一手机号60秒内只能发一次
    if request.phone in sms_send_times:
        recent = [t for t in sms_send_times[request.phone] if (now - t).total_seconds() < 60]
        if recent:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="发送太频繁，请稍后再试"
            )
        sms_send_times[request.phone] = recent
    else:
        sms_send_times[request.phone] = []

    sms_send_times[request.phone].append(now)

    # 存储验证码及过期时间
    expire_at = now + timedelta(minutes=SMS_CODE_EXPIRE_MINUTES)
    sms_code_storage[request.phone] = expire_at

    # Mock: 直接返回验证码（实际应调用短信服务）
    return ResponseModel(
        code=200,
        message="验证码已发送",
        data={
            "phone": request.phone,
            "expire_seconds": SMS_CODE_EXPIRE_MINUTES * 60,
            "mock_code": MOCK_SMS_CODE  # 仅开发环境返回
        }
    )


@router.post("/login", response_model=ResponseModel[LoginResponse])
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """手机号登录"""
    # 验证验证码
    expire_at = sms_code_storage.get(request.phone)
    if not expire_at or datetime.utcnow() > expire_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期"
        )
    
    if request.code != MOCK_SMS_CODE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 查找或创建用户
    user = db.query(User).filter(User.phone == request.phone).first()
    is_new_user = False
    
    if not user:
        # 新用户注册
        user = User(
            phone=request.phone,
            member_level=MemberLevel.NORMAL,
            points=0,
            total_spent=0,
            is_active=True
        )
        db.add(user)
        db.flush()  # 获取user.id
        is_new_user = True
        
        # 赠送注册积分
        register_bonus = POINTS_CONFIG["register_bonus"]
        if register_bonus > 0:
            user.points = register_bonus
            points_log = UserPointsLog(
                user_id=user.id,
                change_amount=register_bonus,
                current_balance=register_bonus,
                type="register",
                description="新用户注册奖励"
            )
            db.add(points_log)
    
    db.commit()
    db.refresh(user)
    
    # 清理验证码
    sms_code_storage.pop(request.phone, None)
    
    # 生成JWT
    access_token = create_access_token({"sub": str(user.id), "phone": user.phone})
    
    return ResponseModel(
        code=200,
        message="登录成功" if not is_new_user else "注册成功",
        data=LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    )
