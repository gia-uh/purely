# Task: reading a nested configuration

A service reads its settings from a nested dictionary, as parsed from JSON or
YAML. Some settings are required, some have defaults, and some must be
numbers. This task uses `safe`, `Option` and `ensure` from the first two
chapters. The program is saved as `docs/examples/config_lookup.py`.

The settings arrive as plain dictionaries, and any section may be missing:

```{python export=examples/config_lookup.py}
"""Read required, optional and typed settings from a nested config."""

from purely import Option, ensure, safe

RAW = {
    "db": {"host": "db.internal", "port": "5432"},
    "cache": None,
}
```

A required setting ends in `ensure`, so its absence stops the program with a
message that names it. An optional one ends in `unwrap` with a default. A
setting that must be a number goes through `convert`, which runs only when the
value is there:

```{python continue export=examples/config_lookup.py}


def required(config, section, key):
    return ensure(safe(config).get(section).get(key), f"{section}.{key} is required")


def optional(config, section, key, default):
    return safe(config).get(section).get(key).unwrap(default=default)


def number(config, section, key, default):
    value: Option = safe(config).get(section).get(key)
    return value.convert(int).unwrap(default=default)
```

The `cache` section is `None`, so every lookup inside it falls back to its
default without a check:

```{python continue export=examples/config_lookup.py}


def main():
    host = required(RAW, "db", "host")
    port = number(RAW, "db", "port", 5432)
    ttl = number(RAW, "cache", "ttl", 300)
    backend = optional(RAW, "cache", "backend", "memory")
    print(f"db at {host}:{port}, cache {backend} with ttl {ttl}s")

    try:
        required(RAW, "db", "password")
    except ValueError as e:
        print("refused to start:", e)


if __name__ == "__main__":
    main()
```
