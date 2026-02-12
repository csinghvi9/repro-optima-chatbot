import time
from app.utils.llm_utils import ask_openai_validation_assistant


async def bot_generate(msg: str, max_token: int = 10):
    start_time = time.time()

    # Call OpenAI function
    llm_answer = await ask_openai_validation_assistant(
        prompt=msg,
        max_tokens=max_token,
    )
    return llm_answer
