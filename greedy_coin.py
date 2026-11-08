#!/usr/bin/env python
"""Greedy Coin Change Algorithm.

Compute the minimum number of US coins for a given amount of change
using a greedy strategy (largest denomination first). The strategy is
optimal for the US coin system because every denomination is a multiple
of the next smaller one.

All internal arithmetic is done in integer cents so the result is
exact: the original float-based implementation under-counted amounts
such as $0.30 because 0.30 - 0.25 evaluates to 0.04999999999999999,
which is less than 0.05 and therefore skips the nickel.

The CLI exposes ``--dollars`` and ``--cents`` flags so the amount is
unambiguous and validated before any computation happens.
"""

import json
import click

from mylib.coin import greedy_coin


def _format_change(change_cents: int, counts: dict) -> str:
    """Render a human-readable summary of the change."""
    lines = [f"Your change for ${change_cents / 100:.2f}:"]
    for name, count in counts.items():
        if count:
            plural = "" if count == 1 else "s"
            lines.append(f"{count} {name}{plural}")
    return "\n".join(lines)


@click.command()
@click.option(
    "--dollars",
    type=click.IntRange(min=0),
    default=0,
    show_default=True,
    help="Whole-dollar part of the amount.",
)
@click.option(
    "--cents",
    type=click.IntRange(0, 99),
    default=0,
    show_default=True,
    help="Cents part of the amount (0-99).",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit the result as JSON instead of human-readable text.",
)
def main(dollars: int, cents: int, as_json: bool) -> None:
    """Return the minimum number of coins for a given change.

    Example: ./greedy_coin.py --dollars 1 --cents 50
    """
    total_cents = dollars * 100 + cents
    counts = greedy_coin(total_cents)

    if as_json:
        click.echo(json.dumps({"total_cents": total_cents, "coins": counts}))
    else:
        click.echo(_format_change(total_cents, counts))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
