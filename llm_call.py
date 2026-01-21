import os
import time

from openai import OpenAI

from models import Conversation
from utils import log_llm_calls, setup_logging


def stream_llm_call(message: str) -> None:
    client = OpenAI(
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    conversation = Conversation()
    conversation.add_system_message("You are a helpful assistant.")
    conversation.add_user_message(message)

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=conversation.messages,  # type: ignore
        stream=True,
        stream_options={"include_usage": True},
    )

    # 3. 处理流式响应
    # 用列表暂存响应片段，最后 join 比逐次 += 字符串更高效
    content_parts = []
    print("AI: ", end="", flush=True)

    time_start = time.time()
    for chunk in completion:
        if chunk.choices:
            content = chunk.choices[0].delta.content or ""
            print(content, end="", flush=True)
            content_parts.append(content)
        elif chunk.usage:
            time_elapsed = time.time() - time_start

            full_response = "".join(content_parts)
            print("\n")
            log_llm_calls(message, full_response, time_elapsed, chunk.usage)

    # print(f"\n--- 完整回复 ---\n{full_response}")


def llm_call(message: str) -> str:
    # get api key from env variable
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("API key not found")
        return "API key not found"

    # create OpenAI client instance with qwen url and apikey
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # send the llm api call
    time_start = time.time()
    conversation = Conversation()
    conversation.add_system_message(
        "You are a helpful assistant. and whatever user input, you just output 'pong!'"
    )
    conversation.add_user_message(message)
    completion = client.chat.completions.create(
        model="qwen-flash",
        messages=conversation.messages,  # type: ignore
        temperature=1.0,  # change this temp for test the creativity and stable of LLM call
    )
    time_elapsed = time.time() - time_start
    response_text = completion.choices[0].message.content

    # just for peace the warning
    if response_text:
        log_llm_calls(message, response_text, time_elapsed, completion.usage)
        return response_text
    return "something went wrong"


if __name__ == "__main__":
    setup_logging()
    stream_llm_call(message="你是谁")
    # llm_call(message="你是谁")
