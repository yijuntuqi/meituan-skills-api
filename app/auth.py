"""
API Key 鉴权中间件
"""
from typing import Optional

from fastapi import Header, HTTPException, status
from .config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """校验请求头中的 X-API-Key，缺失或错误均返回 401"""
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API Key (set X-API-Key header)",
        )
    return x_api_key
