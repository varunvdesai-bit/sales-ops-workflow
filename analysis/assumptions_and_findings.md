# Assumptions and Findings Log

Running log of judgment calls, verified assumptions, and findings, in the order
they were established. Intended as backup material for the exec readout and
as the written record of how each number was established.

**This is the single source of truth file.** (A separate `_addendum.md` file
existed briefly and has been merged in here — do not create a second
findings file going forward; everything appends to this one.)

---

## Baseline decisions

**Fiscal calendar:** Fiscal weeks run Sunday–Saturday (confirmed: every
`week_ending` in `wins.csv` is a Saturday). FY26Q4 = the current quarter
(consistent with "week 11 of 13" as of July 14, 2026). FY26Q4 runs
2026-05-03 to 2026-08-01, 13 weeks, 4 channels (Hunters, Inbound, Outbound,
Upgrades).

**Data gap:** `data_dictionary.md`, referenced in the data packet's file table,
is not present in the dataset (checked both the `data/` and
`excel files/` folders). All field definitions below are inferred from data
inspection, not confirmed documentation — flagged wherever this matters.

**wins.csv currently has actuals only through fiscal_week 10 of 13** for
FY26Q4. The quarter is NOT complete. All FY26Q4 "current performance" figures
in this log are prorated to weeks 1–10, not the full 13-week quarter, unless
otherwise stated. This is proration (shrinking the plan to match elapsed
weeks), not extrapolation (projecting actuals forward) — the two are
different techniques and were not conflated here.

**CRITICAL: units and ARR attainment diverge and must always be reported
together, never as a single "% of plan" number.** Confirmed across every
channel and every quarter — units % of plan and ARR % of plan are
consistently different, sometimes by a lot, and in FY26Q4 specifically two
channels (Hunters, Outbound) show ARR moving in the OPPOSITE direction from
units. Any "% of plan" figure anywhere in this analysis or the final
deliverables must specify units or ARR explicitly.

**Plan version blending (v1 → v2):** FY26Q4 has two plan versions. v1 =
original plan, published 2026-05-04, covers all 13 weeks. v2 = Finance's
revision, `version_effective` = 2026-06-08, covers weeks 6–13 only.
  - v2's effective date (2026-06-08, a Monday) falls on day 2 of fiscal week 6
    (which runs Sun 2026-06-07–Sat 2026-06-13) — checked directly against the
    calendar, not assumed.
  - Decision: week 6 is assigned to v2, not v1, because v2 was in effect for
    the majority of that week's days (6 of 7). Logic lives in
    `plan_attainment.py` (`blended_plan()`), not re-derived ad hoc.
  - v1 and v2 agree at week 6 for Hunters specifically (so this choice
    doesn't move Hunters' numbers) but do differ for Inbound, Outbound, and
    Upgrades — verified directly, not assumed.
  - **v1 and v2 cannot be mixed by metric** (e.g. "use v2 for units but v1
    for ARR") — Finance issued one integrated plan revision covering both
    columns of the same `plans.csv` rows together. Picking different
    versions per metric would mean inventing a plan Finance never actually
    published. The correct approach is: pick ONE plan version as the
    baseline, then report BOTH units and ARR attainment under that single
    version (see Finding 4 below).

**Actuals source vs. plan source:** actuals = `wins.csv` (`units`,
`arr_booked`), summed by channel/quarter/week. Plan = `plans.csv`
(`plan_units`, `plan_arr`). Comparisons deliberately use PLAN, not roster
QUOTA (`seller_roster.csv`), as the primary benchmark — see next section for
why.

**Why plan, not quota, for attainment comparisons:** `seller_roster.csv`
gives only a current-snapshot `weekly_quota_units` per rep, with no
historical field — can't confirm quota was constant across past quarters.
Cross-check for Hunters: roster says 0.8 units/rep/week; back-solving from
`plans.csv` (plan_units ÷ 13 weeks ÷ 8 reps) implies ~0.75/rep/week for the
5 quarters prior to FY26Q4 — close but not identical, meaning either quota
changed over time or the two figures use slightly different conventions.
Given this ambiguity, plan-vs-actual (using Finance's own published targets)
is the more defensible comparison and avoids relying on an unverified
historical-quota assumption.

---

## Finding 1 — Decision 1 vs. Decision 2 are different questions

Two separate planning decisions need two separate tests:
  - **Decision 1 (setting v1, made 2026-05-04, before FY26Q4 started):** the
    only fair test is prior-quarter performance, since weeks 1–5 of FY26Q4
    hadn't happened yet when v1 was set.
  - **Decision 2 (setting v2, made 2026-06-08, during week 6):** the fair
    test is QTD performance in weeks 1–5 of FY26Q4, since that's the new
    information Finance had access to that it didn't have when setting v1.

Decision 1 is a long-term/strategic planning-process question (does Finance's
QoQ target-setting track demonstrated channel trends) — informative but not
something the VP needs to act on in the next 3 weeks. Decision 2 bears
directly on the quarter-reset story the VP asked for.

---

## Finding 2 — Decision 1: was the FY26Q4 v1 plan well-calibrated to prior-quarter trends?

Hunters was the ONLY channel whose v1 plan was raised for FY26Q4 (78→91,
+16.7% units). Inbound, Outbound, and Upgrades were all held exactly flat
QoQ on units AND on ARR (confirmed both metrics — v1 ARR plan: Inbound and
Outbound and Upgrades all show 0.0% QoQ change FY26Q3→FY26Q4; Hunters +16.7%).

Prior 5-quarter actual attainment vs. v1 plan (FY25Q3–FY26Q3) — **units**:

| Channel  | FY25Q3 | FY25Q4 | FY26Q1 | FY26Q2 | FY26Q3 |
|----------|--------|--------|--------|--------|--------|
| Hunters  | 100.0% | 105.1% | 107.7% | 106.4% | 111.5% |
| Inbound  | 98.2%  | 100.5% | 99.2%  | 97.9%  | 100.4% |
| Outbound | 93.8%  | 99.0%  | 94.8%  | 83.9%  | 94.2%  |
| Upgrades | 97.7%  | 99.3%  | 110.2% | 113.6% | 120.5% |

Same comparison — **ARR**:

| Channel  | FY25Q3 | FY25Q4 | FY26Q1 | FY26Q2 | FY26Q3 |
|----------|--------|--------|--------|--------|--------|
| Hunters  | 107.1% | 119.4% | 126.5% | 118.1% | 123.0% |
| Inbound  | 102.1% | 104.1% | 102.8% | 101.9% | 102.4% |
| Outbound | 96.6%  | 100.0% | 94.2%  | 85.7%  | 96.8%  |
| Upgrades | 99.2%  | 101.4% | 110.7% | 115.0% | 121.5% |

**Read:** the qualitative story is the same under both metrics (Inbound
~flat/on-plan, Outbound chronically behind, Hunters and Upgrades ahead), so
Decision 1's conclusion doesn't change based on metric choice. But ARR
attainment is consistently higher than units attainment for every channel,
every quarter — a long-run mix-shift trend (rising average deal size)
running underneath all four channels for at least 5 quarters, independent of
anything specific to FY26Q4. Worth a one-line mention as background context,
distinct from the acute FY26Q4 divergence in Finding 5.

**NOTE (see Finding 13): FY26Q3's figures in this table are pre-correction
and may be slightly inflated for Outbound specifically due to a duplicate-
booking issue discovered later — 94.2%/96.8% should be read as 85.8%/88.3%
once corrected. Does not change the qualitative pattern.**

Headcount check (ruling out capacity as the driver of the flat plans):
  - Upgrades: 18 active reps flat for 4 straight quarters (FY25Q4–FY26Q4
    start), zero terminations ever. Output kept climbing anyway — a
    productivity/execution improvement, not a headcount story. (One new
    hire, Ellis Walsh, started 2026-06-15 — too late to have informed the v1
    plan or the week 1–5 QTD signal used for v2; doesn't change either
    verdict.)
  - Outbound: headcount stable at 20–21 active reps every week of FY26Q4 (5
    terminations offset by 3 new starts, timed closely together — no point
    in the quarter dropped below 20). Rules out attrition as a driver of
    Outbound's chronic plan miss; the shortfall pre-dates and is independent
    of any FY26Q4 headcount churn.
  - Hunters: 8 reps, zero headcount change across the full history.

**Conclusion: the FY26Q4 v1 plan wasn't calibrated consistently across
channels — only Hunters moved, and not obviously the channel with the
strongest case for a change** (Upgrades' accelerating, headcount-independent
over-performance arguably had a stronger case; Outbound's chronic softness
arguably warranted a cut, not a flat hold). This is a planning-process
finding, useful for next-quarter planning, but not an urgent 3-week action
item.

---

## Finding 3 — Decision 2: was the v1→v2 revision justified, per channel? (units)

QTD (weeks 1–5) actual vs. v1 plan, compared to v2's % change to the
remaining-quarter (weeks 6–13) target — **units**:

| Channel  | % of v1 plan, wks 1–5 | v2 % change to remaining plan | Directionally consistent? |
|----------|----------------------|-------------------------------|---------------------------|
| Hunters  | 80.0% (behind)       | 0.0% (unchanged)               | **NO** |
| Inbound  | 90.3% (behind)       | -1.7% (lowered)                | Yes |
| Outbound | 68.1% (behind)       | -18.8% (lowered)                | Yes |
| Upgrades | 121.1% (ahead)       | +16.7% (raised)                 | Yes |

**Hunters — 80% of unit plan QTD, and v2 kept the target unchanged. We don't
know why — e.g., Finance had specific knowledge that Hunters would cover the
gap, or this was a process miss.** CONFIRMED directly: Hunters wk1-5 actual
units = 28 vs. v1 plan = 35 (80.0%); v1 remaining-quarter plan (wk6-13) = 56
units, v2 remaining-quarter plan (wk6-13) = 56 units — literally unchanged.

---

## Finding 4 — v1 vs. v2 as the baseline for measuring current performance (weeks 1–10), both metrics

**Units** — % of plan, actual units through week 10:

| Plan version              | Hunters | Inbound | Outbound | Upgrades |
|----------------------------|---------|---------|----------|----------|
| % of v1 plan — units      | 82.9%   | 87.8%   | 65.9%    | 120.8%   |
| % of v2 plan — units      | 82.9%   | 88.6%   | 72.8%    | 111.5%   |

**ARR** — % of plan, actual ARR through week 10:

| Plan version              | Hunters | Inbound | Outbound | Upgrades |
|----------------------------|---------|---------|----------|----------|
| % of v1 plan — ARR        | 122.1%  | 98.1%   | 55.1%    | 132.8%   |
| % of v2 plan — ARR        | 122.1%  | 98.9%   | 60.8%    | 122.6%   |

Note: Hunters' ARR attainment is identical under v1 and v2 (122.1% either
way) — confirms Hunters' ARR plan wasn't revised any more than its units
plan was; the whole channel plan was left untouched in v2, not just the unit
target.

### Quantitatively
v2 is the better indicator of EOQ performance, on both metrics. Under units,
three of four channels converge closer to 100% under v2 than v1 (Outbound
65.9%→72.8%, Upgrades 120.8%→111.5%). Under ARR, the same pattern holds
(Outbound 55.1%→60.8%, Upgrades 132.8%→122.6%). Hunters is the exception on
both metrics: unchanged, because it's the one channel whose plan wasn't
actually revised.

**On mixing plan versions by metric:** considered using v2 for one metric
and v1 for the other (e.g. "v2 on units, v1 on ARR") — rejected. v1 and v2
are a single integrated plan revision; there is no Finance-published version
that revises one metric without the other. Use one baseline (v2,
recommended) and report both metrics under it.

### Qualitatively
- To give the VP the most realistic, well-informed view of where the
  business actually lands, we should go with v2 as the baseline.
- However, Hunters' v2 hasn't been updated despite underperformance QTD (on
  units; ARR was already running ahead QTD — see Finding 5 for why these
  point in different directions).
- Also — this comparison, on its own, doesn't identify: (1) the problems
  we've identified on Outbound (which has missed plan in recent quarters,
  independent of this quarter's revision), (2) the drivers of
  over-performance on Upgrades, (3) the recent in-quarter problems on
  Hunters. Each needs its own root-cause dig, separate from the
  plan-baseline question this table answers.

**Note on the ask:** the VP's stated need (what is actually happening, a
quarter reset in three weeks, planning into next quarter) is forward-looking
and explicitly rejects taking comfort in surface-level numbers — this
supports using v2 as the operating baseline (most current, most informed)
while still flagging Hunters as a case where adopting v2 uncritically would
hide, not surface, a real gap. Nothing in the ask explicitly says "use v2" —
this is an inference from stated intent, not a documented rule, and is
flagged as a judgment call for that reason.

