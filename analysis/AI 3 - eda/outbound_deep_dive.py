"""
Outbound deep dive: rep concentration, account mix, true YoY timing.

WHAT THIS FILE DOES, IN PLAIN ENGLISH:
Finding 12a (assumptions_and_findings.md) established that Outbound's core
(non-play) business is down ~62% QoQ. This file independently tests three of
the five candidate drivers raised for that decline:

  2. Rep-level variance -- is the ~62% BAU decline spread across the whole
     team, or is it a few reps dragging the average down (a coaching/
     management problem)?
  3. Account/industry mix -- is the decline concentrated in a specific
     industry, revenue band, or region, or is it broad-based?
  4. Timing/seasonality -- is FY26Q4 just a structurally weaker quarter
     (e.g. a summer slowdown), using a TRUE year-over-year comparison
     (FY26Q4 vs FY25Q4, same weeks 1-10 window on both sides) rather than
     the quarter-over-quarter comparisons used elsewhere in this analysis.

Two other candidate drivers from the original question are NOT analyzable here and
are not attempted:
  1. Lead source mix (paid ads vs. cold calling vs. purchased lists) --
     weekly_funnel.csv has no lead-source field, so this can't be split.
  5. Broader market / competitive pressure -- no external market data exists
     in this dataset.

All three checks here use BAU (non-play) wins only, i.e. wins with no
play_id -- consistent with Finding 12a's methodology, so this deep dive is
isolating the same "organic Outbound" signal Finding 12a already sized,
not a different metric.

Run directly for a full printout:
    python3 analysis/outbound_deep_dive.py
"""

import os
import re
from pathlib import Path

import pandas as pd

