import json
from typing import Any, Callable
import inspect
import os
from time import perf_counter
import sys
from copy import deepcopy

from .utils import Logger, END_STR, SPEED_START_STR, MEM_START_STR, _get_logger_mode, \
        _print_common_info, _print_per_run_info, _analyse_benchmark, \
        _format_timing, _format_bytes, get_attributes_from_slots

from .api_types import FunctionMetadata, BmType

HAS_TRACEMALLOC = True
try:
    import tracemalloc as tr_malloc
except ImportError:
    HAS_TRACEMALLOC = False

# If there is a jit, we want more warm ups and more loops to ensure jit is being used
JIT_MULTIPLIER = 1.5 if ("PyPy" in sys.version or (sys.version_info.minor > 13 and sys._jit.is_enabled())) else 1

logger = Logger()
logger.level = 1

def set_logger_level(level: int):
    logger.level = level

class BenchmarkRunner:
    """Used to run a benchmark.

    Attributes
    -----------
    name : :class:`str`
        The name of the benchmark.
    runs : Optional[:class:`int`]
        The number of times to run a benchmark. If not set, it is internally calculated 
        and is the recommended thing to do.
    metadata: `dict[str, Any]` | `None`
        The metadata to add to the run.
    warmup_threshold : Optional[:class:`float`]
        The miminum time taken needed to warmup a benchmark. If not set, it is internally calculated 
        and is the recommended thing to do.
    output_file : Optional[:class:`str`]
        The raw data to write to. You can also set this through the command line:
        ``benchmark.py --output=result.json``
    """

    __slots__: tuple[str, ...] = (
        'name',
        'metadata',
        'runs',
        'warmup_threshold',
        'module_name',
        '_speed_benchmarks',
        '_mem_benchmarks'
    )

    def __init__(self, name: str, *, runs: int | None = None, metadata: dict[str, Any] | None = None, warmup_threshold: float | None = None) -> None:
        self.name = name
        self.metadata = metadata
        self.warmup_threshold = warmup_threshold
        self.runs = runs
        self.module_name: str = "__main__"
        self._speed_benchmarks: list[tuple[Callable, FunctionMetadata]]  = []
        self._mem_benchmarks: list[tuple[Callable, FunctionMetadata]]= []


    def add_benchmark(self, func: Callable, bm_type: BmType, metadata: FunctionMetadata = FunctionMetadata()) -> None:
        """
        Add a benchmark
        
        Parameters
        ----------
        func: :class:`Callable`
            The function to benchmark
        bm_type: :class:`BmType`
            Whether to benchmark this function for speed or for memory usage.
        args: :class:`tuple`
            The args to parse into the benchmark. Defaults to an empty tuple.
        is_manual: :class:`bool`
            Whether the runner should calculate the time taken/memory usage.
            If not, the function itself should return the time taken/memory usage.
        copy_args: :class:`bool`
            Whether to deepy copy the arguments instead of mutating on the actual arguments.
        """
        to_append = (func, metadata)
        if bm_type is BmType.SPEED:
            self._speed_benchmarks.append(to_append)
        else:
            self._mem_benchmarks.append(to_append)

    @staticmethod
    def _deep_copy_args(args: tuple, kwargs: dict | None) -> tuple[tuple, dict]:
        copied_args = tuple(deepcopy(args))
        if kwargs:
            return copied_args, deepcopy(kwargs)
        return tuple(deepcopy(args)), {}
    
    @staticmethod
    def get_args_and_kwargs(args: tuple, kwargs: dict | None, *, copy_args: bool) -> tuple[tuple, dict]:
        if copy_args:
            copied_args, copied_kwargs = BenchmarkRunner._deep_copy_args(args, kwargs)
        else:
            copied_args, copied_kwargs = args, (kwargs or {})

        return copied_args, copied_kwargs

    def add_benchmarks(self, bm_type: BmType, *, bms: list[str] | None = None, module_name: str = "__main__",
                            to_ignore: list[str] | None = None,
                            function_metadata_map: dict[str, FunctionMetadata] | None = None,  args: tuple = (),
                            kwargs: dict | None = None,
                            copy_args: bool = False, is_manual: bool = False, key: Callable | None = None) -> None:
        """Add multiple benchmarks.

        Parameters
        ----------
        bm_type: ``BmType``
            Determines whether benchmarks measure execution speed or
            memory usage.

        bms: list[``str``] | ``None``
            A list of function names to benchmark. If not provided, all functions
            in the module will be considered.

        module_name: ``str`` | ``None``
            The module to search for benchmark functions. Defaults to ``__main__``.

        to_ignore : list[``str``] | ``None``
            A list of function names to exclude from benchmarking.
            The ``main`` function is automatically ignored, as it should be used
            to start the benchmark runner.

        function_metadata_map : dict[``str``, ``FunctionMetadata``] | ``None``
            A mapping of function names to metadata describing how the benchmark
            should run.

            The metadata tuple format is:
                ``((arg1, arg2, ...), is_manual, copy_args)``

            Example:
                ``{"bm": ((arg1, arg2), False, True)}``

            In this example:
                - ``arg1`` and ``arg2`` are passed to the benchmark function
                - The runner measures the results automatically
                - The arguments are deep-copied before execution

        args: ``tuple``
            Arguments passed to all benchmark functions that are not defined
            in ``func_metadata``. Defaults to an empty tuple.

        copy_args: ``bool``
            Whether to deep-copy all provided arguments before running the
            benchmark. This does not override values specified in
            ``func_metadata``. Defaults to ``False``.

        is_manual: ``bool`` | ``None``
            Whether benchmarks return their own timing or memory results.
            This allows more flexible benchmarking but does not override
            values defined in ``func_metadata``.

        key: ``Callable`` | ``None``
            Predicate used to identify benchmark functions. The callable
            receives a function and should return ``True`` if it should
            be included.

        Raises
        -------
        ValueError
            Both `bms` and `key` are set.
        """
        
        if bms and key:
            raise ValueError("Cannot set both 'bms' and 'key'")

        key = key if key is not None else (lambda fn: fn.__qualname__ in bms) if bms else (lambda _: True)

        if to_ignore is None:
            to_ignore = ["main"]
        else:
            to_ignore.append("main")

        functions = []
        for name, fn in inspect.getmembers(sys.modules["__main__"], inspect.isfunction):
            if fn.__module__ != module_name or name in to_ignore or not key(fn):
                continue
            
            func_metadata = FunctionMetadata(args=args, kwargs=kwargs, is_manual=is_manual, copy_args=copy_args)
            if function_metadata_map is not None:
                tmp = function_metadata_map.get(fn.__name__)
                if tmp is not None and not isinstance(tmp, FunctionMetadata):
                    raise TypeError(f"Expected FunctionMetadata got {tmp.__class__!r} instead")
                if tmp:
                    func_metadata = tmp

            functions.append((fn, func_metadata))
        self._speed_benchmarks.extend(functions) if bm_type is BmType.SPEED else self._mem_benchmarks.extend(functions)
        self.module_name = module_name

    def _setup_base_data(self, n_functions: int, bm_type: BmType) -> dict[BmType, Any]:
        description = (sys.modules[self.module_name].__doc__ or "None").strip("\n") if isinstance(self.module_name, str) else ""
        base = {bm_type: {}}
        base[bm_type] = {
            "python_version": sys.version,
            "has_jit": "True (PyPy)" if "PyPy" in sys.version else f"{sys.version_info.minor > 13 and sys._jit.is_enabled()} (Cpython)",
            "cpu_count": os.cpu_count(),
            "name": self.name,
            "description": description,
            "num_bms": n_functions,
            "metadata": self.metadata,
            "runs": self.runs,
            "warmup_threshold": self.warmup_threshold,
            "benchmarks": {}
        }
        return base

    @staticmethod
    def _write_data_to_output(file_path: str, to_write: dict) -> None:
        assert isinstance(file_path, str)

        try:
            with open(file_path, "r") as f:
                curr_data: dict = json.load(f)
        except FileNotFoundError:
            curr_data = to_write
        else:
            if curr_data:
                curr_data.update(to_write)
            else:
                curr_data = to_write
        with open(file_path, "w") as f:
            json.dump(curr_data, f)

    def run(self, *, run_metadata: dict[str, Any] | None = None, output_file: str | None = None) -> None:
        """
        Runs the benchmarks added.

        Parameters
        -----------
        output_file: ``str`` | ``None``
            The json file to write the benchmark results to.
        
        run_metadata: dict[``str``, ``Any``] | ``None``
            Additional information to be printed, does not affect runtime.

        Raises
        --------
        ValueError
            Both benchmarks for speed and memory usage are empty
        """
        speed_base_data = {}
        mem_base_data = {}
        if self._speed_benchmarks:
            speed_base_data = self._benchmark_speed(self._speed_benchmarks)

            speed_data = speed_base_data[BmType.SPEED]
            speed_data['run_metadata'] = run_metadata

            _print_common_info(speed_data)
            logger.blue("\n".join(SPEED_START_STR))
            _print_per_run_info(speed_data, BmType.SPEED)
            self._print_data_speed(speed_data)

        if self._mem_benchmarks:
            mem_base_data = self._benchmark_mem(self._mem_benchmarks)
            mem_data = mem_base_data[BmType.MEMORY]
            mem_data['run_metadata'] = run_metadata

            if not self._speed_benchmarks:
                _print_common_info(mem_data)
            logger.blue("\n".join(MEM_START_STR))
            _print_per_run_info(mem_data, BmType.MEMORY)
            self._print_data_mem(mem_data)
            logger.info("\n".join(END_STR))
        else:
            logger.info("\n".join(END_STR))

        if not speed_base_data and not mem_base_data:
            raise ValueError("Both 'speed_base_data' and 'mem_base_data' are empty!")

        output_file = output_file or (sys.argv[1].removeprefix('--output=') if (len(sys.argv) > 1 and "--output=" in sys.argv[1]) else None)
        if output_file is not None:
            speed_base_data.update(mem_base_data)
            self._write_data_to_output(output_file, speed_base_data)
    

    def clear_benchmarks(self, *, clear_speed: bool = True, clear_memory: bool = True):
        """
        Clears the internal benchmarks. Useful if you want to run benchmarks with different arguments.

        Parameters
        ----------
        clear_speed: ``bool``
            Whether to clear the benchmarks benched for speed. Defaults to ``True``.
        clear_memory: ``bool``
            Whether to clear the benchmarks benched for memory usage. Defaults to ``True``.
        """
        if clear_speed:
            self._speed_benchmarks.clear()
        
        if clear_memory:
            self._mem_benchmarks.clear()


    #  +================================+
    #  |                                |
    #  |        BENCHMARK SPEED         |
    #  |                                |
    #  +================================+
    
    def _get_warmup_theshold_and_runs(self, func: Callable, args: tuple, kwargs: dict | None, target_multiplier: int = 10, 
                                      *, is_manual: bool, copy_args: bool) -> tuple[float, int]:
        tt: float = 0
        n = 5
        for _ in range(n):
            if is_manual:
                if args or kwargs:
                    copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                    tt += func(*copied_args, **copied_kwargs)
                else:
                    tt += func()
            else:
                if args or kwargs:
                    copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                    start = perf_counter()
                    func(*copied_args, **copied_kwargs)
                    tt += perf_counter() - start
                else:
                    start = perf_counter()
                    func()
                    tt += perf_counter() - start

        elapsed = tt / n
        warmup_threshold = max(0.15 * JIT_MULTIPLIER, elapsed * target_multiplier)
        runs = min(max(5 * JIT_MULTIPLIER, int(0.25 * JIT_MULTIPLIER / elapsed)), 1_000_00)

        return warmup_threshold, int(runs)

    def _benchmark_speed(self, functions: list[tuple[Callable, FunctionMetadata]]) -> dict:
        base_data = self._setup_base_data(len(functions), BmType.SPEED)
        data = base_data[BmType.SPEED]

        for bm, func_metadata in functions:
            args, kwargs, is_manual, copy_args = get_attributes_from_slots(func_metadata)
            bm_name = bm.__name__
            bm_map = data['benchmarks'][bm_name] = {}
            bm_map['name'] = bm_name
            bm_map['description'] = bm.__doc__
            bm_map['values'] = []
            # get warmup and the runs per bm
            warmup_threshold, runs = self._get_warmup_theshold_and_runs(bm, args, kwargs, is_manual=is_manual, copy_args=copy_args)
            if self.warmup_threshold:
                warmup_threshold = self.warmup_threshold

            if self.runs:
                runs = self.runs
            elapsed: float = 0
            warmup_loops: int = 0
            while elapsed < warmup_threshold:
                copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                start = perf_counter()
                bm(*copied_args, **copied_kwargs) if (copied_args or copied_kwargs) else bm()
                elapsed += perf_counter() - start
                warmup_loops += 1

            bm_map['warmup_loops'] = warmup_loops
            bm_map['runs'] = runs
            
            if not is_manual:
                for _ in range(runs):
                    copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                    start = perf_counter()
                    bm(*copied_args, **copied_kwargs) if (copied_args or copied_kwargs) else bm()
                    bm_map['values'].append(perf_counter() - start)
            else:
                for _ in range(runs):
                    copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                    bm_map['values'].append(bm(*copied_args, **copied_kwargs) if (copied_args or copied_kwargs) else bm())
        return base_data

    @staticmethod
    def _print_data_speed(data: dict) -> None:
        print(f"\n------- BENCHMARKS -------\n\n")

        analysed_bms = _analyse_benchmark(data, BmType.SPEED)
        if not analysed_bms:
            raise ValueError("analysed_bms is empty!")

        for bm_data in analysed_bms:
            description = (bm_data['description'] or "None").strip('\n') # pypy moment
            bm_general_info = (
                f"Name: {bm_data['name']}",
                f"Description: {description}",
                f"Warmup Loops: {bm_data['warmup_loops']}",
                f"Runs: {bm_data['runs']}\n",
            )
            print("\n".join(bm_general_info))

            bm_mean_min_max = (
                "\nMean: %s",
                "Minimum: %s",
                "Maximum: %s\n"
            )

            logger.info("\n".join(bm_mean_min_max), _format_timing(bm_data['mean']), 
                        _format_timing(bm_data['min']), _format_timing(bm_data['max']))

            q1, q3 = bm_data["quartiles"][0], bm_data["quartiles"][2]
            rv = (q3 - q1) / bm_data['median']
            logger_mode = _get_logger_mode(rv, logger)

            logger_mode("\nStd Dev: +- %s\nRelative Variability: %s\n",
                        _format_timing(bm_data['std_dev']), f"{rv * 100:.1f}%")
    
            if logger_mode == logger.red:
                logger_mode(f"Re-run recommended, variability is too high. (Increase warmup threshold/runs if needed)")
                
            print("---------------------------------------------------------------\
                  \n---------------------------------------------------------------\n")


    #  +==================================+
    #  |                                  |
    #  |     BENCHMARK MEMORY USAGE       |
    #  |                                  |
    #  +==================================+

    def _benchmark_mem(self, functions: list[tuple[Callable, FunctionMetadata]]) -> dict:
        runs = max(self.runs, 150) if isinstance(self.runs, int) else 150
        base_data = self._setup_base_data(len(functions), BmType.MEMORY)
        data = base_data[ BmType.MEMORY]

        for bm, func_metadata in functions:
            args, kwargs, is_manual, copy_args = get_attributes_from_slots(func_metadata)
            bm_name = bm.__name__
            bm_map = data['benchmarks'][bm_name] = {}
            bm_map['name'] = bm_name
            bm_map['description'] = bm.__doc__
            bm_map['memory'] = []
            bm_map['runs'] = runs

            # get warmup and the runs per bm
            n = int(25 * JIT_MULTIPLIER)
            bm_map['warmup_loops'] = n
            for _ in range(n):
                copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                bm(*copied_args, **copied_kwargs) if (copied_args or copied_kwargs) else bm()

            if not is_manual:
                if not HAS_TRACEMALLOC:
                    raise RuntimeError("tracemalloc not found, it is needed to benchmark memory usage")

                tr_malloc.start()
                for _ in range(runs):
                    copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                    bm(*copied_args, **copied_kwargs) if (copied_args or copied_kwargs) else bm()
                    bm_map['memory'].append(tr_malloc.get_traced_memory()[1])
                    tr_malloc.reset_peak()
            else:
                for _ in range(runs):
                    copied_args, copied_kwargs = self.get_args_and_kwargs(args, kwargs, copy_args=copy_args)
                    bm_map['memory'].append(bm(*copied_args, **copied_kwargs) if (copied_args or copied_kwargs) else bm())

        return base_data

    @staticmethod
    def _print_data_mem(data: dict) -> None:
        print(f"\n------- BENCHMARKS -------\n\n")
        analysed_bms = _analyse_benchmark(data, BmType.MEMORY)
        if not analysed_bms:
            raise ValueError("analysed_bms is empty!")
        for bm_data in analysed_bms:
            description = (bm_data['description'] or "None").strip('\n') # pypy moment
            bm_general_info = (
                f"Name: {bm_data['name']}",
                f"Description: {description}",
                f"Warmup Loops: {bm_data['warmup_loops']}",
                f"Runs: {bm_data['runs']}\n",
            )
            print("\n".join(bm_general_info))

            bm_mean_min_max = (
                "\nMean: %s",
                "Minimum: %s",
                "Maximum: %s\n"
            )

            logger.info("\n".join(bm_mean_min_max), _format_bytes(bm_data['mean']), 
                        _format_bytes(bm_data['min']), _format_bytes(bm_data['max']))
            std_dev = bm_data['std_dev']

            q1, q3 = bm_data["quartiles"][0], bm_data["quartiles"][2]
            rv = (q3 - q1) / bm_data['median']
            logger_mode = _get_logger_mode(rv, logger)

            std_dev_fmt = _format_bytes(std_dev)
            rv_str = f"{rv * 100:.1f}%"

            logger_mode("\nStd Dev: +- %s\nRelative Variability: %s\n",
                        std_dev_fmt, rv_str)
            
            if logger_mode == logger.red:
                logger_mode(f"Re-run recommended, variability is too high. (Increase warmup threshold/runs if needed)")
                
            print("---------------------------------------------------------------\
                  \n---------------------------------------------------------------\n")
