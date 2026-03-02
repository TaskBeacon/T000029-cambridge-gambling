# Task Logic Audit: Cambridge Gambling Task

## 1. Paradigm Intent

- Task: `cambridge_gambling`.
- Construct: explicit-risk decision making with sequential probability judgment and stake selection.
- Manipulated factors:
- red/blue box ratio (10 boxes total)
- bet option order (`ascending` vs `descending`).
- Primary dependent measures:
- majority-color choice quality
- win rate
- mean bet percentage
- color and bet RTs
- timeout counts
- points trajectory and delay-aversion proxy.

## 2. Block/Trial Workflow

### Block Structure

- Human profile: `2` blocks x `36` trials.
- QA/sim profiles: `1` block x `20` trials.
- Block order context from controller (`ascending`/`descending`) determines displayed bet option order.
- Trial specification from `Controller.build_trial(block_idx)` includes ratio, majority/minority color, token color, and ordered bet options.

### Trial State Machine

1. `fixation`
- Stimulus: `fixation`.
- Trigger: `fixation_onset`.
- Keys: none.

2. `color_choice`
- Stimuli: `trial_prompt`, `score_text`, `ratio_text`, rebuilt `box_token_template` x10, `color_key_hint`.
- Trigger: `choice_onset`.
- Response triggers: `choice_red` / `choice_blue`.
- Timeout trigger: `color_timeout`.

3. `bet_choice` (only if color was chosen)
- Stimuli: `score_text`, `ratio_text`, rebuilt `box_token_template` x10, `bet_prompt`, rebuilt `bet_option_template` x5, `bet_key_hint`.
- Trigger: `bet_onset`.
- Response triggers: `bet_key_1..5`.
- Timeout trigger: `bet_timeout`.
- Timeout policy: auto-select last displayed bet option.

4. `feedback`
- Stimulus branch: `feedback_outcome`, `feedback_auto_bet`, or `feedback_color_timeout`.
- Trigger: `feedback_onset`.

5. `iti`
- Stimulus: `fixation`.
- Trigger: `iti_onset`.

## 3. Condition Semantics

- Runtime condition ID: `gambling`.
- Trial-level semantics:
- `ratio_label`, `red_boxes`, `blue_boxes` define explicit probability context.
- `bet_order` defines stake option presentation order.
- `token_color` defines outcome realization.

## 4. Response and Scoring Rules

- Color-choice mapping: `red_key` vs `blue_key` (default `f`/`j`).
- Bet-choice mapping: `bet_keys` (default `1..5`) to currently displayed ordered percentages.
- Outcome update:
- `bet_amount = round(points_before * bet_percent / 100)`
- win: `+bet_amount`
- loss: `-bet_amount`
- Color timeout: no bet and no points change.
- Bet timeout: auto-bet at last displayed percentage.

## 5. Stimulus Layout Plan

- Color-choice layout:
- trial prompt top (`y=310`), score (`y=265`), ratio (`y=220`), box row at `y=150`, color key hint (`y=80`).

- Bet-choice layout:
- score and ratio retained, box row retained, bet prompt (`y=115`), bet options near lower center (`y=-70`), bet legend (`y=-245`).

- Feedback layout:
- centered multiline outcome text with score delta and updated points.

All participant-facing labels are config-sourced (`task.color_labels`, `task.order_labels`, `stimuli.*`).

## 6. Trigger Plan

| Trigger | Code | Meaning |
|---|---:|---|
| `exp_onset` | 1 | experiment start |
| `exp_end` | 2 | experiment end |
| `block_onset` | 10 | block start |
| `block_end` | 11 | block end |
| `fixation_onset` | 20 | fixation onset |
| `choice_onset` | 30 | color-choice onset |
| `choice_red` | 31 | red response |
| `choice_blue` | 32 | blue response |
| `color_timeout` | 33 | no color response |
| `bet_onset` | 40 | bet-choice onset |
| `bet_key_1` | 41 | first bet key |
| `bet_key_2` | 42 | second bet key |
| `bet_key_3` | 43 | third bet key |
| `bet_key_4` | 44 | fourth bet key |
| `bet_key_5` | 45 | fifth bet key |
| `bet_timeout` | 46 | no bet response |
| `feedback_onset` | 50 | feedback onset |
| `iti_onset` | 60 | ITI onset |

## 7. Architecture Decisions (Auditability)

- `main.py` uses one standardized execution path across `human|qa|sim` with shared initialization and runtime-context handling.
- `src/run_trial.py` removes MID-template remnants and implements CGT-native phases (`color_choice`, `bet_choice`) with explicit timeout branches.
- Bet-choice context exposes `bet_key_map` to simulation responders, enabling deterministic mapping from key to displayed percentage.
- Trial outputs include QA-required fields (`bet_order`, `red_boxes`, `blue_boxes`, `color_response_key`, `color_timed_out`, `bet_percent`, `bet_timed_out`, `won`, `net_change`, `points_after`).

## 8. Inference Log

- Exact fixation/ITI jitter values and response deadlines are implementation-level inferences aligned to practical CGT runtime constraints.
- Auto-bet-on-timeout policy (selecting last displayed option) is an inferred operationalization to preserve full-trial point dynamics in time-limited runs.
- Display geometry for 10 boxes and 5 bet options is an inferred visual arrangement preserving explicit probability and stake semantics.