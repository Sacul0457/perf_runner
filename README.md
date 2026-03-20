# perf_runner
A python benchmark runner and analyzer for fast and efficient benchmarking.

## Features
- Easy and accurate benchmarking. (I've tested the results with pyperf and the results are fairly close, I'll upload them soon)
- Flexible API.
- Adaptive warmup threshold and runs (including JITs) - This ensures for stable and accurate results.
- Detailed and coloured results.

# Example
Code:
```python
"""
A benchmark to benchmark list operations
"""

from perf_runner import BenchmarkRunner, BmType

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

def main():
    runner = BenchmarkRunner("List Benchmark")
    runner.add_benchmarks(bm_type=BmType.SPEED)
    runner.add_benchmarks(bm_type=BmType.MEMORY)
    runner.run()

if __name__ == "__main__":
    main()
```

- ### [Output](https://github.com/Sacul0457/perf_runner/blob/main/assets/example_1.mp4)

- ### [More Examples](examples)

# CLI Commands

### `show` 
Shows detailed information from a generated json file. 
Useful if you want to store the data and still be able to analyse the information later on.
```sh
-m perf_runner show bm.json
```

#### `compare_to`
This compares the benchmark results of two generated json files.
```sh
-m perf_runner bm1.json bm2.json
```
### [Example Output](https://github.com/Sacul0457/perf_runner/blob/main/assets/example_2.mp4)
