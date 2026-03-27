"""
A benchmark to benchmark string operations
"""

from perf_runner import BenchmarkRunner, BmType
from string import ascii_letters
from random import choice as rand_choice, randint

def test_find(s: str, to_find: str):
    """
    Finds `to_find` in a string 10000 times.
    """
    for _ in range(10000):
        s.find(to_find)

def test_slice(s: str):
    """
    Slices a string 10000 times.
    """
    for i in range(10000):
        _ = s[0: i]


def main():
    runner = BenchmarkRunner("String Benchmark")
    random_str = "".join(char for _ in range(1000) for char in rand_choice(ascii_letters))
    
    func_metadata = {
        "test_find": ((random_str, random_str[randint(1, 999)]))
    }
    args = (random_str, )
    runner.add_benchmarks(BmType.SPEED, args=args, func_metadata=func_metadata)
    runner.add_benchmarks(BmType.MEMORY, args=args, func_metadata=func_metadata)
    
    runner.run()

if __name__ == "__main__":
    main()
