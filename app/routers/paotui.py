"""
美团跑腿路由
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from ..skills.paotui import paotui_skill

router = APIRouter(prefix="/api/paotui", tags=["跑腿"])


class PoiSearchRequest(BaseModel):
    keyword: str
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class OrderRequest(BaseModel):
    sender: Dict[str, Any]
    recipient: Dict[str, Any]
    goods: Dict[str, Any]
    business_type: int = 1
    tip_fee: int = 0
    remark: str = ""
    purchase_detail: str = ""


@router.get("/auth/status", summary="查询跑腿登录状态")
async def paotui_login_status(x_access_token: Optional[str] = Header(None, alias="X-Access-Token")):
    r = await paotui_skill.login(access_token=x_access_token)
    return r.to_dict()


@router.post("/poi/search", summary="POI 地址搜索")
async def paotui_search_poi(
    req: PoiSearchRequest,
    x_access_token: Optional[str] = Header(None, alias="X-Access-Token"),
):
    r = await paotui_skill.search_poi(
        keyword=req.keyword,
        city=req.city,
        lat=req.lat,
        lng=req.lng,
        access_token=x_access_token,
    )
    return r.to_dict()


@router.get("/address-list", summary="获取地址簿")
async def paotui_address_list(x_access_token: Optional[str] = Header(None, alias="X-Access-Token")):
    r = await paotui_skill.get_address_list(access_token=x_access_token)
    return r.to_dict()


@router.post("/order/preview", summary="订单预览（不下单）")
async def paotui_order_preview(
    req: OrderRequest,
    x_access_token: Optional[str] = Header(None, alias="X-Access-Token"),
):
    r = await paotui_skill.preview_order(
        sender=req.sender,
        recipient=req.recipient,
        goods=req.goods,
        business_type=req.business_type,
        tip_fee=req.tip_fee,
        remark=req.remark,
        purchase_detail=req.purchase_detail,
        access_token=x_access_token,
    )
    return r.to_dict()


@router.post("/order/submit", summary="确认下单（真实提交！）")
async def paotui_order_submit(
    req: OrderRequest,
    x_access_token: Optional[str] = Header(None, alias="X-Access-Token"),
):
    r = await paotui_skill.submit_order(
        sender=req.sender,
        recipient=req.recipient,
        goods=req.goods,
        business_type=req.business_type,
        tip_fee=req.tip_fee,
        remark=req.remark,
        purchase_detail=req.purchase_detail,
        access_token=x_access_token,
    )
    return r.to_dict()


@router.get("/order/{order_id}", summary="查询订单状态")
async def paotui_order_status(
    order_id: str,
    x_access_token: Optional[str] = Header(None, alias="X-Access-Token"),
):
    r = await paotui_skill.get_order_status(order_id, access_token=x_access_token)
    return r.to_dict()
