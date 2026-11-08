# Pricing rules

A cart's price goes through several rules: members get a discount, a coupon
takes a fixed amount off, tax is added, and the result is rounded to cents.
The rates are not constants. They come from the settings, and they differ by
country and by campaign.

```{python}
def price(subtotal, member_rate, coupon, tax_rate):
    return round(
        (subtotal * (1 - member_rate) - coupon) * (1 + tax_rate), 2
    )


print(price(80.0, 0.10, 5.0, 0.20))
```

One expression holds every rule, so no rule can be reused, tested or reordered
on its own. Splitting it into functions helps, but then the call reads inside
out:

```{python continue}
def member_discount(rate, amount):
    return amount * (1 - rate)


def coupon(off, amount):
    return amount - off


def add_tax(rate, amount):
    return amount * (1 + rate)


print(round(add_tax(0.20, coupon(5.0, member_discount(0.10, 80.0))), 2))
```

## Steps in reading order

`pipe(value, f, g, h)` computes `h(g(f(value)))`, but lists the steps in the
order they happen. The trouble is that each step must take exactly one
argument, the amount flowing through, and these rules take two.

`curry` fixes that. A curried function called with fewer arguments than it
needs returns a function waiting for the rest. `add_tax(0.20)` is then "add
20% tax", a one-argument step ready for `pipe`. Called with all its arguments
at once, it still works as before.

```{python export=examples/pricing.py}
"""Price a cart through configurable rules, in the order they apply."""

from purely import curry, pipe, tap


@curry
def member_discount(rate, amount):
    return amount * (1 - rate)


@curry
def coupon(off, amount):
    return max(amount - off, 0)


@curry
def add_tax(rate, amount):
    return amount * (1 + rate)


def to_cents(amount):
    return round(amount, 2)


def pricing(member_rate, coupon_off, tax_rate):
    """The rules for one shop and campaign, as a list of steps."""
    return [
        member_discount(member_rate),
        coupon(coupon_off),
        add_tax(tax_rate),
        to_cents,
    ]


if __name__ == "__main__":
    uk_member = pricing(0.10, 5.0, 0.20)
    print(pipe(80.0, *uk_member))
    print(pipe(80.0, *pricing(0.0, 0.0, 0.07)))
    print(add_tax(0.20, 10.0), add_tax(0.20)(10.0))
```

The rules are now values: a list built from the settings, which a test can
build with other rates. To see the amount between two steps, put `tap` in the
list. `tap(value, func)` calls `func` for its side effect and returns `value`
unchanged, so the pipeline goes on as if it were not there. Curried,
`tap` needs the function first, so wrap it once:

```{python continue}
show = curry(lambda label, amount: tap(amount, lambda a: print(f"  {label}: {a:.2f}")))

total = pipe(80.0, member_discount(0.10), show("after discount"), coupon(5.0), add_tax(0.20), to_cents)
print(total)
```

## How many arguments curry waits for

`curry` counts the parameters that have no default. Parameters with a default,
`*args` and `**kwargs` are never waited for, and keyword arguments count like
positional ones:

```{python}
from purely import curry


@curry
def label(currency, amount, symbol="£"):
    return f"{symbol}{amount:.2f} {currency}"


gbp = label("GBP")
print(gbp(12.5), gbp(amount=3), gbp(3, symbol="GBP "))
```

For a type checker, `curry` on a function of two to five parameters returns a
`Curried2`, `Curried3`, `Curried4` or `Curried5` from `purely.curry`. These
protocols describe every way to split the arguments, so `add_tax(0.20)` is
typed as a function from an amount to an amount. They exist only for
annotations.

```{python}
from purely.curry import Curried2, curry


@curry
def add_tax(rate: float, amount: float) -> float:
    return amount * (1 + rate)


rule: Curried2[float, float, float] = add_tax
print(rule(0.2)(10.0))
```
