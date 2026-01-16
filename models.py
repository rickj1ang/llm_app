import enum
import json
from typing import Optional

from openai.types.chat import ChatCompletionMessage

from storage import ConversationStorage


class Role(enum.Enum):
    """消息角色枚举"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Type(enum.Enum):
    """消息类型枚举"""

    TEXT = "text"
    FUNCTION = "function"
    TOOL_RESULT = "tool_result"


class InMemoryStorage:
    """一个空实现的存储类，专门给‘不持久化’的情况使用"""

    def load_messages(self, _id):
        return []

    def create_conversation(self, _id):
        return "mem_session"

    def add_message(self, *args, **kwargs):
        pass  # 啥也不干


class Conversation:
    def __init__(
        self,
        storage: Optional[ConversationStorage | InMemoryStorage] = None,
        conversation_id: Optional[str] = None,
        user_id: str = "default",
    ):
        self.storage = storage or InMemoryStorage()
        self.user_id = user_id
        self.messages: list = []

        if conversation_id:
            self.conversation_id = conversation_id
            raw_messages = self.storage.load_messages(conversation_id)
            self.messages = self._deserialize_messages(raw_messages)
        else:
            self.conversation_id = self.storage.create_conversation(user_id)
            self.messages = []

    def _deserialize_messages(self, raw_messages: list[dict]) -> list:
        """根据 type 字段反序列化消息"""
        messages = []
        for msg in raw_messages:
            msg_type = msg.get("type", Type.TEXT.value)

            if msg_type == Type.FUNCTION.value:
                # function 类型：JSON 反序列化为 ChatCompletionMessage 对象
                tool_calls = json.loads(msg["content"])
                messages.append(
                    {
                        "role": msg["role"],
                        "tool_calls": tool_calls,
                    }
                )
            elif msg_type == Type.TOOL_RESULT.value:
                # tool_result 类型：需要 tool_call_id
                messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                        "tool_call_id": msg.get("tool_call_id"),
                    }
                )
            else:
                # text 类型：普通消息
                messages.append(
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                )
        return messages

    def _record_message(self, role: str, content: str, type: str) -> None:
        message = {"role": role, "content": content}

        self.messages.append(message)

        self.storage.add_message(self.conversation_id, role, content, type)

    def add_system_message(self, content: str) -> None:
        self._record_message(Role.SYSTEM.value, content, Type.TEXT.value)

    def add_user_message(self, content: str) -> None:
        self._record_message(Role.USER.value, content, Type.TEXT.value)

    def add_assistant_message(self, content: str) -> None:
        self._record_message(Role.ASSISTANT.value, content, Type.TEXT.value)

    def add_tool_call(self, tool_call_message: ChatCompletionMessage) -> None:
        # 存储为字典格式，保持与 load 后的格式一致
        message = {
            "role": tool_call_message.role,
            "tool_calls": tool_call_message.tool_calls,
        }
        self.messages.append(message)
        if tool_call_message.tool_calls:
            tool_call_dict = [
                tool_call.model_dump() for tool_call in tool_call_message.tool_calls
            ]
            tool_call_str = json.dumps(tool_call_dict)
            self.storage.add_message(
                self.conversation_id,
                Role.ASSISTANT.value,
                tool_call_str,
                Type.FUNCTION.value,
            )

    def add_tool_result(self, tc_id: str, tool_result: str) -> None:
        tr = {"role": Role.TOOL.value, "content": tool_result, "tool_call_id": tc_id}
        self.messages.append(tr)
        self.storage.add_message(
            self.conversation_id,
            Role.TOOL.value,
            tool_result,
            Type.TOOL_RESULT.value,
            tool_call_id=tc_id,
        )
