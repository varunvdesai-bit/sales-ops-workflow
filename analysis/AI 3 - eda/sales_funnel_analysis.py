"""
Sales funnel & deal economics (simplified).

WHAT THIS FILE DOES, IN PLAIN ENGLISH:
Looks at the underlying business -- lead volume, average deal size, and
funnel conversion rates -- using ONLY actual results, no plan or target
involved at all. This is the companion to plan_attainment.py: that file
asks "did we hit our target," this file asks "what's actually happening
in the business," which matters because a target could be wrong (that's
its own separate question) while the underlying trend is still real.

THREE QUESTIONS THIS FILE ANSWERS:
1. Average deal size: is the average dollar value per sale going up or
   down, by channel, over time?
2. Lead volume: are we generating more or fewer leads than before?
3. Funnel conversion: IF lead volume changed, is it because fewer leads
   are coming in, or because we're converting them worse once they do?
   These need different fixes, so it's worth telling them apart.
"""

import os
import re
from pathlib import Path

import pandas as pd

# data/ now holds one dated subfolder per week (e.g. data/2026-07-18/) instead
# of the files sitting loose in data/ -- this picks the newest one automatically,
# same convention as data_validation.py and plan_attainment.py.
_DATA_ROOT = Path(os.environ.get("SALES_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
_week_dirs = sorted(p for p in _DATA_ROOT.iterdir() if p.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", p.name))
DATA_DIR = _week_dirs[-1] if _week_dirs else _DATA_ROOT


def load_data():
    wins = pd.read_excel(DATA_DIR / "wins_with_plays.xlsx", sheet_name="wins", usecols="A:L")
    funnel = pd.read_excel(DATA_DIR / "weekly_funnel.xlsx")
    return wins, funnel


# ---------------------------------------------------------------------------
# QUESTION 1: Average deal size, by channel, by quarter.
# Just total dollars sold divided by total units sold -- no plan involved.
# ---------------------------------------------------------------------------

def avg_deal_size(wins, channel):
    rows = wins[wins["channel"] == channel]
    results = []
    for q in sorted(rows["fiscal_quarter"].unique()):
        q_rows = rows[rows["fiscal_quarter"] == q]
        units = q_rows["units"].sum()
        arr = q_rows["arr_booked"].sum()
        results.append({
            "fiscal_quarter": q,
            "units": int(units),
            "arr": round(arr, 0),
            "avg_deal_size": round(arr / units, 0) if units else None,
        })
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# QUESTION 2: Lead volume, by channel, by quarter.
# FY26Q4 is still in progress (fewer weeks than a full quarter), so we also
# calculate what the lead count WOULD BE if it kept the same weekly pace for
# a full 13 weeks. This lets us fairly compare an in-progress quarter to a
# finished one. NOTE: this is a projection/estimate, not a measured fact --
# say so if you quote the prorated number.
# ---------------------------------------------------------------------------

def lead_volume(funnel, channel):
    rows = funnel[funnel["channel"] == channel]
    results = []
    for q in sorted(rows["fiscal_quarter"].unique()):
        q_rows = rows[rows["fiscal_quarter"] == q]
        weeks_in_data = q_rows["fiscal_week"].nunique()
        leads = q_rows["leads"].sum()
        # scale up to a 13-week equivalent, in case this quarter isn't done yet
        leads_full_quarter_pace = leads / weeks_in_data * 13
        results.append({
            "fiscal_quarter": q,
            "weeks_in_data": weeks_in_data,
            "actual_leads": int(leads),
            "leads_at_13wk_pace": round(leads_full_quarter_pace, 0),
        })
    return pd.DataFrame(results)


def lead_volume_pct_change(funnel, channel, from_quarter, to_quarter):
    """% change in lead volume between two quarters. Uses the 13-week-pace
    version of `to_quarter` so an in-progress quarter compares fairly
    against a completed `from_quarter`."""
    lv = lead_volume(funnel, channel)
    before = lv.loc[lv["fiscal_quarter"] == from_quarter, "actual_leads"].values[0]
    after = lv.loc[lv["fiscal_quarter"] == to_quarter, "leads_at_13wk_pace"].values[0]
    return round((after / before - 1) * 100, 1)


# ---------------------------------------------------------------------------
# QUESTION 3: Funnel conversion rates, by channel, by quarter.
# Each stage divided by the stage before it. If these rates hold steady but
# lead volume drops, the problem is top-of-funnel (marketing/lead gen), not
# execution (reps converting worse).
# ---------------------------------------------------------------------------

def funnel_conversion(funnel, channel):
    rows = funnel[funnel["channel"] == channel]
    results = []
    for q in sorted(rows["fiscal_quarter"].unique()):
        q_rows = rows[rows["fiscal_quarter"] == q]
        leads = q_rows["leads"].sum()
        mqls = q_rows["mqls"].sum()
        sqls = q_rows["sqls"].sum()
        opps = q_rows["opps_created"].sum()
        results.append({
            "fiscal_quarter": q,
            "lead_to_mql_pct": round(mqls / leads * 100, 1) if leads else None,
            "mql_to_sql_pct": round(sqls / mqls * 100, 1) if mqls else None,
            "sql_to_opp_pct": round(opps / sqls * 100, 1) if sqls else None,
        })
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Run this file directly to see a full sanity-check printout.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    wins, funnel = load_data()
    channels = sorted(wins["channel"].unique())

    print("=== Average deal size, by channel ===")
    for ch in channels:
        print(f"\n--- {ch} ---")
        print(avg_deal_size(wins, ch)[["fiscal_quarter", "avg_deal_size"]].to_string(index=False))

    print("\n\n=== Lead volume change, FY26Q3 -> FY26Q4, by channel ===")
    for ch in channels:
        pct = lead_volume_pct_change(funnel, ch, "FY26Q3", "FY26Q4")
        print(f"  {ch}: {pct:+.1f}%")

    print("\n\n=== Outbound funnel conversion, by quarter ===")
    print(funnel_conversion(funnel, "Outbound").to_string(index=False))
