"""Price a batch of order lines, keeping the rejected ones with their reason."""

from purely import Chain, Err, Ok, Registry, Result, curry, depends, dispatcher


class Catalog:
    def price(self, sku: str) -> float | None: ...


class MemoryCatalog(Catalog):
    def __init__(self, prices):
        self.prices = prices

    def price(self, sku):
        return self.prices.get(sku)


registry = Registry()
registry.register(MemoryCatalog({"tea": 4.5, "mug": 12.0, "spoon": 1.25}))


def parse(line: str) -> Result[tuple[str, int], str]:
    sku, _, quantity = line.partition(",")
    if not quantity.strip().isdigit():
        return Err(f"{line!r}: quantity is not a number")
    return Ok((sku.strip(), int(quantity)))


@curry
def price_with(
    catalog: Catalog, item: tuple[str, int]
) -> Result[tuple[str, int, float], str]:
    sku, quantity = item
    unit = catalog.price(sku)
    if unit is None:
        return Err(f"{sku!r}: unknown product")
    return Ok((sku, quantity, unit * quantity))


@registry.inject
def price_line(line: str, catalog: Catalog = depends(Catalog)) -> Result:
    priced = parse(line).then(price_with(catalog))
    # then() wraps the step's own Result in Ok; flatten one level.
    return priced.unwrap() if priced.is_ok() else priced


@dispatcher
def render(result):
    return f"?? {result!r}"


@render.dispatch
def _(result: Ok):
    sku, quantity, total = result.value
    return f"   {sku:<6} x{quantity:<3} {total:8.2f}"


@render.dispatch
def _(result: Err):
    return f"!! {result.error}"


def report(lines: list[str]) -> str:
    results = Chain(lines).map(price_line).unwrap()
    total = sum(r.value[2] for r in results if r.is_ok())
    body = Chain(results).map(render).then("\n".join).unwrap()
    return f"{body}\n   {'total':<11} {total:8.2f}"


ORDERS = ["tea, 3", "mug,1", "spoon,many", "kettle,1", "spoon,4"]

if __name__ == "__main__":
    print(report(ORDERS))
