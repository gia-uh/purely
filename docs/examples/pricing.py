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
