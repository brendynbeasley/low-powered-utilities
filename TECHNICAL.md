# Technical notes

This is the technical companion to the [README](README.md). It covers the data, the method, the full set of test
statistics and how to reproduce everything. Every table is in [results/FINDINGS.md](results/FINDINGS.md), and a
methods review of the original paper is in [METHODS_REVIEW.md](METHODS_REVIEW.md).

## The original study

Jean-Jacques Laffont and Jean Tirole, "The Politics of Government Decision-Making: A Theory of Regulatory Capture,"
*Quarterly Journal of Economics* 106(4), 1991, pp. 1089–1127 (working-paper version: MIT Department of Economics
Working Paper No. 506, October 1988). The paper models a three-tier hierarchy of Congress, a regulatory agency and a
regulated firm with private cost information. The agency can hide what it learns in exchange for side transfers
that cost the firm $`1+\lambda_f`$ per dollar. The paper is theoretical and reports no data. Its headline results,
from the published abstract, are that the organizational response to capture is to reduce interest groups' stakes,
and that "the threat of producer protection leads to low-powered incentive schemes" (Proposition 1 in the working
paper). Proposition 1 also states that the efficient firm's rent is lower under the threat of collusion and that
the inefficient type's effort rises with $`\lambda_f`$.

## Headline results

| Test | Estimate | SE | 95% CI | p | N |
|---|---|---|---|---|---|
| Non-fuel pass-through $`\gamma_N`$, 1-year, pooled | 0.765 | 0.036 | [0.694, 0.836] | < 0.001 | 1,998 |
| Fuel pass-through $`\gamma_F`$, 1-year, pooled | 0.916 | 0.029 | [0.859, 0.974] | < 0.001 | 1,998 |
| Non-fuel pass-through $`\gamma_N`$, 3-year, pooled | 0.818 | 0.040 | [0.740, 0.895] | < 0.001 | 1,782 |
| Elected × non-fuel $`\delta_N`$, 1-year | 0.166 | 0.078 | [0.013, 0.318] | 0.033 | 1,998 |
| Elected × non-fuel $`\delta_N`$, 3-year | 0.126 | 0.086 | [−0.044, 0.295] | 0.146 | 1,782 |
| Elected, pre-tax return on plant (points) | −0.320 | 0.405 | [−1.113, 0.474] | 0.430 | 1,170 |
| IOU × elected, residential price (¢/kWh), unweighted | −2.035 | 0.817 | [−3.636, −0.435] | 0.013 | 1,204 |
| IOU × elected, residential price, sales-weighted | −0.466 | 1.142 | [−2.704, 1.772] | 0.683 | 1,204 |

Standard errors are clustered by state. The implied power of regulation for non-fuel costs is
$`\hat b_N = 0.235`$ (1-year) and $`0.182`$ (3-year), and for fuel $`0.084`$ and $`0.025`$.

## Data

- **FERC Form 1** via the Catalyst Cooperative's PUDL release v2026.10.0, committed in `data/raw/`:
  `out_ferc1__yearly_income_statements_sched114.parquet` (revenue, operation and maintenance expense, depreciation,
  amortization, taxes other than income taxes; electric column),
  `out_ferc1__yearly_operating_expenses_sched320.parquet` (accounts 501 steam fuel, 518 nuclear fuel, 547 other
  generation fuel, 555 purchased power), `out_ferc1__yearly_utility_plant_summary_sched200.parquet` (net electric
  plant), and `out_eia__yearly_utilities.parquet` (the PUDL crosswalk from EIA utility IDs to PUDL IDs).
- **EIA-861, 2024**: `Sales_Ult_Cust_2024.xlsx` from `f8612024.zip` on eia.gov, sheet "States", giving residential
  revenue, sales and customers, and total customers, by utility, state and service type.
- **Commission selection**: ten voter-elected commissions (AL, AZ, GA, LA, MS, MT, NE, ND, OK, SD) and New Mexico
  through 2022, from Ballotpedia and the Wikipedia table of US public utilities commissions, coded in the scripts.

## Method

Rules fixed before looking at the results:

- **Panel.** FERC respondents 2005–2025, electric column only. $`F`$ = accounts 501 + 518 + 547 + 555. $`N`$ =
  operation expense + maintenance expense − $`F`$ + depreciation + amortization + taxes other than income taxes.
  $`K`$ = net electric utility plant, including construction work in progress. Income taxes are left out because
  their timing is set by tax rules rather than by the commission.
- **Matching.** A respondent is kept if its PUDL ID matches an investor-owned bundled or delivery utility in EIA-861
  2024. $`E_{it}`$ is the share of its 2024 retail customers in elected-commission states in year $`t`$. The main
  state is the state with most customers.
- **Exclusions.** Electric revenue under $50 million or no net plant; one-year revenue changes beyond ±50%
  (±100% for three-year changes); regressors trimmed at the 1st and 99th percentiles.