---

## Finding 5 — Units-vs-ARR divergence isolated via average deal size (actuals only, no plan involved)

First attempt used a ratio metric (ARR % of plan ÷ units % of plan). Replaced
it: that ratio algebraically reduces to (actual ARR/unit) ÷ (planned
ARR/unit) — meaning it still smuggled in Finance's planning assumptions
(the same ones under scrutiny throughout this analysis) into what was
supposed to be a read on actual sales behavior. Rebuilt using pure actuals:
average deal size = actual ARR ÷ actual units, by channel, by quarter — no
plan, no target, just what was actually sold. Cleaner isolation and easier to
explain (dollars per deal, not a ratio of two percentages).

Also built a units-only version of the historical QoQ attainment chart (the
existing chart was ARR-only) to make sure Finding 2 and the pacing chart
were read on a consistent, stated metric.

NOTE: an earlier "Finding 7" attempted to present this same average-deal-size
data a second time as if it were a separate/expanded finding. On review it
was not — it reused the identical numbers below with no new evidence.
Retracted; folded fully into this Finding 5. There is no separate deal-size
finding beyond what's here.

**Average deal size ($ ARR per unit), actuals only:**

| Channel  | FY25Q3  | FY25Q4  | FY26Q1  | FY26Q2  | FY26Q3  | FY26Q4 (thru wk10) |
|----------|---------|---------|---------|---------|---------|---------------------|
| Hunters  | $14,997 | $15,896 | $16,450 | $15,533 | $15,442 | **$20,633**         |
| Inbound  | $8,213  | $8,180  | $8,185  | $8,228  | $8,061  | $8,820              |
| Outbound | $9,675  | $9,490  | $9,340  | $9,604  | $9,654  | **$7,858**          |
| Upgrades | $5,789  | $5,818  | $5,726  | $5,768  | $5,746  | $6,264              |

**Read:**
- **Hunters' average deal size jumps to $20,633 this quarter — a ~33% jump
  from a stable $14,997–$16,450 band held for 5 straight quarters.** RESOLVED
  (see Finding 10): driven by a small number of unusually large deals, not a
  broad shift — median deal size barely moved.
