from typing import Any, Optional, TypeVar, Generic
from fastapi.responses import JSONResponse

T = TypeVar("T")


def success_response(data: Any = None, message: str = "success", code: int = 200) -> JSONResponse:
    """成功响应"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )


def error_response(message: str = "error", code: int = 400, data: Any = None) -> JSONResponse:
    """错误响应"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )
