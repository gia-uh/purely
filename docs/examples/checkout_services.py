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
