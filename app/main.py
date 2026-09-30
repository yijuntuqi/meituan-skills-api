"""
美团 Skills API Gateway — FastAPI 入口
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .auth import verify_api_key
from .routers import travel, coupon, paotui

app = FastAPI(
    title="美团 Skills API Gateway",
    description="将美团官方 Skills（酒旅/领券/跑腿）封装为统一 HTTP API",
    version="1.0.0",
)

# CORS 全开（本地自用场景）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["系统"])
async def health():
    """健康检查"""
    return {"status": "ok", "service": "meituan-skills-api"}


# 所有业务路由统一要求 API Key
app.include_router(travel.router, dependencies=[Depends(verify_api_key)])
app.include_router(coupon.router, dependencies=[Depends(verify_api_key)])
app.include_router(paotui.router, dependencies=[Depends(verify_api_key)])