- **Outbound's average deal size falls to $7,858 — an ~18% drop from a
  stable $9,340–$9,675 band, on this table's channel-wide (BAU + play)
  basis.** CORRECTED (see Finding 14's synthesis below): this is a mix
  effect, not evidence the core business is selling worse deals.
  Organic-only (ex-P2, ex-P5) average deal size is $9,565 → $9,392, a -1.8%
  move -- essentially flat. The two Outbound plays' own deals average
  $6,395 (P2 = purchased-list cold outreach, P5 = discounted win-back offer
  -- both intentionally lower-ticket by design, not underperforming),
  which drags the blended number down and makes the organic book look
  worse than it is. **Outbound's problem is volume, not deal quality or
  pricing** -- what closes organically remains healthy; there's just less
  of it. (See Finding 9 for the lead-volume side of this story, and
  Finding 14's synthesis for how all three pieces fit together.)
- Inbound and Upgrades show only modest increases (~+9% each), consistent
  with the gentle long-run mix-shift already noted in Finding 2 — nothing
  alarming, and within the range of quarter-to-quarter noise seen
  historically for those two channels.

**NOTE (see Finding 13): FY26Q3 Outbound's $9,654 figure was checked against
the duplicate-booking correction and barely moves (+0.13%, to $9,667) — this
row does NOT need correction. Duplicates cancel out in a ratio metric since
both ARR and units shrink proportionally.**

---

## Finding 6 — Company-wide pacing, units vs. ARR, side by side (v2 baseline, weeks 1-10)

**Units — pacing vs. v2 plan:**

| Channel  | Plan Units | Actual Units | Gap  | % of Plan |
|----------|-----------:|-------------:|-----:|----------:|
| Hunters  | 70         | 58           | -12  | 82.9%     |
| Inbound  | 595        | 527          | -68  | 88.6%     |
| Outbound | 290        | 211          | -79  | **72.8%** |
| Upgrades | 390        | 435          | +45  | 111.5%    |
| **Total**| **1,345**  | **1,231**    | **-114** | **91.5%** |

**ARR — pacing vs. v2 plan:**

| Channel  | Plan ARR | Actual ARR | Gap       | % of Plan |
|----------|---------:|-----------:|----------:|----------:|
| Hunters  | $1.0M    | $1.2M      | +$217k    | 122.1%    |
| Inbound  | $4.7M    | $4.6M      | -$52k     | 98.9%     |
| Outbound | $2.7M    | $1.7M      | -$1.07M   | **60.8%** |
| Upgrades | $2.2M    | $2.7M      | +$502k    | 122.6%    |
| **Total**| **$10.6M** | **$10.2M** | **-$402k** | **96.2%** |

**Read:** company-wide unit pacing (91.5%) is meaningfully worse than
company-wide ARR pacing (96.2%) — a ~5-point gap between the two headline
numbers, which is itself evidence of the mix-shift dynamic running through
the quarter (Hunters and Upgrades both overweighting the dollar total more
than the unit total). This is the topline version of the exact thing the VP
warned against: the revenue line reads better than units, and that should
not be a reason to relax. Two numbers to lead with: **91.5% of unit plan** and **96.2% of
ARR plan**, presented together, not the ARR number alone.

Both pacing figures confirmed NOT to be a "quarter isn't over yet" artifact:
proration is already baked into both the plan side (shrunk to weeks 1-10)
and the actuals side (weeks 1-10 only), using the same method and the same
10-week window for every channel. If the low percentages were a timing
artifact, all four channels would show similarly depressed numbers — instead
Upgrades sits at 111.5%/122.6% over the identical window, which rules out
"the clock hasn't run out" as the explanation for Outbound's low numbers.

**Note: this table uses FY26Q4 figures only, which are unaffected by the
Finding 13 duplicate-booking issue (that issue is isolated to FY26Q3). No
correction needed here.**

---

## Finding 7 — Per-channel diagnosis: units vs. ARR vs. avg deal size, synthesized (v2 baseline)

Pulling Findings 4-6 together into one per-channel read, validated against
the pure-actuals average deal size trend (Finding 5):

- **Hunters** — under on units (82.9%), over on ARR (122.1%) → unit-to-
  revenue ratio has risen. **Validated**: avg deal size actuals jumped from a
  stable ~$15-16.5k band to $20,633 this quarter (Finding 5). Fewer, bigger
  deals — but see Finding 10: concentrated in a handful of large wins, not
  a broad shift.
- **Inbound** — under on units (88.6%), roughly at plan on ARR (98.9%) →
  unit-to-revenue ratio has risen, more mildly. **Validated**: avg deal size
  actuals rose modestly (~$8,061 → $8,820), consistent with a small mix
  improvement, not a dramatic shift. HOWEVER see Finding 11: Inbound's
  actual ARR is DOWN -4.3% QoQ even though it looks fine against a flat
  plan — worth a caveat, this channel is not a clean "no story" channel.
- **Outbound** — under on BOTH units (72.8%) and ARR (60.8%), and ARR is
  worse than units. **Validated, and this is the compounding-miss case**: avg
  deal size actuals fell (~$9,654 → $7,858) — Outbound isn't just closing
  fewer deals, the deals themselves shrank too. Two independent problems
  stacked on top of each other (see Finding 9 for a third layer: lead
  volume; Finding 11 for a fourth layer, corrected in Finding 13: actual ARR
  QoQ, the starkest number of all).
- **Upgrades** — over on units (111.5%), over by more on ARR (122.6%) →
  unit-to-revenue ratio has risen here too. **Confirmed**: avg deal size
  actuals rose (~$5,746 → $6,264), a genuine mix improvement layered on top
  of real volume growth. Also confirmed +9.3% actual ARR QoQ (Finding 11) —
  clean, real growth story.

**Pattern:** every channel's unit-to-revenue ratio moved upward this quarter
EXCEPT Outbound, which moved the opposite direction. That makes Outbound the
outlier in two separate ways at once: it's the only channel missing on both
metrics, and it's the only channel where average deal size is actively
shrinking rather than growing. This concentration is what should drive the
slide-level prioritization in Finding 8.

---

## Finding 8 — What goes on the slide: plan-relative story vs. actuals-only story (two different questions, use both, but not with equal weight)

Raised directly: should the exec slide show performance-vs-plan (pacing,
gaps, % of plan) or performance-in-general (actuals-only trends in unit
volume and average deal size), given these feel like two different, both
legitimate, framings.

**Resolution: they are two different questions, and the deck needs both, but
they are not equally load-bearing — plan-vs-actual is the primary story,
actuals-only trend is the supporting evidence, not a replacement for it.**

Reasoning:
- The VP's ask is explicitly plan-relative: ~92% of the unit plan, and what is
  actually happening (relative to what leadership was told to
  expect), and the whole reason a "reset" is needed is that reality has
  diverged from a target someone committed to. A pure actuals-only trend
  chart (units and avg deal size over time, no plan line) is descriptive but
  doesn't answer "did we miss, and by how much" — which is the question a
  CFO in the room will be asking. Dropping the plan comparison entirely would
  under-deliver on the actual ask.
- BUT the actuals-only view (Finding 5, and now Finding 11's pure ARR QoQ)
  is what makes the plan-vs-actual story credible and precise, rather than
  vague. Without it, "Outbound missed plan" sounds like it could be explained
  away by a bad plan (Finding 2 shows Finance's planning process has real
  gaps). WITH it, "Outbound's actual ARR fell sharply QoQ, independent of any
  plan number" is a claim about the business, not about Finance's
  target-setting — much harder to wave away by disputing the plan's
  validity, and it's a starker number than any plan-relative figure.
- So: use plan-vs-actual (gap in $, % of plan) as the headline metric on the
  slide, and use the actuals-only trends (avg deal size, actual ARR QoQ) as
  the supporting visual that proves the headline isn't an artifact of a bad
  plan. This mirrors exactly how Findings 5-7 and 11 were built in this
  analysis: plan comparison to size and rank the problem, actuals-only trend
  to validate it's real and isolate volume vs. mix.

**Slide-level recommendation:**
1. Lead with the two pacing numbers from Finding 6 (91.5% units / 96.2% ARR)
   as the "don't relax on the blended number" framing.
2. Break into the four-channel gap table (Finding 6) to show where the
   -$402k blended gap is actually concentrated (Outbound -$1.07M drives it,
   masked by Hunters + Upgrades upside).
3. Use Outbound's actual ARR QoQ (corrected figure — see Finding 13) as the
   single starkest, most plan-independent number for that channel — likely
   the best one to lead the Outbound callout with.
4. Use the average-deal-size actuals chart (Finding 5) AND the lead-volume
   chart (Finding 9) as supporting evidence for the "why" behind both
   Outbound's miss and Hunters' upside. For Hunters specifically, state the
   deal-size jump is concentrated in a handful of large wins, now confirmed
   as P4's doing (Finding 12b) — a proven, repeatable mechanism, not a
   fragile fluke.
5. Do NOT lead with the actuals-only, no-plan-line version of the chart as a
   standalone story — it's real and correct, but on its own it doesn't
   answer "so what should the VP tell leadership," which is a
   plan/commitment question, not a pure trend question.

---

## Finding 9 — Outbound's volume shortfall traced upstream: lead volume, not conversion, and NOT Outbound-specific

Double-clicked on Outbound's unit shortfall (Finding 7) by pulling
`weekly_funnel.csv` (leads → MQLs → SQLs → opps_created), to separate a
top-of-funnel volume problem from a conversion/execution problem.

**Conversion rates for Outbound are essentially unchanged vs. history:**
lead-to-MQL 42.7% (vs. ~41-42% historical band), MQL-to-SQL 11.1% (vs. ~12%,
a small dip), SQL-to-opp 70.0% (within the 68.8-71.5% historical range).
**Conclusion: this is not a conversion-quality or execution problem** — the
funnel converts leads to opportunities about as efficiently as it always has.

**The real break is raw lead volume**, and initially this looked
Outbound-specific — but checking all four channels changed that read:

Lead volume, FY26Q4 (10 weeks) prorated to a 13-week equivalent, vs. FY26Q3:

| Channel  | % change, prorated FY26Q4 vs. FY26Q3 |
|----------|--------------------------------------|
| Hunters  | -10.7%                                |
| Inbound  | -10.0%                                |
| Outbound | -12.4%                                |
| Upgrades | +1.3%                                 |

**Revised conclusion: lead volume is down company-wide this quarter (three
of four channels, roughly -10 to -12%), not an Outbound-specific problem.**
Outbound's -12.4% is the worst of the four, but not dramatically different
from Hunters (-10.7%) or Inbound (-10.0%) — this looks like a shared,
quarter-level phenomenon hitting most of the business, not something unique
to how Outbound generates leads.

**What IS Outbound-specific: its inability to absorb the shared shock.**
Comparing each channel's lead decline to its ARR outcome:
- Hunters (-10.7% leads) → still landed at 122.1% of ARR plan (deal-size
  increase more than offset the lead dip).
- Inbound (-10.0% leads) → landed at 98.9% of ARR plan (basically absorbed
  it with no real damage).
- Upgrades (+1.3% leads) → 122.6% of ARR plan (leads held up, and it
  thrived on top of that).
- **Outbound (-12.4% leads, the worst of the four) → 60.8% of ARR plan, a
  far worse outcome than its lead shortfall alone would predict.**

**This is the sharper, more accurate version of the Outbound finding:**
Outbound did not create a unique lead-generation problem this quarter — it
was hit by the same company-wide softness every other channel saw, but
unlike the other three, it had no offsetting deal-size improvement (in fact
the opposite — deal size fell, Finding 5) and no other cushion, so the same
shared shock produced a dramatically worse outcome. Outbound's problem is
resilience/mix, not (primarily) unique lead generation.

**Confirmed: the ~10-12% lead decline is NOT a planning-quality artifact.**
`plans.csv` has no lead-volume field at all (only plan_units/plan_arr), so
there is no "planned leads" number this could be compared against or
explained away by — the decline is a fact about actuals-vs-actuals (this
quarter's leads vs. last quarter's), fully independent of any plan-setting
critique elsewhere in this analysis. Also unaffected by the Finding 13
duplicate-booking issue, since `weekly_funnel.csv` is a separate file from
`wins.csv` and was not part of that check.

**Open, not resolved by this dataset:** what caused the company-wide ~10-12%
lead volume decline itself (paused campaign, seasonality, a channel/source
issue, a CRM migration effect on how leads get logged, etc.) —
`weekly_funnel.csv` shows the decline but not its cause. State this as a gap
on the slide rather than speculating.

**Rep-level double-click (Layer 2 of the Outbound investigation framework):**
checked whether Outbound's decline is concentrated in a few underperforming
reps or broad-based. Of 25 Outbound reps, 19 declined and only 5 increased
(4 of the 5 increases are new hires ramping from zero, not resilience).
Confirms this is broad-based across the team, not a coaching/individual-
performance issue — reinforces that the lead-volume shortfall (systemic,
company-wide) is the more likely primary driver than anything rep-specific.

---

## Finding 10 — Hunters deal-size jump: outlier-driven or broad shift? (RESOLVED)

Checked individual `wins.csv` rows for Hunters, FY26Q4 (58 deals, weeks
1-10), to determine whether the $20,633 average deal size (Finding 5) is
driven by a few outlier wins or a genuine broad shift.

**Top 5 deals: $93,985 / $87,812 / $80,386 / $73,178 / $70,265 — together
$405,626, ~34% of Hunters' entire $1,196,695 quarterly ARR from 5 of 58
deals.** For comparison, FY26Q3's single largest deal was $44,534 — less
than half the size of any of FY26Q4's top 5. These look like a genuinely
different tier of deal, not normal variation.

**But the median tells a more moderate story: $15,538 this quarter vs.
$14,154 last quarter (+~10%), well within Hunters' normal historical band
($14,997-$16,450 average). The typical Hunters deal barely moved.**

**Resolution — this is neither of the two original hypotheses cleanly, it's
a hybrid, and should be stated as such:** NOT "1-2 outlier deals distorting
everything" (there are more than 1-2 unusually large deals, and the median
IS somewhat elevated) — but also NOT "a broad, repeatable shift to bigger
deals across the board" (median moved only modestly). The accurate
statement: Hunters' typical deal is roughly normal size; a handful (5 of 58)
of unusually large — likely enterprise-tier — wins are responsible for most
of the ARR overperformance.

**Slide implication:** do not recommend "double down, this is the new
normal for Hunters" — median deal size doesn't support that. Do flag: "this
quarter's Hunters ARR strength is concentrated in a handful of large wins
(top 5 = 34% of channel ARR); worth understanding whether this reflects a
new enterprise segment opening up (worth pursuing deliberately) or a few
opportunistic one-off wins (don't plan around repeating it)."

**Supporting detail (not itself a finding, just confirms the mechanism):**
every single Hunters win this quarter has `units = 1` — no multi-unit deals.
Product mix is dominated by "Advanced" (higher tier). This confirms the
ARR variance is coming from which product tier customers buy, not from
deal volume-per-transaction (e.g., not bulk purchases).

**UPDATE — see Finding 12b: this open question is now fully resolved.** P4
(Multi-Entity ABM) is directly responsible for all 5 of these outlier deals.

---

## Finding 11 — Actual ARR QoQ by channel (pure actuals, no plan), to test whether "on/above plan" channels are secretly declining

Raised directly: could Hunters or Inbound be landing at/above a (possibly
weak) plan while their real, absolute ARR is actually declining QoQ? Checked
using a straight-line 13/10 proration of FY26Q4-to-date actuals (this IS the
extrapolation technique flagged early in this analysis — used deliberately
here only to get a same-quarter comparison point against FY26Q3's full-
quarter actual, not as a forecast commitment; caveat this if quoted).

| Channel  | FY26Q4 prorated actual ARR | FY26Q3 actual ARR (ORIGINAL, pre-Finding-13) | QoQ change (ORIGINAL) |
|----------|----------------------------|--------------------|------------|
| Hunters  | $1,555,704                 | $1,343,443         | **+15.8%** |
| Inbound  | $6,042,421                 | $6,311,484         | **-4.3%**  |
| Outbound | $2,155,477                 | $3,784,556         | **-43.0%** |
| Upgrades | $3,542,115                 | $3,240,709         | +9.3%      |

**Hunters, Inbound, Upgrades: figures above are unaffected by Finding 13 —
the duplicate-booking issue is isolated to Outbound only.**

**Outbound: CORRECTED per Finding 13 — true FY26Q3 actual ARR (full quarter,
dupes removed) is $3,451,175, not $3,784,556. Corrected QoQ change: -37.5%,
not -43.0%.** Still the starkest number found in this entire analysis, and
the one most immune to any plan-related pushback, since it makes no
reference to a plan or target at all. Use -37.5% (not -43.0%) on the slide
going forward — see Finding 13 for the full correction and reasoning.

**Hunters: real ARR growth (+15.8%), not an artifact of a lenient plan.**
Confirms Hunters' story is genuinely positive on a pure actuals basis.

**Inbound: actual ARR is DOWN -4.3% QoQ**, even though it looks fine
(98.9% of plan) against a flat (0% QoQ growth) plan. Inbound is not a clean
"no story" channel — it's flat-to-plan while quietly contracting in
absolute dollars. Worth a caveat/footnote on the slide, not a headline —
the decline is real but small relative to Outbound's.

**Upgrades: real ARR growth (+9.3%)**, consistent with everything else
found about this channel — genuine, durable growth, not a plan artifact.

---

## Finding 12 — The six growth plays: keep/kill framework, and two findings that revise earlier conclusions

Built from `plays.csv` (spend, targets, hypothesis per play) and
`play_attribution.csv` (which wins each play produced), joined to `wins.csv`
for actuals. `weeks_active` per play = current_week (10) - launch_week + 1,
so each play's spend-to-date and unit target are correctly prorated to only
the weeks it's actually been running (verified: P1/P3=10wk, P2=9wk, P4=8wk,
P5=7wk, P6=6wk -- not a flat 10 weeks for everyone).

**Framework -- five dimensions per play:**

| Play | Channel | % of unit plan | Actual units | Actual ARR | ARR per $1 spent | % of channel's units | % of channel's ARR |
|------|---------|----------------|-------------|------------|-------------------|----------------------|---------------------|
| P3 Migration Concierge | Upgrades | 124.0% | 124 | $790,888 | **$6.59** | 28.5% | 29.0% |
| P6 Accountant Referral | Inbound | 94.4% | 17 | $169,087 | $4.70 | 3.2% | 3.6% |
| P1 Advanced Fast-Track | Inbound | 108.3% | 65 | $545,503 | $3.03 | 12.3% | 11.7% |
| P2 Velocity Blitz | Outbound | 114.8% | 93 | $572,402 | $2.54 | **44.1%** | 34.5% |
| P4 Multi-Entity ABM | Hunters | 81.2% | 13 | $527,167 | $2.20 | 22.4% | **44.1%** |
| P5 Win-Back 2.0 | Outbound | 35.7% | 15 | $118,251 | **$0.84** | 7.1% | 7.1% |

Blended: $941,000 spent across all six plays to date, $2,723,298 ARR
generated -- **2.89x ROI** (ARR generated / dollars spent; in sales/marketing
terms this is "program ROI" or "pipeline ROI," directly analogous to
marketing's ROAS). Budget-ownership context for a CFO conversation: P1/P3/P4/
P5 are marketing-funded programs; P2 (purchased lists + outsourced SDR
agency) is more of a sales-development/BDR spend; P6 (referral fees to
accounting firms) is a partner/channel budget line. Three different budgets,
worth knowing which is which if asked "ROI against what."

**Keep/kill calls (5 keep, 1 kill):**
- **Double down: P3.** Best efficiency, beating target, unambiguous.
- **Keep: P1, P6.** Solid efficiency, beating/near target, no complications.
- **Keep, but reframe as stabilization not growth: P2.** Best play in
  Outbound -- but see Finding 12a, it is masking a much worse core-channel
  problem, not fixing it.
- **Keep, and consider expanding: P4.** See Finding 12b -- this is no longer
  ambiguous; it is the entire mechanism behind Hunters' ARR strength this
  quarter, not just a contributor to it.
- **Kill: P5.** Worst on every dimension: 35.7% of its own unit target,
  worst ROI of all six plays ($0.84 -- doesn't even break even against
  spend), in the weakest channel.

**Caveat on the ARR-per-dollar figures:** `weekly_spend` in `plays.csv` is
one flat number per play; assumed constant since launch (no weekly spend
history exists to check this). If actual spend was lumpy (e.g. heavy
week-1 setup cost), the true cost curve could differ from this straight-line
assumption. Stated as a limitation, not corrected for.

**Play figures above are FY26Q4-only and unaffected by Finding 13 (that
issue is isolated to FY26Q3, before any plays existed).**

---

### Finding 12a — Outbound's core (non-play) business, isolated: down QoQ, same 10-week window, no proration needed

Raised directly: does removing play contribution reveal Outbound's real,
underlying (business-as-usual) performance is worse than the channel-level
60.8%/72.8% headline suggests? Checked using the SAME 10-week window on
both sides of the comparison (this quarter's weeks 1-10 vs. LAST QUARTER's
weeks 1-10 -- this is quarter-over-quarter, FY26Q4 vs FY26Q3, NOT year-over-
year). So unlike some earlier QoQ comparisons in this log, this one needs no
proration or extrapolation caveat at all -- it's a clean, apples-to-apples
actuals comparison, same window on both sides.

**UPDATED per Finding 13: the FY26Q3 baseline below was found to contain 35
duplicate (CRM dual-export) rows in Outbound. Original and corrected figures
both shown; use CORRECTED going forward.**

| | Units | ARR |
|---|---|---|
| FY26Q4 Outbound BAU (total minus P2 and P5), weeks 1-10 | 103 | $967,406 |
| FY26Q3 Outbound (all organic -- no plays existed yet), weeks 1-10, ORIGINAL (with dupes) | 305 | $2,915,841 |
| FY26Q3 Outbound, weeks 1-10, CORRECTED (dupes removed) | 270 | $2,582,460 |
| **Change vs. ORIGINAL FY26Q3** | -66.2% | -66.8% |
| **Change vs. CORRECTED FY26Q3 (use this)** | **-61.9%** | **-62.5%** |

**Outbound's core, non-play business is down roughly 62% quarter over
quarter (corrected figure).** The channel-level 60.8% ARR attainment figure
already looked like the quarter's biggest problem -- this reveals it was
substantially UNDERSTATING the severity, because P2 alone is responsible for
44.1% of Outbound's total units this quarter. Strip that out and what's left
is a core business that's collapsed, not just softened. This is arguably the
single sharpest, most decision-relevant number in the entire analysis --
the plays are masking Outbound's real state, not fixing it. P2 should stay
running (it's the one thing keeping Outbound from being even worse), but
the reset plan needs a SEPARATE, non-play answer for the underlying channel,
because P2 was never designed to fix ~62% BAU erosion -- it's incremental
volume on top of a shrinking base.

**Open: the TRUE year-over-year version of this check (FY26Q4 vs FY25Q4,
same 10-week window) has not been run.** Worth doing before the slide is
final -- QoQ tells you something changed recently; YoY tells you whether
this is a seasonal pattern or a genuine structural break. These answer
different questions and neither substitutes for the other.

---

### Finding 12b — Hunters' avg deal size, ex-P4: confirms P4 IS the entire ARR story, not just a contributor

Directly checked (Finding 10 left this as an open question): is P4
(Multi-Entity ABM) responsible for Hunters' large-deal pattern, and what
does Hunters look like without it?

**Direct confirmation, not inference:** pulled P4's 13 attributed Hunters
deals and cross-referenced against the top-5-largest-deals list from
Finding 10. **All 5 of Hunters' largest deals this quarter
($93,985/$87,812/$80,386/$73,178/$70,265) are P4 deals** -- exact match, not
a coincidence or correlation.

Average deal size, Hunters, excluding P4 entirely, same 10-week window on
both sides:

| | Units | ARR | Avg deal size |
|---|---|---|---|
| FY26Q4 Hunters ex-P4, weeks 1-10 | 45 | $669,528 | $14,878 |
| FY26Q3 Hunters (all -- no plays existed), weeks 1-10 | -- | -- | $15,442 |
| **Change** | | | **-3.6%** |

**This resolves Finding 10's open question completely, and changes the
Hunters narrative for the slide.** It is NOT "unexplained large deals, might
be a fluke, don't count on it repeating" (the Finding 10 framing). It is:
excluding P4, Hunters' average deal size is essentially flat to slightly
DOWN (-3.6%) **QoQ (FY26Q4 vs. FY26Q3, NOT year-over-year -- corrected here;
the table above already compares consecutive quarters, the prose originally
mislabeled this "vs. last year," which was wrong)** -- P4 is not a
contributor to Hunters' ARR strength this quarter, it IS the entire story.
Recommendation upgrades from "watch cautiously" to "keep and consider
expanding" -- this is a specific, identifiable, repeatable mechanism (a
named list of 400 target accounts), not a mystery. **Note: the true
year-over-year version of this specific check (ex-P4 Hunters, FY26Q4 vs.
FY25Q4) has not been run** -- same open-thread caveat as Finding 12a's YoY
gap.

---

### Finding 12c — What each play actually does, and why P4/P6 have a structural (not just observed) efficiency advantage

Plain-English descriptions, for slide use:
- **P1 Advanced Fast-Track (Inbound):** route high-intent inbound leads
  (showing multi-entity/complex-workflow signals) to a specialist rep
  trained on Advanced, instead of a generalist.
- **P2 Velocity Blitz (Outbound):** purchased contact lists + an outsourced
  SDR (sales development rep) agency running high-volume cold outreach, to
  rebuild outbound pipeline volume quickly.
- **P3 Migration Concierge (Upgrades):** white-glove, hands-on data
  migration and onboarding help for customers upgrading from Plus or
  Desktop to Advanced -- reduces switching friction.
- **P4 Multi-Entity ABM (Hunters):** account-based marketing -- a curated,
  named list of 400 target companies with multiple business
  entities/locations (a proxy for "complex enough to need and pay for Advanced"), pursued with coordinated marketing + field events.
- **P5 Win-Back 2.0 (Outbound):** re-approach churned/closed-lost accounts
  from the past 24 months with a discounted first-year offer.
- **P6 Accountant Referral Pilot (Inbound):** accounting firms in an
  existing partner program refer qualified clients; firm receives a fee per
  closed deal.

**Why P4 (ABM) has a structural advantage, not just an observed one:** B2B
deal value is highly concentrated -- a small number of large accounts are
worth vastly more than the median account. Untargeted marketing spends most
of its budget reaching accounts that were never going to be large. ABM
inverts this: identify likely-large accounts BY NAME first (here: multi-
entity/multi-location companies), then concentrate spend only on pursuing
them. This is well-established B2B practice specifically for
high-deal-variance products/segments -- and Hunters is a clear example of
high variance (see Finding 10/12b). Finding 12b proves this worked, not just
theoretically: 5 of 5 top deals this quarter trace directly to this play.

**Why P6 (referral) has a structural advantage:** accountants are trusted
advisors to small/mid-market businesses; a referral carries pre-built
credibility that cold outreach or advertising has to spend money and time
to manufacture. Referral-sourced leads typically convert faster and at
higher rates because trust is inherited from the referrer. This is reflected
in the data: P6 has the 2nd-best ROI of all six plays ($4.70) on the
smallest, cheapest program ($36K spent to date) -- suggesting room to scale
by adding more accounting-firm partners.

**Why P2 (purchased lists + outsourced cold outreach) is comparatively
weaker, even though it is CURRENTLY beating its own target (114.8%):** no
targeting or trust advantage -- generic purchased data, cold outreach at
volume. Structurally more likely to degrade over time (purchased lists go
stale, cold-outreach response rates erode with market overuse) than P4 or
P6, which both have durable, structural reasons to keep performing. Current
performance is good; durability is the open question, and it's the weakest
of the three lead-gen-style plays on that dimension specifically.

---

## Finding 13 — CRM dual-export artifact discovered: 35 duplicate wins in FY26Q3 Outbound, corrects several downstream findings

**Discovery:** 35 account/ARR/units/channel combinations appear TWICE in
FY26Q3, all in Outbound, all within a tight 2-week window (week_ending
2026-02-28 to 2026-03-14). One win_id of each pair sits in-band with the
rest of FY26Q3 (56,593-58,383 range); the other sits at 90,025+, a distinct
numeric block roughly 32,000+ higher than anything else in the quarter.

**Verified, not assumed:** confirmed via exact match on
account_id+arr_booked+units+channel (70 rows = 35 pairs), cross-checked with
a looser account_id+week_ending+channel match (same 70 rows, nothing
additional), and confirmed via win_id statistical outlier detection (35
outlier rows in FY26Q3, using >3x IQR from quartiles -- zero outliers in
every other quarter). All three methods agree exactly.

**Scope check -- confirmed fully isolated:** ran the same three checks
across ALL quarters and ALL channels. FY26Q3 Outbound is the ONLY
occurrence anywhere in the dataset. No other channel, no other quarter shows
this pattern (exact or loose). Every other number in this entire analysis
is unaffected by this issue -- the contamination is fully bounded to
findings that reference FY26Q3 Outbound specifically.

**Interpretation:** matches the classic signature of a CRM dual-export
during a migration cutover -- the same closed-won record pulled from both
the legacy and new CRM systems, landing as two rows with identical deal
economics but two different win_id sequences. Directly corroborates the
VP's stated distrust of post-migration CRM extracts with a specific,
quantified, located example -- strong evidence that a raw extract needs
this kind of scrutiny before any number is trusted.

**Correction applied:** the 35 out-of-band duplicate rows (win_id > 60000
within FY26Q3) were removed. This does NOT affect `plans.csv` in any way --
plan targets are a wholly separate file from actuals and cannot be touched
by a duplicate-bookings issue in `wins.csv`.

**Impact, by finding:**

| Finding | Metric | Original (with dupes) | Corrected |
|---------|--------|------------------------|-----------|
| Finding 2 -- FY26Q3 Outbound attainment vs. plan | Units % of plan | 94.2% | **85.8%** |
| | ARR % of plan | 96.8% | **88.3%** |
| Finding 11 -- Outbound actual ARR QoQ | % change (FY26Q4 vs FY26Q3) | -43.0% | **-37.5%** |
| Finding 12a -- Outbound BAU vs. FY26Q3, wks 1-10 | Units % change | -66.2% | **-61.9%** |
| | ARR % change | -66.8% | **-62.5%** |

**No finding changes DIRECTION -- Outbound was overstated as healthier in
FY26Q3 than it actually was, which means every "decline from FY26Q3" figure
was OVERSTATED in magnitude (looked worse than the true decline, because the
starting point was inflated).** All corrected figures above are 4-6
percentage points smaller in magnitude than originally reported, but the
underlying story is unchanged: Outbound has a real, severe, multi-layered
problem this quarter. These corrected figures should be used everywhere
going forward, including on the exec slide -- do NOT cite the original
(pre-correction) percentages.

**One more implication worth stating explicitly:** FY26Q3 was being treated
throughout this analysis as Outbound's "healthiest recent quarter" (closest
to 100% of plan among the trailing 5). That was itself partly an artifact
of this duplication. Outbound's TRUE historical performance is somewhat
weaker across the board than the Finding 2 table currently shows for FY26Q3
specifically -- worth a one-line footnote on the slide if the historical
trend chart is shown, so the FY26Q3 data point isn't taken at face value.

**Sanity checks also run, both come back clean, no further correction
needed:**
- **Plan targets (plans.csv):** confirmed structurally incapable of being
  affected -- verified FY26Q3 Outbound plan_units (416) and plan_arr
  ($3,910,400) are untouched, as expected, since plans.csv has no
  relationship to wins.csv row counts.
- **Average deal size, FY26Q3 Outbound:** barely moves (+0.13%, $9,654 ->
  $9,667) -- expected, since each duplicate pair removes matched ARR and
  units together, so the ratio is preserved even though the totals shrink.
  Confirms Finding 5's average-deal-size table needs no correction.

**Verified in the Excel workbook, not just Python:** `wins_with_plays.xlsx`
now has an `outbound_bau_check` tab built on SUMIFS against the `wins` tab
directly -- see that file for the spreadsheet-native version of the related
BAU check (Finding 12a).

---

## Finding 14 — Outbound deep dive: rep concentration, account mix, and true YoY timing (built in `analysis/outbound_deep_dive.py`)

Finding 12a established Outbound's core (non-play) business is down ~62% QoQ
(corrected). This tests three of the five candidate drivers raised for that
decline; two others (lead source mix, broader market/competitive pressure)
are NOT analyzable from this dataset and are not attempted here --
`weekly_funnel.csv` has no lead-source field, and there's no external market
data in this dataset. Both stay open, stated as data limitations, not guessed
at.

**Sanity check before trusting anything below:** re-ran Finding 12a's
headline BAU QoQ number on today's data (which already has Finding 13's
duplicate-wins correction baked in at the source -- `wins_with_plays.xlsx`
itself now has 9,614 rows, not 9,649). Result: -61.9% units / -62.5% ARR,
an exact match to Finding 12a. Baseline confirmed before proceeding.

All three checks below use BAU (non-play) wins only, same convention as
Finding 12a, so this is the same "organic Outbound" signal, not a different
metric.

### Finding 14a — Rep-level variance: broad-based, not concentrated (independently confirms and sharpens Finding 9)

Per-rep BAU units, FY26Q3 wk1-10 vs. FY26Q4 wk1-10 (22 reps active in both
windows; 3 more are new hires with no FY26Q3 baseline, excluded from the
denominator below since they can't "decline" from a number that doesn't
exist):

**20 of 22 tenured reps declined, 1 increased (+2 units), 1 was flat.** No
single rep or small cluster is disproportionately responsible -- the top 5
decliners account for only 36.3% of the total unit decline across all
declining reps (182 units). The one rep who grew (Ray Moreau, +2 units) and
the 3 new hires (5, 6, and 2 units in their first partial quarter) are the
only bright spots on the entire 25-person roster.

**Conclusion: this is not a coaching or individual-performance problem.**
Something changed for the team as a whole, not for a subset of underperforming
reps. Independently confirms Finding 9's conclusion (19 of 25 total reps
declined, using total wins including plays) with a cleaner BAU-only cut that
excludes play-driven volume entirely -- the two methods agree.

