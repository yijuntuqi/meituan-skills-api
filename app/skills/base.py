"""
子进程调用基类：统一封装 subprocess 调用、超时、错误处理、JSON 解析
"""
import asyncio
import json
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

# Windows 下 npx 是 npx.cmd 批处理文件，create_subprocess_exec 不会自动解析 PATHEXT
_IS_WINDOWS = platform.system() == "Windows"
_CMD_ALIASES = {"npx": "npx.cmd", "npm": "npm.cmd"}


def _resolve_executable(cmd: List[str]) -> List[str]:
    # Windows 下 .cmd 批处理必须经 cmd.exe /c 启动，CreateProcess 无法直接执行
    if _IS_WINDOWS and cmd and cmd[0] in _CMD_ALIASES:
        return ["cmd.exe", "/c", _CMD_ALIASES[cmd[0]], *cmd[1:]]
    return cmd


class SkillResult:
    """子进程执行结果"""

    def __init__(self, ok: bool, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.ok = ok
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def parse_json(self) -> Optional[Any]:
        """尝试将 stdout 解析为 JSON"""
        if not self.stdout.strip():
            return None
        try:
            return json.loads(self.stdout)
        except json.JSONDecodeError:
            return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


class BaseSkill:
    """Skill 封装基类"""

    skill_dir: Path  # 子类设置

    async def run_cmd(
        self,
        cmd: List[str],
        *,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 60,
    ) -> SkillResult:
        """异步执行命令，返回 SkillResult"""
        cmd = _resolve_executable(cmd)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return SkillResult(ok=False, stderr=f"Command timed out after {timeout}s")

        stdout_str = stdout.decode("utf-8", errors="replace").strip()
        stderr_str = stderr.decode("utf-8", errors="replace").strip()
        return SkillResult(
            ok=proc.returncode == 0,
            stdout=stdout_str,
            stderr=stderr_str,
            returncode=proc.returncode or 0,
        )

    @staticmethod
    def merge_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """合并当前环境变量与额外变量"""
        import os

        env = os.environ.copy()
        if extra:
            env.update(extra)
        return env
