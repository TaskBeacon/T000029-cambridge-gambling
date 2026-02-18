# Stimulus Mapping

Task: `Cambridge Gambling Task`

| Condition | Implemented Stimulus IDs | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Notes |
|---|---|---|---|---|---|
| `low_risk` | `low_risk_cue`, `low_risk_target`, `low_risk_hit_feedback`, `low_risk_miss_feedback`, `fixation` | `W1497041452` | Condition-specific trial flow and outcome/response mapping described in selected paradigm references. | `psychopy_builtin` | Condition row resolved against current `config/config.yaml` stimuli and `src/run_trial.py` phase logic. |
| `medium_risk` | `medium_risk_cue`, `medium_risk_target`, `medium_risk_hit_feedback`, `medium_risk_miss_feedback`, `fixation` | `W1497041452` | Condition-specific trial flow and outcome/response mapping described in selected paradigm references. | `psychopy_builtin` | Condition row resolved against current `config/config.yaml` stimuli and `src/run_trial.py` phase logic. |
| `high_risk` | `high_risk_cue`, `high_risk_target`, `high_risk_hit_feedback`, `high_risk_miss_feedback`, `fixation` | `W1497041452` | Condition-specific trial flow and outcome/response mapping described in selected paradigm references. | `psychopy_builtin` | Condition row resolved against current `config/config.yaml` stimuli and `src/run_trial.py` phase logic. |
| `all_conditions` | `instruction_text`, `block_break`, `good_bye`, `fixation` | `W1497041452` | Shared instruction, transition, and fixation assets support the common task envelope across all conditions. | `psychopy_builtin` | Shared assets are condition-agnostic and used in every run mode. |

Implementation mode legend:
- `psychopy_builtin`: stimulus rendered via PsychoPy primitives in config.
- `generated_reference_asset`: task-specific synthetic assets generated from reference-described stimulus rules.
- `licensed_external_asset`: externally sourced licensed media with protocol linkage.
