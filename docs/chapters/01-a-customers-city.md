# A customer's city

The order confirmation page says where the books will go: "Shipping to
London". A customer record comes from the database, and not every customer
has filled in an address yet, nor every address a city.

```{python}
from dataclasses import dataclass


@dataclass
class Address:
    city: str | None


@dataclass
class Customer:
    name: str
    address: Address | None


ada = Customer("Ada", Address("london"))
grace = Customer("Grace", Address(None))
alan = Customer("Alan", None)
```

The first version checks each step for `None`:

```{python continue}
def shipping_line(customer):
    if customer.address is not None and customer.address.city is not None:
        return f"Shipping to {customer.address.city.title()}"
    return "Shipping address missing"


for c in (ada, grace, alan):
    print(shipping_line(c))
```

It works, and it is already the shape that grows badly. The shop only ships to
some cities, so another check goes in. Then the line has to be shown in the
customer's language, and another goes in. Every new step adds a condition, and
each condition repeats the path to the value: `customer.address.city`, three
times in two lines.

## A box that may be empty

`Option` wraps a value that may be `None`. Instead of checking before each
step, you hand the step to the `Option` with `convert`, and it runs the step
only when there is a value inside. When there is none, or when a step returns
`None`, the result is an empty `Option`, and every later step is skipped. At
the end, `unwrap` takes the value out, or gives back the `default` you pass
when the box is empty.

```{python continue}
from purely import Option


def shipping_line(customer):
    return (
        Option(customer.address)
        .convert(lambda address: address.city)
        .convert(str.title)
        .convert(lambda city: f"Shipping to {city}")
        .unwrap(default="Shipping address missing")
    )


for c in (ada, grace, alan):
    print(shipping_line(c))
```

Each step now says one thing, and none of them mentions `None`. Adding the
rule about where the shop ships is one more step. `keepif` keeps the value
only when a test passes, and empties the box otherwise. `|` is a shorter way
to write `convert`.

```{python continue export=examples/shipping_line.py}
"""The shipping line on the order confirmation page."""

from dataclasses import dataclass

from purely import Option

SHIPS_TO = {"London", "Paris"}


@dataclass
class Address:
    city: str | None


@dataclass
class Customer:
    name: str
    address: Address | None


def shipping_line(customer: Customer) -> str:
    city = (
        Option(customer.address)
        .convert(lambda address: address.city)
        .convert(str.title)
        .keepif(lambda city: city in SHIPS_TO)
    )
    return (city | (lambda c: f"Shipping to {c}")).unwrap(
        default="We cannot ship to this address yet"
    )


if __name__ == "__main__":
    for customer in [
        Customer("Ada", Address("london")),
        Customer("Grace", Address(None)),
        Customer("Alan", None),
        Customer("Edsger", Address("amsterdam")),
    ]:
        print(f"{customer.name:<7} {shipping_line(customer)}")
```

## Asking the box

Sometimes you only need to know whether there is a value: the checkout button
stays disabled until the customer can be shipped to. `is_some` and `is_none`
answer that without taking the value out. Only `None` counts as empty: `0`,
`""` and `[]` are values.

```{python continue}
def can_ship(customer):
    return (
        Option(customer.address)
        .convert(lambda address: address.city)
        .convert(str.title)
        .keepif(lambda city: city in SHIPS_TO)
        .is_some()
    )


print(can_ship(Customer("Ada", Address("london"))), can_ship(alan))
print(Option(0).is_some(), Option(None).is_none())
```

When there is no sensible default and an empty box is a bug, `unwrap` can
raise instead: `unwrap(error="no city")` raises `ValueError("no city")`. The
next chapter has a better tool for that case. An `Option` also compares equal
to the plain value it holds, so `Option("Paris") == "Paris"` is true, which
keeps tests short.
