# Dispatch

A pipeline step sometimes has to treat a list differently from a number, or a
negative number differently from a positive one. Instead of an `if` chain
inside the function, `dispatcher` turns it into a `Dispatcher`: the decorated
function becomes the default, and you register other implementations on it.

## By type

`dispatch` registers an implementation for the types in its annotations. A
call goes to the implementation whose types match the arguments most closely,
one argument at a time, measured by distance in the argument's class
hierarchy. When nothing matches, the default runs.

```{python}
from purely import dispatcher


@dispatcher
def describe(value):
    return "something"


@describe.dispatch
def _(value: int):
    return "an integer"


@describe.dispatch
def _(value: list):
    return f"a list of {len(value)}"


print(type(describe).__name__)
print(describe(3), describe(True), describe([1, 2]), describe("x"))
```

`bool` is a subclass of `int`, so `describe(True)` takes the `int`
implementation. An unannotated parameter counts as `object`. With several
arguments, the first one narrows the candidates and the next ones break ties:

```{python}
from purely import dispatcher


@dispatcher
def combine(a, b):
    return "default"


@combine.dispatch
def _(a: int, b: object):
    return "int, anything"


@combine.dispatch
def _(a: int, b: str):
    return "int, str"


print(combine(1, "x"), combine(1, 2.0), combine("x", 1))
```

## By value

`when` registers an implementation for a predicate over the arguments.
Predicates are tried first, in the order they were registered, before any type
match. A predicate that raises is skipped.

```{python continue}
@combine.when(lambda a, b: a == b)
def _(a, b):
    return "equal"


print(combine(2, 2), combine(1, "x"))
```

## Ambiguity

Abstract base classes such as `collections.abc.Sized` match by registration,
not inheritance, so they have no place in a class's hierarchy and every one of
them is equally distant. When two implementations match equally well with the
same number of parameters, the call raises `AmbiguityError`, a subclass of
`TypeError` in `purely.dispatch`:

```{python}
from collections.abc import Iterable, Sized
from purely import dispatcher
from purely.dispatch import AmbiguityError


@dispatcher
def size(value):
    return "unknown"


@size.dispatch
def _(value: Sized):
    return "sized"


@size.dispatch
def _(value: Iterable):
    return "iterable"


try:
    size([1, 2])
except AmbiguityError as e:
    print(type(e).__name__, isinstance(e, TypeError))
```
