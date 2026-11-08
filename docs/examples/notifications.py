"""Send each order event the right message, by type and by value."""

from dataclasses import dataclass

from purely import dispatcher


@dataclass
class OrderPlaced:
    order: int
    total: float


@dataclass
class OrderShipped:
    order: int
    carrier: str


@dataclass
class Refunded:
    order: int
    amount: float


@dispatcher
def notify(event):
    return f"(no message for {type(event).__name__})"


@notify.dispatch
def _(event: OrderPlaced):
    return f"Thanks! Order #{event.order} is confirmed, £{event.total:.2f}."


@notify.dispatch
def _(event: OrderShipped):
    return f"Order #{event.order} is on its way with {event.carrier}."


@notify.dispatch
def _(event: Refunded):
    return f"We refunded £{event.amount:.2f} for order #{event.order}."


@notify.when(lambda event: isinstance(event, Refunded) and event.amount > 100)
def _(event):
    return f"to manager: review refund of £{event.amount:.2f} on #{event.order}"


if __name__ == "__main__":
    for event in [
        OrderPlaced(1, 42.0),
        OrderShipped(1, "Royal Mail"),
        Refunded(2, 250.0),
        Refunded(3, 12.5),
        "unknown",
    ]:
        print(notify(event))
