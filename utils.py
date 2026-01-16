import json
import logging
from datetime import datetime

from openai import types


# 1. 定义一个 JSON Formatter
class JSONFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record) -> str:
        # 1. 准备基础字段
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
        }

        # 2. 将 msg（如果是字典）合并进来，或者作为 message 字段
        # 这里我们约定：如果传入的是字典，就展开；如果是字符串，就放入 message
        if isinstance(record.msg, dict):
            log_record.update(record.msg)
        else:
            log_record["message"] = record.msg

        # 3. 处理 args (如果有额外的格式化参数)
        if record.args:
            # 简单的字符串格式化处理
            if "message" in log_record and record.args:
                try:
                    log_record["message"] = log_record["message"] % record.args
                except Exception as e:
                    log_record["message"] += f" [Formatting Error: {e}]"

        # 4. 处理异常
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # 5. 转为 JSON 字符串
        return json.dumps(log_record, ensure_ascii=False, default=str)


# 2. 修改 setup_logging 函数，使用 JSONFormatter
def setup_logging():
    logger = logging.getLogger("llm_logger")  # 建议使用命名 logger
    logger.setLevel(logging.INFO)

    # 防止重复添加 handler (重要)
    if logger.handlers:
        return logger

    # 创建处理器
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("llm_calls.log", encoding="utf-8")

    # 实例化我们的 JSON Formatter
    json_formatter = JSONFormatter()

    # 设置格式化器
    console_handler.setFormatter(json_formatter)
    file_handler.setFormatter(json_formatter)

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 3. 修改 log_llm_calls 函数，传入字典数据
def log_llm_calls(
    message: str,
    response_text: str,
    elapsed_time: float,
    chatCompletionUsage: types.CompletionUsage | None,
) -> None:
    if chatCompletionUsage is None:
        return

    # 提取 Token 信息
    prompt_tokens = chatCompletionUsage.prompt_tokens
    completion_tokens = chatCompletionUsage.completion_tokens
    cached_tokens = (
        chatCompletionUsage.prompt_tokens_details.cached_tokens
        if chatCompletionUsage.prompt_tokens_details
        else 0
    )

    # 获取 logger
    logger = logging.getLogger("llm_logger")

    # 将所有信息构造成一个字典发送
    # 这样 JSON Formatter 会自动将其展开为 JSON 字段
    log_data = {
        "event": "llm_call",  # 标记事件类型，方便后续解析
        "message": message,
        "response_text": response_text,
        "elapsed_time": round(elapsed_time, 2),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "cached_tokens": cached_tokens,
        "total_tokens": chatCompletionUsage.total_tokens,
    }

    # 使用 extra={} 是为了防止日志系统尝试对字典进行 % 格式化
    logger.info(log_data, extra={"_": ""})


def log_tool_call(tc_name: str, arguments: str, tc_result: str) -> None:
    logger = logging.getLogger("llm_logger")
    log_data = {
        "event": "tool_call",
        "tool_name": tc_name,
        "tool_arguments": arguments,
        "tool_result": tc_result,
    }
    logger.info(log_data, extra={"_": ""})
