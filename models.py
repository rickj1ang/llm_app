from typing import Optional

from storage import ConversationStorage


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
        self.messages: list[dict[str, str]] = []

        if conversation_id:
            self.conversation_id = conversation_id
            self.messages = self.storage.load_messages(conversation_id)
        else:
            self.conversation_id = self.storage.create_conversation(user_id)
            self.messages = []

    def _record_message(self, role: str, content: str) -> None:
        message = {"role": role, "content": content}

        self.messages.append(message)

        self.storage.add_message(self.conversation_id, role, content)

    def add_system_message(self, content: str) -> None:
        self._record_message("system", content)

    def add_user_message(self, content: str) -> None:
        self._record_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        self._record_message("assistant", content)
