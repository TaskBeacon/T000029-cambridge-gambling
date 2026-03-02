# Task Logic Audit: Cambridge Gambling Task

## 1. Paradigm Intent

- Task: `cambridge_gambling`
- Primary construct: risk-sensitive decision-making under explicit probabilities.
- Manipulated factors:
  - visible box ratio (`9:1`, `8:2`, `7:3`, `6:4`)
  - majority-color side assignment (red-majority or blue-majority)
  - bet-order context (`ascending`, `descending`) across blocks
- Dependent measures:
  - quality of decision (chose majority color)
  - betting level (% of current points)
  - outcome sensitivity (win/loss points)
  - delay-aversion proxy (`descending_mean_bet - ascending_mean_bet`)
  - color-choice and bet-choice RT
- Key citations:
  - `W2132469266`
  - `W2109668460`
  - `W2097485712`
  - `W2016985323`

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: `2` (human baseline), `1` (QA/sim profiles).
- Trials per block: `36` (human baseline), `20` (QA/sim profiles).
- Block order factor: controller maps block index to `ascending` or `descending` bet order.
- Randomization:
  - each trial samples one ratio from `[[9,1],[8,2],[7,3],[6,4]]`
  - majority color and left/right arrangement are sampled each trial
  - token color is sampled from the visible ratio distribution

### Trial State Machine

1. `fixation`
   - Onset trigger: `fixation_onset`
   - Stimuli shown: central fixation (`+`)
   - Valid keys: `[]`
   - Timeout behavior: auto-advance after jittered fixation duration
   - Next state: `color_choice`

2. `color_choice`
   - Onset trigger: `choice_onset`
   - Stimuli shown together:
     - trial prompt
     - score text
     - ratio text
     - key hint (`F/J`)
     - concrete 10-box red/blue array
   - Valid keys: `[red_key, blue_key]`
   - Response triggers:
     - `choice_red`
     - `choice_blue`
   - Timeout trigger: `color_timeout`
   - Timeout behavior: no bet is placed; score unchanged
   - Next state: `feedback` (if timeout) or `bet_choice`

3. `bet_choice`
   - Onset trigger: `bet_onset`
   - Stimuli shown together:
     - trial prompt + score text
     - order label (`ascending`/`descending`)
     - key legend
     - five concrete bet buttons mapped to 5/25/50/75/95% in condition-specific order
   - Valid keys: `['1','2','3','4','5']`
   - Response triggers:
     - `bet_key_1` .. `bet_key_5`
   - Timeout trigger: `bet_timeout`
   - Timeout behavior: automatically select the last displayed percentage (protocol-aligned fallback)
   - Next state: `feedback`

4. `feedback`
   - Onset trigger: `feedback_onset`
   - Stimuli shown:
     - normal outcome text (`feedback_outcome`) or
     - auto-bet timeout outcome text (`feedback_auto_bet`) or
     - color-timeout text (`feedback_color_timeout`)
   - Valid keys: `[]`
   - Timeout behavior: auto-advance after feedback duration
   - Next state: `iti`

5. `iti`
   - Onset trigger: `iti_onset`
   - Stimuli shown: fixation (`+`)
   - Valid keys: `[]`
   - Timeout behavior: auto-advance after jittered ITI
   - Next state: next trial

## 3. Condition Semantics

- Condition ID: `gambling`
  - Participant-facing meaning: explicit-probability color judgment followed by proportional bet decision.
  - Concrete stimulus realization:
    - 10 colored boxes (red/blue) with ratio displayed numerically and visually
    - two-key color response (`F/J`)
    - five-key bet response (`1..5`) mapped to percentages shown on screen
  - Outcome rules:
    - token color is sampled from visible ratio
    - if chosen color matches token color, points increase by stake; otherwise decrease
    - stake is computed as percentage of current points

## 4. Response and Scoring Rules

- Response mapping:
  - `F -> red`
  - `J -> blue`
  - `1..5 -> bet options shown left-to-right`
- Missing-response policy:
  - color timeout: trial ends with no bet and no point change
  - bet timeout: last displayed bet option is auto-selected
- Correctness logic:
  - `chose_majority`: selected majority color (quality-of-decision metric)
  - `won`: selected color equals sampled token color
- Reward/penalty updates:
  - `bet_amount = round(points_before * bet_percent / 100)`
  - `points_after = max(0, points_before ± bet_amount)`
- Running metrics:
  - quality rate, win rate, mean bet %, color/bet RT, timeout counts
  - delay-aversion proxy from ascending vs descending mean bets

## 5. Stimulus Layout Plan

- Color-choice screen (`color_choice`)
  - `trial_prompt`: top center (`0, 310`)
  - `score_text`: upper center (`0, 265`)
  - `ratio_text`: upper center (`0, 220`)
  - 10 box array: single horizontal row near upper-middle (`y=150`), equal spacing
  - `color_key_hint`: center-lower (`0, 80`)

- Bet-choice screen (`bet_choice`)
  - `bet_prompt`: center-top (`0, 115`)
  - `bet_key_hint`: near bottom (`0, -245`)
  - 5 bet buttons: horizontal row (`y=-75`) with percentage text inside each rectangle
  - left-to-right order explicitly reflects `ascending` or `descending` context

- Feedback screen (`feedback`)
  - centered multiline outcome text, non-overlapping wrap widths (`<= 1040`)

All participant-facing text uses `font: SimHei` and UTF-8 Chinese content.

## 6. Trigger Plan

| Trigger | Code | Semantics |
|---|---:|---|
| `exp_onset` | 1 | experiment start |
| `exp_end` | 2 | experiment end |
| `block_onset` | 10 | block start |
| `block_end` | 11 | block end |
| `fixation_onset` | 20 | fixation onset |
| `choice_onset` | 30 | color-choice screen onset |
| `choice_red` | 31 | red-key response |
| `choice_blue` | 32 | blue-key response |
| `color_timeout` | 33 | no color response before deadline |
| `bet_onset` | 40 | bet-choice screen onset |
| `bet_key_1` | 41 | bet key #1 |
| `bet_key_2` | 42 | bet key #2 |
| `bet_key_3` | 43 | bet key #3 |
| `bet_key_4` | 44 | bet key #4 |
| `bet_key_5` | 45 | bet key #5 |
| `bet_timeout` | 46 | no bet response before deadline |
| `feedback_onset` | 50 | feedback onset |
| `iti_onset` | 60 | ITI onset |

## 7. Inference Log

- Decision: use one runtime condition (`gambling`) and encode `ascending/descending` as a block-level factor.
- Why inference was required: CGT manipulates bet-order context and trial probabilities within a single paradigm rather than separate MID-style condition streams.
- Citation-supported rationale: lesion and clinical CGT papers report behavior as functions of probability and bet-order components.

- Decision: keep 72 total trials in baseline run with two 36-trial blocks.
- Why inference was required: publications vary in exact session length and include task-specific operator constraints.
- Citation-supported rationale: this preserves adequate sampling over ratios and order contexts while matching existing task runtime conventions.

- Decision: implement bet-timeout auto-selection of last displayed option.
- Why inference was required: many task shells omit explicit timeout policy despite requiring deterministic outcomes.
- Citation-supported rationale: protocol text in `W2016985323` explicitly states auto-assignment of the final bet option on timeout.
