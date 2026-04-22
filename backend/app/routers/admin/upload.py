import os
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.admin import get_current_admin
from app.schemas.common import ResponseModel

router = APIRouter()

# 上传目录
UPLOAD_DIR = "/opt/aceoffix/frontend/img/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image", response_model=ResponseModel[dict])
async def upload_image(
    file: UploadFile = File(...),
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """上传商品图片"""
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式，仅支持：{', '.join(ALLOWED_EXTENSIONS)}")

    # 生成唯一文件名
    timestamp = int(time.time() * 1000)
    unique_name = f"{timestamp}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # 读取并保存文件
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过5MB")

    with open(file_path, "wb") as f:
        f.write(contents)

    # 返回访问路径
    url = f"/img/uploads/{unique_name}"
    return ResponseModel(code=200, message="上传成功", data={"url": url})
