import json
import os
import random
import time

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCallUnion

from llm_call import llm_call
from models import Conversation, Role
from prompts import get_tool_system_prompt, get_tool_weird_system_prompt
from storage import ConversationStorage
from utils import log_llm_calls, log_tool_call, setup_logging

tools_weather = [
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

tool_werid = [
    {
        "type": "function",
        "function": {
            "name": "get_anwser",
            "description": "用来回答用户的一切问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "直接输入用户想要咨询的问题",
                    }
                },
                "required": ["location"],
            },
        },
    },
]


def get_weather(arguments) -> str:
    weather_conditions = ["晴天", "多云", "雨天"]
    random_weather = random.choice(weather_conditions)
    location = arguments["location"]
    return f"{location}今天是{random_weather}。"


def get_temp(arguments) -> str:
    temps = ["21摄氏度", "1摄氏度", "35摄氏度"]
    random_temp = random.choice(temps)
    location = arguments["location"]
    return f"{location}今天是{random_temp}。"


def answer_question(arguments) -> str:
    question = arguments["question"]
    result = llm_call(question)
    return result


def llm_call_with_tool(conversation: Conversation) -> None:
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

    while True:
        time_start = time.time()
        completion = client.chat.completions.create(
            model="qwen-flash",
            messages=conversation.messages,  # type: ignore
            tools=tool_werid,  # type: ignore
        )
        time_elapsed = time.time() - time_start
        assistant_output = completion.choices[0].message
        if assistant_output.tool_calls is None:
            response_text = assistant_output.content
            # peace the warning
            if response_text:
                conversation.add_assistant_message(response_text)
                log_llm_calls(
                    conversation.messages[-1]["content"],
                    response_text,
                    time_elapsed,
                    completion.usage,
                )
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
        case "get_anwser":
            tc_result = answer_question(arguments)
    log_tool_call(tc_name, tool_call.function.arguments, tc_result)  # type: ignore
    return tc_result or "function call fail, no result"


def start_chat_tool_cli(conversation_id: str):
    """启动简单的多轮对话 CLI"""
    storage = ConversationStorage()

    conversation = Conversation(storage, conversation_id)

    # 如果是新对话，添加 system message
    if len(conversation.messages) == 0:
        conversation.add_system_message(get_tool_weird_system_prompt())

    print("多轮对话 CLI (输入 'quit' 或 'exit' 退出，Ctrl+C 也可以)")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                print("再见!")
                break

            conversation.add_user_message(user_input)
            llm_call_with_tool(conversation)

            # 打印助手的回复
            if (
                conversation.messages
                and conversation.messages[-1]["role"] == Role.ASSISTANT.value
                and conversation.messages[-1]["content"]
            ):
                print(f"AI: {conversation.messages[-1]['content']}\n")

        except KeyboardInterrupt:
            print("\n再见!")
            break


if __name__ == "__main__":
    setup_logging()
    start_chat_tool_cli("new_tool")
