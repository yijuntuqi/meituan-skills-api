"""
异步任务内存存储（酒旅查询耗时长，用 task_id 轮询）
"""
import asyncio
import time
import uuid
from typing import Any, Dict, Optional


class TaskStore:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self) -> str:
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "status": "pending",
            "result": None,
            "error": None,
            "created_at": time.time(),
        }
        return task_id

    def update_task(self, task_id: str, *, status: str, result: Any = None, error: Optional[str] = None):
        if task_id in self._tasks:
            self._tasks[task_id]["status"] = status
            self._tasks[task_id]["result"] = result
            self._tasks[task_id]["error"] = error

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def cleanup_old(self, ttl_seconds: int = 3600):
        """清理超过 TTL 的任务"""
        now = time.time()
        expired = [tid for tid, t in self._tasks.items() if now - t["created_at"] > ttl_seconds]
        for tid in expired:
            del self._tasks[tid]


task_store = TaskStore()
