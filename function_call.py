import json
import os
import random
import time

from openai import OpenAI

from models import Conversation
from utils import log_llm_calls, setup_logging

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"],
            },
        },
    },
]


def get_weather(arguments):
    weather_conditions = ["晴天", "多云", "雨天"]
    random_weather = random.choice(weather_conditions)
    location = arguments["location"]
    return f"{location}今天是{random_weather}。"


def llm_call(message: str) -> None:
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
        temperature=1.0,  # change this temp for test the creativity and stable of LLM call
        tools=tools,  # type: ignore
    )
    time_elapsed = time.time() - time_start
    if completion.choices[0].message.tool_calls is None:
        response_text = completion.choices[0].message.content
        # peace the warning
        if response_text:
            log_llm_calls(message, response_text, time_elapsed, completion.usage)

    else:
        tool_call = completion.choices[0].message.tool_calls[0]
        tc_name = tool_call.function.name  # type: ignore
        arguments = json.loads(tool_call.function.arguments)  # type: ignore
        tc_results = None
        match tc_name:
            case "get_current_weather":
                tc_results = get_weather(arguments)
        print(tc_results)


def process_tool_call():
    pass


if __name__ == "__main__":
    setup_logging()
    llm_call(message="深圳现在多少适合出去玩吗")
