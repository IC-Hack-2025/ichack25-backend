from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Self, ClassVar
import pydantic
from pydantic_core import PydanticSerializationError
from util.file import project_standard_path_format, from_project_standard_path_format
from util.time import timedelta_to_h_m_s_micro_str


_to_rename: set[str] = {"model_computed_fields", "model_config", "model_extra", "model_fields", "model_fields_set"}
_renamed = {f"_{p}" for p in _to_rename}


class DataModel(pydantic.BaseModel):

    _id: int = pydantic.PrivateAttr()
    _id_counter: ClassVar[int] = 0

    model_config = pydantic.ConfigDict(
        extra="ignore",
        use_enum_values=True
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        cls = self.__class__
        if not hasattr(cls, "_id_counter"):
            setattr(cls, "_id_counter", 0)
        self._id = cls._id_counter
        setattr(cls, "_id_counter", getattr(cls, "_id_counter") + 1)

    def __dir__(self):
        d = [
            f"_{p}" if p in _to_rename else p
            for p in super().__dir__()
        ]
        return d

    def __getattr__(self, item):
        if item in _renamed:
            item = item.strip("_")
        return super().__getattr__(item)

    def __setattr__(self, key, value):
        if key in _renamed:
            key = key.strip("_")
        return super().__setattr__(key, value)

    @pydantic.computed_field
    @property
    def id(self) -> int:
        return self._id

    def to_dict(self, mode="json", exclude_none=False, exclude_defaults=False):
        return self.model_dump(mode=mode, exclude_none=exclude_none, exclude_defaults=exclude_defaults)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls.model_validate(data)

    def to_json(self, include: set[str] = None, exclude_none=False, exclude_defaults=False):
        try:
            return self.model_dump_json(
                indent=4,
                include=include,
                exclude_none=exclude_none,
                exclude_defaults=exclude_defaults
            )
        except PydanticSerializationError as e:
            # Breakpoint here for debugging. Serialization error should never happen.
            raise e

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        return cls.model_validate_json(json_str)

    def write_json(self, file: Path, *args, **kwargs):
        j_str = self.to_json(*args, **kwargs)
        with open(file, 'w+', encoding="utf-8") as fp:
            fp.write(j_str)

    @classmethod
    def read_json(cls, file: Path, context: Any | None = None):
        with open(file, 'r', encoding="utf-8") as fp:
            j_str = fp.read()
        return cls.model_validate_json(j_str, strict=False, context=context)

    @pydantic.field_serializer("*", when_used="json")
    @classmethod
    def _serialize_field(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, timedelta):
            return timedelta_to_h_m_s_micro_str(value)
        if isinstance(value, set):
            return list(value)
        if isinstance(value, Path) or issubclass(type(value), Path):
            return project_standard_path_format(value)
        return value

    @pydantic.model_validator(mode="after")
    @classmethod
    def _path_validator(cls, instance: Self) -> Self:
        for field, field_info in instance.model_fields.items():
            value = getattr(instance, field)
            if type(value) is Path or issubclass(type(value), Path):
                value = from_project_standard_path_format(value)
                setattr(instance, field, value)
        return instance
