import json
import os
import random
import time

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCallUnion

from models import Conversation
from utils import log_llm_calls, log_tool_call, setup_logging

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的天气时非常有用。比如多云，晴，雨，等",
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
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "当你想查询指定城市的气温时非常有用。",
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


def get_temp(arguments):
    temps = ["21摄氏度", "1摄氏度", "35摄氏度"]
    random_temp = random.choice(temps)
    location = arguments["location"]
    return f"{location}今天是{random_temp}。"


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
    conversation = Conversation()
    # conversation.add_system_message(
    #     "You are a helpful assistant. and whatever user input, you just output 'pong!'"
    # )
    conversation.add_user_message(message)
    while True:
        time_start = time.time()
        completion = client.chat.completions.create(
            model="qwen-flash",
            messages=conversation.messages,  # type: ignore
            temperature=1.0,  # change this temp for test the creativity and stable of LLM call
            tools=tools,  # type: ignore
        )
        time_elapsed = time.time() - time_start
        assistant_output = completion.choices[0].message
        if assistant_output.tool_calls is None:
            response_text = assistant_output.content
            # peace the warning
            if response_text:
                log_llm_calls(message, response_text, time_elapsed, completion.usage)
                break

        else:
            conversation.add_tool_call(completion.choices[0].message)
            for tool_call in assistant_output.tool_calls:
                tc_id = tool_call.id
                tool_result = process_tool_call(tool_call)
                conversation.add_tool_result(tc_id, tool_result)


def process_tool_call(tool_call: ChatCompletionMessageToolCallUnion) -> str:
    tc_name = tool_call.function.name  # type: ignore
    arguments = json.loads(tool_call.function.arguments)  # type: ignore
    tc_result = None
    match tc_name:
        case "get_current_weather":
            tc_result = get_weather(arguments)
        case "get_current_temperature":
            tc_result = get_temp(arguments)
    log_tool_call(tc_name, tool_call.function.arguments, tc_result)  # type: ignore
    return tc_result or "function call fail, no result"


if __name__ == "__main__":
    setup_logging()
    llm_call(message="综合考虑下来深圳现在适合出去玩吗")
