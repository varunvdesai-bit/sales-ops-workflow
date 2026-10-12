"""
Weekly data validation pipeline.

WHAT THIS FILE DOES, IN PLAIN ENGLISH:
Runs a fixed set of checks against the raw Excel extracts for one week and
writes a report into this same folder. Meant to be re-run every time a fresh weekly
extract lands, BEFORE any performance analysis touches the new data -- if
this pipeline finds ERROR-level issues, don't trust the numbers yet.

HOW TO ADD A NEW WEEK'S DATA (no code changes needed):
1. Inside data/, make a new folder named for that week's ending date, e.g.
   data/2026-07-18/  (use the same "week ending" date convention as the
   rest of this analysis -- a Saturday).
2. Copy that week's 6 Excel files into it (accounts.xlsx, plans.xlsx,
   plays.xlsx, seller_roster.xlsx, weekly_funnel.xlsx, wins_with_plays.xlsx).
3. Run:  python3 analysis/data_validation.py
   With no arguments, it automatically finds and checks the NEWEST dated
   folder in data/ -- you don't need to tell it which week. (To check an
   older week on purpose, pass the folder name:
   python3 analysis/data_validation.py 2026-07-11)

The old files directly inside data/ (not in a dated folder) are no longer
used by this script -- every week's files should live in their own dated
folder from now on, so nothing gets silently overwritten week to week.

FOUR CHECK CATEGORIES (each returns a list of Finding objects):
1. Duplicates       -- full-row duplicates, primary/composite-key duplicates,
                        and "near-duplicates" (same business fields, different
                        ID) -- the shape of the FY26Q3 CRM-migration duplicate
                        wins found in the initial data-quality pass.
2. Missing values    -- any null in a field that isn't explicitly allowed to
                        be null (e.g. plans.version_effective is null for v1
                        rows on purpose; that's not an error).
3. Join validation   -- every foreign-key relationship between tables, plus
                        cross-table consistency (seller's channel on the
                        roster must match the channel on their wins; a win
                        must fall within its seller's tenure window).
4. Impossible values -- values that can't be true no matter what the data
                        means (negative ARR, zero units, term_date before
                        start_date, funnel stages that un-shrink, fiscal
                        weeks outside 1-13, etc.), plus an ID-sequence-gap
                        detector that generalizes the migration-artifact
                        pattern so it will catch a RECURRENCE of the same
                        kind of issue in a future weekly extract, not just
                        this one.

Writes exactly one report per week checked: outputs/data_validation_report_<week>.md
(named after the week's folder, e.g. data_validation_report_2026-07-18.md).
Re-running against the same week's folder overwrites that week's report;
each new week's folder produces its own new report -- so you end up with a
running history of one report per week, matching one week's data folder.
The report groups everything under the four category headers above in plain
English -- it does not surface internal check names or severity levels.

Exit code is 1 if any ERROR-severity finding exists (so this can gate a cron
job or CI step), 0 otherwise. WARNING/INFO findings never fail the run.
"""

import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

