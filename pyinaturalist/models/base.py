"""Base class and utilities for model objects.

Note: when using classmethods as converters, mypy will raise a false positive error, hence all the
``type: ignore`` statements in BaseModel subclasses. See:
https://github.com/python/mypy/issues/6172
https://github.com/python/mypy/issues/7912
"""
# TODO: More refactoring and tests for load_json, from_json, and from_json_list
import json
from datetime import datetime, timezone
from logging import getLogger
from os.path import expanduser
from pathlib import Path
from typing import Dict, Iterable, List, Type, TypeVar, Union

from attr import asdict, define, field, fields_dict

from pyinaturalist.constants import AnyFile, JsonResponse, ResponseOrFile, ResponseOrResults
from pyinaturalist.converters import convert_lat_long, ensure_list, try_datetime

T = TypeVar('T', bound='BaseModel')
logger = getLogger(__name__)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Some aliases for common attribute types
kwarg = field(default=None)
coordinate_pair = field(converter=convert_lat_long, default=None)  # type: ignore
datetime_attr = field(converter=try_datetime, default=None)  # type: ignore
datetime_now_attr = field(converter=try_datetime, factory=utcnow)  # type: ignore


@define(auto_attribs=False)
class BaseModel:
    """Base class for models"""

    partial: bool = field(default=None, repr=False)
    temp_attrs: List[str] = []
    headers: Dict[str, str] = {}

    @classmethod
    def from_json(cls: Type[T], value: JsonResponse, **kwargs) -> 'BaseModel':
        """Initialize a single model object from an API response or response result.
        Omits any invalid fields and ``None`` values, so we use our default factories instead
        (e.g. for empty dicts and lists).
        """
        attr_names = [a.lstrip('_') for a in fields_dict(cls)]
        if cls.temp_attrs:
            attr_names.extend(cls.temp_attrs)
        valid_json = {k: v for k, v in value.items() if k in attr_names and v is not None}
        return cls(**valid_json, **kwargs)  # type: ignore

    @classmethod
    def from_json_file(cls: Type[T], value: AnyFile) -> List['BaseModel']:
        """Initialize a collection of model objects from a JSON string, file path, or file-like object"""
        return cls.from_json_list(load_json(value))

    @classmethod
    def from_json_list(cls: Type[T], value: ResponseOrResults) -> List['BaseModel']:
        """Initialize a collection of model objects from a JSON path, file-like object, string, or
        API response
        """
        return [cls.from_json(item) for item in ensure_list(value)]

    @classmethod
    def to_table(cls, objects: List['BaseModel']):
        """Format a list of model objects as a table. If ``rich`` isn't installed or the model
        doesn't have a table format defined, just return a basic list of stringified objects.
        """
        try:
            from rich.box import SIMPLE_HEAVY
            from rich.table import Column, Table

            objects[0].row
        except (ImportError, NotImplementedError):
            return '\n'.join([str(obj) for obj in objects])

        columns = [Column(header, style=style) for header, style in cls.headers.items()]
        table = Table(*columns, box=SIMPLE_HEAVY, header_style='bold white', row_styles=['dim', 'none'])

        for obj in objects:
            table.add_row(*[_str(value) for value in obj.row])
        return table

    @property
    def row(self) -> List:
        raise NotImplementedError

    # TODO: Use cattr.unstructure() to handle recursion properly (for nested model objects)?
    def to_json(self) -> Dict:
        return asdict(self)


# Type aliases
ModelObjects = Union[BaseModel, Iterable[BaseModel]]
ResponseOrObject = Union[BaseModel, JsonResponse]
ResponseOrObjects = Union[ModelObjects, ResponseOrResults]


def ensure_model(cls: Type[T], value: ResponseOrObject) -> BaseModel:
    if not value:
        return cls()
    elif isinstance(value, BaseModel):
        return value
    else:
        return cls.from_json(value)


def ensure_model_list(cls: Type[T], values: ResponseOrObjects) -> List[BaseModel]:
    return [ensure_model(cls, obj) for obj in ensure_list(values)]


def load_json(value: ResponseOrFile) -> ResponseOrResults:
    """Load a JSON string, file path, or file-like object"""
    if not value:
        return {}
    if isinstance(value, (dict, list)):
        json_value = value
    elif isinstance(value, (Path, str)):
        with open(expanduser(str(value))) as f:
            json_value = json.load(f)
    else:
        json_value = json.load(value)  # type: ignore

    if 'results' in json_value:
        json_value = json_value['results']
    return json_value
