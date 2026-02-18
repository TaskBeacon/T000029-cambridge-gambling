# Cambridge Gambling Task

![Maturity: draft](https://img.shields.io/badge/Maturity-draft-64748b?style=flat-square&labelColor=111827)

| Field | Value |
|---|---|
| Name | Cambridge Gambling Task |
| Version | v0.1.1-dev |
| URL / Repository | https://github.com/TaskBeacon/T000029-cambridge-gambling |
| Short Description | Risk-taking and betting strategy assessment under known probabilities. |
| Created By | TaskBeacon |
| Date Updated | 2026-02-19 |
| PsyFlow Version | 0.1.9 |
| PsychoPy Version | 2025.1.1 |
| Modality | Behavior |
| Language | Chinese |
| Voice Name | zh-CN-YunyangNeural (voice disabled by default) |

## 1. Task Overview

This task implements a Cambridge Gambling-style risk paradigm with `low_risk`, `medium_risk`, and `high_risk` condition streams. Trials include cueing, anticipation, target response capture, and condition-specific feedback.

The current implementation is organized for standardized PsyFlow execution across human, QA, and simulation modes with trial-level logging and trigger event coverage.

## 2. Task Flow

### Block-Level Flow

| Step | Description |
|---|---|
| 1. Prepare trials | Condition schedule is loaded per block. |
| 2. Execute trials | `run_trial(...)` runs cue, anticipation, target, and feedback phases. |
| 3. Block summary | Accuracy and score summary is shown. |
| 4. Final summary | End-of-task score is shown. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Cue | Risk-level cue is shown. |
| Anticipation | Fixation interval with response monitoring. |
| Target | Condition target is displayed and response is captured. |
| Pre-feedback fixation | Brief fixation transition stage. |
| Feedback | Hit/miss feedback is shown and score updates. |

### Controller Logic

| Component | Description |
|---|---|
| Adaptive duration | Controller adjusts target duration based on recent accuracy. |
| Condition tracking | Histories are updated for each condition. |
| Scoring update | Trial hit/miss drives score delta. |

### Runtime Context Phases

| Phase Label | Meaning |
|---|---|
| `anticipation` | Pre-target monitoring stage. |
| `target` | Active response window for target. |

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
| `bg_color` | `gray` |
| `fullscreen` | `false` |
| `monitor_width_cm` | `35.5` |
| `monitor_distance_cm` | `60` |

### c. Stimuli

| Name | Type | Description |
|---|---|---|
| `*_cue` | text | Risk-level cue prompts by condition. |
| `*_target` | text | Condition-specific target prompts. |
| `*_hit_feedback`, `*_miss_feedback` | text | Condition-specific outcome feedback. |
| `fixation`, `block_break`, `good_bye` | text | Shared fixation and summary screens. |

### d. Timing

| Phase | Duration |
|---|---|
| cue | 0.5 s |
| anticipation | 1.0 s |
| prefeedback | 0.4 s |
| feedback | 0.8 s |
| target | adaptive via controller (`0.08`-`0.40` s bounds) |

## 4. Methods (for academic publication)

Participants completed a risk-based decision task with three risk-level conditions. Each trial included cue exposure, anticipation, response-window target presentation, and immediate feedback, enabling estimation of condition-wise performance metrics.

A controller adapted target exposure duration as a function of recent accuracy to keep task difficulty within bounds. Trial logs include response status, timing, condition identity, and score updates.

Trigger codes were emitted at major trial transitions (cue, anticipation, target, feedback), supporting synchronized acquisition workflows.
