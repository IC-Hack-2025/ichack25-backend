import os
import openai
from openai.types.chat.chat_completion import ChatCompletion

openai_api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai_api_key
openai_model = "gpt-4o"

openai_client = openai.OpenAI(api_key=openai_api_key)


def query_openai(prompt) -> str | None:
    result: ChatCompletion = openai_client.chat.completions.create(
        model=openai_model,
        messages=[{
            "role": "user",
            "content": prompt,
        }],
    )
    return result.choices[0].message.content
