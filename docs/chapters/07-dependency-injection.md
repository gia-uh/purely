# Dependency injection

Functions that talk to a database or a clock are hard to test when they create
those services themselves. A `Registry` holds the services, and the functions
declare what they need with `depends`.

## Registering and resolving

`register(instance)` maps an object to its own class and to every base class
in its hierarchy, so code can ask for the interface rather than the concrete
class. A class that is already mapped keeps its first provider. `resolve`
returns the provider for a type, and raises `LookupError` when there is none.

```{python}
from purely import Registry


class Storage:
    def save(self, key, value): ...


class MemoryStorage(Storage):
    def __init__(self):
        self.data = {}

    def save(self, key, value):
        self.data[key] = value


registry = Registry()
registry.register(MemoryStorage())

print(type(registry.resolve(Storage)).__name__)
print(registry.resolve(Storage) is registry.resolve(MemoryStorage))

try:
    registry.resolve(int)
except LookupError as e:
    print(e)
```

To build a fresh object on every `resolve`, register a zero-argument factory
function together with the interface it provides:

```{python continue}
from itertools import count

ids = count(1)
registry.register(lambda: next(ids), int)
print(registry.resolve(int), registry.resolve(int))
```

In purely 1.2, pass an instance or a factory function, not a bare class:
`register(MemoryStorage)` maps the class object itself. A factory registered
without an interface is called once at registration to learn its type, and an
object that defines `__call__` is taken as a factory.

## Injecting

`depends(Interface)` marks a parameter's default. `registry.inject` wraps a
function so that each marked parameter not passed by the caller is resolved
from the registry when the function is called. A caller can still pass its own
value, which is how a test replaces a service. Async functions work the same
way.

```{python continue}
import asyncio
from purely import depends


@registry.inject
def remember(key, value, storage: Storage = depends(Storage)):
    storage.save(key, value)
    return storage


print(remember("lang", "python").data)

other = MemoryStorage()
print(remember("lang", "ocaml", storage=other).data)


@registry.inject
async def next_id(source: int = depends(int)):
    return source


print(asyncio.run(next_id()))
```

Each `Registry` is independent, so a test can build its own with fakes and
leave the application's alone.
