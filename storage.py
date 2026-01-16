import sqlite3
import uuid


class ConversationStorage:
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL DEFAULT 'default'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    tool_call_id TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            conn.commit()

    def create_conversation(self, user_id: str = "default") -> str:
        """创建新对话，返回 conversation_id"""
        conversation_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (id, user_id) VALUES (?, ?)",
                (conversation_id, user_id),
            )
            conn.commit()
        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        type: str,
        tool_call_id: str | None = None,
    ):
        """添加单条消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, type, tool_call_id) VALUES (?, ?, ?, ?, ?)",
                (conversation_id, role, content, type, tool_call_id),
            )
            conn.commit()

    def load_messages(self, conversation_id: str) -> list[dict[str, str]]:
        """加载对话的所有消息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT role, content, type, tool_call_id FROM messages
                   WHERE conversation_id = ?
                   ORDER BY id ASC""",
                (conversation_id,),
            )
            messages = []
            for row in cursor.fetchall():
                msg = {"role": row[0], "content": row[1], "type": row[2]}
                if row[3]:  # tool_call_id 存在时才添加
                    msg["tool_call_id"] = row[3]
                messages.append(msg)
            return messages

    def list_by_user(self, user_id: str = "default") -> list[str]:
        """列出用户的所有对话 ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM conversations WHERE user_id = ?", (user_id,)
            )
            return [row[0] for row in cursor.fetchall()]
