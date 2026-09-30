"""
美团分销领券 Skill 封装
认证脚本: python auth.py <command>
发券脚本: python issue.py --token <user_token>
凭证存储: ~/.xiaomei-workspace/auth_tokens.json（脚本自行读写）
"""
from pathlib import Path
from typing import Optional

from ..config import settings
from .base import BaseSkill, SkillResult


class CouponSkill(BaseSkill):
    skill_dir = settings.SKILLS_DIR / "meituan-fenxiao-promotion-coupon"

    @property
    def _scripts_dir(self) -> Path:
        return self.skill_dir / "scripts"

    @property
    def _python(self) -> str:
        return settings.COUPON_PYTHON

    async def _run_auth(self, args: list) -> SkillResult:
        cmd = [self._python, str(self._scripts_dir / "auth.py"), *args]
        return await self.run_cmd(
            cmd,
            cwd=self.skill_dir,
            timeout=settings.COUPON_TIMEOUT,
        )

    async def _run_issue(self, token: str) -> SkillResult:
        cmd = [self._python, str(self._scripts_dir / "issue.py"), "--token", token]
        return await self.run_cmd(
            cmd,
            cwd=self.skill_dir,
            timeout=settings.COUPON_TIMEOUT,
        )

    async def auth_status(self) -> SkillResult:
        """查询认证状态"""
        return await self._run_auth(["status"])

    async def token_verify(self) -> SkillResult:
        """校验本地 token 是否有效，返回 {valid, user_token, phone_masked}"""
        return await self._run_auth(["token-verify"])

    async def send_sms(self, phone: str) -> SkillResult:
        """发送短信验证码"""
        return await self._run_auth(["send-sms", "--phone", phone])

    async def verify(self, phone: str, code: str) -> SkillResult:
        """验证码登录"""
        return await self._run_auth(["verify", "--phone", phone, "--code", code])

    async def logout(self) -> SkillResult:
        """退出登录（清除 user_token，保留 device_token）"""
        return await self._run_auth(["logout"])

    async def clear_device_token(self) -> SkillResult:
        """清除设备标识（同时清除 user_token）"""
        return await self._run_auth(["clear-device-token"])

    async def issue(self) -> SkillResult:
        """
        一键领券：自动读取本地 user_token 并调用发券脚本。
        需要先完成短信登录（verify）。
        """
        # 先校验 token
        verify_result = await self.token_verify()
        if not verify_result.ok:
            return verify_result

        data = verify_result.parse_json()
        if not data or not data.get("valid"):
            return SkillResult(ok=False, stderr="Token 无效或未登录，请先完成短信登录")

        user_token = data.get("user_token")
        if not user_token:
            return SkillResult(ok=False, stderr="未获取到 user_token")

        return await self._run_issue(user_token)


coupon_skill = CouponSkill()
