# Sending notifications

Things happen to an order: it is placed, it ships, it is refunded. Each event
sends the customer a different message, and a refund over £100 also goes to
the manager for review.

```{python}
from dataclasses import dataclass


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
```

The usual answer is one function with an `isinstance` ladder:

```{python continue}
def notify(event):
    if isinstance(event, Refunded) and event.amount > 100:
        return f"to manager: review refund of £{event.amount:.2f} on #{event.order}"
    if isinstance(event, OrderPlaced):
        return f"Thanks! Order #{event.order} is confirmed, £{event.total:.2f}."
    if isinstance(event, OrderShipped):
        return f"Order #{event.order} is on its way with {event.carrier}."
    if isinstance(event, Refunded):
        return f"We refunded £{event.amount:.2f} for order #{event.order}."
    return f"(no message for {type(event).__name__})"


for e in [OrderPlaced(1, 42.0), OrderShipped(1, "Royal Mail"), Refunded(2, 250.0)]:
    print(notify(e))
```

Every new event edits this one function, and the order of the branches
matters: the large-refund rule has to come before the general refund branch,
or it never runs. Nothing in the code says so.

## One function, several implementations

`dispatcher` turns a function into a `Dispatcher`. The decorated function
becomes the default, and `dispatch` registers another implementation for the
types in its annotations. A call goes to the implementation whose types match
the arguments most closely, so a subclass of `Refunded` would still find the
`Refunded` message. When nothing matches, the default runs. Each event's
message now lives in its own function, which can sit next to the event it
belongs to.

`when` registers an implementation for a condition on the values rather than
the types. Conditions are tried first, in the order they were registered, so
the large-refund rule wins without depending on where it is written.

```{python continue export=examples/notifications.py}
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
```

A condition that raises is skipped, as if it had returned false.

## Several arguments

With several arguments, the first argument narrows the candidates and the
next ones break ties. An argument without an annotation matches anything.
Here the channel decides the format, and the event decides the text:

```{python}
from purely import dispatcher


class Email: ...


class Sms: ...


@dispatcher
def send(channel, text):
    return f"[log] {text}"


@send.dispatch
def _(channel: Email, text):
    return f"Subject: Bookshop\n\n{text}"


@send.dispatch
def _(channel: Sms, text: str):
    return text[:20] + ("…" if len(text) > 20 else "")


print(send(Email(), "Order #1 is on its way."))
print(send(Sms(), "Order #1 is on its way with Royal Mail."))
print(send(None, "no channel"))
```

## When two implementations tie

An abstract base class such as `collections.abc.Sized` matches by
registration, not inheritance, so it has no position in a class's ancestry,
and two of them match a list equally well. Rather than pick one at random, the
call raises `AmbiguityError`, a `TypeError` from `purely.dispatch`. Register
an implementation for the concrete type to settle it.

```{python}
from collections.abc import Iterable, Sized
from purely import dispatcher
from purely.dispatch import AmbiguityError


@dispatcher
def describe(items):
    return "something"


@describe.dispatch
def _(items: Sized):
    return "has a size"


@describe.dispatch
def _(items: Iterable):
    return "can be iterated"


try:
    describe([1, 2])
except AmbiguityError as e:
    print(type(e).__name__)


@describe.dispatch
def _(items: list):
    return "a list"


print(describe([1, 2]))
```
