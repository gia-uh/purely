# Results

`Option` says that a value is missing, but not why. When the reason matters,
return a result instead: `Ok(value)` for a success, `Err(error)` for a
failure. The `Result[T, E]` type alias is `Ok[T] | Err[E]`, for annotations.

## Returning a result

```{python}
from purely import Ok, Err, Result


def parse_age(text: str) -> Result[int, str]:
    if not text.isdigit():
        return Err(f"not a number: {text!r}")
    return Ok(int(text))


print(parse_age("42"), parse_age("forty"))
print(parse_age("42").is_ok(), parse_age("forty").is_err())
```

`Ok` and `Err` define `__match_args__`, so a `match` statement takes them
apart:

```{python continue}
for text in ["42", "forty"]:
    match parse_age(text):
        case Ok(age):
            print("age", age)
        case Err(reason):
            print("rejected:", reason)
```

## Chaining steps: then and catch

`then` applies a function to the value of an `Ok` and wraps the result in a
new `Ok`. On an `Err` it does nothing, so the first failure travels to the end
of the chain. When the function raises, `then` returns `Err` with the
exception.

`catch` is the mirror image. On an `Err` it calls the function with the error
and returns `Ok` with what it returns. On an `Ok` it does nothing.

```{python continue}
print(parse_age("42").then(lambda age: age + 1))
print(parse_age("forty").then(lambda age: age + 1))
print(Ok(10).then(lambda n: n / 0))
print(parse_age("forty").catch(lambda reason: 0))
```

## Getting the value out

`Ok.unwrap()` returns the value. `Err.unwrap()` raises: the error itself when
it is an exception, and a `ValueError` with its text otherwise. Pass a default
to get that instead. In purely 1.2 the default must not be `None`, because
`None` is read as "no default".

```{python continue}
print(parse_age("42").unwrap())
print(parse_age("forty").unwrap(-1))

try:
    parse_age("forty").unwrap()
except ValueError as e:
    print(e)
```
