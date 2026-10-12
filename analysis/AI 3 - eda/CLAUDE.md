# CLAUDE.md — AI 3: Exploratory Analysis

Layered on top of the root `CLAUDE.md`. This folder's job: investigate open-ended "why" questions
that don't have a fixed script or a fixed report format — the opposite mode from Use Cases 1 and 2.

## What's in this folder

- **`outbound_deep_dive.py`** — the worked example. Built to answer one specific question (why did
  Outbound miss plan) by testing three candidate drivers — rep-level concentration, account/industry/
  region mix, true year-over-year timing — and reporting all three together rather than stopping at
  the first plausible-looking one.
- **`sales_funnel_analysis.py`** — a broader underlying-trends script: average deal size by
  channel/quarter, lead volume (with a 13-week-pace projection for in-progress quarters), and funnel
  conversion rates (lead→MQL→SQL→opp). Reads `wins_with_plays.xlsx` and `weekly_funnel.xlsx`
  directly, no CSV conversion needed. Meant to be read alongside `AI 2 - plan attainment report`'s
  output: that folder says whether a channel missed its number, this one says why, or whether the
  number was ever realistic.

A shared helper module (`exploration_toolkit.py`) was tried and cut — not enough investigations
existed yet to know which patterns were actually worth generalizing, and a speculative abstraction
with no real second user was adding a file to understand rather than removing work. Worth revisiting
once two or three more investigations exist and a real repeated pattern shows up on its own.

## This folder is not auto-triggered

Do not proactively run anything here the way Use Cases 1 and 2 are triggered by a topic keyword.
Exploratory analysis starts from a specific question a human poses, not a topic match — "why did
Outbound miss plan" needs a human to have asked that, not an assistant guessing it's relevant.

## Standards for this folder specifically

- **Every new investigation gets written as a new script and a new finding** in
  `analysis/assumptions_and_findings.md` — same convention `outbound_deep_dive.py` follows: state the
  hypothesis, the method, the result, and whether it's QoQ or YoY. A script that runs but doesn't get
  logged there didn't really happen, for the purposes of this engagement.
- **Always separate BAU from play-driven volume explicitly** when a channel has an active play
  running. A scope mismatch here (comparing an all-wins figure against a BAU-only figure without
  saying so) already produced two contradictory-looking numbers once in this engagement — reconciled
  in `assumptions_and_findings.md`, worth reading before repeating the pattern.
- **A baseline run-rate projection is not the same thing as an incremental lift from new spend or an
  incentive.** State explicitly which one a projection is before it goes anywhere near a
  recommendation — this exact conflation produced a wrong draft slide number once (the ABM
  incentive-sizing question) before it was caught.
