"""Import a partner's daily orders, all or nothing."""

from purely import Chain


def parse(line):
    isbn, quantity = line.split(",")
    if not quantity.isdigit():
        raise ValueError(f"cannot read {line!r}")
    return isbn, int(quantity)


def import_orders(text):
    return (
        Chain(text)
        .then(str.splitlines)
        .map(str.strip)
        .filter(lambda line: line and not line.startswith("#"))
        .map(parse)
    )


def report(text):
    batch = import_orders(text)
    if batch.is_ok:
        books = batch.then(lambda orders: sum(q for _, q in orders)).unwrap()
        return f"imported {len(batch.unwrap())} orders, {books} books"
    return f"imported nothing: {batch.error()}"


EXPORT = """
# orders for 2026-11-07
9780262046305,2
9780134685991,1

9781492056355,3
"""

BROKEN = EXPORT + "9780596007126,many\n"

if __name__ == "__main__":
    print(report(EXPORT))
    print(report(BROKEN))
