"""
Plan attainment (simplified).

WHAT THIS FILE DOES, IN PLAIN ENGLISH:
Compares actual sales (from wins_with_plays.xlsx, the "wins" sheet) against
the sales plan (from plans.xlsx), by channel and by quarter. The tricky
part: FY26Q4 has TWO plan versions (v1 = original, v2 = Finance's
mid-quarter revision), so this file also picks the correct blended plan for
FY26Q4 and explains why.

KEY DECISIONS THIS FILE MAKES (say these out loud if asked):
1. For FY26Q4, use v1 for weeks 1-5, v2 for weeks 6-13. Why week 6 and not
   week 7? v2 became official on 2026-06-08, which falls on day 2 of a
   7-day fiscal week (weeks run Sunday-Saturday). Since v2 was in effect for
   6 of that week's 7 days, the whole week counts as v2.
2. FY26Q4 isn't finished yet -- the wins data only goes through week 10 of
   13. So instead of comparing 10 weeks of actual sales to a full 13-week
   plan (which would look artificially bad), we shrink the plan down to
   match: "what were we supposed to sell in weeks 1-10 only?"
3. We compare against PLAN (plans.xlsx), not QUOTA (seller_roster.xlsx),
   because quota only has ONE current value per rep with no history --
   we can't verify quota was the same in past quarters. Plan has one
   row per week per quarter, so it's a fair comparison across time.

WHICH WEEK'S DATA IT USES:
Same convention as analysis/data_validation.py -- data/ holds one dated
subfolder per week (e.g. data/2026-07-18/), and this reads directly from
the .xlsx files in there, no CSV conversion step needed. With no arguments
it picks the newest folder automatically; pass a folder name to check an
older week on purpose:
    python3 analysis/plan_attainment.py           # newest week
    python3 analysis/plan_attainment.py 2026-07-11  # a specific week
"""

import os
import re
import sys
from pathlib import Path

import pandas as pd

