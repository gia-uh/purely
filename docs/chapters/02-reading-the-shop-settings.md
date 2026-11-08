# Reading the shop's settings

The shop reads its settings at startup from a JSON file, parsed into nested
dictionaries. Some settings are required: without a payment key, the shop must
refuse to start. Others are optional and have a default. Any section may be
missing or `null`.

```{python}
SETTINGS = {
    "payments": {"provider": "stripe", "key": "sk_test_123"},
    "shipping": {"free_over": 50},
    "newsletter": None,
}
```

With plain dictionaries every lookup is a small negotiation:

```{python continue}
shipping = SETTINGS.get("shipping") or {}
free_over = shipping.get("free_over", 40)

newsletter = SETTINGS.get("newsletter") or {}
sender = newsletter.get("sender", "books@example.com")

payments = SETTINGS.get("payments") or {}
key = payments.get("key")
if key is None:
    raise SystemExit("payments.key is required")

print(free_over, sender, key)
```

Three settings took nine lines, and the important difference, which ones are
required, is buried in an `if` at the end.

## Walking through with safe

An `Option` does more than `convert`. Ask it for an attribute, call it, or
index it, and it passes the request on to the value inside and wraps the
answer in a new `Option`. When the box is empty, it stays empty and asks
nothing. A chain of lookups therefore stops quietly at the first `None`.

`safe(value)` starts such a chain. It returns an `Option`, but tells your
editor and type checker that it returned the value's own type, so completion
on `.get` or `.address` keeps working.

```{python continue}
from purely import safe

free_over = safe(SETTINGS).get("shipping").get("free_over").unwrap(default=40)
sender = safe(SETTINGS).get("newsletter").get("sender").unwrap(default="books@example.com")
print(free_over, sender)
```

`newsletter` is `None`, so `.get("sender")` was never called on it, and the
default came back.

Use `.get` for dictionaries, not `[...]`. `safe` protects only against `None`.
A key that is not in the dictionary still raises `KeyError`, and an attribute
an object does not have still raises `AttributeError`, because the program
asked for something that is not there.

```{python continue}
try:
    safe(SETTINGS)["tax"]
except KeyError as e:
    print("KeyError:", e)
```

## Insisting with ensure

A required setting needs the opposite of a default: stop with a message that
says what is missing. `ensure(value, error)` returns the value inside an
`Option`, or raises `error` when it is empty. A string becomes a `ValueError`
with that message, and you can pass any exception instead. It also accepts a
plain value, which it returns unless it is `None`.

```{python continue export=examples/settings.py}
"""Read the shop's settings: required ones stop the start, optional ones default."""

from purely import ensure, safe

SETTINGS = {
    "payments": {"provider": "stripe", "key": "sk_test_123"},
    "shipping": {"free_over": 50},
    "newsletter": None,
}


def required(*path):
    node = safe(SETTINGS)
    for key in path:
        node = node.get(key)
    return ensure(node, f"{'.'.join(path)} is required")


def optional(*path, default):
    node = safe(SETTINGS)
    for key in path:
        node = node.get(key)
    return node.unwrap(default=default)


if __name__ == "__main__":
    print("payment key:", required("payments", "key"))
    print("free shipping over:", optional("shipping", "free_over", default=40))
    print(
        "newsletter sender:",
        optional("newsletter", "sender", default="books@example.com"),
    )
    try:
        required("payments", "webhook_secret")
    except ValueError as e:
        print("refusing to start:", e)
```

The rule about which settings are required is now in the name of the function
that reads them.

## Back to the city

The same forwarding shortens the first chapter's shipping line. Attribute
access replaces the `convert(lambda address: address.city)` step:

```{python}
from dataclasses import dataclass
from purely import ensure, safe


@dataclass
class Address:
    city: str | None


@dataclass
class Customer:
    address: Address | None


print(safe(Customer(Address("london"))).address.city.title().unwrap(default="?"))
print(safe(Customer(None)).address.city.title().unwrap(default="?"))
print(ensure(safe(Customer(Address("paris"))).address.city))
```

Assigning through an `Option` (`safe(d)["k"] = v`) writes to the value inside.
In purely 1.2 that case is not guarded against `None`: on an empty `Option`
it raises `AttributeError`.

One more check fits here. A setting such as `free_over` must be a number, and
JSON may hand you a string. `cast(int, value)` from `purely.core` returns the
value when it has that type and raises `TypeError` otherwise, which makes a
wrong type fail at startup rather than at the first order. Unlike
`typing.cast`, it checks at run time.

```{python}
from purely.core import cast

print(cast(int, 50))
try:
    cast(int, "50")
except TypeError as e:
    print(e)
```
