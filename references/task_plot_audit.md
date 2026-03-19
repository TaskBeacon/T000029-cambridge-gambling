# Task Plot Audit

- generated_at: 2026-03-19T09:19:27
- mode: existing
- task_path: E:\xhmhc\TaskBeacon\T000029-cambridge-gambling

## 1. Inputs and provenance

- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\README.md
- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\config\config.yaml
- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\src\run_trial.py

## 2. Evidence extracted from README

- | Step | Description |
- |---|---|
- | Fixation | Short jittered fixation (`+`) from `timing.fixation_duration`. |
- | Color choice | Show 10 red/blue boxes + ratio text; participant chooses `F=红` or `J=蓝`. |
- | Bet choice | Show five bet options (5/25/50/75/95) ordered by block context; participant selects with `1-5`. |
- | Feedback | Reveal token color, applied stake, point delta, and updated score. |
- | ITI | Short jittered fixation before next trial from `timing.iti_duration`. |

## 3. Evidence extracted from config/source

- gambling: phase=fixation, deadline_expr=_deadline_s(fixation_duration), response_expr=n/a, stim_expr='fixation'
- gambling: phase=color choice, deadline_expr=_deadline_s(color_deadline), response_expr=color_deadline, stim_expr='trial_prompt+score_text+ratio_text+box_token_template*10+color_key_hint'
- gambling: phase=bet choice, deadline_expr=_deadline_s(bet_deadline), response_expr=bet_deadline, stim_expr='score_text+ratio_text+box_token_template*10+bet_prompt+bet_option_template*5+bet_key_hint'
- gambling: phase=feedback, deadline_expr=_deadline_s(feedback_duration), response_expr=n/a, stim_expr='feedback'
- gambling: phase=iti, deadline_expr=_deadline_s(iti_duration), response_expr=n/a, stim_expr='fixation'

## 4. Mapping to task_plot_spec

- timeline collection: one representative timeline per unique trial logic
- phase flow inferred from run_trial set_trial_context order and branch predicates
- participant-visible show() phases without set_trial_context are inferred where possible and warned
- duration/response inferred from deadline/capture expressions
- stimulus examples inferred from stim_id + config stimuli
- conditions with equivalent phase/timing logic collapsed and annotated as variants
- root_key: task_plot_spec
- spec_version: 0.2

## 5. Style decision and rationale

- Single timeline-collection view selected by policy: one representative condition per unique timeline logic.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 3
- screens_per_timeline: 5
- screen_overlap_ratio: 0.0
- screen_slope: 0.08
- screen_slope_deg: 34.0
- screen_aspect_ratio: 1.65
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.039, right=0.041, blank=0.146
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.039, 'right_ratio': 0.0414, 'blank_ratio': 0.1456}
- validator_warnings:
  - timelines[0].phases[1] missing duration_ms; renderer will annotate as n/a.
  - timelines[0].phases[2] missing duration_ms; renderer will annotate as n/a.
  - timelines[0].phases[3] missing duration_ms; renderer will annotate as n/a.

## 7. Output files and checksums

- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\references\task_plot_spec.yaml: sha256=8e02061a27a816a3e23d09a167e9cc2de28219fdf78d982122fd49b6b4a2aaef
- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\references\task_plot_spec.json: sha256=1d84587a3ea71656e45103d04fdd1f199dfd090a03a8a81f3324cc74b65fbde7
- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\references\task_plot_source_excerpt.md: sha256=2dff4466dd3d8064e4c96b38a6b59234451ad6c25ef8bfaa652877904d9f8288
- E:\xhmhc\TaskBeacon\T000029-cambridge-gambling\task_flow.png: sha256=778e849d9002cd2e58b9344350d67bb56b124a7020841607994e4e4c4b987170

## 8. Inferred/uncertain items

- gambling:fixation:heuristic range parse from 'getattr(settings, 'fixation_duration', (0.3, 0.6))'
- gambling:color choice:unable to resolve duration from 'float(settings.color_choice_deadline)'
- gambling:bet choice:unable to resolve duration from 'float(settings.bet_choice_deadline)'
- gambling:feedback:unable to resolve duration from 'float(settings.feedback_duration)'
- gambling:iti:heuristic range parse from 'getattr(settings, 'iti_duration', (0.3, 0.6))'
- unparsed if-tests defaulted to condition-agnostic applicability: color_response_key == blue_key; color_response_key == red_key; color_timed_out; not bet_keys; not bet_timed_out
