"""Laffont & Tirole (1991) on modern data: how high-powered is US utility regulation,
and is it lower-powered where the regulated firm has a cheap channel to its regulator?

In Laffont-Tirole's linear form, the regulated firm is paid t = a - b*C on top of its
cost C, so its revenue is R = a + (1 - b) C and b is the "power" of the scheme: the
share of each dollar of cost the firm's owners bear. b = 1 is a fixed price, b = 0 is
cost-plus. The paper's central result is that the threat of capture pushes b down.

This script builds a utility-year panel of investor-owned electric utilities from FERC
Form 1 (as cleaned by the Catalyst Cooperative's PUDL release), assigns each utility to
the states it serves from EIA Form 861 (2024), and estimates

    dR/R_{t-k} = year effects + g_F dF/R_{t-k} + g_N dN/R_{t-k} + g_K dK/R_{t-k} + e

where F is fuel and purchased power, N is every other operating cost except income
taxes, and K is net electric plant. b_F = 1 - g_F and b_N = 1 - g_N. It then lets the
pass-through differ for utilities whose customers sit in states that elect their
utility commissioners, and compares earned returns on plant across the two groups.

Run from the repository root:
    python src/incentive_power.py
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

# Ten states whose voters elect the utility commission (Ballotpedia and the Wikipedia
# "Public utilities commission" table, checked November 2026). New Mexico elected its
# commission until the end of 2022 and appoints it from 2023.
ELECTED = {"AL", "AZ", "GA", "LA", "MS", "MT", "NE", "ND", "OK", "SD"}
ELECTED_UNTIL_2022 = {"NM"}

FIRST_YEAR, LAST_YEAR = 2005, 2025   # FERC Form 1 years used (levels); changes start 2006
MIN_REVENUE = 50e6       # drop very small respondents, nominal dollars of electric revenue
MAX_REV_JUMP = 0.5       # drop utility-years whose revenue moves more than 50% (mergers, spin-offs)
TRIM = 0.01              # trim regressors at the 1st and 99th percentiles
VERT_INT_FUEL_SHARE = 0.05   # "owns generation": fuel burned in its own plants >= 5% of revenue
LONG_GAP = 3             # years for the long-difference version (one rate-case cycle)

FUEL_TYPES = ["fuel_steam_power_generation", "nuclear_fuel_expense", "fuel", "purchased_power"]


def load_ferc():
    inc = pd.read_parquet(RAW / "out_ferc1__yearly_income_statements_sched114.parquet")
    inc = inc[(inc.utility_type == "electric")]
    keep = ["operating_revenues", "operation_expense", "maintenance_expense", "depreciation_expense",
            "amortization_and_depletion_of_utility_plant", "taxes_other_than_income_taxes_utility_operating_income"]
    inc = inc[inc.income_type.isin(keep)]
    print(f"FERC income statement, electric rows kept: {len(inc):,}")
    wide = inc.pivot_table(index=["utility_id_ferc1", "report_year"], columns="income_type",
                           values="dollar_value", aggfunc="sum")
    opx = pd.read_parquet(RAW / "out_ferc1__yearly_operating_expenses_sched320.parquet")
    opx = opx[opx.expense_type.isin(FUEL_TYPES)]
    print(f"FERC operating expenses, fuel and purchased-power rows: {len(opx):,}")
    fuel = opx.groupby(["utility_id_ferc1", "report_year"]).dollar_value.sum().rename("fuel_pp")
    own = opx[opx.expense_type != "purchased_power"]
    own = own.groupby(["utility_id_ferc1", "report_year"]).dollar_value.sum().rename("fuel_own")
    plant = pd.read_parquet(RAW / "out_ferc1__yearly_utility_plant_summary_sched200.parquet")
    plant = plant[(plant.utility_type == "electric") & (plant.utility_plant_asset_type == "utility_plant_net")]
    plant = plant.groupby(["utility_id_ferc1", "report_year"]).ending_balance.sum().rename("net_plant")
    names = inc.groupby("utility_id_ferc1").agg(name=("utility_name_ferc1", "last"),
                                                 utility_id_pudl=("utility_id_pudl", "last"))
    df = wide.join(fuel).join(own).join(plant).reset_index()
    df = df.merge(names, left_on="utility_id_ferc1", right_index=True)
    df["report_year"] = df.report_year.astype(int)
    df["utility_id_ferc1"] = df.utility_id_ferc1.astype(int)
    df["utility_id_pudl"] = df.utility_id_pudl.astype(int)
    for c in df.columns.drop(["report_year", "utility_id_ferc1", "utility_id_pudl", "name"]):
        df[c] = df[c].astype(float)
    df = df[(df.report_year >= FIRST_YEAR) & (df.report_year <= LAST_YEAR)].copy()
    df["fuel_pp"] = df.fuel_pp.fillna(0.0)
    df["fuel_own"] = df.fuel_own.fillna(0.0)
    for c in keep[1:]:
        df[c] = df[c].fillna(0.0)
    df = df.rename(columns={"operating_revenues": "rev"})
    df["om"] = df.operation_expense + df.maintenance_expense
    df["nonfuel"] = (df.om - df.fuel_pp + df.depreciation_expense
                     + df.amortization_and_depletion_of_utility_plant
                     + df.taxes_other_than_income_taxes_utility_operating_income)
    # operating income before income taxes (the after-tax electric line is blank before 2021)
    df["op_income"] = df.rev - df.om - df.depreciation_expense - df.amortization_and_depletion_of_utility_plant \
        - df.taxes_other_than_income_taxes_utility_operating_income
    print(f"Utility-years {FIRST_YEAR}-{LAST_YEAR}: {len(df):,} from {df.utility_id_ferc1.nunique()} respondents")
    return df


def load_states():
    """Customer share of each investor-owned utility in each state, EIA-861 2024."""
    x = pd.read_excel(RAW / "Sales_Ult_Cust_2024.xlsx", sheet_name="States", header=2, engine="openpyxl")
    x = x.rename(columns={"Utility Number": "utility_id_eia", "Count.4": "customers",
                          "Thousand Dollars.4": "rev_k", "Megawatthours.4": "mwh"})
    print(f"EIA-861 2024 rows: {len(x):,}")
    x = x[(x.Ownership == "Investor Owned") & x["Service Type"].isin(["Bundled", "Delivery"])]
    x = x[pd.to_numeric(x.customers, errors="coerce") > 0].copy()
    x["customers"] = pd.to_numeric(x.customers)
    print(f"  investor-owned bundled or delivery rows with customers: {len(x):,}")
    eia = pd.read_parquet(RAW / "out_eia__yearly_utilities.parquet", columns=["utility_id_eia", "utility_id_pudl"])
    eia = eia.drop_duplicates("utility_id_eia")
    x = x.merge(eia, on="utility_id_eia", how="left")
    st = x.groupby(["utility_id_pudl", "State"]).customers.sum().reset_index()
    st["share"] = st.customers / st.groupby("utility_id_pudl").customers.transform("sum")
    return st


def elected_share(st, year):
    el = ELECTED | (ELECTED_UNTIL_2022 if year <= 2022 else set())
    s = st.assign(e=st.State.isin(el) * st.share)
    return s.groupby("utility_id_pudl").e.sum()


def build_panel(df, st):
    prim = st.sort_values("share").groupby("utility_id_pudl").tail(1).set_index("utility_id_pudl")
    df = df[df.utility_id_pudl.isin(prim.index)].copy()
    print(f"Matched to an EIA-861 2024 investor-owned retail utility: {df.utility_id_ferc1.nunique()} respondents,"
          f" {len(df):,} utility-years")
    df["state"] = df.utility_id_pudl.map(prim.State)
    df["primary_share"] = df.utility_id_pudl.map(prim.share)
    df["elected"] = np.nan
    for y in df.report_year.unique():
        m = df.report_year == y
        df.loc[m, "elected"] = df.loc[m, "utility_id_pudl"].map(elected_share(st, y)).values
    n0 = len(df)
    df = df[(df.rev >= MIN_REVENUE) & df.net_plant.gt(0)]
    print(f"Dropped {n0 - len(df)} utility-years with electric revenue under $50M or no net plant")
    df["vi"] = (df.fuel_own / df.rev >= VERT_INT_FUEL_SHARE).astype(int)
    return df.sort_values(["utility_id_ferc1", "report_year"])


def differences(df, k):
    g = df.groupby("utility_id_ferc1")
    lag = g[["rev", "fuel_pp", "nonfuel", "net_plant", "report_year"]].shift(k)
    d = df.copy()
    ok = (d.report_year - lag.report_year) == k
    base = lag.rev
    d["gR"] = (d.rev - lag.rev) / base
    d["gF"] = (d.fuel_pp - lag.fuel_pp) / base
    d["gN"] = (d.nonfuel - lag.nonfuel) / base
    d["gK"] = (d.net_plant - lag.net_plant) / base
    d = d[ok & base.gt(0)].dropna(subset=["gR", "gF", "gN", "gK", "elected"])
    n0 = len(d)
    d = d[d.gR.abs() <= MAX_REV_JUMP * (1 if k == 1 else 2)]
    n1 = len(d)
    for c in ["gF", "gN", "gK"]:
        lo, hi = d[c].quantile([TRIM, 1 - TRIM])
        d = d[d[c].between(lo, hi)]
    print(f"  {k}-year changes: {n0:,} available, {n0 - n1} dropped for revenue jumps, "
          f"{n1 - len(d)} trimmed, {len(d):,} kept ({d.utility_id_ferc1.nunique()} utilities, {d.state.nunique()} states)")
    return d


def fit(formula, d, cluster="state"):
    groups = pd.factorize(d[cluster])[0]
    return smf.ols(formula, data=d).fit(cov_type="cluster", cov_kwds={"groups": groups})


def row(label, res, term, d, sample):
    b, se = res.params[term], res.bse[term]
    return dict(spec=label, sample=sample, term=term, coef=b, se=se, ci_lo=b - 1.96 * se, ci_hi=b + 1.96 * se,
                p=res.pvalues[term], n=int(res.nobs), utilities=d.utility_id_ferc1.nunique(),
                clusters=d.state.nunique(), r2=res.rsquared)


def main():
    OUT.mkdir(exist_ok=True)
    df = load_ferc()
    st = load_states()
    df = build_panel(df, st)
    df.to_csv(OUT / "utility_panel.csv", index=False)

    # Worked example for the README: Georgia Power, 2021 to 2022, in billions of dollars
    ga = df[df.name.str.contains("Georgia Power") & df.report_year.isin([2021, 2022])].set_index("report_year")
    ex = pd.DataFrame({c: [ga.loc[2021, c] / 1e9, ga.loc[2022, c] / 1e9, (ga.loc[2022, c] - ga.loc[2021, c]) / 1e9]
                       for c in ["rev", "fuel_pp", "nonfuel", "net_plant"]}, index=["2021", "2022", "change"])
    ex.to_csv(OUT / "worked_example_georgia_power.csv")
    s24 = df[df.report_year == 2024].assign(group=lambda x: np.where(x.elected >= 0.5, "elected", "appointed"))
    s24.groupby("group").agg(utilities=("rev", "size"), revenue_bn=("rev", lambda v: v.sum() / 1e9),
                             owns_generation=("vi", "sum")).to_csv(OUT / "sample_2024.csv")

    print("Building changes:")
    d1 = differences(df, 1)
    d3 = differences(df, LONG_GAP)

    rows = []
    base = "gR ~ gF + gN + gK + C(report_year)"
    inter = "gR ~ gF + gN + gK + gF:elected + gN:elected + elected + C(report_year)"
    for d, lab in [(d1, "1-year"), (d3, f"{LONG_GAP}-year")]:
        for sample, dd in [("all", d), ("owns generation", d[d.vi == 1])]:
            r = fit(base, dd)
            for t in ["gF", "gN", "gK"]:
                rows.append(row(f"pooled, {lab}", r, t, dd, sample))
            r = fit(inter, dd)
            for t in ["gF", "gN", "gF:elected", "gN:elected", "elected"]:
                rows.append(row(f"elected interaction, {lab}", r, t, dd, sample))
        r = fit(inter, d, cluster="utility_id_ferc1")
        for t in ["gF:elected", "gN:elected"]:
            x = row(f"elected interaction, {lab}, clustered by utility", r, t, d, "all")
            x["clusters"] = d.utility_id_ferc1.nunique()
            rows.append(x)
    reg = pd.DataFrame(rows)
    reg["power_b"] = np.where(reg.term.isin(["gF", "gN"]), 1 - reg.coef, np.nan)
    reg.to_csv(OUT / "passthrough_regressions.csv", index=False)
    print(reg[["spec", "sample", "term", "coef", "se", "p", "n"]].round(3).to_string())

    # Power by group, estimated separately (easier to read than an interaction)
    grp = []
    for d, lab in [(d1, "1-year"), (d3, f"{LONG_GAP}-year")]:
        for name, dd in [("elected (share >= 0.5)", d[d.elected >= 0.5]), ("appointed (share < 0.5)", d[d.elected < 0.5])]:
            r = fit(base, dd)
            for t in ["gF", "gN"]:
                x = row(lab, r, t, dd, name)
                x["power_b"] = 1 - x["coef"]
                grp.append(x)
    grp = pd.DataFrame(grp)
    grp.to_csv(OUT / "power_by_commission.csv", index=False)
    print(grp[["spec", "sample", "term", "coef", "se", "power_b", "n", "utilities"]].round(3).to_string())

    # Rents: earned return on lagged net plant, 2015-2025
    lagged = df.groupby("utility_id_ferc1")[["net_plant", "report_year"]].shift(1)
    df["lag_plant"] = lagged.net_plant.where(df.report_year - lagged.report_year == 1)  # consecutive years only
    rr = df[(df.report_year >= 2015) & df.lag_plant.gt(0)].copy()
    rr["ret"] = 100 * rr.op_income / rr.lag_plant
    rr = rr[rr.ret.between(-10, 50)].dropna(subset=["elected"])
    rows = []
    for lab, f in [("no controls", "ret ~ elected + C(report_year)"),
                   ("owns-generation control", "ret ~ elected + vi + C(report_year)")]:
        r = fit(f, rr)
        rows.append(row(lab, r, "elected", rr, "2015-2025 utility-years"))
    ret = pd.DataFrame(rows)
    means = rr.assign(g=np.where(rr.elected >= 0.5, "elected", "appointed")).groupby("g").agg(
        mean_return=("ret", "mean"), utility_years=("ret", "size"), utilities=("utility_id_ferc1", "nunique"))
    ret.to_csv(OUT / "returns_by_commission.csv", index=False)
    means.to_csv(OUT / "returns_means.csv")
    print(ret[["spec", "coef", "se", "p", "n"]].round(3).to_string())
    print(means.round(2).to_string())

    # The names: largest utilities, own pass-through over 3-year changes and average return
    names = []
    big = df[df.report_year == 2024].nlargest(40, "rev")
    for uid in big.utility_id_ferc1:
        u = d3[d3.utility_id_ferc1 == uid]
        if len(u) < 8:
            continue
        r = smf.ols("gR ~ gF + gN + gK", data=u).fit()
        last = df[(df.utility_id_ferc1 == uid) & (df.report_year == 2024)].iloc[0]
        names.append(dict(utility=last["name"], state=last.state, elected_share=round(last.elected, 2),
                          revenue_2024_bn=last.rev / 1e9, fuel_share_2024=last.fuel_pp / last.rev,
                          nonfuel_passthrough=r.params["gN"], fuel_passthrough=r.params["gF"],
                          avg_return_on_plant=rr[rr.utility_id_ferc1 == uid].ret.mean(), changes=len(u)))
    names = pd.DataFrame(names).sort_values("revenue_2024_bn", ascending=False)
    names.to_csv(OUT / "utility_names.csv", index=False)
    print(names.round(2).to_string())

    # Figure: binned scatter of revenue change on non-fuel cost change, 1-year changes, with year
    # effects, fuel and plant growth partialled out (Frisch-Waugh), group means added back
    fig, ax = plt.subplots(figsize=(7, 4.6))
    for name, dd, col in [("Elected commissions", d1[d1.elected >= 0.5], "#b2182b"),
                          ("Appointed commissions", d1[d1.elected < 0.5], "#2166ac")]:
        ry = smf.ols("gR ~ gF + gK + C(report_year)", data=dd).fit().resid + dd.gR.mean()
        rx = smf.ols("gN ~ gF + gK + C(report_year)", data=dd).fit().resid + dd.gN.mean()
        bins = pd.qcut(rx, 12, duplicates="drop")
        m = pd.DataFrame({"x": rx, "y": ry}).groupby(bins, observed=True).mean()
        slope = np.polyfit(rx, ry, 1)
        ax.scatter(100 * m.x, 100 * m.y, color=col, s=28, label=f"{name} (slope {slope[0]:.2f})")
        xs = np.linspace(m.x.min(), m.x.max(), 10)
        ax.plot(100 * xs, 100 * np.polyval(slope, xs), color=col, lw=1)
    ax.axline((100 * d1.gN.mean(), 100 * d1.gR.mean()), slope=1, color="grey", ls="--", lw=0.8,
              label="Slope 1 (cost-plus, b = 0)")
    ax.set_xlabel("1-year change in non-fuel operating cost, % of last year's revenue")
    ax.set_ylabel("1-year change in revenue, %")
    ax.set_title("Utilities under elected commissions pass more of their non-fuel costs into revenue",
                 fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "passthrough_binned.png", dpi=150)
    print("Wrote results/passthrough_regressions.csv, power_by_commission.csv, returns_by_commission.csv,"
          " returns_means.csv, utility_names.csv, utility_panel.csv, passthrough_binned.png")


if __name__ == "__main__":
    main()
