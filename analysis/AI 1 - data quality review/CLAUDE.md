# CLAUDE.md — AI 1: Data Quality Review

Layered on top of the root `CLAUDE.md`. This folder's job: catch data problems before anything
downstream (attainment numbers, findings, slides) trusts this week's data.

## Architecture

```
data/<new dated folder>            (human drops it in manually, once/week)
        |
        v
data_validation.py                 (deterministic pandas -- already built, unchanged)
        |
        v
data_validation_report_<week>.md   (structured Markdown, this same folder: 4 categories --
                                     duplicates, missing values, join problems, impossible values)
        |
        v
Claude Code synthesis (below)      (LLM step -- turns the structured report into a
                                     one-page plain-English summary)
        |
        v
HUMAN REVIEW                       (required before anything goes to Sales Ops --
                                     this step is not automated and should not be)
```

## Answering questions without being told which script to run

When asked anything about data quality, whether this week's data is trustworthy, or whether it's
safe to analyze — run `data_validation.py` proactively, don't wait to be told to "run" it:

```bash
python3 "analysis/AI 1 - data quality review/data_validation.py"
```

Then write a one-page synthesis using this prompt against the report it produces:

> Read `data_validation_report_<week>.md`. Write a one-page summary for Sales Ops: what's new or
> different from last week's report, which issues (if any) block trusting this week's numbers, and
> which are cosmetic. Do not restate every line of the report -- lead with whether this week's data
> is safe to analyze, then the two or three items that actually matter. Flag anything you are not
> confident about rather than smoothing over it.

Save as `data_quality_summary_<week>.md`, in this same folder. This sits for human review before
reaching Sales Ops — nothing here sends or distributes anything on its own.

This is intent-triggered automation inside a session, not unattended scheduling — it still requires
the user to ask something. It removes the need to name a script, not the need for a human to be
present.

## On "automatically run this weekly"

Real constraint, checked directly before promising this: Claude Code's cloud scheduling
(`RemoteTrigger`/routines) runs in an isolated cloud sandbox with **no access to local files**, and
requires a git repository to check out from — this project folder is not one. So a cloud routine
cannot see a file dropped into a local `data/` folder. Two real paths forward, not yet decided:

1. **Local scheduling (macOS `launchd`)** — a scheduled job on this machine invokes Claude Code
   headlessly once a week. Stays fully local, matches the current manual-drop workflow exactly.
   Requires installing a persistent system LaunchAgent — a real system change, not something to do
   silently.
2. **Move to a git repo + cloud routine** — turns this into a real repo, and the weekly step becomes
   "commit and push the new data folder" instead of "drop it locally." More infrastructure, but
   genuinely hands-off once set up.
3. **n8n or similar workflow orchestration** — a scheduled/webhook-triggered flow that runs the
   script against a newly dropped folder and lands the draft report for review, no chat session
   required to kick it off. Named as the target future
   architecture — not built.

None of the three is built yet. Until one is chosen, "weekly" means: the human runs this (or asks
Claude Code to) after dropping in a new data folder, same as it does today.

## Standards for this folder specifically

- **The deterministic script stays deterministic.** The one-page synthesis interprets and
  prioritizes what the script found; it never invents a check the script doesn't actually perform,
  and never softens a real ERROR-level finding into something that reads as optional.
- **State blast radius precisely.** "1 row, 1 week, 1 channel" is a different sentence than "this
  affects the dataset" — say which one is true, every time, the way the week-7 Inbound SQL>MQL
  issue was scoped exactly (one row) rather than implied to be systemic.
- **Cosmetic vs. blocking gets an explicit label, always** — never leave a reader to infer severity
  from tone.
- **When a check's own assumption might be stale or wrong** (e.g. a column that's "supposed" to
  always be filled in but no longer needs to be, given how the workflow evolved) — say so as a
  possibility, don't silently assume the check is right and the data is wrong.
