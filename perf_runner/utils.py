import statistics
from json import load as j_load
from collections.abc import Iterable
from os.path import getsize as os_getsize
from .api_types import BmType


from typing import Generator, Any

SPEED_START_STR = ("\n+============================================+",
                     "|              Speed Benchmark               |",
                     "+============================================+\n")

MEM_START_STR = ("\n+============================================+",
                   "|              Memory Benchmark              |",
                   "+============================================+\n")

END_STR = ("\n+============================================+",
             "|               Benchmark End                |",
             "+============================================+\n\n")

class Logger:
    RED = "\033[31m"
    PURPLE = "\033[35m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    BLUE = "\x1b[94m"

    def __init__(self, *, level: int = 2) -> None:
        # 1 for errors only
        # 2 for warnings also also
        self.level = level

    def _color_subs_percent(self, fmt: str, color: str, *args, colour_all: bool):
        """Safely replace each %s in the string with colored args, handles literals like %ss"""
        if not args:
            fmt = f"{color}{fmt}{self.RESET}"
        elif not colour_all:
            for arg in args:
                fmt = fmt.replace("%s", f"{color}{arg}{self.RESET}", count=1)
        else:
            for arg in args:
                fmt = fmt.replace("%s", str(arg), count=1)
            fmt = f"{color}{fmt}{self.RESET}"
        return fmt

    def _log(self, fmt: str, *args, color=GREEN, colour_all: bool, **kwargs):
        if not args:
            message = f"{color}{fmt}{self.RESET}"
        elif "%s" in fmt:
            message = self._color_subs_percent(fmt, color, *args, colour_all=colour_all)
        else:
            message = fmt
        print(message, **kwargs)


    def info(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        self._log(fmt, *args, color=self.PURPLE, colour_all=colour_all, **kwargs)

    def warn(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        if self.level < 2:
            return
        self._log(fmt, *args, color=self.YELLOW, colour_all=colour_all, **kwargs)

    def error(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        if self.level < 1:
            return
        self._log(fmt, *args, color=self.RED, colour_all=colour_all, **kwargs)


    def red(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        self._log(fmt, *args, color=self.RED, colour_all=colour_all, **kwargs)

    def yellow(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        self._log(fmt, *args, color=self.YELLOW, colour_all=colour_all, **kwargs)

    def blue(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        self._log(fmt, *args, color=self.BLUE, colour_all=colour_all, **kwargs)

    def purple(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        self._log(fmt, *args, color=self.PURPLE, colour_all=colour_all, **kwargs)

    def green(self, fmt: str, *args, colour_all: bool = False, **kwargs):
        self._log(fmt, *args, color=self.GREEN, colour_all=colour_all, **kwargs)

_utils_logger = Logger()


def _get_logger_mode(rv: float, logger: Logger):
    if rv <= 0.1:
        logger_mode = logger.green
    elif rv <= 0.2:
        logger_mode = logger.yellow
    else:
        logger_mode = logger.red

    return logger_mode

def _print_common_info(data: dict) -> None:
    info = (
        f"- Python Version: {data['python_version']}",
        f"- Has JIT: {data['has_jit']}",
        f"- Cpu Count: {data['cpu_count']}",
        f"- Name: {data['name']}",
        f"- Description: {data['description']}",
    )
    print("\n".join(info))

def _print_per_run_info(data: dict, bm_type: BmType) -> None:
    info = (
        f"- BM Type: {bm_type}",
        f"- No. of BMs: {data['num_bms']}",
        f"- Generic Warmup Threshold: {data['warmup_threshold']}",
        f"- Generic Runs per BM: {data['runs']}\n"
    )
    print("\n".join(info))

def _print_metadata(data: dict) -> None:
    if data['metadata']:
        print(f"Common Metadata:")
        for key, value in data['metadata'].items():
            print(f"- {key}: {value}")


def _analyse_benchmark(data: dict, bm_type: BmType) -> Generator[dict[str, Any]]:
    
    key = "values" if bm_type == BmType.SPEED else "memory"
    for bm_name, bm_data in data['benchmarks'].items():
        analysed_bm = {
            "name": bm_name,
            "description": bm_data['description'],
            "warmup_loops": bm_data['warmup_loops'],
            "runs": bm_data['runs'],
            "mean": statistics.mean(bm_data[key]),
            "min": min(bm_data[key]),
            "max": max(bm_data[key]),
            "std_dev": statistics.stdev(bm_data[key]),
            "median": statistics.median(bm_data[key]),
            "quartiles": statistics.quantiles(bm_data[key]),
        }
        yield analysed_bm



# +=====================================
#         JSON/DICT FILE UTILS
# +=====================================


def get_json_metadata(obj: str | dict,) -> tuple[str, int, dict]:
    if isinstance(obj, str):
        with open(obj, "r") as f:
            bytes_size = (f"{os_getsize(obj)} bytes")
            dict_o: dict = j_load(f)
    else:
        dict_o = obj
    md: dict[str, int] = {
        "int": 0,
        "list": 0,
        "str": 0,
        "float": 0,
        "dict": 0,
        "bool": 0
    }

    def get_dict_metadata(d: dict) -> int:
        count = 0
        for key, value in d.items():
            count += 1
            # get metadata
            if type(value).__name__ in md:
                md[type(value).__name__] += 1
            if type(key).__name__ in md:
                md[type(key).__name__] += 1

            if isinstance(value, dict):
                count += get_dict_metadata(value)
            elif isinstance(value, Iterable):
                for v in value:
                    if type(v).__name__ in md:
                        md[type(v).__name__] += 1
                    if isinstance(v, dict):
                        count += get_dict_metadata(v)
        return count
    keys = get_dict_metadata(dict_o)
    
    return bytes_size, keys, md


def _format_timing(timing: float) -> str:
    if timing < 0.0003:
        return f"{timing * 1_000_000:.0f}us"
    elif timing < 1:
        return f"{timing * 1000:.1f}ms"
    else:
        return f"{timing:.3f}s"

def _format_bytes(bytes: int) -> str:
    if bytes < 10000:
        return f"{bytes:.1f} bytes"
    else:
        return f"{bytes / 1000:.1f} KiB"

def _print_bm_info(bm_data: dict, bm_type: BmType) -> None:
    base_bm_general_info = (
        f"- Warmup Loops: {bm_data['warmup_loops']}",
        f"- Runs: {bm_data['runs']}",
    )
    print("\n".join(base_bm_general_info))
    bm_mean_min_max = (
        "- Mean: %s",
        "- Minimum: %s",
        "- Maximum: %s\n"
    )
    if bm_type == BmType.SPEED:
        _utils_logger.info("\n".join(bm_mean_min_max), _format_timing(bm_data['mean']), 
                    _format_timing(bm_data['min']), _format_timing(bm_data['max']))
    else:
        _utils_logger.info("\n".join(bm_mean_min_max), _format_bytes(bm_data['mean']), 
                    _format_bytes(bm_data['min']), _format_bytes(bm_data['max']))
        
def _compute_diff(base: float, other: float, bm_type: BmType) -> tuple[float, str]:
    # we assume 'other' is faster

    diff = (base - other) / base * 100
    if other > base:
        x_diff = other / base
        str_value = f"{x_diff:.1f}x/{abs(diff):.1f}% slower" if bm_type == BmType.SPEED else f"{x_diff:.1f}x/{abs(diff):.1f}% more"
    else:
        x_diff = base / other
        str_value = f"{x_diff:.1f}x/{diff:.1f}% faster" if bm_type == BmType.SPEED else f"{x_diff:.1f}x/{abs(diff):.1f}% less"

    return diff, str_value

def _print_mean_stddev(base_args: tuple, other_args: tuple, *, bm_name: str, bm_type: BmType) -> None:
    base_mean, base_stddev, base_name = base_args
    other_mean, otherstddev, other_name = other_args
    
    print(f"{bm_name}: ", end='')
    
    # im lazy to do the whole thing so yeah
    formatter = _format_timing if bm_type == BmType.SPEED else _format_bytes

    p_diff, diff_str = _compute_diff(base_mean, other_mean, bm_type)
    if -2.5 < p_diff < 2.5:
        base_logger = _utils_logger.blue
        other_logger = _utils_logger.blue
    elif base_mean > other_mean:
        base_logger = _utils_logger.red
        other_logger = _utils_logger.green
    else:
        base_logger = _utils_logger.green
        other_logger = _utils_logger.red

    base_logger("[%s] %s %s -> ", base_name, formatter(base_mean), f"+- {formatter(base_stddev)}", end='')
    other_logger("[%s] %s %s", other_name, formatter(other_mean), f"+- {formatter(otherstddev)} ({diff_str})")

def merge_data(base: dict, other: dict) -> None:
    # to be done
    pass
    
