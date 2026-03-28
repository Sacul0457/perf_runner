> [!WARNING]
> This project is still under development. There will be breaking changes to the API and CLI commands.
> The internals are going to be re-written/changed frequently.
> 
> Not recommended to be used in production yet, but testing it out is much appreciated if possible!

# perf_runner
A python benchmark runner and analyzer for fast and efficient benchmarking.

## Features
- Easy and accurate benchmarking.
- Flexible API.
- Adaptive warmup threshold and runs (including JITs) - This ensures stable and accurate results.
- Detailed and colour coded results.

## Installing

Currently it is not on Pip sadly, but probably will be in the future!
Hence you have to install the development version.

> [!NOTE]
> Python 3.11 or higher is required

```sh
# Linux/macOS
python3 -m pip install -U git+https://github.com/Sacul0457/perf_runner

# Windows
py -3 -m pip install -U git+https://github.com/Sacul0457/perf_runner
```

# Example
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
-m perf_runner compare_to bm1.json bm2.json
```


## Side notes
- The code is really a mess, I know 😭... (This is a project I picked up along the way while attempting to do something else :p)
- I have roughly compared the results with pyperf and it fairly similar, sometimes exactly the same!
- Contributions are absolutely welcomed!
