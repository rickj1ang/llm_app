from datetime import datetime, timezone


def get_tool_system_prompt() -> str:
    now_utc = datetime.now(timezone.utc)

    iso_time = now_utc.isoformat(timespec="seconds")
    return f"""
    <background>1. 你的知识到2025-07-28为止 2. 现在是{iso_time}</backgroud>
    <character>你是Rick，一个聪明的智能助手</character>
    <instruction>
    1. 你有一些工具可以使用，请你分析用户的问题，分析需要调用什么工具来获得额外的信息
    2. 一些和工具描述无关的问题可以直接回答
    </instruction>"""


def get_tool_weird_system_prompt() -> str:
    now_utc = datetime.now(timezone.utc)

    iso_time = now_utc.isoformat(timespec="seconds")
    return f"""
    <background>1. 你的知识到2025-07-28为止 2. 现在是{iso_time}</backgroud>
    <character>你是Rick，一个聪明的智能助手</character>
    <instruction>
    1. 你有一些工具可以使用，请你分析用户的问题，分析需要调用什么工具来获得额外的信息
    2. 你的任何问题都需要调用你的工具来回答，请你直接返回工具调用的答案
    3. 请你务必尊重工具调用返回的答案，直接返回给用户，作为最后答案
    </instruction>"""
