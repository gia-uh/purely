# Pipelines

Nested calls such as `str(round(abs(x)))` read from the inside out. A pipeline
writes the same steps in the order they happen. Purely has two: `pipe`, a
plain function, and `Chain`, a container that adds list operations and error
handling the way `Ok` and `Err` do.

## pipe and tap

`pipe(value, f, g, h)` returns `h(g(f(value)))`. `tap(value, f)` calls `f` for
its side effect, such as logging, and returns `value` unchanged, so it can sit
inside a pipeline.

```{python}
from functools import partial
from purely import pipe, tap

result = pipe(
    -3.7,
    abs,
    round,
    partial(tap, func=lambda n: print("rounded to", n)),
    str,
)
print(repr(result))
```

## Chain

`Chain(value)` holds a value and an error, of which at most one is set.
`then` passes the whole value through a function, and `|` is the same as
`then`. `unwrap` returns the value at the end.

```{python}
from purely import Chain

print(Chain(5).then(lambda x: x * 2).then(str).unwrap())
print((Chain(5) | (lambda x: x * 2) | str).unwrap())
```

### Lists: map and filter

`map` and `filter` work on each item of the value, which must be an iterable
other than a string or bytes. Both build a list straight away.

```{python}
from purely import Chain

names = (
    Chain(["ada", "alan", "grace", "edsger"])
    .filter(lambda n: len(n) > 3)
    .map(str.title)
    .unwrap()
)
print(names)
```

### Errors: catch, test, error, fail

When any step raises, the `Chain` stores the exception, skips every later
step, and `is_ok` turns false. `unwrap` then raises the stored exception, or
returns the default you pass it. `error()` returns the exception without
raising, and `test()` raises it and returns nothing, for a chain run only for
its side effects. `catch` recovers: it calls a function with the exception and
continues with what it returns. `Chain.fail(e)` builds a chain that has
already failed.

```{python}
from purely import Chain

failed = Chain(10).then(lambda x: x / 0).then(lambda x: x + 1)
print(failed.is_ok, repr(failed.error()))
print(failed.unwrap(default=0))
print(failed.catch(lambda e: -1).unwrap())

print(Chain("abc").map(str.upper).error())

try:
    Chain.fail(ValueError("bad input")).test()
except ValueError as e:
    print("test raised:", e)
```

`Chain.tap` calls a function with the value and keeps the value, like `tap`.
If the function raises, the chain fails.

```{python}
from purely import Chain

seen = []
total = Chain([3, 1, 2]).tap(seen.append).then(sum).unwrap()
print(total, seen)
```

A `Chain` compares equal to a value, an `Option` or another `Chain` holding
the same value: `Chain([1, 2]) == [1, 2]`. Comparing a failed chain raises its
error.

In purely 1.2, `Chain.then`, `Chain.tap` and `Ok.then` catch every exception,
including a `NameError` or `AttributeError` from a typo in your own function.
When a chain fails unexpectedly, look at `error()` first.
