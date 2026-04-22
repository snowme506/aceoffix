from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdminUser
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse, AdminUserResponse
from app.schemas.common import ResponseModel
from app.utils.security import verify_password, create_access_token
from app.dependencies.admin import get_current_admin

router = APIRouter()


@router.post("/login", response_model=ResponseModel[AdminLoginResponse])
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    admin = db.query(AdminUser).filter(AdminUser.username == request.username).first()
    
    if not admin or not verify_password(request.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 更新最后登录时间
    admin.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({
        "sub": str(admin.id),
        "role": "admin",
        "username": admin.username
    })
    
    return ResponseModel(
        code=200,
        message="登录成功",
        data=AdminLoginResponse(
            access_token=access_token,
            token_type="bearer",
            admin=AdminUserResponse.model_validate(admin)
        )
    )


@router.get("/profile", response_model=ResponseModel[AdminUserResponse])
async def get_admin_profile(current_admin: AdminUser = Depends(get_current_admin)):
    """获取当前管理员信息"""
    return ResponseModel(
        code=200,
        message="success",
        data=AdminUserResponse.model_validate(current_admin)
    )
