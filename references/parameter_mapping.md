# Parameter Mapping

| Parameter | Implemented Value | Source Paper ID | Confidence | Rationale |
|---|---|---|---|---|
| `task.conditions` | `['gambling']` | `W2132469266` | `high` | CGT trials are defined by explicit box-probability and bet-order factors, not MID-style condition labels. |
| `task.total_blocks` | `2` | `W2097485712` | `inferred` | Two-block structure used to expose both ascending and descending bet-order contexts while keeping runtime practical. |
| `task.trial_per_block` | `36` | `W2132469266` | `inferred` | Keeps 72 total trials, matching common CGT-scale study runs. |
| `task.red_key` | `f` | `W2132469266` | `inferred` | Stable binary color-choice mapping for explicit probability decisions. |
| `task.blue_key` | `j` | `W2132469266` | `inferred` | Stable binary color-choice mapping for explicit probability decisions. |
| `task.bet_keys` | `['1','2','3','4','5']` | `W2016985323` | `inferred` | Five-key mapping aligns with five discrete betting percentages. |
| `timing.color_choice_deadline` | `3.0 s` | `W2097485712` | `inferred` | Bounded response window supports timeout logging and consistent RT collection. |
| `timing.bet_choice_deadline` | `3.5 s` | `W2016985323` | `inferred` | Implements explicit bet-selection window with deterministic timeout handling. |
| `timing.feedback_duration` | `1.0 s` | `W2109668460` | `inferred` | Dedicated post-outcome display stage for synchronized event logging. |
| `controller.initial_points` | `100` | `W2132469266` | `inferred` | Provides a bounded starting bankroll for proportional betting updates. |
| `controller.box_ratios` | `[[9,1],[8,2],[7,3],[6,4]]` | `W2016985323` | `high` | Matches canonical CGT explicit-probability ratio set. |
| `controller.bet_options` | `[5,25,50,75,95]` | `W2016985323` | `high` | Directly follows documented CGT betting percentages. |
| `controller.block_order` | `['ascending','descending']` | `W2016985323` | `high` | Captures order-manipulation factor underlying delay-aversion metrics. |
| `run_trial.timeout_rule` | `bet timeout auto-selects last displayed percentage` | `W2016985323` | `high` | Explicitly documented in protocol description. |
| `run_trial.token_probability` | `P(red)=red_boxes/10, P(blue)=blue_boxes/10` | `W2132469266` | `high` | Probability of outcome follows visible box distribution by design. |
| `scoring.rule` | `delta = ± round(points_before * bet_percent / 100)` | `W2132469266` | `inferred` | Implements proportional stake updates consistent with CGT point betting behavior. |
| `triggers.map.choice_onset` | `30` | `W2109668460` | `inferred` | Marks onset of explicit probability decision stage for synchronization. |
| `triggers.map.bet_onset` | `40` | `W2097485712` | `inferred` | Marks onset of betting stage for event-aligned analyses. |
| `triggers.map.bet_key_1..5` | `41..45` | `W2097485712` | `inferred` | Separates each bet-key response event for traceability. |
| `triggers.map.feedback_onset` | `50` | `W2109668460` | `inferred` | Marks outcome reveal after color+bet decisions. |
| `summary.delay_aversion` | `mean_bet(descending) - mean_bet(ascending)` | `W2097485712` | `inferred` | Operationalizes early-bet tendency under order manipulation. |
