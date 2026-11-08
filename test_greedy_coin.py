"""Tests for the greedy change CLI and the pure logic in mylib.coin."""

import json

import pytest
from click.testing import CliRunner

from greedy_coin import main
from mylib.coin import greedy_coin

# --- pure logic ---------------------------------------------------------


def test_greedy_coin_one_fifty():
    assert greedy_coin(150) == {"quarter": 6, "dime": 0, "nickel": 0, "penny": 0}


def test_greedy_coin_thirty_cents_regression():
    # The original float implementation returned 29 cents here because
    # 0.30 - 0.25 == 0.04999999999999999 < 0.05, so the nickel was skipped.
    assert greedy_coin(30) == {"quarter": 1, "dime": 0, "nickel": 1, "penny": 0}


def test_greedy_coin_zero():
    assert greedy_coin(0) == {"quarter": 0, "dime": 0, "nickel": 0, "penny": 0}


def test_greedy_coin_ninety_nine():
    assert greedy_coin(99) == {"quarter": 3, "dime": 2, "nickel": 0, "penny": 4}


def test_greedy_coin_negative_raises():
    with pytest.raises(ValueError):
        greedy_coin(-1)


# --- CLI ----------------------------------------------------------------


def test_cli_dollars_and_cents():
    runner = CliRunner()
    result = runner.invoke(main, ["--dollars", "1", "--cents", "50"])
    assert result.exit_code == 0
    assert "Your change for $1.50:" in result.output
    assert "6 quarters" in result.output


def test_cli_only_cents():
    runner = CliRunner()
    result = runner.invoke(main, ["--cents", "41"])
    assert result.exit_code == 0
    assert "1 quarter" in result.output
    assert "1 dime" in result.output
    assert "1 nickel" in result.output
    assert "1 penny" in result.output


def test_cli_defaults_to_zero():
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "Your change for $0.00:" in result.output
    assert "quarter" not in result.output


def test_cli_singular_plural():
    runner = CliRunner()
    one = runner.invoke(main, ["--cents", "25"])
    two = runner.invoke(main, ["--cents", "50"])
    assert "1 quarter\n" in one.output
    assert "2 quarters\n" in two.output


def test_cli_rejects_cents_out_of_range():
    runner = CliRunner()
    result = runner.invoke(main, ["--cents", "100"])
    assert result.exit_code != 0


def test_cli_rejects_negative_dollars():
    runner = CliRunner()
    result = runner.invoke(main, ["--dollars", "-1"])
    assert result.exit_code != 0


def test_cli_json_output():
    runner = CliRunner()
    result = runner.invoke(main, ["--dollars", "1", "--cents", "50", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload == {
        "total_cents": 150,
        "coins": {"quarter": 6, "dime": 0, "nickel": 0, "penny": 0},
    }
