from enum import StrEnum


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


class FunctionMetadata:
    """Function metadata to such as arguments

    Attributes
    -----------
    args : :class:`tuple`
        The arguments to pass to the benchmark.
    is_manual : :class:`bool`
        whether the function itself should manually time/measure memory usage. If ``True``, 
        it should return the calculated value. Defaults to ``False``
    copy_args : :class:`bool`
        Whether to use copied version of the arguments. Defaults to ``False``
    kwargs : Optional[:class:`dict`]
        The kwargs to pass to the benchmark.`
    """

    __slots__ = ('args', 'kwargs', 'is_manual', 'copy_args')

    def __init__(self, *, args: tuple = (), kwargs: dict | None = None, is_manual: bool = False, copy_args: bool = False) -> None:
        self.args = args
        self.kwargs = kwargs
        self.is_manual = is_manual
        self.copy_args = copy_args

