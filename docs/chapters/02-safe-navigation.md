# Safe navigation

The forwarding that `Option` does on attributes, calls and items is enough to
walk a chain such as `user.address.city`, where any link may be `None`.
This chapter adds the two functions that start and end such a walk.

## Starting with safe

`safe(obj)` returns `Option(obj)`, but tells the type checker that it returned
the object's own type. Your editor keeps completing `.address` and `.city`,
while at run time every step is an `Option` and a `None` anywhere stops the
walk.

```{python}
from dataclasses import dataclass
from purely import safe


@dataclass
class City:
    name: str


@dataclass
class Address:
    city: City | None


@dataclass
class User:
    address: Address | None


ada = User(Address(City("London")))
nobody = User(None)

print(safe(ada).address.city.name)
print(safe(nobody).address.city.name.is_none())
```

`safe` only protects against `None`. A missing attribute still raises
`AttributeError`, and a missing key still raises `KeyError`, because the
object was asked for something it does not have. For dictionaries, navigate
through `.get`, which returns `None` for a missing key:

```{python}
from purely import safe

config = {"db": {"host": "localhost"}}

print(safe(config).get("db").get("host").unwrap())
print(safe(config).get("cache").get("ttl").is_none())

try:
    safe(config)["cache"]
except KeyError as e:
    print("KeyError:", e)
```

## Ending with ensure

`ensure(value, error)` is where the walk ends. Given an `Option`, it unwraps it
or raises `error`. Given a plain value, it returns it, or raises `error` when
the value is `None`. The same call works whether or not the value came out of
`safe`.

```{python}
from purely import ensure, safe

config = {"db": {"host": "localhost"}}

host = ensure(safe(config).get("db").get("host"), "db.host is required")
print(host)

try:
    ensure(safe(config).get("db").get("port"), "db.port is required")
except ValueError as e:
    print(e)

print(ensure(5))
```

Pass an exception instead of a string to raise your own type:
`ensure(x, KeyError("db.port"))`.

## Checking a type: cast

`purely.core.cast(t, x)` returns `x` when it is an instance of `t` and raises
`TypeError` otherwise. Unlike `typing.cast`, it checks at run time. It is not
exported from the top-level package.

```{python}
from purely.core import cast

print(cast(int, 3))

try:
    cast(int, "3")
except TypeError as e:
    print(e)
```
