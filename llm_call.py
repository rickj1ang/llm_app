from openai import OpenAI
import os
import time
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
    completion = client.chat.completions.create(
        model="qwen-flash",
        messages=[{'role': 'user', 'content': message}]
    )
    time_elapsed = time.time() - time_start
    response_text = completion.choices[0].message.content
    log_llm_calls(message, response_text, time_elapsed, completion.usage)


if __name__ == "__main__":
    setup_logging()
    llm_call(message="hello")