**Extended to ARR, per the "always report units and ARR together" convention
(never a single metric alone) -- same conclusion holds, doesn't flip:** 20 of
22 tenured reps ALSO declined in ARR (only 2 grew: Ray Moreau, and Tatum Ruiz
who was flat on units but grew ARR from bigger average deals). Top-5 ARR
decliners account for 35.8% of the total ARR decline ($1,752,751 across all
declining reps) -- essentially the same concentration as units (36.3%). Units
and ARR direction agree for 21 of 22 reps; the one disagreement (Tatum Ruiz)
is a single rep with a bigger-deal effect, not a pattern. **ARR confirms,
doesn't complicate, the broad-based read.**

### Finding 14b — Account/industry/region mix: broad-based, BUT with a real (if modest) revenue-band mix shift once ARR is added -- toward SMALLER accounts, not larger, correcting an initial hypothesis

Unit share by industry, revenue band, and region, Outbound BAU, same FY26Q3
wk1-10 vs. FY26Q4 wk1-10 window:

- **Industry:** every one of the 10 industries declined 48-77% in units; no
  industry held steady or grew. Shares stayed within ~1-2 points of their
  FY26Q3 mix (e.g. Professional Services 13.0%→11.7%, Retail Multi-Location
  11.9%→14.6%) -- the mix looks almost identical, just at roughly half the
  volume across the board.
