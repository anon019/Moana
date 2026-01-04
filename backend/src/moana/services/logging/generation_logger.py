# src/moana/services/logging/generation_logger.py
"""生成过程日志记录器.

提供结构化的日志记录 API，用于跟踪内容生成的每个步骤。
支持异步和同步操作，自动记录耗时和错误信息。
"""
import asyncio
import json
import logging
import time
import traceback
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import text as sql_text

from moana.database import get_session_factory
from moana.models.generation_log import GenerationStep, LogLevel

logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """步骤执行结果."""
    success: bool
    output: dict = field(default_factory=dict)
    error: Optional[str] = None
    duration: float = 0.0


class GenerationLogger:
    """生成过程日志记录器.

    用法示例:
    ```python
    gen_logger = GenerationLogger(task_id="xxx")

    # 记录单个步骤
    await gen_logger.log_step(
        step=GenerationStep.STORY_GENERATE,
        message="生成故事大纲",
        input_params={"theme": "刷牙", "child_name": "小明"},
        output_result={"title": "小明爱刷牙", "pages": [...]},
        duration=2.5
    )

    # 使用上下文管理器自动记录耗时
    async with gen_logger.step(GenerationStep.IMAGE_GENERATE, "生成第1页图片") as step:
        step.input_params = {"prompt": "..."}
        result = await image_service.generate(...)
        step.output_result = {"url": result.url}
    ```
    """

    def __init__(self, task_id: str, content_id: Optional[str] = None):
        """初始化日志记录器.

        Args:
            task_id: 异步任务 ID
            content_id: 关联的内容 ID（可选，生成完成后更新）
        """
        self.task_id = task_id
        self.content_id = content_id
        self._sequence = 0
        self._session_factory = get_session_factory()

    async def log_step(
        self,
        step: GenerationStep,
        message: str,
        input_params: Optional[dict] = None,
        output_result: Optional[dict] = None,
        level: LogLevel = LogLevel.INFO,
        duration: Optional[float] = None,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> str:
        """记录一个生成步骤.

        Args:
            step: 步骤类型
            message: 日志消息
            input_params: 输入参数
            output_result: 输出结果
            level: 日志级别
            duration: 耗时（秒）
            error_message: 错误消息
            error_traceback: 错误堆栈
            extra_data: 额外元数据

        Returns:
            日志记录 ID
        """
        log_id = str(uuid4())
        self._sequence += 1

        # 清理参数，移除不可序列化的内容
        input_params = self._sanitize_params(input_params or {})
        output_result = self._sanitize_params(output_result or {})
        extra_data = self._sanitize_params(extra_data or {})

        try:
            async with self._session_factory() as db:
                await db.execute(
                    sql_text("""
                        INSERT INTO generation_logs
                        (id, task_id, content_id, step, level, sequence, message,
                         input_params, output_result, duration_seconds,
                         error_message, error_traceback, extra_data, created_at, updated_at)
                        VALUES
                        (:id, :task_id, :content_id, :step, :level, :sequence, :message,
                         :input_params, :output_result, :duration,
                         :error_message, :error_traceback, :extra_data, NOW(), NOW())
                    """),
                    {
                        "id": log_id,
                        "task_id": self.task_id,
                        "content_id": self.content_id,
                        "step": step.value,
                        "level": level.value,
                        "sequence": self._sequence,
                        "message": message[:500],  # 截断过长消息
                        "input_params": json.dumps(input_params, ensure_ascii=False),
                        "output_result": json.dumps(output_result, ensure_ascii=False),
                        "duration": duration,
                        "error_message": error_message,
                        "error_traceback": error_traceback,
                        "extra_data": json.dumps(extra_data, ensure_ascii=False),
                    }
                )
                await db.commit()

            # 同时记录到标准日志
            log_func = getattr(logger, level.value, logger.info)
            log_func(f"[{self.task_id[:8]}] {step.value}: {message}")

        except Exception as e:
            logger.error(f"Failed to save generation log: {e}")

        return log_id

    async def log_error(
        self,
        step: GenerationStep,
        message: str,
        error: Exception,
        input_params: Optional[dict] = None,
    ) -> str:
        """记录错误.

        Args:
            step: 步骤类型
            message: 错误描述
            error: 异常对象
            input_params: 输入参数

        Returns:
            日志记录 ID
        """
        return await self.log_step(
            step=step,
            message=message,
            input_params=input_params,
            level=LogLevel.ERROR,
            error_message=str(error),
            error_traceback=traceback.format_exc(),
        )

    async def update_content_id(self, content_id: str) -> None:
        """更新关联的内容 ID.

        在内容保存到数据库后调用，将所有日志记录关联到该内容。

        Args:
            content_id: 内容 ID
        """
        self.content_id = content_id

        try:
            async with self._session_factory() as db:
                await db.execute(
                    sql_text("""
                        UPDATE generation_logs
                        SET content_id = :content_id, updated_at = NOW()
                        WHERE task_id = :task_id
                    """),
                    {"content_id": content_id, "task_id": self.task_id}
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to update content_id in logs: {e}")

    @asynccontextmanager
    async def step(
        self,
        step: GenerationStep,
        message: str,
        input_params: Optional[dict] = None,
    ):
        """上下文管理器，自动记录步骤的耗时和结果.

        用法:
        ```python
        async with gen_logger.step(GenerationStep.IMAGE_GENERATE, "生成图片") as ctx:
            ctx.input_params = {"prompt": "..."}
            result = await image_service.generate(...)
            ctx.output_result = {"url": result.url}
        ```
        """
        ctx = StepContext(input_params=input_params or {})
        start_time = time.time()

        try:
            yield ctx
            duration = time.time() - start_time

            await self.log_step(
                step=step,
                message=message,
                input_params=ctx.input_params,
                output_result=ctx.output_result,
                level=LogLevel.INFO,
                duration=duration,
                extra_data=ctx.extra_data,
            )
        except Exception as e:
            duration = time.time() - start_time

            await self.log_step(
                step=step,
                message=f"{message} - 失败",
                input_params=ctx.input_params,
                output_result=ctx.output_result,
                level=LogLevel.ERROR,
                duration=duration,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
                extra_data=ctx.extra_data,
            )
            raise

    def _sanitize_params(self, params: dict) -> dict:
        """清理参数，确保可以 JSON 序列化."""
        def sanitize_value(v):
            if isinstance(v, (str, int, float, bool, type(None))):
                return v
            elif isinstance(v, (list, tuple)):
                return [sanitize_value(i) for i in v]
            elif isinstance(v, dict):
                return {k: sanitize_value(val) for k, val in v.items()}
            elif isinstance(v, bytes):
                return f"<bytes: {len(v)} bytes>"
            else:
                return str(v)

        return sanitize_value(params)


@dataclass
class StepContext:
    """步骤上下文，用于在 async with 块中收集信息."""
    input_params: dict = field(default_factory=dict)
    output_result: dict = field(default_factory=dict)
    extra_data: dict = field(default_factory=dict)
