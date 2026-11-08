"""Read required, optional and typed settings from a nested config."""

from purely import Option, ensure, safe

RAW = {
    "db": {"host": "db.internal", "port": "5432"},
    "cache": None,
}


def required(config, section, key):
    return ensure(safe(config).get(section).get(key), f"{section}.{key} is required")


def optional(config, section, key, default):
    return safe(config).get(section).get(key).unwrap(default=default)


def number(config, section, key, default):
    value: Option = safe(config).get(section).get(key)
    return value.convert(int).unwrap(default=default)


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
