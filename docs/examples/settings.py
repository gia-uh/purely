"""Read the shop's settings: required ones stop the start, optional ones default."""

from purely import ensure, safe

SETTINGS = {
    "payments": {"provider": "stripe", "key": "sk_test_123"},
    "shipping": {"free_over": 50},
    "newsletter": None,
}


def required(*path):
    node = safe(SETTINGS)
    for key in path:
        node = node.get(key)
    return ensure(node, f"{'.'.join(path)} is required")


def optional(*path, default):
    node = safe(SETTINGS)
    for key in path:
        node = node.get(key)
    return node.unwrap(default=default)


if __name__ == "__main__":
    print("payment key:", required("payments", "key"))
    print("free shipping over:", optional("shipping", "free_over", default=40))
    print(
        "newsletter sender:",
        optional("newsletter", "sender", default="books@example.com"),
    )
    try:
        required("payments", "webhook_secret")
    except ValueError as e:
        print("refusing to start:", e)
