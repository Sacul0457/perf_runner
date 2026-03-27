"""
A benchmark to benchmark list operations
"""

from perf_runner import BenchmarkRunner, BmType
from time import perf_counter

def test_append():
    """
    Appends an integer to a list 10000 times
    """

    l = []
    for i in range(10000):
        l.append(i)

def test_extend():
    """
    Extends a list of 4 elements to a list 10000 times
    """
    l = []
    for i in range(10000):
        l.extend([i, "c", [i], 10.5])

def test_insert():
    """
    Inserts an integer into a list at index 0 10000 times
    """
    l = []
    for i in range(10000):
        l.insert(0, i)

def test_pop(l):
    """
    Pops the last item from a list 10000 times
    """
    for i in range(10000):
        l.pop()

def test_pop_index(l):
    """
    Pops the first item from a list 10000 times
    """
    start = perf_counter()
    for i in range(10000):
        l.pop(0)
    return perf_counter() - start


def main():
    runner = BenchmarkRunner("List Benchmark")
    l = list(range(10000))
    args = (l, )
    func_speed_metadata = {
        # We are going to deep copy the args but not measure the timing manually
        "test_pop": (args, False, True),

        # We are going to deep copy the args and measure the timing manually
        "test_pop_index": ((args, True, True))
    }
    # The rest of the args do not need to be deep copied
    runner.add_benchmarks(BmType.SPEED, func_metadata=func_speed_metadata)
    
    func_mem_metadata = {
        # We are going to deep copy the args but not measure the timing manually
        "test_pop": (args, False, True),

        # We are going to deep copy the args but not measure the timing manually
        "test_pop_index": ((args, False, True))
    }

    runner.add_benchmarks(BmType.MEMORY, func_metadata=func_mem_metadata)
    runner.run()

if __name__ == "__main__":
    main()
