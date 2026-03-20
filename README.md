# perf_runner
A python benchmark runner and analyzer for fast and efficient benchmarking.

## Features
- Easy and accurate benchmarking.
- Flexible API.
- Adaptive warmup threshold and runs (including JITs) - This ensures stable and accurate results.
- Detailed and colour coded results.

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

### Output Format
```sh
- python version:
- has_jit:
...

Benchmark for Speed:
Name:
Description:
runs:
...

Mean:
Min:
Max:

std dev:
Relative Variability: 
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

### Example Output
```sh
- python version:
- has_jit:
...

Benchmark for Speed:

bm1:
 - Name:
 - Description:
 - runs:
 - Mean:
 - Min:
 - Max:

bm2:
 - ...


bm_name: [bm1] mean +- std_dev -> [bm2] mean +- mean +- std_dev (1x/x% faster/slower)
```

## Side notes
- The code is really a mess, I know 😭... (This is a project I picked up along the way while attempting to do something else :p)
- I have roughly compared the results with pyperf and it fairly similar, sometimes exactly the same!
- Contribution is absolutely welcomed!
