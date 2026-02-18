# Stimulus Mapping

Task: `Cambridge Gambling Task`

| Condition | Implemented Stimulus IDs | Source Paper ID | Evidence (quote/figure/table) | Implementation Mode | Notes |
|---|---|---|---|---|---|
| `low_risk` | `low_risk_cue`, `low_risk_target` | `W2132469266` | Methods section describes condition-specific cue-target structure and response phase. | `psychopy_builtin` | Cue label text for LOW RISK; target token for condition-specific response context. |
| `medium_risk` | `medium_risk_cue`, `medium_risk_target` | `W2132469266` | Methods section describes condition-specific cue-target structure and response phase. | `psychopy_builtin` | Cue label text for MEDIUM RISK; target token for condition-specific response context. |
| `high_risk` | `high_risk_cue`, `high_risk_target` | `W2132469266` | Methods section describes condition-specific cue-target structure and response phase. | `psychopy_builtin` | Cue label text for HIGH RISK; target token for condition-specific response context. |

Implementation mode legend:
- `psychopy_builtin`: stimulus rendered via PsychoPy primitives in config.
- `generated_reference_asset`: task-specific synthetic assets generated from reference-described stimulus rules.
- `licensed_external_asset`: externally sourced licensed media with protocol linkage.
