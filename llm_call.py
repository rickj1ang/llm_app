import os
import time

from openai import OpenAI

from models import Conversation
from utils import log_llm_calls, setup_logging


def llm_call(message: str):
    # get api key from env variable
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("API key not found")
        return

    # create OpenAI client instance with qwen url and apikey
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # send the llm api call
    time_start = time.time()
    conversation = Conversation()
    # conversation.add_system_message(
    #     "You are a helpful assistant. and whatever user input, you just output 'pong!'"
    # )
    conversation.add_user_message(message)
    completion = client.chat.completions.create(
        model="qwen-flash",
        messages=conversation.messages,  # type: ignore
        temperature=1.9,
    )
    time_elapsed = time.time() - time_start
    response_text = completion.choices[0].message.content

    # just for peace the warning
    if response_text:
        log_llm_calls(message, response_text, time_elapsed, completion.usage)


if __name__ == "__main__":
    setup_logging()
    llm_call(message="你是谁")
