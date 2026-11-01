"""Extension: Besley & Coate (2003) against Laffont & Tirole (1991) on 2024 electricity bills.

Besley and Coate argued that voters who elect their utility commissioners get more
pro-consumer regulation, which should show up as lower prices. A Stigler-style capture
story says the opposite. Laffont and Tirole say the institution responds to capture
risk by lowering the power of incentives, so prices track costs and the firm's rent is
squeezed rather than raised.

The test compares the residential price charged by investor-owned utilities, which state
commissions regulate, with the price charged by municipal and cooperative utilities in
the same state, which in most states they do not. State fixed effects absorb fuel costs,
weather and geography that both kinds of utility share:

    price_us = state effect + beta * IOU_u + delta * IOU_u x Elected_s + e

delta is the elected-commission effect on the investor-owned price, measured against
the public-power price next door.

Run from the repository root:
    python src/elected_prices.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "results"

# Voter-elected utility commissions in 2024 (see incentive_power.py for sources)
ELECTED = {"AL", "AZ", "GA", "LA", "MS", "MT", "NE", "ND", "OK", "SD"}
PUBLIC = {"Municipal", "Cooperative", "Political Subdivision", "State"}
MIN_MWH = 10_000           # drop tiny utility-state cells (about 900 homes' annual use)
PRICE_RANGE = (2.0, 100.0)  # cents per kWh; outside this is a reporting error
DROP_STATES = {"HI", "AK", "DC"}  # no or almost no public-power comparison in HI and DC; AK is isolated grids


def main():
    OUT.mkdir(exist_ok=True)
    x = pd.read_excel(RAW / "Sales_Ult_Cust_2024.xlsx", sheet_name="States", header=2, engine="openpyxl")
    x = x.rename(columns={"Utility Number": "uid", "Utility Name": "utility", "Thousand Dollars": "rev_k",
                          "Megawatthours": "mwh", "Count": "customers"})
    print(f"EIA-861 2024 sales rows: {len(x):,}")
    x = x[x["Service Type"] == "Bundled"]
    x = x[x.Ownership.isin(PUBLIC | {"Investor Owned"})].copy()
    for c in ["rev_k", "mwh", "customers"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    n0 = len(x)
    x = x[x.mwh >= MIN_MWH]
    x["price"] = 100 * x.rev_k / x.mwh          # thousand dollars per MWh -> cents per kWh
    x = x[x.price.between(*PRICE_RANGE) & ~x.State.isin(DROP_STATES)].copy()
    print(f"Bundled investor-owned and public-power residential cells: {n0:,}; kept {len(x):,} "
          f"(dropped those under {MIN_MWH:,} MWh, prices outside {PRICE_RANGE} cents, and HI, AK, DC)")
    x["iou"] = (x.Ownership == "Investor Owned").astype(int)
    x["elected"] = x.State.isin(ELECTED).astype(int)
    both = x.groupby("State").iou.agg(["min", "max"])
    keep = both[(both["min"] == 0) & (both["max"] == 1)].index
    x = x[x.State.isin(keep)]
    print(f"States with both kinds of utility: {len(keep)} ({x[x.elected == 1].State.nunique()} elected); "
          f"cells {len(x):,}, of which investor-owned {x.iou.sum()}")

    groups = pd.factorize(x.State)[0]
    rows = []
    specs = [("unweighted", None), ("weighted by residential MWh", "mwh")]
    for lab, w in specs:
        f = "price ~ iou + iou:elected + C(State)"
        if w is None:
            r = smf.ols(f, data=x).fit(cov_type="cluster", cov_kwds={"groups": groups})
        else:
            r = smf.wls(f, data=x, weights=x[w]).fit(cov_type="cluster", cov_kwds={"groups": groups})
        for t in ["iou", "iou:elected"]:
            b, se = r.params[t], r.bse[t]
            rows.append(dict(spec=lab, term=t, coef=b, se=se, ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se,
                             p=r.pvalues[t], n=int(r.nobs), states=len(keep)))
    # Besley-Coate's own comparison: IOU price level, elected vs appointed, no public-power benchmark
    iou = x[x.iou == 1]
    g2 = pd.factorize(iou.State)[0]
    r = smf.wls("price ~ elected", data=iou, weights=iou.mwh).fit(cov_type="cluster", cov_kwds={"groups": g2})
    rows.append(dict(spec="IOU price level only, weighted", term="elected", coef=r.params["elected"],
                     se=r.bse["elected"], ci_lo=r.params["elected"] - 1.96 * r.bse["elected"],
                     ci_hi=r.params["elected"] + 1.96 * r.bse["elected"], p=r.pvalues["elected"],
                     n=int(r.nobs), states=iou.State.nunique()))
    reg = pd.DataFrame(rows)
    reg.to_csv(OUT / "price_regressions.csv", index=False)
    print(reg.round(3).to_string())

    # State table: sales-weighted residential price by ownership
    def wavg(g):
        return 100 * g.rev_k.sum() / g.mwh.sum()
    st = x.groupby(["State", "iou"]).apply(wavg, include_groups=False).unstack()
    st.columns = ["public_price", "iou_price"]
    st["gap"] = st.iou_price - st.public_price
    st["elected"] = st.index.isin(ELECTED).astype(int)
    st["iou_mwh"] = x[x.iou == 1].groupby("State").mwh.sum()
    st = st.sort_values("gap")
    st.to_csv(OUT / "state_price_gaps.csv")
    summ = st.groupby("elected").agg(states=("gap", "size"), mean_gap=("gap", "mean"), median_gap=("gap", "median"),
                                     mean_iou_price=("iou_price", "mean"), mean_public_price=("public_price", "mean"))
    summ.to_csv(OUT / "price_gap_summary.csv")
    print(summ.round(2).to_string())

    # Largest investor-owned utilities in elected states, next to public power in the same state
    big = (x[(x.iou == 1) & (x.elected == 1)].sort_values("mwh", ascending=False)
           .head(12)[["utility", "State", "price", "mwh", "customers"]])
    big["public_price_same_state"] = big.State.map(st.public_price)
    big.to_csv(OUT / "elected_state_utilities.csv", index=False)
    print(big.round(2).to_string())

    fig, ax = plt.subplots(figsize=(7, 7.5))
    ys = np.arange(len(st))
    cols = np.where(st.elected == 1, "#b2182b", "#9e9e9e")
    ax.barh(ys, st.gap, color=cols)
    ax.set_yticks(ys)
    ax.set_yticklabels(st.index, fontsize=7)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("Investor-owned minus public-power residential price, cents per kWh (2024)")
    ax.set_title("Red: states whose voters elect the utility commission", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "price_gap_by_state.png", dpi=150)
    print("Wrote results/price_regressions.csv, state_price_gaps.csv, price_gap_summary.csv,"
          " elected_state_utilities.csv, price_gap_by_state.png")


if __name__ == "__main__":
    main()
