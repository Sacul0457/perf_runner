import sys
from .utils import _analyse_benchmark, _print_common_info, _print_per_run_info, \
    _print_bm_info, _print_mean_stddev, Logger, END_STR, SPEED_START_STR, MEM_START_STR, \
    GeometricMean, _compute_diff
from json import load
from .bm_runner import BenchmarkRunner
from .api_types import BmType
from argparse import ArgumentParser

from typing import Literal

_main_logger = Logger()

def _compare(base: dict, base_name: str, other: dict, other_name: str):
    print_speed =  BmType.SPEED in base and BmType.SPEED in other
    if print_speed:
        gm = GeometricMean()
        _main_logger.blue("\n".join(SPEED_START_STR))
        base_data = _analyse_benchmark(base[BmType.SPEED], BmType.SPEED)
        other_data = _analyse_benchmark(other[BmType.SPEED], BmType.SPEED)

        print(f"{base_name}:")
        _print_common_info(base[BmType.SPEED])
        _print_per_run_info(base[BmType.SPEED], BmType.SPEED)

        print(f"{other_name}:")
        _print_common_info(other[BmType.SPEED])
        _print_per_run_info(other[BmType.SPEED], BmType.SPEED)

        print(f"------- BENCHMARKS -------\n\n")
        

        for base_bm, other_bm in zip(base_data, other_data):
            description = (base_bm['description'] or "None").strip('\n') # pypy moment
            bm_info = (
                "Benchmark:",
                f"- Name: {base_bm['name']}",
                f"- Description: {description}\n",
            )
            print("\n".join(bm_info))

            print(f"{base_name}:")
            _print_bm_info(base_bm, BmType.SPEED)

            print(f"{other_name}:")
            _print_bm_info(other_bm, BmType.SPEED)

            bm_name = base_bm['name']
            base_mean = base_bm['mean']
            base_std_dev = base_bm['std_dev']

            other_mean = other_bm['mean']
            other_std_dev = other_bm['std_dev']


            diff = _compute_diff(base_mean, other_mean, BmType.SPEED)
            _print_mean_stddev((base_mean, base_std_dev, base_name), (other_mean, other_std_dev, other_name), diff, bm_name=bm_name, bm_type = BmType.SPEED)
            gm.add(diff[1], base_mean=base_mean, other_mean=other_mean)

            print("\n========================================\n========================================\n")

        gm.print_geomean(BmType.SPEED)

    if BmType.MEMORY in base and BmType.MEMORY in other:
        gm = GeometricMean()
        _main_logger.blue("\n".join(MEM_START_STR))
        base_data = _analyse_benchmark(base[BmType.MEMORY], BmType.MEMORY)
        other_data = _analyse_benchmark(other[BmType.MEMORY], BmType.MEMORY)

        print(f"{base_name}:")
        if not print_speed:
            _print_common_info(base[BmType.MEMORY])
        _print_per_run_info(base[BmType.MEMORY], BmType.MEMORY)

        print(f"{other_name}:")
        if not print_speed:
            _print_common_info(base[BmType.MEMORY])
        _print_per_run_info(other[BmType.MEMORY], BmType.MEMORY)

        print(f"------- BENCHMARKS -------\n\n")
        

        for base_bm, other_bm in zip(base_data, other_data):
            description = (base_bm['description'] or "None").strip('\n') # pypy moment
            bm_info = (
                "Benchmark:",
                f"- Name: {base_bm['name']}",
                f"- Description: {description}\n",
            )
            print("\n".join(bm_info))

            print(f"{base_name}:")
            _print_bm_info(base_bm, BmType.MEMORY)

            print(f"{other_name}:")
            _print_bm_info(other_bm, BmType.MEMORY)

            bm_name = base_bm['name']
            base_mean = base_bm['mean']
            base_std_dev = base_bm['std_dev']

            other_mean = other_bm['mean']
            other_std_dev = other_bm['std_dev']

            diff = _compute_diff(base_mean, other_mean, BmType.MEMORY)
            _print_mean_stddev((base_mean, base_std_dev, base_name), (other_mean, other_std_dev, other_name), diff, bm_name=bm_name, bm_type = BmType.MEMORY)
            gm.add(diff[1], base_mean=base_mean, other_mean=other_mean)

            print("\n========================================\n========================================\n")

        gm.print_geomean(BmType.MEMORY)
        _main_logger.info("\n".join(END_STR))
    else:
        _main_logger.info("\n".join(END_STR))


