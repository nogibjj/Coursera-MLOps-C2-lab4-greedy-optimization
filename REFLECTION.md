# Lab reflections — Greedy Optimization

## Part A — Greedy change CLI

### A.1 Is the `--dollars`/`--cents` version more robust against errors?

Yes, in three concrete ways, each backed by a change and a test in
this repository.

**1. Float drift is eliminated by design.** The original
implementation operated on Python floats:

    coins = [0.25, 0.10, 0.05, 0.01]
    while change >= coin:
        change -= coin

Because `0.30 - 0.25` evaluates to `0.04999999999999999` (strictly
less than `0.05`), the loop skips the nickel and `greedy_coin(0.30)`
returns 29 cents instead of 30. The new core in `mylib/coin.py` works
on integer cents (`divmod(remaining, 25)`), so there is no drift at
all. Regression test: `test_greedy_coin_thirty_cents_regression`.

**2. Validation happens before computation.** `click.IntRange(min=0)`
on `--dollars` and `click.IntRange(0, 99)` on `--cents` reject
invalid inputs at parse time. The original version accepted
`python greedy_coin.py -1`, `1e10`, `NaN`, and `1.005` without
complaint; now they fail with a clear error before any logic runs.
Tests: `test_cli_rejects_cents_out_of_range`,
`test_cli_rejects_negative_dollars`.

**3. The interface is unambiguous.** `1.50` could be read as
"one dollar fifty" or "one and fifty hundredths". `--dollars 1
--cents 50` cannot. This matters more in scripts than for a human
at a terminal.

**Trade-off:** the CLI is more verbose for one-off use cases. For a
single amount coming from another program, a positional `amount`
argument is more idiomatic. The lab explicitly asks for flags, and
I accept the verbosity in exchange for the three robustness gains
above.

### A.2 What could you build to enhance this script?

**Implemented in this repo:**

- **`--json` output.** Turns the CLI into something a downstream
  script can consume without screen-scraping the human-readable
  output. Test: `test_cli_json_output`.
- **A full test suite** (`test_greedy_coin.py`, 12 tests) covering
  the pure core, the CLI flags, range validation, singular/plural
  formatting, and the `$0.30` regression. Coverage of
  `mylib/coin.py`: 0% → 100%.

**Not implemented, noted for future work:**

- **FastAPI endpoint** wrapping `greedy_coin()` so a web client
  can POST a JSON payload and receive the coin breakdown. This is
  a natural next step given the course material.
- **Google Cloud Function** deployed with an HTTP trigger and the
  same payload format. The function body would be a two-line
  wrapper around `mylib.coin.greedy_coin`.
- **Signed/unsigned distinction** if the tool were ever adapted
  to currencies with negative adjustments (refunds, corrections).
  Out of scope for the lab.

## Part B — Traveling salesman

### B.1 What is the optimal number of simulations to run?

**Data.** Sweep with `python tsp.py simulate --count N`, Nominatim
cached after the first run:

| count  | best distance (mi) | wall time | notes                             |
|--------|--------------------|-----------|-----------------------------------|
| 10     | 22,012.25          | 27 s      | includes ~22 s geocode cache fill |
| 100    | 26,412.66          | 4 s       | pure simulation (cache warm)      |
| 1,000  | 22,810.77          | 34 s      | pure simulation                   |
| 5,000  | 20,355.48          | 189 s     | pure simulation                   |

**First observation — low counts are dominated by noise.** The
`count=100` run produced a *worse* result than `count=10`
(26,412 vs 22,012 miles). This is not a bug. The implementation
shuffles the city list with `random.shuffle` (no seed) and returns
the best of N random permutations. A single run of N=100 is one
sample of a highly variable quantity; it tells us nothing reliable
about the expected minimum. The trend only becomes visible above
N≈1,000.

**Second observation — the curve flattens around N≈1,000.**
From 1,000 to 5,000 simulations, the best distance improves by
~10.8% (22,811 → 20,355) at 5.5× the wall time (34 s → 189 s).
That is classic diminishing-returns behaviour: the expected minimum
of N samples from a light-tailed distribution decreases roughly as
1/√(log N), not linearly.

**Answer.** It depends on what "optimal" means:

- **Knee of the curve** (best marginal improvement per unit time):
  **count ≈ 1,000**. It costs ~34 s, gets within ~12% of the
  `count=5,000` result, and the next 5× more samples buys only
  another ~10%.
- **Best achievable result in a tolerable wall time:** count = 5,000
  (189 s) is a defensible upper bound for an interactive tool.

**Caveat 1 — single-run measurements are not proof.** To determine
the plateau rigorously I would need to run each count K times
(e.g. K=10) and look at the mean and standard deviation of the
minimum. The sweep above is a screening tool, not a statistical
proof. The non-monotonicity between `count=10` and `count=100`
is the clearest evidence of why this matters.

**Caveat 2 — this is not a TSP solver.** The current code samples
random permutations and returns the best one. A real solver
(Held-Karp for small N, or 2-opt / simulated annealing for larger
N) would find a much shorter tour with far fewer evaluations. The
"optimal number of simulations" for this implementation is bounded
by that algorithmic inefficiency, not by the problem itself.

**Caveat 3 — performance.** `tsp()` performs ~40 pandas DataFrame
filters per simulation (two lookups per city, O(n) each). The wall
time scales roughly linearly with `count` (34 s → 189 s for a 5×
increase, i.e. ~40 ms per simulation). Converting the DataFrame to
a precomputed `{city: (lat, lon)}` dict once and using O(1) lookups
would cut this by an order of magnitude. Noted as a known
limitation; not implemented because it is outside the scope of
this lab.