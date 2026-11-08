# Greedy Optimization Lab — Coursera MLOps C2

Solution to **Lab 4** of the Coursera MLOps course. This repository
contains two command-line tools and a small library:

- **`greedy_coin.py`** — computes the minimum number of US coins for a
  given amount of change (Part A of the lab).
- **`tsp.py`** — runs a randomized traveling-salesman simulation over
  20 US cities, using Nominatim for geocoding and `geopy` for
  distances (Part B of the lab).
- **`mylib/`** — pure-Python library modules used by both CLIs. No
  I/O, no `print`, no `click`. This is where the logic lives; the
  scripts at the repository root are thin wrappers.

The full analysis of what was changed and why is in
[`REFLECTION.md`](REFLECTION.md).

---

## Requirements

- Python **3.12** (the `requirements.txt` in this branch has been
  updated to versions with prebuilt wheels for CPython 3.12).
- See [`requirements.txt`](requirements.txt) for the exact versions.

## Setup

```bash
make install
```

or, without `make`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Project structure

```
.
├── greedy_coin.py            # CLI wrapper for mylib.coin
├── main.py                   # CLI wrapper for mylib.calculator
├── tsp.py                    # CLI wrapper for the TSP logic
├── mylib/
│   ├── __init__.py
│   ├── calculator.py         # add / subtract / multiply / divide
│   └── coin.py               # greedy_coin(change_cents) -> dict
├── test_main.py              # tests for mylib.calculator
├── test_greedy_coin.py       # tests for mylib.coin and greedy_coin CLI
├── REFLECTION.md             # answers to the four lab reflection questions
├── Makefile
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Part A — Greedy change CLI

### Usage

The original positional form (`python greedy_coin.py 1.50`) has been
**replaced** by two flags, as required by task A.2. The old form is
still available on the `main` branch for reference.

```bash
# 1 dollar 50 cents
python greedy_coin.py --dollars 1 --cents 50
# Your change for $1.50:
# 6 quarters

# 30 cents — demonstrates the float-drift bug fixed in this branch
python greedy_coin.py --cents 30
# Your change for $0.30:
# 1 quarter
# 1 nickel

# Same as the first example, but machine-readable
python greedy_coin.py --dollars 1 --cents 50 --json
# {"total_cents": 150, "coins": {"quarter": 6, "dime": 0, "nickel": 0, "penny": 0}}
```

### Flags

| Flag        | Type             | Default | Description                                    |
|-------------|------------------|---------|------------------------------------------------|
| `--dollars` | integer `>= 0`   | `0`     | Whole-dollar part of the amount.               |
| `--cents`   | integer `0..99`  | `0`     | Cents part of the amount.                      |
| `--json`    | flag             | off     | Emit JSON instead of the human-readable text.  |

Invalid values (`--cents 100`, `--dollars -1`) are rejected by Click
at parse time, before any computation runs.

### What changed vs. the original

1. **Input moved from a positional float to two `IntRange` flags.**
   The amount is unambiguous and validation is done by the CLI layer.
2. **The core logic was extracted into `mylib/coin.py`** and now
   operates on **integer cents** rather than floats. This removes a
   real bug: the original implementation returned 29 cents for
   `$0.30` because `0.30 - 0.25 == 0.04999999999999999` (strictly
   less than `0.05`), so the loop skipped the nickel.
3. **`--json` output was added** so the tool can be consumed by
   other scripts without screen-scraping the text output.
4. **A full test suite was added** (`test_greedy_coin.py`, 12 tests)
   covering the pure core, the CLI flags, range validation,
   singular/plural formatting, and a regression test for the `$0.30`
   bug.

Detailed reasoning in [`REFLECTION.md` § A](REFLECTION.md).

---

## Part B — Traveling salesman

### Usage

```bash
# Run the simulation with the default count (10)
python tsp.py simulate

# Run a specific number of simulations
python tsp.py simulate --count 1000

# Run against an explicit list of cities
python tsp.py cities "New York" "Boston" "Chicago" "Miami" --count 100
```

The command prints the best tour found across all runs and the
corresponding total distance (in miles).

### Geocoding cache

The 20 default city coordinates are cached in
`city_coords_cache.json` after the first run. This is required by
Nominatim's usage policy (cache results, ≤ 1 request/second) and
avoids rate limits during sweeps. The cache file is gitignored and
is regenerated automatically if missing.

### Optimal number of simulations

A sweep over `count = 10, 100, 1,000, 5,000` (with cache warm) is
documented in [`REFLECTION.md` § B](REFLECTION.md). Short version:
the knee of the curve is around **`count ≈ 1,000`**; beyond that the
best distance improves by ~10% per 5× more samples. Low counts are
dominated by the randomness of `random.shuffle`, which has no seed.

---

## Testing and quality

```bash
make test       # pytest + coverage
make lint       # pylint (root + mylib/)
make format     # black (root + mylib/)
```

Current status on this branch:

- **13 tests pass** (`test_main.py` + `test_greedy_coin.py`).
- `mylib/coin.py` coverage: **100%**.
- `pylint`: **10.00 / 10**.

> **Known pre-existing warning:** `make test` prints
> `Module main was never imported` because the Makefile uses
> `--cov=main --cov=mylib` but `test_main.py` imports
> `mylib.calculator`, not `main.py`. This is left unchanged here to
> keep the diff focused; it will be addressed in a follow-up refactor
> that reorganizes the project into a proper package layout.

## Docker

```bash
make container-lint
```

runs `hadolint` against the `Dockerfile`.

---

## Original lab tasks

Preserved here for reference (the commands below reflect the
*original* state of the repository at `main`, not the current
branch):

> **A. Run the greedy change command-line tool**
>
> 1. Run the greedy change command-line tool: `python greedy_coin.py 1.50`
> 2. Change the code to have a flag for dollars and flag for cents,
>    i.e., `--dollars` and `--cents`.
>
> **Reflection question:** Is this version of the command-line tool
> more robust against errors?
>
> **Reflection question:** What could you build to enhance this
> script? Do it and add it to your portfolio.
>
> **B. Run the traveling salesman algorithm**
>
> 1. Run the traveling salesman algorithm: `python tsp.py simulate`
> 2. What is the optimal number of simulations to run?

Both reflection questions and the TSP analysis are answered in
[`REFLECTION.md`](REFLECTION.md).