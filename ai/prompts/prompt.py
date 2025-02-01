import abc
from typing import Self

import pydantic

from ai import query_openai


class FormattedPromptClass(abc.ABC, pydantic.BaseModel):

    @classmethod
    @abc.abstractmethod
    def _prompt(cls, *args, **kwargs) -> str | dict:
        pass

    @classmethod
    def do_query(cls, *args, **kwargs) -> Self:
        prompt = cls._prompt(*args, **kwargs)
        prompt = prompt.strip()
        result = query_openai(prompt, response_type=cls)
        return result
