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
