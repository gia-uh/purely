# The checkout, end to end

Everything is in place for the whole checkout. A batch of carts arrives, and
each one goes through the same path: check the cart, price it with the
campaign's rules, charge it through the gateway, and tell the customer. One bad
cart must not stop the others, and each failure must say why. This chapter
adds nothing new to purely: it only combines the previous seven.

| Step | Tool | Chapter |
|---|---|---|
| a missing coupon defaults to none | `safe`, `Option` | 1, 2 |
| a cart is valid or says why not | `Ok`, `Err`, `then` | 3 |
| the batch runs as one pipeline | `Chain` | 4 |
| the rules apply in order | `curry`, `pipe` | 5 |
| each outcome gets its own message | `dispatcher` | 6 |
| the gateway is injected | `Registry`, `depends` | 7 |

## The pieces

The services and the pricing rules come straight from chapters 5 and 7:

```{python export=examples/checkout.py}
"""Check, price, charge and notify a batch of carts."""

from dataclasses import dataclass, field

from purely import Chain, Err, Ok, Registry, curry, depends, dispatcher, pipe, safe


class Gateway:
    def charge(self, amount: float) -> str: ...


class FakeGateway(Gateway):
    def __init__(self):
        self.charged = []

    def charge(self, amount):
        self.charged.append(amount)
        return f"rcpt-{len(self.charged)}"


registry = Registry()
registry.register(FakeGateway())


@curry
def coupon(off, amount):
    return max(amount - off, 0)


@curry
def add_tax(rate, amount):
    return amount * (1 + rate)
```

A cart may or may not carry a coupon code, and the code may be unknown. That is
a missing value with a default, the job of `safe` and `unwrap`:

```{python continue export=examples/checkout.py}


COUPONS = {"WELCOME5": 5.0}


@dataclass
class Cart:
    customer: str
    books: list[float] = field(default_factory=list)
    coupon: str | None = None


def coupon_value(cart):
    return safe(COUPONS).get(cart.coupon).unwrap(default=0.0)
```

## One cart, as a result

Checking and pricing a cart can fail with a reason, so they run in a result
chain. Each step raises when something is wrong, and `then` turns that into an
`Err`. Charging needs the gateway, which comes from the registry:

```{python continue export=examples/checkout.py}


def check(cart):
    if not cart.books:
        raise ValueError(f"{cart.customer}: the cart is empty")
    return cart


def price(cart):
    return pipe(
        sum(cart.books),
        coupon(coupon_value(cart)),
        add_tax(0.20),
        lambda a: round(a, 2),
    )


@registry.inject
def charge(cart, gateway: Gateway = depends(Gateway)):
    total = price(cart)
    return cart.customer, total, gateway.charge(total)


def process(cart):
    return Ok(cart).then(check).then(charge)
```

## Telling the customer

An outcome is an `Ok` or an `Err`, and each gets a different message, so
`dispatcher` picks by type:

```{python continue export=examples/checkout.py}


@dispatcher
def message(outcome):
    return f"?? {outcome!r}"


@message.dispatch
def _(outcome: Ok):
    customer, total, receipt = outcome.value
    return f"{customer}: charged £{total:.2f}, receipt {receipt}"


@message.dispatch
def _(outcome: Err):
    return f"not charged: {outcome.error}"
```

## The batch

The batch is a `Chain`: each cart becomes an outcome, each outcome a message.
Because every cart's failure is held inside its own `Err`, the chain itself
does not fail, and every cart gets an answer.

```{python continue export=examples/checkout.py}


def run(carts):
    return Chain(carts).map(process).map(message).then("\n".join).unwrap()


CARTS = [
    Cart("ada", [12.0, 30.0], "WELCOME5"),
    Cart("grace", []),
    Cart("alan", [8.5], "NOSUCHCODE"),
]

if __name__ == "__main__":
    print(run(CARTS))
    print("charged:", registry.resolve(Gateway).charged)
```

The plain-Python version of this program would hold every rule from the
previous chapters in one function, with its `None` checks, `try` blocks and
`isinstance` ladder interleaved. Here each rule is a few lines with one job,
and the last function only says in what order they run.
