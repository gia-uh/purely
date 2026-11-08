# Importing a batch of orders

A partner bookshop sends its orders once a day as lines of text,
`isbn,quantity`. The file also has blank lines and comments. The import is all
or nothing: if one line is broken, the shop imports none of them and tells the
partner which line to fix, because half an import is harder to repair than
none.

```{python}
EXPORT = """
# orders for 2026-11-07
9780262046305,2
9780134685991,1

9781492056355,3
"""

BROKEN = EXPORT + "9780596007126,many\n"
```

The plain version is a loop with an accumulator, a `try` around the parsing,
and a flag:

```{python continue}
def import_orders(text):
    orders = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            isbn, quantity = line.split(",")
            orders.append((isbn, int(quantity)))
        except ValueError:
            return None, f"cannot read {line!r}"
    return orders, None


print(import_orders(EXPORT))
print(import_orders(BROKEN))
```

The steps are all there: split, strip, skip, parse, collect. They are
interleaved, though, and the error travels back as the second half of a tuple.
Every caller has to unpack the tuple and check it.

## One chain for the whole batch

`Chain(value)` is a pipeline you can read from top to bottom. `then` passes the
whole value to a function, `filter` keeps the items of a list that pass a
test, and `map` applies a function to each item. `|` is a shorter way to write
`then`. Like `then` on an `Ok`, a `Chain` catches an exception raised by any
step, remembers it, and skips every later step. The all-or-nothing rule needs
no code of its own.

```{python continue export=examples/import_orders.py}
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
```

At the end of the chain you decide what a failure means. `is_ok` says whether
every step succeeded, `unwrap` returns the value (or raises the remembered
exception), and `error()` returns that exception without raising it. `catch`
recovers, by running a function on the error and continuing with its result.

```{python continue export=examples/import_orders.py}


def report(text):
    batch = import_orders(text)
    if batch.is_ok:
        books = batch.then(lambda orders: sum(q for _, q in orders)).unwrap()
        return f"imported {len(batch.unwrap())} orders, {books} books"
    return f"imported nothing: {batch.error()}"
```

The saved example carries its own copy of the sample export, a good one and
one with a broken last line:

```{python continue export=examples/import_orders.py}


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
```

## Inspecting and failing on purpose

Three more methods come up when chains get longer. `tap` runs a function for
its side effect, such as logging, and passes the value on unchanged.
`Chain.fail(error)` starts a chain that has already failed, for when the input
is wrong before any step runs. `test()` raises the remembered error and
returns nothing, for a chain run only for what it does.

```{python continue}
seen = []
count = import_orders(EXPORT).tap(seen.append) | len
print(count.unwrap(), "orders,", len(seen[0]), "seen by tap")

empty = Chain.fail(ValueError("the partner sent an empty file"))
print(empty.unwrap(default=[]))

try:
    import_orders(BROKEN).test()
except ValueError as e:
    print("test raised:", e)
```

`map` and `filter` need a list, a tuple or another iterable that is not a
string: mapping over a string's letters is almost always a mistake, so the
chain fails instead. A `Chain` compares equal to the value it holds, which
keeps tests short, and comparing a failed chain raises its error.

```{python continue}
print(Chain("9780262046305").map(int).error())
print(Chain([1, 2]).map(lambda n: n * 10) == [10, 20])
```
