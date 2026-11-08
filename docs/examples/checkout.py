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


COUPONS = {"WELCOME5": 5.0}


@dataclass
class Cart:
    customer: str
    books: list[float] = field(default_factory=list)
    coupon: str | None = None


def coupon_value(cart):
    return safe(COUPONS).get(cart.coupon).unwrap(default=0.0)


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
