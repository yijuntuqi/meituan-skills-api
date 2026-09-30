"""
美团酒旅 Skill 封装
CLI: npx @meituan-travel/ht-ai query --query '<query>' --origin-query '<origin>' --channel meituan-developer [-o json]
依赖环境变量: MEITUAN_HT_TOKEN
"""
from pathlib import Path
from typing import Optional

from ..config import settings
from .base import BaseSkill, SkillResult


class TravelSkill(BaseSkill):
    skill_dir = settings.SKILLS_DIR / "meituan-travel"

    async def query(
        self,
        query: str,
        origin_query: Optional[str] = None,
        city: Optional[str] = None,
        raw_json: bool = False,
    ) -> SkillResult:
        """
        发起酒旅查询（耗时 1-2 分钟）
        :param query: 自然语言查询
        :param origin_query: 原始查询（用于统计，默认同 query）
        :param city: 城市，默认北京
        :param raw_json: 是否返回原始 JSON，默认 Markdown
        """
        if origin_query is None:
            origin_query = query

        cmd = [
            "npx", "@meituan-travel/ht-ai@latest", "query",
            "--query", query,
            "--origin-query", origin_query,
            "--channel", "meituan-developer",
        ]
        if city:
            cmd += ["--city", city]
        if raw_json:
            cmd += ["-o", "json"]

        env = self.merge_env({"MEITUAN_HT_TOKEN": settings.MEITUAN_HT_TOKEN})
        return await self.run_cmd(
            cmd,
            cwd=self.skill_dir,
            env=env,
            timeout=settings.TRAVEL_TIMEOUT,
        )


travel_skill = TravelSkill()