_DATA_ROOT = Path(os.environ.get("SALES_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
_week_dirs = sorted(p for p in _DATA_ROOT.iterdir() if p.is_dir() and re.match(r"^\d{4}-\d{2}-\d{2}$", p.name))
DATA_DIR = _week_dirs[-1] if _week_dirs else _DATA_ROOT
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"

THROUGH_WEEK = 10  # FY26Q4 only has actuals through week 10; every comparison here uses the same window on both sides


def load_data():
    # usecols A:L = the raw CRM columns only. The workbook also carries helper columns added for the
    # Excel workings (industry, region, is_BAU, ...); reading them would collide with the accounts merge below.
    wins = pd.read_excel(DATA_DIR / "wins_with_plays.xlsx", sheet_name="wins", usecols="A:L")
    attrib = pd.read_excel(DATA_DIR / "wins_with_plays.xlsx", sheet_name="play_attribution")
    roster = pd.read_excel(DATA_DIR / "seller_roster.xlsx")
    accounts = pd.read_excel(DATA_DIR / "accounts.xlsx")
    return wins, attrib, roster, accounts


def _window(df, quarter, through_week=THROUGH_WEEK):
    return df[(df["fiscal_quarter"] == quarter) & (df["fiscal_week"] <= through_week)]


def outbound_bau(wins, attrib):
    """Outbound wins with no play attribution -- the 'organic' book of business."""
    play_ids = set(attrib["win_id"])
    ob = wins[wins["channel"] == "Outbound"]
    return ob[~ob["win_id"].isin(play_ids)]


# ---------------------------------------------------------------------------
# DRIVER #2: Rep-level variance
# ---------------------------------------------------------------------------

def rep_level_variance(wins, attrib, roster, from_quarter="FY26Q3", to_quarter="FY26Q4"):
    """
    Per-rep BAU units, from_quarter vs to_quarter (same week-1-through-THROUGH_WEEK
    window both sides). Flags reps who are new (started after the from_quarter's
    comparison window closed -- they have no from_quarter baseline to compare
    against) so they don't get miscounted as "declining."
    """
    ob_bau = outbound_bau(wins, attrib)
    from_window = _window(ob_bau, from_quarter)
    to_window = _window(ob_bau, to_quarter)
    from_cutoff = _window(wins, from_quarter)["week_ending"].max()

    from_by_rep = from_window.groupby("seller_id")["units"].sum().rename("units_from")
    to_by_rep = to_window.groupby("seller_id")["units"].sum().rename("units_to")
    rep = pd.concat([from_by_rep, to_by_rep], axis=1).fillna(0)
    rep = rep.merge(roster[["seller_id", "seller_name", "start_date"]], left_index=True, right_on="seller_id")
    rep["units_change"] = rep["units_to"] - rep["units_from"]
    rep["is_new_hire"] = rep["start_date"] > from_cutoff
    return rep.sort_values("units_change")


# ---------------------------------------------------------------------------
# DRIVER #3: Account / industry / revenue-band / region mix
# ---------------------------------------------------------------------------

def account_mix_shift(wins, attrib, accounts, dimension, from_quarter="FY26Q3", to_quarter="FY26Q4"):
    """Unit share of `dimension` (industry / annual_revenue_band / region), from_quarter
    vs to_quarter -- a stable share across quarters means the decline is broad-based,
    not concentrated in that dimension."""
    ob_bau = outbound_bau(wins, attrib).merge(accounts, on="account_id", how="left")
    from_units = _window(ob_bau, from_quarter).groupby(dimension)["units"].sum()
    to_units = _window(ob_bau, to_quarter).groupby(dimension)["units"].sum()
    tbl = pd.DataFrame({f"{from_quarter}_units": from_units, f"{to_quarter}_units": to_units}).fillna(0)
    tbl[f"{from_quarter}_share_%"] = (tbl[f"{from_quarter}_units"] / tbl[f"{from_quarter}_units"].sum() * 100).round(1)
    tbl[f"{to_quarter}_share_%"] = (tbl[f"{to_quarter}_units"] / tbl[f"{to_quarter}_units"].sum() * 100).round(1)
    tbl["units_change_%"] = ((tbl[f"{to_quarter}_units"] / tbl[f"{from_quarter}_units"] - 1) * 100).round(1)
    return tbl.sort_values(f"{from_quarter}_units", ascending=False)


# ---------------------------------------------------------------------------
# DRIVER #4: True year-over-year timing check (not QoQ)
# ---------------------------------------------------------------------------

def yoy_by_channel(wins, current_quarter="FY26Q4", prior_year_quarter="FY25Q4"):
    """Same weeks-1-through-THROUGH_WEEK window, one year apart, every channel --
    the control group that answers 'is this a seasonal Q4 effect hitting
    everyone, or specific to Outbound.' Uses TOTAL actuals (including plays,
    where they exist) since the question here is about the whole business's
    seasonal pattern, not the organic/BAU split."""
    results = []
    for channel in sorted(wins["channel"].unique()):
        ch = wins[wins["channel"] == channel]
        prior = _window(ch, prior_year_quarter)
        current = _window(ch, current_quarter)
        results.append({
            "channel": channel,
            f"{prior_year_quarter}_units": int(prior["units"].sum()),
            f"{current_quarter}_units": int(current["units"].sum()),
            "yoy_units_%": round((current["units"].sum() / prior["units"].sum() - 1) * 100, 1),
            f"{prior_year_quarter}_arr": round(prior["arr_booked"].sum(), 0),
            f"{current_quarter}_arr": round(current["arr_booked"].sum(), 0),
            "yoy_arr_%": round((current["arr_booked"].sum() / prior["arr_booked"].sum() - 1) * 100, 1),
        })
    return pd.DataFrame(results)


def outbound_bau_yoy(wins, attrib, current_quarter="FY26Q4", prior_year_quarter="FY25Q4"):
    """Same YoY check as yoy_by_channel, but Outbound-only and BAU-only (ex-play) --
    isolates the organic YoY trend from this year's play-driven volume, which
    didn't exist a year ago."""
    ob_bau = outbound_bau(wins, attrib)
    prior = _window(ob_bau, prior_year_quarter)
    current = _window(ob_bau, current_quarter)
    return {
        "prior_units": int(prior["units"].sum()),
        "current_units": int(current["units"].sum()),
        "yoy_units_%": round((current["units"].sum() / prior["units"].sum() - 1) * 100, 1),
        "prior_arr": round(prior["arr_booked"].sum(), 0),
        "current_arr": round(current["arr_booked"].sum(), 0),
        "yoy_arr_%": round((current["arr_booked"].sum() / prior["arr_booked"].sum() - 1) * 100, 1),
    }


# ---------------------------------------------------------------------------
# Sanity check: reproduce Finding 12a's headline BAU QoQ number on today's
# data before trusting anything else in this file -- if this doesn't match
# the findings log, something upstream (e.g. the FY26Q3 duplicate-wins
# correction) has drifted and needs investigating before proceeding.
# ---------------------------------------------------------------------------

def sanity_check_finding_12a(wins, attrib):
    ob_bau = outbound_bau(wins, attrib)
    q3 = _window(ob_bau, "FY26Q3")
    q4 = _window(ob_bau, "FY26Q4")
    units_pct = round((q4["units"].sum() / q3["units"].sum() - 1) * 100, 1)
    arr_pct = round((q4["arr_booked"].sum() / q3["arr_booked"].sum() - 1) * 100, 1)
    return {
        "q3_units": int(q3["units"].sum()), "q4_units": int(q4["units"].sum()), "units_change_%": units_pct,
        "q3_arr": round(q3["arr_booked"].sum(), 0), "q4_arr": round(q4["arr_booked"].sum(), 0), "arr_change_%": arr_pct,
        "matches_finding_12a": (units_pct == -61.9 and arr_pct == -62.5),
    }


if __name__ == "__main__":
    wins, attrib, roster, accounts = load_data()

    print("=== Sanity check vs. Finding 12a (expect -61.9% units / -62.5% ARR) ===")
    check = sanity_check_finding_12a(wins, attrib)
    print(check)
    print()

    print("=== Driver #2: rep-level variance (Outbound BAU units, FY26Q3 wk1-10 -> FY26Q4 wk1-10) ===")
    rep = rep_level_variance(wins, attrib, roster)
    print(rep[["seller_id", "seller_name", "units_from", "units_to", "units_change", "is_new_hire"]].to_string(index=False))
    tenured = rep[~rep["is_new_hire"] & (rep["units_from"] > 0)]
    print(f"\nTenured reps active in FY26Q3 (n={len(tenured)}): "
          f"{(tenured['units_change'] < 0).sum()} declined, "
          f"{(tenured['units_change'] > 0).sum()} increased, "
          f"{(tenured['units_change'] == 0).sum()} flat")
    print()

    print("=== Driver #3: account mix shift, Outbound BAU units, FY26Q3 wk1-10 -> FY26Q4 wk1-10 ===")
    for dim in ["industry", "annual_revenue_band", "region"]:
        print(f"\n-- {dim} --")
        print(account_mix_shift(wins, attrib, accounts, dim).to_string())
    print()

    print("=== Driver #4: true YoY, all channels, FY25Q4 wk1-10 -> FY26Q4 wk1-10 (control group) ===")
    print(yoy_by_channel(wins).to_string(index=False))
    print()

    print("=== Driver #4: true YoY, Outbound BAU only ===")
    print(outbound_bau_yoy(wins, attrib))
