"""
美团领券路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..skills.coupon import coupon_skill

router = APIRouter(prefix="/api/coupon", tags=["领券"])


class SendSmsRequest(BaseModel):
    phone: str


class VerifyRequest(BaseModel):
    phone: str
    code: str


@router.get("/auth/status", summary="查询领券登录状态")
async def coupon_auth_status():
    r = await coupon_skill.auth_status()
    return r.to_dict()


@router.post("/auth/send-sms", summary="发送短信验证码")
async def coupon_send_sms(req: SendSmsRequest):
    r = await coupon_skill.send_sms(req.phone)
    return r.to_dict()


@router.post("/auth/verify", summary="验证码登录")
async def coupon_verify(req: VerifyRequest):
    r = await coupon_skill.verify(req.phone, req.code)
    return r.to_dict()


@router.post("/auth/logout", summary="退出登录")
async def coupon_logout():
    r = await coupon_skill.logout()
    return r.to_dict()


@router.post("/issue", summary="一键领券（需先登录）")
async def coupon_issue():
    r = await coupon_skill.issue()
    return r.to_dict()
