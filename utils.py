import logging
from openai import types

def log_llm_calls(message: str, response_text: str, elapsed_time: float, chatCompletionUsage: types.CompletionUsage | None) -> None:

    prompt_tokens = chatCompletionUsage.prompt_tokens
    completion_tokens = chatCompletionUsage.completion_tokens
    cached_tokens = chatCompletionUsage.prompt_tokens_details.cached_tokens

    logging.info(message)
    logging.info("time taken: {:.2f}".format(elapsed_time))
    logging.info(response_text)
    logging.info(f"Prompt Tokens: {prompt_tokens}")
    logging.info(f"Completion Tokens: {completion_tokens}")
    logging.info(f"Cached Tokens: {cached_tokens}")

def setup_logging():
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('llm_calls.log')
        ]
    )