DATA_DIR = Path(os.environ.get("SALES_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
OUTPUT_DIR = Path(__file__).resolve().parent

# Weekly data folders are named YYYY-MM-DD (the week-ending date), e.g. "2026-07-18".
WEEK_FOLDER_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# ---------------------------------------------------------------------------
# STEP 1: What tables exist, where they live, and what their keys are.
# Update this config -- not the check logic below -- when the schema changes.
# ---------------------------------------------------------------------------

TABLE_SPECS = {
    "accounts": {"file": "accounts.xlsx", "sheet": "accounts", "primary_key": ["account_id"]},
    "plans": {"file": "plans.xlsx", "sheet": "plans",
              "composite_key": ["fiscal_quarter", "fiscal_week", "channel", "plan_version"]},
    "plays": {"file": "plays.xlsx", "sheet": "plays", "primary_key": ["play_id"]},
    "seller_roster": {"file": "seller_roster.xlsx", "sheet": "seller_roster", "primary_key": ["seller_id"]},
    "weekly_funnel": {"file": "weekly_funnel.xlsx", "sheet": "weekly_funnel",
                       "composite_key": ["fiscal_quarter", "fiscal_week", "channel"]},
    "wins": {"file": "wins_with_plays.xlsx", "sheet": "wins", "primary_key": ["win_id"]},
    "play_attribution": {"file": "wins_with_plays.xlsx", "sheet": "play_attribution", "primary_key": ["win_id"]},
}

# Fields that are ALLOWED to be null -- everything else in a table is required.
NULLABLE_FIELDS = {
    "plans": {"version_effective"},   # only populated for v2 rows
    "seller_roster": {"term_date"},   # null = still active
    "wins": {"play_id"},              # null = not attributed to any play
}

# Business-key columns to use for near-duplicate detection: same values on
# all of these, but a different primary key, is suspicious (see wins finding).
NEAR_DUP_KEYS = {
    "wins": ["account_id", "week_ending", "channel", "product", "units", "arr_booked"],
}

# Columns that look like "<letter-prefix><number>" IDs, used by the
# ID-sequence-gap detector, grouped by which column scopes the sequence.
ID_SEQUENCE_CHECKS = [
    # table, id_column, group_by_column
    ("wins", "win_id", "fiscal_quarter"),
    ("accounts", "account_id", None),
]


# The four plain-English buckets everything gets sorted into for the report.
# (Internal check names like "near_duplicate" are still used in code for
# precision, but the report only ever shows one of these four.)
CATEGORY_DUPLICATES = "Duplicates"
CATEGORY_MISSING_VALUES = "Missing values"
CATEGORY_JOINS = "Join problems"
CATEGORY_IMPOSSIBLE_VALUES = "Impossible values"
CATEGORY_ORDER = [CATEGORY_DUPLICATES, CATEGORY_MISSING_VALUES, CATEGORY_JOINS, CATEGORY_IMPOSSIBLE_VALUES]


@dataclass
class Finding:
    severity: str       # "ERROR" | "WARNING" | "INFO"
    category: str        # one of the CATEGORY_* constants above ("INFO" housekeeping notes excepted)
    check: str
    table: str
    message: str
    sample: pd.DataFrame = field(default_factory=pd.DataFrame)
    sample_columns: list = field(default_factory=list)  # subset of columns to show; empty = show all


# ---------------------------------------------------------------------------
# STEP 1b: Figure out WHICH week's folder to check.
# data/ is expected to contain one subfolder per week, each named for that
# week's ending date (e.g. data/2026-07-18/). If no week is specified, this
# picks the most recent one just by sorting the folder names -- YYYY-MM-DD
# names sort chronologically as plain text, so "newest" is just "last".
# ---------------------------------------------------------------------------

def find_week_folder(week: str | None = None, data_dir: Path = DATA_DIR) -> Path:
    week_folders = sorted(
        p for p in data_dir.iterdir()
        if p.is_dir() and WEEK_FOLDER_PATTERN.match(p.name)
    )
    if not week_folders:
        raise FileNotFoundError(
            f"No weekly data folders found in {data_dir}. Expected at least one folder "
            f"named like 2026-07-18 containing that week's Excel files."
        )

    if week is None:
        return week_folders[-1]  # most recent

    match = data_dir / week
    if match not in week_folders:
        available = ", ".join(p.name for p in week_folders)
        raise FileNotFoundError(f"No folder named '{week}' in {data_dir}. Available weeks: {available}")
    return match


# ---------------------------------------------------------------------------
# STEP 2: Load every sheet from every workbook in the config, directly from
# the .xlsx files -- no CSV conversion step, so this can run on whatever
# raw extract lands in that week's folder.
# ---------------------------------------------------------------------------

def load_tables(data_dir: Path) -> tuple[dict[str, pd.DataFrame], list[Finding]]:
    tables = {}
    findings = []
    for name, spec in TABLE_SPECS.items():
        path = data_dir / spec["file"]
        if not path.exists():
            raise FileNotFoundError(f"Expected {path} for table '{name}' but it doesn't exist.")
        df = pd.read_excel(path, sheet_name=spec["sheet"])

        # "Unnamed: N" columns are Excel's name for a column with no header --
        # stray cells (e.g. a pasted legend) rather than real data. Drop them
        # so they don't trigger false-positive missing-value findings below,
        # but log that it happened so a genuinely new blank-header column
        # doesn't disappear silently.
        junk_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
        if junk_cols:
            findings.append(Finding(
                "INFO", "Housekeeping", "dropped_unnamed_columns", name,
                f"Ignored {len(junk_cols)} blank/unlabeled column(s) in '{name}' -- leftover Excel "
                f"formatting, not real data.",
            ))
            df = df.drop(columns=junk_cols)

        tables[name] = df
    return tables, findings


# ---------------------------------------------------------------------------
# CHECK 1: Duplicates
#
# Three sub-checks, in order:
#   (a) Two rows identical in EVERY column -- the exact same record appears
#       twice, verbatim.
#   (b) Two rows reusing the same ID (primary key) -- should be structurally
#       impossible if the ID is really a primary key.
#   (c) The important one: two rows with the same account/week/channel/
#       product/units/ARR but a DIFFERENT ID -- i.e. the same real-world deal,
#       entered twice under two different IDs. This is exactly the shape a
#       CRM double-export leaves behind, and it's how the 35 duplicate
#       FY26Q3 wins were originally caught.
# ---------------------------------------------------------------------------

def check_duplicates(tables: dict[str, pd.DataFrame]) -> list[Finding]:
    findings = []

    for name, df in tables.items():
        # Full-row duplicates: two rows identical in every column.
        dupe_mask = df.duplicated(keep=False)
        if dupe_mask.any():
            findings.append(Finding(
                "ERROR", CATEGORY_DUPLICATES, "full_row_duplicate", name,
                f"'{name}' has {dupe_mask.sum()} rows that are 100% identical to another row.",
                df[dupe_mask].head(6),
            ))

        # Primary-key duplicates: same ID used twice (should be impossible).
        spec = TABLE_SPECS[name]
        key_cols = spec.get("primary_key") or spec.get("composite_key")
        if key_cols:
            key_dupe_mask = df.duplicated(subset=key_cols, keep=False)
            if key_dupe_mask.any():
                findings.append(Finding(
                    "ERROR", CATEGORY_DUPLICATES, "primary_key_duplicate", name,
                    f"'{name}' has {key_dupe_mask.sum()} rows reusing the same ID "
                    f"({' + '.join(key_cols)}) as another row.",
                    df[key_dupe_mask].sort_values(key_cols).head(6),
                ))

        # Near-duplicates: same deal in every business field, just a different ID.
        # This is the check that catches a CRM double-export -- the FY26Q3
        # duplicate-wins issue looked exactly like this.
        near_dup_cols = NEAR_DUP_KEYS.get(name)
        if near_dup_cols:
            near_dupe_mask = df.duplicated(subset=near_dup_cols, keep=False)
            if near_dupe_mask.any():
                findings.append(Finding(
                    "ERROR", CATEGORY_DUPLICATES, "near_duplicate", name,
                    f"'{name}' has {near_dupe_mask.sum()} rows that look like the same real-world "
                    f"record entered twice under two different IDs (same {', '.join(near_dup_cols)}, "
                    f"different ID) -- this is the pattern a CRM migration double-export leaves behind.",
                    df[near_dupe_mask].sort_values(near_dup_cols).head(6),
                    sample_columns=[df.columns[0]] + near_dup_cols,
                ))

    return findings


# ---------------------------------------------------------------------------
# CHECK 2: Missing values
#
# Flags any blank cell in a field that isn't SUPPOSED to be blank. Not every
# blank is a problem -- e.g. `term_date` is null for every seller still
# actively employed, on purpose. NULLABLE_FIELDS (top of this file) is the
# explicit list of "blank here is fine" exceptions; anything blank that ISN'T
# on that list gets flagged, because it means a required field didn't get
# filled in for at least one row.
# ---------------------------------------------------------------------------

def check_missing_values(tables: dict[str, pd.DataFrame]) -> list[Finding]:
    findings = []

    for name, df in tables.items():
        allowed_null = NULLABLE_FIELDS.get(name, set())
        null_counts = df.isna().sum()
        for col, n_null in null_counts.items():
            if n_null == 0:
                continue
            if col in allowed_null:
                continue  # expected, not a finding
            findings.append(Finding(
                "ERROR", CATEGORY_MISSING_VALUES, "unexpected_null", name,
                f"'{name}.{col}' is blank on {n_null} row(s) ({n_null / len(df):.1%} of the table) -- "
                f"this field should always be filled in.",
                df[df[col].isna()].head(6),
            ))

    return findings


# ---------------------------------------------------------------------------
# CHECK 3: Join validation (foreign keys + cross-table consistency)
#
# Checks every foreign-key relationship between tables -- e.g. a win's
# account_id must exist in `accounts`, its seller_id must exist in
# `seller_roster`, its play_id (if any) must exist in `plays`. A row that
# references an ID nobody else has is called an "orphan."
#
# Also two sanity checks that go beyond a plain ID lookup: a seller's channel
# on their wins must match their channel on the roster (did the same person
# get logged under two different channels somewhere?), and a win can't be
# dated before the seller who closed it had started, or after they'd already
# left the company.
# ---------------------------------------------------------------------------

def _orphan_check(child: pd.DataFrame, child_col: str, parent: pd.DataFrame, parent_col: str,
                   child_name: str, parent_name: str, allow_null: bool = False) -> Finding | None:
    rows = child[child[child_col].notna()] if allow_null else child
    orphan_mask = ~rows[child_col].isin(parent[parent_col])
    if orphan_mask.any():
        return Finding(
            "ERROR", CATEGORY_JOINS, "orphaned_foreign_key", child_name,
            f"{orphan_mask.sum()} row(s) in '{child_name}' reference a '{child_col}' that doesn't "
            f"exist in '{parent_name}'.",
            rows[orphan_mask].head(6),
            sample_columns=[child_col],
        )
    return None


def check_joins(tables: dict[str, pd.DataFrame]) -> list[Finding]:
    findings = []
    wins = tables["wins"]
    accounts = tables["accounts"]
    roster = tables["seller_roster"]
    plays = tables["plays"]
    attrib = tables["play_attribution"]

    fk_checks = [
        (wins, "account_id", accounts, "account_id", "wins", "accounts", False),
        (wins, "seller_id", roster, "seller_id", "wins", "seller_roster", False),
        (wins, "play_id", plays, "play_id", "wins", "plays", True),
        (attrib, "win_id", wins, "win_id", "play_attribution", "wins", False),
        (attrib, "play_id", plays, "play_id", "play_attribution", "plays", False),
    ]
    for child, ccol, parent, pcol, cname, pname, allow_null in fk_checks:
        f = _orphan_check(child, ccol, parent, pcol, cname, pname, allow_null)
        if f:
            findings.append(f)

    # Channel vocabulary must match exactly across every table that has a channel column.
    channel_tables = {name: set(df["channel"].dropna().unique())
                       for name, df in tables.items() if "channel" in df.columns}
    all_channels = set().union(*channel_tables.values()) if channel_tables else set()
    for name, values in channel_tables.items():
        missing = all_channels - values
        if missing:
            findings.append(Finding(
                "WARNING", CATEGORY_JOINS, "channel_vocabulary_mismatch", name,
                f"'{name}' is missing channel(s) {sorted(missing)} that show up elsewhere in the "
                f"data. Could be fine (e.g. a channel that launched later) or a typo/rename -- worth "
                f"a quick look.",
            ))

    # Cross-table consistency: a win's channel must match its seller's roster channel.
    merged = wins.merge(roster[["seller_id", "channel", "start_date", "term_date"]],
                         on="seller_id", suffixes=("_win", "_roster"))
    channel_mismatch = merged[merged["channel_win"] != merged["channel_roster"]]
    if len(channel_mismatch):
        findings.append(Finding(
            "ERROR", CATEGORY_JOINS, "seller_channel_mismatch", "wins",
            f"{len(channel_mismatch)} win(s) are logged on a different channel than the seller who "
            f"closed them is assigned to on the roster.",
            channel_mismatch[["win_id", "seller_id", "channel_win", "channel_roster"]].head(6),
        ))

    # Cross-table consistency: a win must fall within its seller's tenure window.
    before_start = merged[merged["week_ending"] < merged["start_date"]]
    after_term = merged[merged["term_date"].notna() & (merged["week_ending"] > merged["term_date"])]
    if len(before_start):
        findings.append(Finding(
            "ERROR", CATEGORY_JOINS, "win_before_seller_start", "wins",
            f"{len(before_start)} win(s) are dated before the seller who closed them had even started.",
            before_start[["win_id", "seller_id", "week_ending", "start_date"]].head(6),
        ))
    if len(after_term):
        findings.append(Finding(
            "ERROR", CATEGORY_JOINS, "win_after_seller_term", "wins",
            f"{len(after_term)} win(s) are dated after the seller who closed them had already left.",
            after_term[["win_id", "seller_id", "week_ending", "term_date"]].head(6),
        ))

    return findings


# ---------------------------------------------------------------------------
# CHECK 4: Impossible values
#
# Things that can't be true no matter what the data means -- no interpretation
# needed to know they're wrong: zero or negative units/ARR on a "won" deal,
# a seller whose term_date is earlier than their start_date, a fiscal_week
# outside 1-13, a funnel stage with MORE records than the stage that feeds it
# (e.g. more SQLs than the MQLs they're supposed to be qualified from).
#
# Also includes the ID-sequence-gap detector at the bottom of this function:
# it looks for an ID column (e.g. win_id) jumping far outside its normal step
# size within a quarter. That's a generalized version of exactly how the
# original 35 duplicate FY26Q3 wins were first spotted -- so this check will
# automatically flag a REPEAT of that same kind of migration/re-export
# artifact if it shows up in a future week's data, not just this one.
# ---------------------------------------------------------------------------

def check_impossible_values(tables: dict[str, pd.DataFrame]) -> list[Finding]:
    findings = []
    wins = tables["wins"]
    plans = tables["plans"]
    roster = tables["seller_roster"]
    accounts = tables["accounts"]
    funnel = tables["weekly_funnel"]

    def flag(mask, table_name, df, check_name, message, cols=None):
        if mask.any():
            findings.append(Finding(
                "ERROR", CATEGORY_IMPOSSIBLE_VALUES, check_name, table_name, message,
                df[mask].head(6), sample_columns=cols or [],
            ))

    flag(wins["units"] <= 0, "wins", wins, "non_positive_units",
         f"{(wins['units'] <= 0).sum()} win(s) have units <= 0 (a win with zero or negative units "
         f"isn't a real sale).", ["win_id", "units"])
    flag(wins["arr_booked"] <= 0, "wins", wins, "non_positive_arr",
         f"{(wins['arr_booked'] <= 0).sum()} win(s) have arr_booked <= 0.", ["win_id", "arr_booked"])
    flag(~wins["fiscal_week"].between(1, 13), "wins", wins, "fiscal_week_out_of_range",
         f"{(~wins['fiscal_week'].between(1, 13)).sum()} win(s) have a fiscal_week outside 1-13.",
         ["win_id", "fiscal_week"])

    flag(plans["plan_units"] < 0, "plans", plans, "negative_plan_units",
         f"{(plans['plan_units'] < 0).sum()} plan row(s) have negative plan_units.")
    flag(plans["plan_arr"] < 0, "plans", plans, "negative_plan_arr",
         f"{(plans['plan_arr'] < 0).sum()} plan row(s) have negative plan_arr.")
    flag(~plans["fiscal_week"].between(1, 13), "plans", plans, "fiscal_week_out_of_range",
         f"{(~plans['fiscal_week'].between(1, 13)).sum()} plan row(s) have a fiscal_week outside 1-13.")

    flag(roster["weekly_quota_units"] <= 0, "seller_roster", roster, "non_positive_quota",
         f"{(roster['weekly_quota_units'] <= 0).sum()} seller(s) have weekly_quota_units <= 0.",
         ["seller_id", "weekly_quota_units"])
    term_before_start = roster["term_date"].notna() & (roster["term_date"] < roster["start_date"])
    flag(term_before_start, "seller_roster", roster, "term_before_start",
         f"{term_before_start.sum()} seller(s) have a term_date earlier than their start_date.",
         ["seller_id", "start_date", "term_date"])

    flag(accounts["employee_count"] <= 0, "accounts", accounts, "non_positive_employee_count",
         f"{(accounts['employee_count'] <= 0).sum()} account(s) have employee_count <= 0.",
         ["account_id", "employee_count"])

    for col in ["leads", "mqls", "sqls", "opps_created"]:
        flag(funnel[col] < 0, "weekly_funnel", funnel, f"negative_{col}",
             f"{(funnel[col] < 0).sum()} funnel row(s) have a negative {col} count.")
    non_monotonic = (
        (funnel["leads"] < funnel["mqls"]) |
        (funnel["mqls"] < funnel["sqls"]) |
        (funnel["sqls"] < funnel["opps_created"])
    )
    flag(non_monotonic, "weekly_funnel", funnel, "funnel_stage_not_monotonic_decreasing",
         f"{non_monotonic.sum()} funnel row(s) show a stage with MORE records than the stage that "
         f"feeds it (e.g. more SQLs than MQLs) -- that can't happen if each stage is a subset of "
         f"the one before it.",
         ["fiscal_quarter", "fiscal_week", "channel", "leads", "mqls", "sqls", "opps_created"])

    # ID-sequence-gap detector: generalizes the FY26Q3 win_id block-jump finding so it
    # will catch the SAME KIND of migration/export artifact in a future weekly extract.
    for table_name, id_col, group_col in ID_SEQUENCE_CHECKS:
        df = tables[table_name]
        numeric_ids = df[id_col].astype(str).str.extract(r"(\d+)")[0]
        if numeric_ids.isna().any():
            continue  # not a clean "<prefix><number>" ID, skip rather than false-flag
        numeric_ids = numeric_ids.astype(int)
        groups = df[group_col] if group_col else pd.Series("all", index=df.index)
        for group_value, idx in df.groupby(groups).groups.items():
            nums = sorted(numeric_ids.loc[idx].unique())
            if len(nums) < 3:
                continue
            gaps = pd.Series(nums).diff().dropna()
            median_gap = gaps.median()
            if median_gap == 0:
                continue
            big_gaps = gaps[gaps > max(50, median_gap * 20)]
            if len(big_gaps):
                findings.append(Finding(
                    "WARNING", CATEGORY_IMPOSSIBLE_VALUES, "id_sequence_gap", table_name,
                    f"'{id_col}' numbering has an unusually large jump within "
                    f"{group_col or 'the table'} = {group_value!r} -- IDs are normally issued in "
                    f"order about {median_gap:.0f} apart, but here they suddenly jump much further. "
                    f"That's the signature a re-exported or renumbered batch of records leaves "
                    f"behind (this is how the FY26Q3 duplicate wins were first spotted) -- worth "
                    f"checking the rows right after the jump for duplicates.",
                ))

    return findings


# ---------------------------------------------------------------------------
# STEP 3: Run everything, print + write a report, and set an exit code that a
# weekly cron job / CI step can gate on.
# ---------------------------------------------------------------------------

def run_all_checks(week: str | None = None, data_dir: Path = DATA_DIR) -> tuple[list[Finding], Path]:
    """Runs every check against one week's folder. `week=None` picks the newest
    folder in data/ automatically. Returns (findings, the week folder that was checked)."""
    week_folder = find_week_folder(week, data_dir)
    tables, findings = load_tables(week_folder)
    findings += check_duplicates(tables)
    findings += check_missing_values(tables)
    findings += check_joins(tables)
    findings += check_impossible_values(tables)
    return findings, week_folder


def write_report(findings: list[Finding], week_folder: Path, output_dir: Path = OUTPUT_DIR) -> Path:
    """
    One file per week checked: data_validation_report_<week>.md, in this same
    folder, named after the week's data folder (not the day the script happened
    to run). Re-running against the same week's folder overwrites that week's
    report; a new week's folder produces a new report -- so this folder ends up
    holding one report per week, matching one data/ folder per week.

    Layout is deliberately simple: a pass/fail line for each of the four
    check categories, then plain-English detail only for the categories that
    found something. Severity (ERROR/WARNING) and internal check names are
    still tracked in the data so the exit code can gate a cron job, but they
    aren't the organizing structure of the report -- the four categories are.
    """
    output_dir.mkdir(exist_ok=True)
    week_label = week_folder.name
    report_path = output_dir / f"data_validation_report_{week_label}.md"

    issues = [f for f in findings if f.severity in ("ERROR", "WARNING")]
    housekeeping = [f for f in findings if f.severity == "INFO"]

    lines = [f"# Data Validation Report -- week of {week_label}", ""]

    if not issues:
        lines.append("**All checks passed. No issues found.**")
    else:
        n_errors = sum(1 for f in issues if f.severity == "ERROR")
        lines.append(f"**{len(issues)} issue(s) found ({n_errors} need attention before trusting "
                      f"this week's numbers).**")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    for category in CATEGORY_ORDER:
        cat_issues = [f for f in issues if f.category == category]
        if not cat_issues:
            lines.append(f"- **{category}:** OK, nothing found.")
        else:
            lines.append(f"- **{category}:** {len(cat_issues)} issue(s) found -- see below.")
    lines.append("")

    for category in CATEGORY_ORDER:
        cat_issues = [f for f in issues if f.category == category]
        if not cat_issues:
            continue
        lines.append(f"## {category}")
        lines.append("")
        for f in cat_issues:
            lines.append(f"- {f.message}")
            if not f.sample.empty:
                sample = f.sample[f.sample_columns] if f.sample_columns else f.sample
                lines.append("")
                lines.append(sample.to_markdown(index=False))
                lines.append("")
        lines.append("")

    if housekeeping:
        lines.append("## Notes")
        lines.append("")
        for f in housekeeping:
            lines.append(f"- {f.message}")
        lines.append("")

    report_path.write_text("\n".join(lines))
    return report_path


if __name__ == "__main__":
    # Optional: python3 analysis/data_validation.py 2026-07-11
    # to check a specific week instead of the newest one.
    requested_week = sys.argv[1] if len(sys.argv) > 1 else None

    findings, week_folder = run_all_checks(week=requested_week)
    report_path = write_report(findings, week_folder)

    n_errors = sum(1 for f in findings if f.severity == "ERROR")
    n_warnings = sum(1 for f in findings if f.severity == "WARNING")

    print(f"Checked week: {week_folder.name}")
    print(f"Data validation complete: {n_errors} error(s), {n_warnings} warning(s).")
    print(f"Full report: {report_path}")

    if n_errors:
        for f in findings:
            if f.severity == "ERROR":
                print(f"  [ERROR] {f.table}: {f.message}")
        sys.exit(1)
    sys.exit(0)
