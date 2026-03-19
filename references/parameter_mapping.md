# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| task.conditions | `task.conditions` | `['gambling']` | W1978492017 | CGT is implemented as one explicit-risk trial stream with two within-trial decisions. | inferred | Color-choice and bet-choice phases carry primary semantics. |
| task.keys.color | `task.red_key`, `task.blue_key` | `f` for red, `j` for blue | W2010490259 | First decision is a binary color-probability judgment. | inferred | Keys are configurable for localization/hardware constraints. |
| task.keys.bet | `task.bet_keys` | `['1','2','3','4','5']` | W1992731065 | Second decision selects bet proportion from ordered options. | inferred | Response keys map to on-screen percentage options. |
| task.localization.labels | `task.color_labels`, `task.order_labels` | red/blue labels and ascending/descending labels | W2102212556 | Participant-facing choice and order labels must be explicit in CGT instructions. | inferred | Runtime avoids hardcoded labels for localization. |
| timing.fixation | `timing.fixation_duration` | `[0.3, 0.6]` s | W1978492017 | Trial event separation with short fixation is standard in CGT variants. | inferred | Passed directly to `StimUnit.show(...)`; controller does not resample fixation jitter. |
| timing.color_choice_deadline | `timing.color_choice_deadline` | `3.0` s | W2010490259 | Explicit but time-limited color selection is a core CGT component. | inferred | Timeout branch yields no-bet outcome. |
| timing.bet_choice_deadline | `timing.bet_choice_deadline` | `3.5` s | W1992731065 | Bet decision phase uses bounded response windows in computerized implementations. | inferred | Timeout auto-selects last displayed bet option. |
| timing.feedback | `timing.feedback_duration` | `1.0` s | W2091361525 | Outcome and points update feedback support trialwise performance monitoring. | inferred | Same trigger code for all feedback branches. |
| timing.iti | `timing.iti_duration` | `[0.3, 0.6]` s | W2102212556 | ITI jitter reduces expectancy and response carry-over. | inferred | Passed directly to `StimUnit.show(...)`; controller does not resample ITI jitter. |
| controller.ratios | `controller.box_ratios` | `[[9,1],[8,2],[7,3],[6,4]]` | W1978492017 | CGT uses explicit 10-box red/blue ratios for probability judgment. | inferred | Ratio is sampled trialwise and logged (`ratio_label`). |
| controller.bet_options | `controller.bet_options` | `[5,25,50,75,95]` | W1992731065 | Canonical CGT betting percentages use five discrete stake levels. | supported | Reversed order in descending blocks. |
| controller.block_order | `controller.block_order` | `ascending`, `descending` | W1992731065 | Delay aversion is assessed via order effects on selected bet percentages. | inferred | Delay-aversion proxy = descending mean - ascending mean. |
| controller.initial_points | `controller.initial_points` | `100` | W2102212556 | Points ledger is needed to compute proportional gains/losses from bet percentages. | inferred | Bet amount is proportional to current points. |
| trigger.choice | `triggers.map.choice_onset`, `choice_red`, `choice_blue`, `color_timeout` | `30`, `31`, `32`, `33` | W2010490259 | Color-choice onset/response/timeout events are core CGT stage markers. | inferred | Response trigger emitted after key mapping. |
| trigger.bet | `triggers.map.bet_onset`, `bet_key_1..5`, `bet_timeout` | `40`, `41..45`, `46` | W1992731065 | Bet decision stage needs key-specific event coding and timeout handling. | inferred | Bet key trigger index follows displayed key order. |
| trigger.feedback_iti | `triggers.map.feedback_onset`, `iti_onset` | `50`, `60` | W2102212556 | Outcome and inter-trial stage boundaries are required for auditability. | inferred | Feedback branch type is encoded in trial data. |
