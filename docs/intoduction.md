# perf runner
Generally how you should use this:
- Import `BencharmkRunner` and `BmType` from `perf_runner`.
- Create an instance of `BencharmkRunner`
- Use the `BencharmkRunner.add_benchmarks` to add the benchmarks - This will add all the functions in the file except for `main`.
- Having said that, you should setup and call `BencharmkRunner.run` inside a function called `main`.
- Just like that, you are done!

See [More Examples](examples)

## Table of Contents