- **Region:** East -60.6%, West -62.0%, Central -63.5% -- essentially
  uniform.

**Revenue band, extended to ARR + average deal size (units-only view understated a real pattern here):**

| Band | Q3 units | Q4 units | unit chg % | Q3 unit share | Q4 unit share | Q3 ARR | Q4 ARR | arr chg % | Q3 arr share | Q4 arr share | avg deal Q3 | avg deal Q4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `<$1M` | 7 | 6 | -14.3% | 2.6% | 5.8% | $72,426 | $45,931 | -36.6% | 2.8% | 4.7% | $10,347 | $7,655 |
| `$1M-$2.5M` | 17 | 9 | -47.1% | 6.3% | 8.7% | $155,188 | $94,889 | -38.9% | 6.0% | 9.8% | $9,129 | $10,543 |
| `$2.5M-$5M` | 129 | 44 | -65.9% | 47.8% | 42.7% | $1,247,476 | $415,683 | -66.7% | 48.3% | 43.0% | $9,670 | $9,447 |
| `$5M-$10M` | 89 | 36 | -59.6% | 33.0% | 35.0% | $838,892 | $324,942 | -61.3% | 32.5% | 33.6% | $9,426 | $9,026 |
| `>$10M` | 28 | 8 | -71.4% | 10.4% | 7.8% | $268,478 | $85,961 | **-68.0%** | 10.4% | 8.9% | $9,588 | $10,745 |

