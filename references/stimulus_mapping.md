# Stimulus Mapping

Task: `Cambridge Gambling Task`

| Condition | Implemented Stimulus IDs | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Notes |
|---|---|---|---|---|---|
| `gambling` | `trial_prompt`, `score_text`, `ratio_text`, dynamic `box_rect_*` (10 red/blue boxes by ratio), `color_key_hint`, `bet_prompt`, `bet_key_hint`, dynamic `bet_box_*`, `feedback_outcome`, `feedback_auto_bet`, `feedback_color_timeout`, `fixation` | `W2132469266` | CGT separates explicit probability judgment from betting under visible red/blue box ratios. | `psychopy_builtin` | Trial runtime constructs concrete red/blue box arrays and per-trial betting options; no abstract condition labels are shown to participants. |
| `betting_order_factor` | dynamic `bet_box_*` value ordering (`ascending` or `descending`) with keys `1-5` | `W2016985323` | Bet options are the canonical five percentages (5/25/50/75/95) with order manipulation and timeout rule. | `psychopy_builtin` | Timeout in bet stage auto-selects the last displayed percentage to preserve paradigm flow. |
| `all_conditions` | `instruction_text`, `block_break`, `good_bye`, `fixation` | `W2109668460` | Shared envelope screens provide instruction, pacing, and summary for explicit-risk decision runs. | `psychopy_builtin` | All participant-facing text remains Chinese and UTF-8 clean across human/QA/sim profiles. |

Implementation mode legend:
- `psychopy_builtin`: stimulus rendered via PsychoPy primitives in config or dynamic trial code.
- `generated_reference_asset`: task-specific synthetic assets generated from reference-described stimulus rules.
- `licensed_external_asset`: externally sourced licensed media with protocol linkage.
