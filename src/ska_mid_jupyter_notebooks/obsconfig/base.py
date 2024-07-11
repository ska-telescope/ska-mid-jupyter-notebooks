"""Configuration for observation."""
import json
from datetime import datetime
from typing import Any, Callable, Generic, NamedTuple, ParamSpec, TypeVar

from ska_tmc_cdm.schemas import CODEC


class SB(NamedTuple):
    """Store the execution block and processing block identifiers."""
    eb: str
    pb: str


def load_next_sb() -> SB:
    """
    Returns the next execution block and processing block ids.
    :return: SB instance
    """
    date = datetime.now()
    unique = f"{date.year}{date.month:02}{date.day:02}-{str(int(date.timestamp()))[-5:]}"
    pb = f"pb-mid-{unique}"
    eb = f"eb-mid-{unique}"

    return SB(eb, pb)


class SchedulingBlock:
    def __init__(self, *_: Any, **__: Any) -> None:
        """
        Initializes the Scheduling Block
        """
        eb_id, pb_id = load_next_sb()
        self.eb_id = eb_id
        self.pb_id = pb_id

    def load_next_sb(self) -> None:
        """
        Assigns next execution block and processing block ids
        :return: None
        """
        eb_id, pb_id = load_next_sb()
        self.eb_id = eb_id
        self.pb_id = pb_id


T = TypeVar("T")
P = ParamSpec("P")


class EncodedObject(Generic[T]):
    def __init__(self, object_to_encode: T):
        """
        Rock and roll.

        :param object_to_encode: object to encode
        """
        self._object_to_encode = object_to_encode

    @property
    def as_json(self) -> str:
        """
        Returns the encoded object as a JSON string.

        :return: JSON string
        """
        if isinstance(self._object_to_encode, dict):
            return json.dumps(self._object_to_encode)
        return CODEC.dumps(self._object_to_encode)

    @property
    def as_json_skip_validation(self) -> str:
        """
        Returns the encoded object as a JSON string and skips validation.

        :return: JSON String
        """
        if isinstance(self._object_to_encode, dict):
            return json.dumps(self._object_to_encode)
        return CODEC.dumps(self._object_to_encode, validate=False)

    @property
    def as_dict(self) -> dict[Any, Any]:
        """
        Returns the encoded object as a dictionary.

        :return: encoded object as a dictionary
        """
        return json.loads(self.as_json)

    @property
    def as_object(self) -> T:
        """
        Returns the encoded object as an object.

        :return: encoded object as an object
        """
        return self._object_to_encode


def encoded(func: Callable[P, T]) -> Callable[P, EncodedObject[T]]:
    """
    Wraps a function that returns an object in an EncodedObject
    :param func: function that returns an object to be encoded
    :return: inner function which returns an encoded object
    """

    def inner(*args: P.args, **kwargs: P.kwargs) -> EncodedObject:
        """
        The inner sanctum.

        :param args: arguments
        :param kwargs: keywords and arguments
        :return: encoded object
        """
        return EncodedObject(func(*args, **kwargs))

    return inner