def print_help_command(cmd_type: Literal['-h', '--help','compare_to', '' \
'show']):
    if cmd_type in ('-h', '--help'):
        usg_descr = (
            "Usage: -m Runner [commands | options]",
            "Description: Display and compare benchmark results.\n",
        )

        options = (
            "Options:",
            "   - [-h | --help], Prints this command.\n",
        )

        commands = (
            "Commands:",
            "   show            Prints detailed information about a benchmark from a json file.",
            "   compare_to      Compares the results of two benchmark results",
            "(Add the option '-h' after the command to get more information)\n"
        )

        examples = (
            "Examples:",
            "   -m Runner show [files]",
            "   -m Runner compare_to [files]",
        )

        print("\n".join(usg_descr))
        _main_logger.blue("\n".join(options))
        _main_logger.info("\n".join(commands))
        _main_logger.green("\n".join(examples))
    elif cmd_type == 'show':
        usg_descr = (
            "Usage: -m Runner show [files]",
            "Description: Display benchmark results from json files.\n",
        )

        examples = (
            "Examples:",
            "   -m Runner show bm1.json",
            "   -m Runner show bm2.json bm2.json",
        )

        _main_logger.info("\n".join(usg_descr))
        _main_logger.green("\n".join(examples))
    else:
        usg_descr = (
            "Usage: -m Runner compare_to {file1} {file2}",
            "Description: Compare benchmarks results from 2 json files.\n",
        )

        examples = (
            "Examples:",
            "   -m Runner compare_to bm1.json bm2.json",
        )

        _main_logger.info("\n".join(usg_descr))
        _main_logger.green("\n".join(examples))

    sys.exit(0)


def compare_to(base_file_path: str, other_file_path: str):
    
    with open(base_file_path, "r") as f:
        base_data = load(f)

    with open(other_file_path, "r") as f:
        other_data = load(f)

    if not base_data or not other_data:
        raise ValueError(f"Missing data")
    
    _compare(base_data, base_file_path.removesuffix(".json"), other_data, other_file_path.removesuffix(".json"))


def _show(data: dict):
    if BmType.SPEED in data:
        speed_data = data[BmType.SPEED]
        _print_common_info(speed_data)
        _main_logger.blue("\n".join(SPEED_START_STR))
        _print_per_run_info(speed_data, BmType.SPEED)
        BenchmarkRunner._print_data_speed(speed_data)

    if  BmType.MEMORY in data:
        mem_data = data[BmType.MEMORY]
        if not BmType.SPEED in data:
            _print_common_info(mem_data)

        _main_logger.blue("\n".join(MEM_START_STR))
        _print_per_run_info(mem_data, BmType.MEMORY)
        BenchmarkRunner._print_data_mem(mem_data)
        _main_logger.info("\n".join(END_STR))
    else:
        _main_logger.info("\n".join(END_STR))


def show(args: list[str]):
    for i in range(0, len(args)):
        file_path = args[i]
        try:
            with open(file_path, "r") as f:
                data = load(f)
        except FileNotFoundError:
            _main_logger.error("%s could not be opened, skipping", repr(file_path), colour_all=True)
            continue

        if not data:
            _main_logger.error("%s is empty, skipping", repr(file_path), colour_all=True)
            continue

        _show(data)


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # show command
    show_parser = subparsers.add_parser("show")
    show_parser.add_argument(
        "files",
        nargs="+",
        type=str,
        help="JSON files containing benchmark data"
    )

    # compare_to command
    compare_parser = subparsers.add_parser("compare_to")
    
    compare_parser.add_argument(
        "file1",
        type=str
    )
    compare_parser.add_argument(
        "file2",
        type=str
    )

    args = parser.parse_args()
    if hasattr(args, "files"):
        show(args.files)
    else:
        assert(args.file1 and args.file2)
        compare_to(args.file1, args.file2)


if __name__ == "__main__":
    main()
