Purely is a small, dependency-free library that brings a handful of
functional-programming tools into ordinary Python: values that may be missing,
computations that may fail, pipelines that read from top to bottom, currying,
multiple dispatch and dependency injection. It needs Python 3.12 or later.

```bash
pip install purely
```

The guide builds the library up in the order its pieces depend on each other.
Each chapter uses only what the chapters before it introduced:

1. **Option** wraps a value that may be `None` and lets you work on it without
   checking for `None` at every step.
2. **Safe navigation** uses `Option` to walk through nested objects, with
   `safe` and `ensure` at the two ends.
3. **Results** replace exceptions with values: `Ok` for a success and `Err` for
   a failure.
4. **Pipelines** pass a value through functions with `pipe`, `tap` and
   `Chain`, which also catches errors along the way.
5. **Currying** turns a function of several arguments into a chain of
   one-argument calls, which is what pipelines want.
6. **Dispatch** picks an implementation by the types or values of the
   arguments.
7. **Dependency injection** hands functions the services they need through a
   `Registry`.

The last two chapters are tasks. Each one builds a complete program from those
pieces, and the program is also saved under `docs/examples/` in the repository.

Every code block in this guide runs against the installed package when the
guide is built. The output under a block is what that run printed.
