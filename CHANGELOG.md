# CHANGELOG

All notable development changes for `T000029-cambridge-gambling` are documented here.

## [v0.2.0-dev] - 2026-02-19

### Changed
- Replaced MID-derived `cue -> anticipation -> target -> feedback` scaffold with Cambridge Gambling Task logic (`color_choice -> bet_choice -> feedback`).
- Rewrote `src/utils.py` to a CGT controller: box-ratio sampling, block-level bet order, token outcome sampling, and proportional point updates.
- Rewrote `src/run_trial.py` to render concrete 10-box red/blue arrays and five-option betting controls (5/25/50/75/95).
- Rewrote `main.py` summaries to report CGT metrics (quality-of-decision, win rate, mean bet, delay-aversion proxy, timeout counts).
- Replaced generic sampler with phase-aware responder that handles both color and bet stages.
- Rebuilt all configs (`config.yaml`, `config_qa.yaml`, `config_scripted_sim.yaml`, `config_sampler_sim.yaml`) with UTF-8 Chinese participant text and CGT-specific triggers.
- Replaced poisoned reference artifacts (`references/*.md`, `references/*.yaml`, `references/selected_papers.json`, `references/candidate_papers.json`) with CGT-aligned literature and mappings.
- Updated metadata/docs (`README.md`, `taskbeacon.yaml`) to reflect the repaired paradigm and release.

### Verified
- `python -m py_compile main.py src/run_trial.py src/utils.py responders/task_sampler.py`
- `python ../psyflow/skills/task-build/scripts/check_task_standard.py --task-path .`
- `python -m psyflow.validate .`
- `psyflow-qa . --config config/config_qa.yaml --no-maturity-update`
- `python main.py sim --config config/config_scripted_sim.yaml`
- `python main.py sim --config config/config_sampler_sim.yaml`

## [v0.1.1-dev] - 2026-02-19

### Changed
- Rebuilt literature bundle with task-relevant curated papers and regenerated reference artifacts.
- Replaced corrupted `references/task_logic_audit.md` with a full state-machine audit.
- Updated `references/stimulus_mapping.md` to concrete implemented stimulus IDs per condition.
- Synced metadata (`README.md`, `taskbeacon.yaml`) with current configuration and evidence.

## [0.1.0] - 2026-02-17

### Added
- Added initial PsyFlow/TAPS task scaffold for Cambridge Gambling Task.
- Added mode-aware runtime (`human|qa|sim`) in `main.py`.
- Added split configs (`config.yaml`, `config_qa.yaml`, `config_scripted_sim.yaml`, `config_sampler_sim.yaml`).
- Added responder trial-context plumbing via `set_trial_context(...)` in `src/run_trial.py`.
- Added generated cue/target image stimuli under `assets/generated/`.

### Verified
- `python -m psyflow.validate <task_path>`
- `psyflow-qa <task_path> --config config/config_qa.yaml --no-maturity-update`
- `python main.py sim --config config/config_scripted_sim.yaml`
- `python main.py sim --config config/config_sampler_sim.yaml`
