# BenchmarkRunner
The main way to benchmark a function through using the `run` method.
### Parameters:
- name: `str`
  - The name of the benchmark.
- runs: `int` | `None`
  - The number of times to run a benchmark. If not set, it is internally calculated and is the recommended thing to do.
- metadata: dict[`str`, `Any`] | `None`
  - The metadata to add to the run.
- warmup_threshold: `int` | `None`
  - The miminum time needed to warmup a benchmark. If not set, it is internally calculated and is the recommended thing to do.
- output_file: `str` | `None`
  - The raw data to write to. You can also set this through the command line:
      ``benchmark.py --output=result.json``

### Attributes:
- Those stated in `Parameters`.
- module_name: `str`
  - The name of the module to get the functions from. Defaults to `__main__`.

## Functions

### `add_benchmark`
- _add_benchmark(func: Callable, bm_type: BmType, *, args: tuple = (), is_manual: bool = False, copy_args: bool = False) -> None_
  - Adds a function you want to benchmark.
  - ### Parameters:
    - func: `Callable`
      - The function to benchmark
    - bm_type: `BmType`
      - Whether to benchmark this function for speed or for memory usage.
    - args: `tuple`
      - The args to parse into the benchmark. Defaults to an empty tuple.
    - is_manual: `bool`
      - Whether the runner should calculate the time taken/memory usage. If not, the function itself should return the time taken/memory usage.
    - copy_args: `bool`
      - Whether to deepy copy the arguments instead of mutating on the actual arguments.

### `add_benchmarks`
- _add_benchmarks(bm_type: BmType, *, bms: list[str] | None = None, module_name: str = "\__main\__", to_ignore: list[str] | None = None,
                            func_metadata: dict[str, tuple] | None = None,  args: tuple = (),
                            copy_args: bool = False, is_manual: bool = False, key: Callable | None = None) -> None_
  - Adds multiple functions you want to benchmark.
  - ### Parameters:
    - bm_type: ``BmType``
        - Determines whether benchmarks measure speed or memory usage.
    - bms: list[``str``] | ``None``
        - A list of function names to benchmark. If not provided, all functions in the module will be added.
    - module_name: ``str`` | ``None``
        - The module to search for benchmark functions. Defaults to ``__main__``.
    - to_ignore : list[``str``] | ``None``
        - A list of function names to exclude from benchmarking. The ``main`` function is automatically ignored, as it should be used to start the benchmark runner.
    - func_metadata : dict[``str``, ``tuple``] | ``None``
        - A mapping of function names to metadata describing how the benchmark should run.
        - The metadata tuple format is:
          - ``((arg1, arg2, ...), is_manual, copy_args)``
        - Example:
          - ``{"bm": ((arg1, arg2), False, True)}``
        - In this example:
            - ``arg1`` and ``arg2`` are passed to the benchmark function
            - The runner measures the results automatically
            - The arguments are deep-copied before execution
    - args: ``tuple``
        - Arguments passed to all benchmark functions that are not defined in ``func_metadata``. Defaults to an empty tuple.
    - copy_args: ``bool``
        - Whether to deep-copy all provided arguments before running the benchmark. This does not override values specified in ``func_metadata``. Defaults to ``False``.
    - is_manual: ``bool`` | ``None``
        - Whether benchmarks return their own timing or memory results. This allows more flexible benchmarking but does not override values defined in ``func_metadata``.
    - key: ``Callable`` | ``None``
        - Predicate used to identify benchmark functions. The callable receives a function and should return ``True`` if it should be included.

  - ### Raises
    - ValueError - Both `bms` and `key` are set.
