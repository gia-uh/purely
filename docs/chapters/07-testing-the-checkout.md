# Testing the checkout

The checkout charges the customer's card through a payment gateway. In
production that is a real provider. In a test, charging a real card is the
last thing anyone wants, and yet the first version of the checkout builds the
gateway itself:

```{python}
class StripeGateway:
    def charge(self, amount):
        raise RuntimeError("tried to reach the real payment provider")


def checkout(amount):
    gateway = StripeGateway()
    gateway.charge(amount)
    return f"charged £{amount:.2f}"


try:
    checkout(42.0)
except RuntimeError as e:
    print("in a test:", e)
```

Passing the gateway as an argument fixes the test, but now every caller up
the stack has to carry a gateway down to the checkout, and the next service
(stock, email, a clock) adds another argument to each of them.

## Asking for what you need

A `Registry` holds the shop's services. `register(service)` adds an instance
under its own class and under every class it inherits from, so code can ask
for the general `Gateway` rather than for Stripe. `resolve(Gateway)` returns
it, and raises `LookupError` when nothing is registered for that type.

A function declares what it needs with `depends(Gateway)` as a parameter's
default. `registry.inject` wraps the function so that, on each call, every
such parameter the caller did not pass is resolved from the registry. A caller
that does pass one, such as a test, gets its own value.

```{python export=examples/checkout_services.py}
"""A checkout that asks a registry for its payment gateway."""

from purely import Registry, depends


class Gateway:
    def charge(self, amount: float) -> str: ...


class StripeGateway(Gateway):
    def charge(self, amount):
        raise RuntimeError("tried to reach the real payment provider")


class FakeGateway(Gateway):
    def __init__(self):
        self.charged = []

    def charge(self, amount):
        self.charged.append(amount)
        return f"fake-{len(self.charged)}"


registry = Registry()
registry.register(StripeGateway())


@registry.inject
def checkout(amount: float, gateway: Gateway = depends(Gateway)) -> str:
    receipt = gateway.charge(amount)
    return f"charged £{amount:.2f}, receipt {receipt}"
```

Production code calls `checkout(42.0)` and gets Stripe. A test passes its own
gateway, or builds its own registry, and the production one is never touched:

```{python continue export=examples/checkout_services.py}


def test_checkout_charges_the_amount():
    fake = FakeGateway()
    assert checkout(42.0, gateway=fake) == "charged £42.00, receipt fake-1"
    assert fake.charged == [42.0]


if __name__ == "__main__":
    test_checkout_charges_the_amount()
    print("test passed")
    print(type(registry.resolve(Gateway)).__name__)
    try:
        registry.resolve(int)
    except LookupError as e:
        print(e)
```

## A fresh value on every call

Some services must not be shared: an order number, a timestamp, a database
session. Register a function with no arguments together with the type it
provides, and `resolve` calls it each time. Injection works the same on
`async` functions.

```{python continue}
import asyncio
from itertools import count

order_numbers = count(1001)
registry.register(lambda: next(order_numbers), int)


@registry.inject
async def place_order(order_number: int = depends(int)):
    return f"order #{order_number}"


print(asyncio.run(place_order()), asyncio.run(place_order()))
```

Three cases work differently in purely 1.2. `register(StripeGateway)`, the
class rather than an instance, registers the class object itself, so pass an
instance or a factory function. A factory registered without a type is called
once at registration, to learn what it returns. An object that has a
`__call__` method is taken as a factory.