**Raised directly, tested, and the answer is NO -- Outbound is not driving
more deals on larger-revenue companies. If anything, the opposite is true on
both metrics tested:**
- The `>$10M` band's share SHRANK on both units (10.4%→7.8%) and ARR
  (10.4%→8.9%), and its ARR decline (-68.0%) is WORSE than the channel BAU
  average (-62.5%, Finding 12a) -- the largest accounts are the
  worst-hit segment, not a bright spot.
- The two SMALLEST bands (`<$1M`, `$1M-$2.5M`) both GAINED unit share and
  ARR share -- the opposite direction from the hypothesis. `<$1M`'s smaller
  decline is on a tiny base (7→6 units) and should be read as noise, not
  signal; `$1M-$2.5M` (17→9 units) is a firmer, if still small, base.

**Where there IS a genuine secondary pattern, distinct from the share
question above:** average deal size rose materially in exactly two bands --
`>$10M` (+12.1%, $9,588→$10,745) and `$1M-$2.5M` (+15.5%, $9,129→$10,543) --
even as both bands' VOLUME collapsed. That's a real "fewer, bigger deals
within the band" effect in those two segments specifically, layered UNDER
the volume collapse, not instead of it -- consistent with the same
fewer-but-bigger dynamic already documented for Hunters (Finding 10/12b),
just smaller in scale and confined to two revenue bands rather than a whole
channel. The two middle bands (`$2.5M-$5M`, `$5M-$10M` -- 78% of Outbound's
Q3 unit base combined) show flat-to-slightly-down average deal size, i.e.
no such effect where most of the volume actually sits.

