"""
美团跑腿 Skill 封装
Node 脚本: node paotui.js <command> [args]
依赖环境变量: MCP_ACCESS_TOKEN (passport token), MEITUAN_PAOTUI_SOURCE_FROM
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import settings
from .base import BaseSkill, SkillResult


class PaotuiSkill(BaseSkill):
    skill_dir = settings.SKILLS_DIR / "meituan-paotui"

    @property
    def _node_script(self) -> str:
        return str(self.skill_dir / "paotui.js")

    def _env(self, access_token: Optional[str] = None) -> Dict[str, str]:
        token = access_token or settings.MCP_ACCESS_TOKEN
        return self.merge_env({
            "MCP_ACCESS_TOKEN": token,
            "MEITUAN_PAOTUI_SOURCE_FROM": settings.MEITUAN_PAOTUI_SOURCE_FROM,
        })

    async def _run(self, args: list, access_token: Optional[str] = None) -> SkillResult:
        cmd = ["node", self._node_script, *args]
        return await self.run_cmd(
            cmd,
            cwd=self.skill_dir,
            env=self._env(access_token),
            timeout=settings.PAOTUI_TIMEOUT,
        )

    async def login(self, access_token: Optional[str] = None) -> SkillResult:
        """检查鉴权状态"""
        return await self._run(["login"], access_token)

    async def search_poi(
        self,
        keyword: str,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        access_token: Optional[str] = None,
    ) -> SkillResult:
        """POI 地址搜索"""
        args = ["search_poi", "--keyword", keyword]
        if city:
            args += ["--city", city]
        if lat is not None:
            args += ["--lat", str(lat)]
        if lng is not None:
            args += ["--lng", str(lng)]
        return await self._run(args, access_token)

    async def get_address_list(self, access_token: Optional[str] = None) -> SkillResult:
        """获取用户地址簿"""
        return await self._run(["get_address_list"], access_token)

    async def preview_order(
        self,
        sender: Dict[str, Any],
        recipient: Dict[str, Any],
        goods: Dict[str, Any],
        business_type: int = 1,
        tip_fee: int = 0,
        remark: str = "",
        purchase_detail: str = "",
        access_token: Optional[str] = None,
    ) -> SkillResult:
        """订单预览（不下单）"""
        args = [
            "preview_and_submit",
            "--sender", json.dumps(sender, ensure_ascii=False),
            "--recipient", json.dumps(recipient, ensure_ascii=False),
            "--goods", json.dumps(goods, ensure_ascii=False),
            "--business-type", str(business_type),
            "--tip-fee", str(tip_fee),
            "--remark", remark,
        ]
        if purchase_detail:
            args += ["--purchase-detail", purchase_detail]
        return await self._run(args, access_token)

    async def submit_order(
        self,
        sender: Dict[str, Any],
        recipient: Dict[str, Any],
        goods: Dict[str, Any],
        business_type: int = 1,
        tip_fee: int = 0,
        remark: str = "",
        purchase_detail: str = "",
        access_token: Optional[str] = None,
    ) -> SkillResult:
        """确认下单（真实提交订单！）"""
        args = [
            "preview_and_submit",
            "--sender", json.dumps(sender, ensure_ascii=False),
            "--recipient", json.dumps(recipient, ensure_ascii=False),
            "--goods", json.dumps(goods, ensure_ascii=False),
            "--business-type", str(business_type),
            "--tip-fee", str(tip_fee),
            "--remark", remark,
            "--confirm",
        ]
        if purchase_detail:
            args += ["--purchase-detail", purchase_detail]
        return await self._run(args, access_token)

    async def get_order_status(self, order_id: str, access_token: Optional[str] = None) -> SkillResult:
        """查询订单状态"""
        return await self._run(["get_order_status", "--order-id", order_id], access_token)


paotui_skill = PaotuiSkill()
