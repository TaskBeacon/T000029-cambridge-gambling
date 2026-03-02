# Cambridge Gambling Task

![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Cambridge Gambling Task |
| Version | v0.2.0-dev |
| URL / Repository | https://github.com/TaskBeacon/T000029-cambridge-gambling |
| Short Description | Explicit-risk decision task with red/blue probability judgment and proportional betting. |
| Created By | TaskBeacon |
| Date Updated | 2026-02-19 |
| PsyFlow Version | 0.1.9 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural (voice disabled by default) |

## 1. Task Overview

This implementation follows the Cambridge Gambling Task (CGT) structure: participants view explicit red/blue box ratios (10 boxes total), choose the color most likely to hide a token, then choose a betting percentage of current points.

Unlike MID-style templates, this task has no cue-target reaction stage. The core logic is probability judgment + bet selection + point outcome update.

## 2. Task Flow

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Block context | Controller sets block-level bet order (`ascending` or `descending`). |
| 2. Trial execution | Each trial samples a box ratio, majority color side, and token outcome probability. |
| 3. Block summary | Reports score, quality-of-decision, win rate, mean bet, RTs, timeout counts, delay-aversion proxy. |
| 4. Task summary | Final metrics shown with ascending vs descending bet comparison. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Fixation | Short jittered fixation (`+`). |
| Color choice | Show 10 red/blue boxes + ratio text; participant chooses `F=红` or `J=蓝`. |
| Bet choice | Show five bet options (5/25/50/75/95) ordered by block context; participant selects with `1-5`. |
| Feedback | Reveal token color, applied stake, point delta, and updated score. |
| ITI | Short jittered fixation before next trial. |

### Controller Logic

| Component | Description |
|---|---|
| Ratio sampler | Samples one pair from `[[9,1],[8,2],[7,3],[6,4]]` each trial. |
| Outcome sampler | Token color sampled by visible probability (`P(red)=red_boxes/10`). |
| Bet order | `ascending` block uses `[5,25,50,75,95]`; `descending` reverses this order. |
| Score update | `bet_amount = round(points_before * bet_percent / 100)`; win adds, loss subtracts. |
| Timeout policy | Color timeout -> no bet and no score change; bet timeout -> auto-select last displayed percentage. |

### Runtime Context Phases

| Phase Label | Meaning |
|---|---|
| `fixation` | Inter-stage fixation. |
| `color_choice` | Explicit probability judgment stage. |
| `bet_choice` | Percentage betting stage. |
| `feedback` | Outcome/score update display. |
| `iti` | Inter-trial interval fixation. |

## 3. Configuration Summary

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | 3-digit participant identifier. |

### b. Window Settings

| Parameter | Value |
|---|---|
| `size` | `[1280, 720]` |
| `units` | `pix` |
| `screen` | `0` |
| `bg_color` | `black` |
| `fullscreen` | `false` |
| `monitor_width_cm` | `35.5` |
| `monitor_distance_cm` | `60` |

### c. Stimuli

| Name | Type | Description |
|---|---|---|
| `trial_prompt`, `score_text`, `ratio_text`, `color_key_hint` | text | Color-choice stage envelope with explicit ratio and key mapping. |
| dynamic `box_rect_*` | rect | Ten red/blue boxes generated per trial from sampled ratio and side assignment. |
| `bet_prompt`, `bet_key_hint` | text | Bet-choice instruction and key legend. |
| dynamic `bet_box_*` | rect + text | Five on-screen bet options mapped to keys `1-5` in block-specific order. |
| `feedback_outcome`, `feedback_auto_bet`, `feedback_color_timeout` | text | Outcome and timeout-specific feedback messages. |
| `fixation`, `block_break`, `good_bye`, `instruction_text` | text | Shared trial separators and task envelope screens. |

### d. Timing

| Phase | Duration |
|---|---|
| fixation | jittered (`0.3-0.6 s` human) |
| color choice | `3.0 s` deadline |
| bet choice | `3.5 s` deadline |
| feedback | `1.0 s` |
| ITI | jittered (`0.3-0.6 s` human) |

### e. Triggers

| Trigger | Code | Description |
|---|---:|---|
| `choice_onset` | 30 | Color-choice screen onset |
| `choice_red` / `choice_blue` | 31 / 32 | Color response events |
| `color_timeout` | 33 | No color response |
| `bet_onset` | 40 | Bet-choice screen onset |
| `bet_key_1..5` | 41..45 | Bet key responses |
| `bet_timeout` | 46 | No bet response |
| `feedback_onset` | 50 | Outcome screen onset |

## 4. Methods (for academic publication)

Participants completed an explicit-risk gambling paradigm in which probabilities were represented by visible red/blue box ratios (total = 10). On each trial, participants first selected the color judged most likely to hide a token, then selected a stake as a percentage of current points.

The task manipulated bet-order context (`ascending` vs `descending`) at block level and recorded key CGT outputs: majority-color choice quality, betting magnitude, outcome sensitivity, and response latency. Score updates were proportional to selected stake and outcome congruence.

All phases were instrumented with phase-level triggers and trial context metadata, enabling synchronized behavioral and acquisition-aligned analyses across human, QA, and simulation modes.
