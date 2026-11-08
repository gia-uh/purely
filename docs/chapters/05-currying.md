# Currying

Every step of a pipeline takes one argument: the value flowing through it. A
function that needs more, such as `scale(factor, x)`, has to be wrapped in a
`lambda` or a `partial` first. `curry` removes that wrapper: a curried function
called with fewer arguments than it needs returns a function waiting for the
rest.

```{python}
from purely import curry, pipe


@curry
def scale(factor, x):
    return factor * x


@curry
def clamp(low, high, x):
    return max(low, min(high, x))


print(scale(3, 4), scale(3)(4))
print(clamp(0, 10)(42), clamp(0)(10)(-5))
print(pipe(7, scale(2), clamp(0, 10)))
```

The number of arguments needed is the number of parameters without a default.
Parameters with defaults and `*args` or `**kwargs` are not waited for.
Keyword arguments count like positional ones:

```{python continue}
@curry
def greet(greeting, name, punctuation="!"):
    return f"{greeting}, {name}{punctuation}"


hello = greet("Hello")
print(hello("Ada"), hello(name="Grace"))
```

## Types

To a type checker, `curry` on a function of two to five parameters returns
`Curried2`, `Curried3`, `Curried4` or `Curried5`, protocols in `purely.curry`
that describe every way of splitting the arguments. `scale(3)` is typed as a
function from the second parameter to the result, and `clamp(0)` as a
`Curried2`. They exist only for annotations and are never instantiated.

```{python}
from purely.curry import Curried2, curry


@curry
def scale(factor: float, x: float) -> float:
    return factor * x


double: Curried2[float, float, float] = scale
print(double(2.0)(21.0))
```
