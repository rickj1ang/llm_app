import os
import time

from openai import OpenAI

from models import Conversation
from storage import ConversationStorage
from utils import log_llm_calls, setup_logging


def multi_turn_dialog(conversation: Conversation):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY is not set")
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    time_start = time.time()
    completion = client.chat.completions.create(
        model="qwen-flash",
        messages=conversation.messages,  # type: ignore
    )
    time_elapsed = time.time() - time_start

    response_text = completion.choices[0].message.content

    # just for peace the warning
    if response_text:
        log_llm_calls(
            conversation.messages[-1]["content"],
            response_text,
            time_elapsed,
            completion.usage,
        )
        conversation.add_assistant_message(response_text)


def start_chat_cli(conversation_id: str):
    """启动简单的多轮对话 CLI"""
    storage = ConversationStorage()

    conversation = Conversation(storage, conversation_id)

    # 如果是新对话，添加 system message
    if len(conversation.messages) == 0:
        conversation.add_system_message("You are a helpful assistant.")

    print("多轮对话 CLI (输入 'quit' 或 'exit' 退出，Ctrl+C 也可以)")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                print("再见!")
                break

            conversation.add_user_message(user_input)
            multi_turn_dialog(conversation)

            # 打印助手的回复
            if (
                conversation.messages
                and conversation.messages[-1]["role"] == "assistant"
            ):
                print(f"AI: {conversation.messages[-1]['content']}\n")

        except KeyboardInterrupt:
            print("\n再见!")
            break


if __name__ == "__main__":
    # setup_logging()
    # 使用示例：调用 CLI
    # 123456 rick
    start_chat_cli("1234567")

    # 或者使用硬编码的测试对话
    # conversation = Conversation()
    # conversation.add_system_message("You are a helpful assistant.")
    # conversation.add_user_message("hello!, my name is Rick")
    # multi_turn_dialog(conversation)
    # conversation.add_user_message("What is my name?")
    # multi_turn_dialog(conversation)
