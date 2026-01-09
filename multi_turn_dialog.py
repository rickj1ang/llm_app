import os

from openai import OpenAI

from models import Conversation
from utils import log_llm_calls


def multi_turn_dialog(conversation: Conversation):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY is not set")
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=conversation.messages,  # type: ignore
    )

    response_text = completion.choices[0].message.content

    # just for peace the warning
    if response_text:
        log_llm_calls(conversation.messages[-1]., response_text, time_elapsed, completion.usage)