_DATA_ROOT = Path(os.environ.get("SALES_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
WEEK_FOLDER_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def find_week_folder(week: str = None, data_root: Path = _DATA_ROOT) -> Path:
    week_folders = sorted(p for p in data_root.iterdir() if p.is_dir() and WEEK_FOLDER_PATTERN.match(p.name))
    if not week_folders:
        raise FileNotFoundError(f"No weekly data folders (e.g. 2026-07-18) found in {data_root}")
    if week is None:
        return week_folders[-1]  # newest
    match = data_root / week
    if match not in week_folders:
        available = ", ".join(p.name for p in week_folders)
        raise FileNotFoundError(f"No folder named '{week}' in {data_root}. Available weeks: {available}")
    return match


# ---------------------------------------------------------------------------
# STEP 1: Load the raw data straight from that week's .xlsx files.
# ---------------------------------------------------------------------------

def load_data(week: str = None):
    week_dir = find_week_folder(week)
    plans = pd.read_excel(week_dir / "plans.xlsx", sheet_name="plans")
    wins = pd.read_excel(week_dir / "wins_with_plays.xlsx", sheet_name="wins", usecols="A:L")
    return plans, wins


# ---------------------------------------------------------------------------
# STEP 2: Figure out the correct plan target for FY26Q4.
# This is the one function that does something non-obvious, so it has the
# most comments. Everything else in this file is straightforward filtering.
# ---------------------------------------------------------------------------

def get_correct_plan(plans, fiscal_quarter, channel, through_week):
    """
    Returns the plan_units and plan_arr we SHOULD compare actuals against,
    for one channel, for weeks 1 through `through_week` of one quarter.

    For quarters with only one plan version, this is simple: just add up
    that version's weekly numbers.

    For FY26Q4 (which has v1 AND v2), we use v1 for the early weeks and
    switch to v2 partway through -- see the module docstring for why.
    """
    # Narrow down to just this channel and quarter
    rows = plans[(plans["fiscal_quarter"] == fiscal_quarter) & (plans["channel"] == channel)]

    v2_rows = rows[rows["plan_version"] == "v2"]

    if v2_rows.empty:
        # No revision exists for this quarter -- just use v1, plain and simple.
        selected = rows[rows["plan_version"] == "v1"]
    else:
        # A revision exists. Find the first week v2 covers -- that's our
        # switchover point. Everything before it: v1. That week onward: v2.
        switchover_week = v2_rows["fiscal_week"].min()
        early_weeks = rows[(rows["plan_version"] == "v1") & (rows["fiscal_week"] < switchover_week)]
        later_weeks = rows[(rows["plan_version"] == "v2") & (rows["fiscal_week"] >= switchover_week)]
        selected = pd.concat([early_weeks, later_weeks])

    # Only keep weeks we're actually comparing against (e.g. weeks 1-10,
    # because that's all the actual sales data we have so far)
    selected = selected[selected["fiscal_week"] <= through_week]

    return selected["plan_units"].sum(), selected["plan_arr"].sum()


# ---------------------------------------------------------------------------
# STEP 3: Find out how many weeks of REAL sales data we actually have for
# a given quarter. FY26Q4 is still in progress, so this will return 10 for
# FY26Q4 and 13 for every completed prior quarter.
# ---------------------------------------------------------------------------

def latest_week_with_data(wins, fiscal_quarter):
    rows = wins[wins["fiscal_quarter"] == fiscal_quarter]
    if rows.empty:
        return None
    return int(rows["fiscal_week"].max())


# ---------------------------------------------------------------------------
# STEP 4: The main comparison. Plan vs. actual, for one channel, one quarter.
# ---------------------------------------------------------------------------

def compare_plan_to_actual(plans, wins, fiscal_quarter, channel):
    # How many weeks of this quarter do we actually have sales data for?
    through_week = latest_week_with_data(wins, fiscal_quarter)

    # What SHOULD we have sold, through that many weeks?
    plan_units, plan_arr = get_correct_plan(plans, fiscal_quarter, channel, through_week)

    # What did we ACTUALLY sell, through that many weeks?
    actual_rows = wins[
        (wins["fiscal_quarter"] == fiscal_quarter) &
        (wins["channel"] == channel) &
        (wins["fiscal_week"] <= through_week)
    ]
    actual_units = actual_rows["units"].sum()
    actual_arr = actual_rows["arr_booked"].sum()

    return {
        "fiscal_quarter": fiscal_quarter,
        "channel": channel,
        "weeks_included": f"1-{through_week}",
        "plan_units": int(plan_units),
        "actual_units": int(actual_units),
        "pct_of_unit_plan": round(actual_units / plan_units * 100, 1),
        "plan_arr": round(plan_arr, 0),
        "actual_arr": round(actual_arr, 0),
        "pct_of_arr_plan": round(actual_arr / plan_arr * 100, 1),
    }


# ---------------------------------------------------------------------------
# STEP 5: Convenience wrapper -- run the comparison for EVERY quarter, so
# you can see the full historical trend for one channel in one call.
# ---------------------------------------------------------------------------

def compare_all_quarters(plans, wins, channel):
    all_quarters = sorted(wins["fiscal_quarter"].unique())
    results = [compare_plan_to_actual(plans, wins, q, channel) for q in all_quarters]
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Run this file directly to see a full sanity-check printout.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    requested_week = sys.argv[1] if len(sys.argv) > 1 else None
    plans, wins = load_data(requested_week)

    print(f"Checked week: {find_week_folder(requested_week).name}\n")

    print("How many weeks of real data do we have, per quarter?")
    for q in sorted(wins["fiscal_quarter"].unique()):
        print(f"  {q}: through week {latest_week_with_data(wins, q)}")
    print()

    print("Plan vs. actual, every channel, every quarter:")
    for channel in sorted(wins["channel"].unique()):
        print(f"\n--- {channel} ---")
        df = compare_all_quarters(plans, wins, channel)
        print(df[["fiscal_quarter", "weeks_included", "pct_of_unit_plan", "pct_of_arr_plan"]].to_string(index=False))
