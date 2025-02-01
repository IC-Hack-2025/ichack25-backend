import os
from typing import Type, TypeVar, Union

import openai
import paths
import pydantic


openai_api_key = os.getenv('OPENAI_API_KEY')
if openai_api_key is None:
    from dotenv import load_dotenv
    load_dotenv(paths.ENV_PATH)
    openai_api_key = os.getenv('OPENAI_API_KEY')

openai_model = "gpt-4o-mini"
openai_client = openai.OpenAI(api_key=openai_api_key)


RT = TypeVar('RT', bound=pydantic.BaseModel)


def query_openai(prompt: str, response_type: Type[Union[str, RT]] = str) -> Union[str, RT, None]:
    query_data = {
        "model": openai_model,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    if response_type is str:
        query_func = openai_client.chat.completions.create
    else:
        query_func = openai_client.beta.chat.completions.parse
        query_data["response_format"] = response_type

    result = query_func(**query_data)

    if response_type is str:
        return result.choices[0].message.content
    else:
        return result.choices[0].message.parsed
