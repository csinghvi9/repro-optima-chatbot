# from openai import OpenAI
from openai import AzureOpenAI
from app.utils.config import ENV_PROJECT

# Use this client for all requests
# client = OpenAI(api_key=ENV_PROJECT.OPENAI_API_KEY)


client = AzureOpenAI(
    azure_endpoint=ENV_PROJECT.AZURE_OPENAI_ENDPOINT,
    api_key=ENV_PROJECT.AZURE_OPENAI_API_KEY,
    api_version=ENV_PROJECT.AZURE_OPENAI_API_VERSION,
)


async def ask_openai_validation_assistant(
    prompt: str, model="gpt-4.1-nano", max_tokens=500, temperature=0
):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a validation assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        answer = response.choices[0].message.content.strip()
        usage = response.usage
        step_total = usage.total_tokens
        return answer
    except Exception as e:
        return None, 0


token_tracker = {}


def update_token_usage(thread_id: str, tokens: int):
    token_tracker[thread_id] = token_tracker.get(thread_id, 0) + tokens
    return token_tracker[thread_id]