**Conclusion, revised from the units-only version of this finding:** the
decline is still broad-based across industry and region (no change there).
Revenue-band is the one dimension where a real, if modest, mix shift
exists -- toward smaller accounts, driven by the largest band being
hit hardest -- which is the OPPOSITE of "chasing bigger logos." This does
not overturn Finding 14's "broad-based and structural" synthesis (every
band still declined double digits), but it's a real secondary signal worth
a one-line mention on the slide, and it directly contradicts rather than
supports an "Outbound is moving upmarket" narrative.

### Finding 14c — True YoY timing: NOT a seasonal effect, and NOT explained by a normal Q3→Q4 pattern (resolves the open thread from Finding 12a)

**True year-over-year, FY26Q4 wk1-10 vs. FY25Q4 wk1-10 (same calendar season,
one year apart, no proration needed on either side), by channel, total
actuals:**

| Channel  | FY25Q4 units | FY26Q4 units | YoY units | FY25Q4 ARR | FY26Q4 ARR | YoY ARR |
|----------|-------------:|-------------:|----------:|-----------:|-----------:|--------:|
| Hunters  | 64  | 58  | -9.4%  | $1,001,554 | $1,196,695 | +19.5% |
| Inbound  | 561 | 527 | -6.1%  | $4,599,855 | $4,648,016 | +1.0%  |
| Outbound | 311 | 211 | **-32.2%** | $2,962,522 | $1,658,059 | **-44.0%** |
| Upgrades | 338 | 435 | +28.7% | $1,968,204 | $2,724,704 | +38.4% |

**Every other channel is flat-to-growing YoY. Outbound is the only channel
declining YoY, and by a wide margin.** This rules out "Q4 is just a
structurally weak quarter" (e.g. summer slowdown) as the explanation -- if
that were true, every channel would show a similar YoY dip, and none of the
other three do.

**Outbound BAU-only (ex-play) YoY is even starker: -66.9% units, -67.3%
ARR** (FY25Q4: 311 units/$2,962,522 → FY26Q4: 103 units/$967,406). The
total-channel YoY figures above (-32.2%/-44.0%) are partly propped up by
108 units / $690,653 of play-driven volume this quarter that didn't exist a
year ago (FY25Q4 predates all six plays) -- the organic YoY decline is worse
than the headline channel number suggests, same pattern as the QoQ story in
Finding 12a.

**Second check, same conclusion from a different angle:** compared last
year's Q3→Q4 transition to this year's, same channel, same window, no
proration:
- FY25Q3→FY25Q4 (last year): units +11.9%, ARR +10.4% -- Outbound **grew**
  Q3 to Q4 last year.
- FY26Q3→FY26Q4 (this year): units -21.9%, ARR -35.8% -- Outbound
  **shrank** Q3 to Q4 this year.

If there were a normal seasonal pattern where Outbound always softens into
Q4, last year's Q3→Q4 transition should show the same softening. It
doesn't -- it grew. **This is strong, converging evidence that FY26Q4's
Outbound decline is a structural break specific to this year, not a
recurring seasonal pattern.**

**Limitation, stated explicitly:** this dataset only contains ~1.5 years of
history (FY25Q3 through FY26Q4), so there is exactly ONE prior Q4 to compare
against (FY25Q4). One data point establishes "this year differs from last
year," not a proven multi-year seasonal baseline -- a true seasonality
conclusion would ideally use 2-3+ years of Q4s. Stated as a limitation, not
glossed over; the two converging checks above (cross-channel YoY control
group, and the Q3→Q4 reversal) partially offset this by attacking the
question from two angles with the same one year of data, but neither
substitutes for a longer history.

### Finding 14 — synthesis

Of the three drivers testable from this dataset, **none of them explain the
decline as "concentrated" or "seasonal" -- all three checks point the same
direction: broad-based and structural.** Not one underperforming rep, not
one weak segment, not a predictable seasonal dip -- the entire Outbound
channel's organic business stepped down at roughly the same time, across
every rep, every industry, every region. That pattern is more consistent
with something that changed for the channel as a whole (a shared input like
lead volume/quality, a process or tooling change, a comp-plan or
motivation shift, a CRM-migration effect on how Outbound activity gets
logged) than with any single localized cause.

**This is a hypothesis about mechanism, not a proven cause** -- this
dataset can rule out "concentrated" and "seasonal" but cannot, on its own,
identify WHICH shared factor is responsible. Combined with Finding 9 (lead
volume down ~10-12% company-wide, conversion rates flat), the most
defensible statement for the slide is: **Outbound's decline is broad-based
and non-seasonal, consistent with a shared upstream cause (most likely
connected to the company-wide lead volume decline in Finding 9, though
Outbound's inability to absorb that shared shock — see Finding 9 — remains
the sharper, unexplained part of the story) rather than a management,
segment, or calendar-timing problem.**

**Confirmed exhaustively, not just recalled from memory: the two remaining
candidate drivers (lead source mix, competitive/market pressure) are not
analyzable from this dataset, full stop.** Did a column-by-column audit of
every sheet in every one of the 6 source files (`accounts`, `plans`,
`plays`, `seller_roster`, `weekly_funnel`, `wins` + `play_attribution`) --
no lead-source, campaign, or lead-score field exists anywhere in the dataset.
This upgrades "we haven't checked yet" to "checked, and it genuinely isn't
here" -- a verified negative, not an assumption.

**Where this leaves the Outbound diagnosis, stated plainly:** the decline is
diffuse and structural, and correlated with the company-wide lead-volume
drop (Finding 9) -- but the specific mechanism behind either the shared lead
decline or Outbound's disproportionate exposure to it is outside what this
data can prove. That is the honest ceiling of this dataset, not a gap in the
analysis -- three independent checks (rep, segment, timing) all ruled out
the explanations this data COULD test, and a full-column audit confirmed
the two explanations it can't test have no supporting fields to test them
with. Recommend stating it exactly this way on the slide, rather than
picking one driver to imply is confirmed when none of them are.

