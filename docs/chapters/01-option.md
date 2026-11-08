# Option

Most code that handles a missing value does it with `if x is None` checks
spread over every step. `Option` wraps the value once and lets each step
decide what to do when there is nothing inside.

## Wrapping a value

`Option(value)` holds either a value or `None`. `is_some` and `is_none` say
which. Only `None` counts as empty: `0`, `""` and `[]` are values.

```{python}
from purely import Option

print(Option(10).is_some(), Option(None).is_none(), Option(0).is_some())
```

## Transforming it

`convert` applies a function to the value and wraps the result. On an empty
`Option` it skips the function and stays empty, so a sequence of steps needs
no checks between them. The `|` operator is the same as `convert`.
`keepif` keeps the value only when a predicate holds.

```{python}
from purely import Option

price = Option(40).convert(lambda p: p * 1.25) | round
print(price.unwrap())

missing = Option(None).convert(lambda p: p * 1.25) | round
print(missing.is_none())

print(Option(7).keepif(lambda n: n % 2 == 0).is_none())
```

## Getting the value out

`unwrap` returns the value. On an empty `Option` it returns `default` when you
pass one, and otherwise raises `error`. A string becomes a `ValueError` with
that message.

```{python}
from purely import Option

print(Option(None).unwrap(default=0))

try:
    Option(None).unwrap(error="no price")
except ValueError as e:
    print(e)
```

An `Option` compares equal to another `Option` with the same value, and to the
bare value itself, so `Option(3) == 3` holds.

```{python}
from purely import Option

print(Option(3) == 3, Option(3) == Option(3), Option(None) == None)
```

## Reaching inside

An `Option` forwards attribute access, calls and indexing to the value it
holds, and wraps each answer in a new `Option`. On an empty `Option` each of
them returns an empty `Option`. This is what the next chapter builds on.

```{python}
from purely import Option

name = Option("ada lovelace").title()
print(name.unwrap())

print(Option(None).title().is_none())
print(Option([10, 20, 30])[1].unwrap())
```

Assigning through an `Option` (`Option(d)["k"] = v`) writes to the value it
holds. Purely 1.2 does not guard that case against `None`: on an empty
`Option` it raises `AttributeError`.
