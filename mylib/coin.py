"""Greedy coin change logic (pure, no I/O)."""

COIN_VALUES = {"quarter": 25, "dime": 10, "nickel": 5, "penny": 1}


def greedy_coin(change_cents: int) -> dict:
    """Return a mapping of coin name -> count for ``change_cents``.

    Every denomination is present in the result, including zero counts,
    mirroring the original lab contract. Raises ``ValueError`` if
    ``change_cents`` is negative.
    """
    if change_cents < 0:
        raise ValueError("change_cents must be non-negative")
    result = {}
    remaining = change_cents
    for name, value in COIN_VALUES.items():
        result[name], remaining = divmod(remaining, value)
    return result
