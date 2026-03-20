from enum import StrEnum
from typing import NamedTuple, Callable, Any


class BmType(StrEnum):
    """
    Attributes
    -----------
        SPEED: 
            Benchmarks for speed.

        MEMORY: 
            Benchmarks for memory usage.
    """
    SPEED = "Speed"
    MEMORY = "Memory"

class FunctionMetadata(NamedTuple):
    func: Callable
    args: tuple[Any, ...]
    is_manual: bool
    copy_args: bool

