"""
环境变量与全局配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # API 鉴权
    API_KEY: str = os.getenv("API_KEY", "change-me-please")

    # 美团酒旅 Skill
    MEITUAN_HT_TOKEN: str = os.getenv("MEITUAN_HT_TOKEN", "")

    # 美团跑腿 Skill（passport token，可选，也可由调用方动态传入）
    MCP_ACCESS_TOKEN: str = os.getenv("MCP_ACCESS_TOKEN", "")

    # 美团跑腿 Skill 来源渠道
    MEITUAN_PAOTUI_SOURCE_FROM: str = os.getenv("MEITUAN_PAOTUI_SOURCE_FROM", "aihub")

    # Skill 根目录
    SKILLS_DIR: Path = BASE_DIR / "skills"

    # 领券 Skill 的 Python 解释器路径（默认用系统 python）
    COUPON_PYTHON: str = os.getenv("COUPON_PYTHON", "python")

    # 酒旅查询超时（秒），官方说 1-2 分钟，给 180s
    TRAVEL_TIMEOUT: int = int(os.getenv("TRAVEL_TIMEOUT", "180"))

    # 跑腿命令超时（秒）
    PAOTUI_TIMEOUT: int = int(os.getenv("PAOTUI_TIMEOUT", "60"))

    # 领券命令超时（秒）
    COUPON_TIMEOUT: int = int(os.getenv("COUPON_TIMEOUT", "60"))


settings = Settings()