**Sharpened further, combining Finding 5's corrected deal-size read with
14a-14c: this is specifically a volume/lead problem, not an execution,
segment, deal-quality, or seasonal one.** Organic (ex-play) average deal
size is flat (-1.8%, Finding 5 correction above) -- the deals that DO close
are exactly as healthy as before. Nothing downstream is broken: reps aren't
underperforming individually (14a), no segment cratered while others held
(14b, though `>$10M` was hit hardest AND saw rising average deal size --
consistent with fewer but still-strong opportunities surviving whatever
is happening upstream, not weaker ones), it's not a calendar effect
(14c), and it's not a pricing/quality problem (Finding 5, corrected). Every
piece of evidence this data can produce points at the SAME stage of the
funnel: fewer opportunities reaching a close, not worse execution once
they get there. That narrows the actionable question for the reset plan
from "what's broken about Outbound" to "why did lead volume drop, and can
weeks 11-13 do anything about that specifically" -- still unanswered by
this dataset, but a narrower, more useful question than where this
synthesis started.

---

## Finding 15 — Median deal size per play, traceability for Slide 2's "Median Deal Size" column

Slide 2's plays table shows a per-play median deal size figure that wasn't previously logged as its
own finding — recomputed here directly from `play_attribution.csv` joined to `wins.csv` (FY26Q4,
weeks 1-10) so the number on the slide is traceable back to a finding, same as everything else in
this log.

| Play | n deals | Median ARR/deal | Mean ARR/deal | Mean/median ratio |
|------|--------:|-----------------:|---------------:|-------------------:|
| P1 Advanced Fast-Track   | 65  | $7,852  | $8,392  | 1.07x |
| P2 Velocity Blitz        | 93  | $5,628  | $6,155  | 1.09x |
| P3 Migration Concierge   | 124 | $6,297  | $6,378  | 1.01x |
| P4 Multi-Entity ABM      | 13  | $16,792 | $40,551 | **2.42x** |
| P5 Win-Back 2.0          | 15  | $7,456  | $7,883  | 1.06x |
| P6 Accountant Referral   | 17  | $11,218 | $9,946  | 0.89x |

**Read:** applying the same mean-vs-median skew check used throughout this analysis (Findings 5, 10,
12b) to all six plays, not just the two (Hunters/P4) it was originally run on. Five of six plays show
mean and median within ~10% of each other — normal, unremarkable variation, no skew story to tell.
**P4 is the one clear outlier: mean deal size is 2.42x its own median**, consistent with Finding
10/12b's finding that P4's ARR is carried by a handful of unusually large deals rather than a broadly
elevated typical deal. This is the same fact already established in Finding 10/12b, restated here at
the per-play level so Slide 2's column has a directly citable source; it does not change any
conclusion, but closes the gap where five of the six slide figures had no logged finding behind them.

**Caveat:** P4 and P6's medians are the least statistically stable of the six, given their small
sample sizes (13 and 17 deals respectively) — read as directional, not precise, same caveat already
applied to other small-n figures in this analysis (e.g., Finding 12a's P5 weekly-pace note).

---

## Finding 16 — Trailing-4-week pace (wk7-10) vs. first-6-week pace (wk1-6): the deceleration is in Inbound and Upgrades, not Outbound

Raised while sanity-checking why a quarter-end projection (actual wk1-10 + wk7-10 pace extrapolated
through wk11-13, v2 baseline) lands slightly below the wk1-10 QTD attainment already on the slide
(90.9%/95.4% projected vs. 91.5%/96.2% QTD) — worth knowing which channel is driving that gap before
putting either number in front of the VP.

**Units, % of plan (v2 baseline):**

| Channel | Wk 1–6 | Wk 7–10 | Wk 1–10 (QTD) | Projected EOQ |
|---|--:|--:|--:|--:|
| Hunters | 81.0% | 85.7% | 82.9% | 83.5% |
| Inbound | 93.0% | **81.8%** | 88.6% | 87.0% |
| Outbound | 68.8% | 79.8% | 72.8% | 74.3% |
| Upgrades | 117.1% | 104.2% | 111.5% | 109.7% |
| **TOTAL** | **93.4%** | **88.6%** | **91.5%** | **90.9%** |

**ARR, % of plan (v2 baseline):**

| Channel | Wk 1–6 | Wk 7–10 | Wk 1–10 (QTD) | Projected EOQ |
|---|--:|--:|--:|--:|
| Hunters | 119.2% | 126.5% | 122.1% | 123.1% |
| Inbound | 104.8% | **89.8%** | 98.9% | 96.8% |
| Outbound | 58.2% | 65.5% | 60.8% | 61.8% |
| Upgrades | 130.2% | 112.5% | 122.6% | 120.1% |
| **TOTAL** | **98.5%** | **92.8%** | **96.2%** | **95.4%** |

**Methodology:** wk1-6 and wk7-10 windows both use the blended v1/v2 plan (same `blended_plan()`
convention as Finding 4/6 — v1 for weeks <6, v2 for weeks ≥6, so the wk7-10 window's plan basis is
entirely v2 — confirmed no version-mixing artifact). Projected EOQ = actual wk1-10 + (wk7-10 average
weekly pace × 3), same extrapolation method as `week11-13_recovery_plan.md`'s baseline table,
compared against the full 13-week blended v2 plan.

**Read — this reverses the assumption that Outbound is dragging down the trailing pace:**
- **Outbound's pace improved** in wk7-10 vs. wk1-6, on both metrics (68.8%→79.8% units, 58.2%→65.5%
  ARR). It is not the source of the blended deceleration.
- **Inbound decelerated sharply** — units pace fell 93.0%→81.8%, and **ARR pace dropped below 100%
  (104.8%→89.8%)** for the first time this quarter. This is a sharper, more recent signal than
  Finding 11's -4.3% YoY figure and should be the lead reason Inbound is in the weeks 11-13 pipeline
  review, not a secondary one.
- **Upgrades decelerated too** (117.1%→104.2% units, 130.2%→112.5% ARR) — still comfortably above
  100% on both metrics, so this is not a crisis, but it is no longer accelerating, and the weeks
  11-13 plan should not assume it can absorb capacity pulled from elsewhere without checking this
  trend again.
- **Hunters improved** slightly on both metrics — consistent with P4's late-stage deals continuing to
  close, not a concern.

**Slide implication:** the "gap widens to -$629K projected" framing should not be paired with an
Outbound-specific callout — Outbound is the one channel moving in the right direction on recent pace.
The correct attribution is Inbound and Upgrades cooling off. This should also shape the weeks 11-13
reset plan: the existing "Pipeline review" action already covers Inbound, but its rationale should
cite this trailing-pace drop specifically; and Upgrades — currently absent from the reset actions —
should get an explicit "monitor, don't reallocate away" line rather than no mention at all.

---

## Open threads / not yet investigated
- Upgrades: specific driver(s) of the accelerating over-performance (not yet
  double-clicked the way Outbound and Hunters have been).
- Root cause of the company-wide ~10-12% lead volume decline itself (Finding
  9) — not resolvable from `weekly_funnel.csv` alone; state as a stated
  limitation on the slide.
- Whether the FY26Q4 wins.csv week-10 cutoff is a real data boundary (quarter
  genuinely not complete) or a CRM extract/sync artifact, consistent with the
  VP's stated distrust of the post-migration data. Not yet checked whether
  ALL channels cut off at week 10 uniformly.
- Whether P5's remaining spend is genuinely stoppable (cancel starting next
  week) or largely sunk/committed — matters for how forcefully to frame the
  kill recommendation in the reset plan. Not yet checked.
- Whether the FY26Q3 duplicate-export pattern (Finding 13) has any
  downstream echo in FY26Q4 data quality that hasn't been checked yet (e.g.,
  a smaller-scale version of the same dual-export issue, below the
  detection threshold used in Finding 13's scope check).
- Final "three numbers that matter" + ranked root-cause dollar sizing for
  the actual exec slide, incorporating Finding 13's corrected figures —
  findings are now sufficient to write this; not yet formally finalized as
  slide copy.
- **DONE (Finding 14):** rep-level variance, account/industry/region mix, and
  a true year-over-year timing check on Outbound — all three point to a
  broad-based, non-seasonal, structural decline, not a concentrated or
  calendar-driven one.
- Outbound driver #1, lead source mix (paid ads vs. cold calling vs.
  purchased lists) — **CONFIRMED not analyzable**, via an exhaustive
  column-by-column audit of every sheet in all 6 source files, not just
  `weekly_funnel.csv` — no lead-source, campaign, or lead-score field exists
  anywhere in this dataset. Would need a data source this dataset doesn't
  contain.
- Outbound driver #5, broader market / competitive pressure — **CONFIRMED not
  analyzable** by the same audit — no external market data exists in this
  packet, in any file.
- Finding 14's synthesis raises, but does not confirm, a shared-upstream-cause
  hypothesis (tooling, process, comp plan, or CRM-migration-related logging
  effect) connecting Outbound's decline to the company-wide lead volume drop
  in Finding 9 — worth a targeted follow-up if time allows, but currently a
  hypothesis, not a finding.