- **Estimating equation.** For $`k \in \{1, 3\}`$,

```math
\begin{aligned}
g^R_{it} = \mu_t &+ \gamma_F g^F_{it} + \gamma_N g^N_{it} + \gamma_K g^K_{it} \\
&+ \delta_F E_{it} g^F_{it} + \delta_N E_{it} g^N_{it} + \theta E_{it} + \varepsilon_{it}
\end{aligned}
```

  with $`\mu_t`$ year effects, $`g^X_{it} = \Delta_k X_{it} / R_{i,t-k}`$, and power $`b_X = 1 - \gamma_X`$. $`H_0: \delta_N = 0`$; the
  capture-channel reading of Laffont and Tirole predicts $`\delta_N > 0`$ under elected commissions. Standard errors
  are clustered by main state, with utility clustering as a check.
- **Rents.** Pre-tax operating income (revenue − O&M − depreciation − amortization − other taxes) divided by the
  previous year's net plant (consecutive years only), 2015–2025, values outside −10% to 50% dropped, regressed on $`E_{it}`$ with year effects.
- **Prices (extension).** EIA-861 2024 bundled residential sellers, investor-owned, municipal, cooperative,
  political subdivision and state, with at least 10,000 MWh; prices outside 2–100 ¢/kWh dropped; Hawaii, Alaska and
  DC dropped; only states with both investor-owned and public sellers kept (46 states, 9 elected; Nebraska has no
  investor-owned utility).

```math
p_{us} = \alpha_s + \beta\,\text{IOU}_u + \delta\,(\text{IOU}_u \times E_s) + \varepsilon_{us}
```

## Full test statistics

Group-specific estimates (each group estimated separately, year effects, clustered by state):

| Group | Horizon | $`\hat\gamma_F`$ | $`\hat\gamma_N`$ | $`\hat b_N`$ | N | Utilities |
|---|---|---|---|---|---|---|
| Elected | 1-year | 0.955 (0.085) | 0.921 (0.074) | 0.079 | 313 | 19 |
| Appointed | 1-year | 0.902 (0.029) | 0.742 (0.037) | 0.258 | 1,685 | 97 |
| Elected | 3-year | 0.928 (0.017) | 1.019 (0.065) | −0.019 | 284 | 19 |
| Appointed | 3-year | 0.981 (0.026) | 0.801 (0.043) | 0.199 | 1,498 | 94 |

Robustness of $`\hat\delta_N`$: utility-clustered, 1-year 0.166 (0.083), p = 0.047; 3-year 0.126 (0.085),
p = 0.139. Restricted to the utilities whose own-plant fuel is at least 5% of revenue: 1-year 0.120 (0.083),
p = 0.145, N = 1,246; 3-year 0.150 (0.098), p = 0.125, N = 1,124. The fuel interaction $`\hat\delta_F`$ is 0.065
(0.057) at one year and −0.028 (0.031) at three. The pooled capital coefficient $`\hat\gamma_K`$ is 0.046 (0.008) at
one year. Mean pre-tax return on lagged net plant: 7.08% elected (183 utility-years, 17 utilities), 7.32% appointed
(987, 94); with an own-generation control the difference is −0.200 (0.398). The investor-owned price level alone,
sales-weighted, is 2.888 ¢ lower in elected states (1.430), p = 0.043, a comparison that does not net out regional
costs.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/incentive_power.py
python src/elected_prices.py
```

Both scripts read only `data/raw/` and write CSVs and PNGs to `results/`. They run offline in under a minute.

## Repository layout

| Path | What it is |
|---|---|
| [src/incentive_power.py](src/incentive_power.py) | Panel construction, pass-through regressions, rents, names table, figure 1 |
| [src/elected_prices.py](src/elected_prices.py) | Besley–Coate extension on 2024 residential prices, figure 2 |
| [results/FINDINGS.md](results/FINDINGS.md) | Plain-English summary and every table |
| `results/*.csv`, `results/*.png` | All outputs |
| `data/raw/` | PUDL extracts of FERC Form 1 and EIA-861 2024 |

## References

- Besley, T. & Coate, S. (2003). Elected versus appointed regulators: theory and evidence. *Journal of the European
  Economic Association* 1(5), 1176–1206.
- Laffont, J.-J. & Tirole, J. (1986). Using cost observation to regulate firms. *Journal of Political Economy* 94(3).
- Laffont, J.-J. & Tirole, J. (1991). The politics of government decision-making: a theory of regulatory capture.
  *Quarterly Journal of Economics* 106(4), 1089–1127.
- Laffont, J.-J. & Tirole, J. (1993). *A Theory of Incentives in Procurement and Regulation*. MIT Press.
- Stigler, G. J. (1971). The theory of economic regulation. *Bell Journal of Economics and Management Science* 2(1).
- Catalyst Cooperative. PUDL data release v2026.10.0. US Energy Information Administration, Form EIA-861 (2024).
