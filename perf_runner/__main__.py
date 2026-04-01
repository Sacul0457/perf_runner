import sys
from .utils import _analyse_benchmark, _print_common_info, _print_per_run_info, \
    _print_bm_info, _print_mean_stddev, Logger, END_STR, SPEED_START_STR, MEM_START_STR, \
    GeometricMean, _compute_diff
from json import load
from .bm_runner import BenchmarkRunner
from .api_types import BmType

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


def compare_to(args: list[str]):
    if len(args) < 3:
        _main_logger.error("Expected at least 1 arg, got %s instead.\
                           \nRun `-m Runner compare_to -h' for more information.", len(args) - 2, colour_all=True)
        sys.exit(1)

    if len(args) < 4:
        if args[2] in ('-h', '--help'):
            print_help_command('compare_to')
        else:
            _main_logger.error("Expected 2 args, got %s instead.\
                               \nRun `-m Runner compare_to -h' for more information", len(args) - 2, colour_all=True)
            sys.exit(1)

    
    base_file_path = args[2]
    other_file_path = args[3]

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
    if len(args) == 2:
        _main_logger.error("Expected 1 arg at least, got %s instead.\
                           \nRun '-m Runner show -h' for more information", len(args) - 2, colour_all=True)
        sys.exit(1)
    
    if args[2] in ('-h' or '--h'):
        print_help_command('show')
        return
    
    for i in range(2, len(args)):
        file_path = args[i]
        try:
            with open(file_path, "r") as f:
                data = load(f)
        except FileNotFoundError:
            _main_logger.error("%s could not be opened", repr(file_path), colour_all=True)
            continue

        if not data:
            _main_logger.error("Missing data", colour_all=True)
            continue

        _show(data)


def main():
    args = sys.argv
    if len(args) < 2:
        # print help command
        sys.exit(0)
    
    command: str = args[1]
    if command == "compare_to":
        compare_to(args)
    elif command == "show":
        show(args)
    elif command in ('-h', "--help"):
        print_help_command(command)
    else:
        _main_logger.error("%s is not a valid command.\n", repr(command), colour_all=True)
        print_help_command('-h')
        sys.exit(1)

if __name__ == "__main__":
    main()
