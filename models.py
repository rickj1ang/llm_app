from storage import ConversationStorage


class Conversation:
    def __init__(self, storage: ConversationStorage, conversation_id: str | None = None, user_id: str = "default"):
        self.storage = storage
        self.user_id = user_id

        if conversation_id:
            self.conversation_id = conversation_id
            self.messages = storage.load_messages(conversation_id)
        else:
            self.conversation_id = storage.create_conversation(user_id)
            self.messages: list[dict[str, str]] = []

    def add_system_message(self, content: str) -> None:
        self.storage.add_message(self.conversation_id, "system", content)
        self.messages.append({"role": "system", "content": content})

    def add_user_message(self, content: str) -> None:
        self.storage.add_message(self.conversation_id, "user", content)
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.storage.add_message(self.conversation_id, "assistant", content)
        self.messages.append({"role": "assistant", "content": content})
