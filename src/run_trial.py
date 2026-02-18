from functools import partial

from psyflow import StimUnit, set_trial_context


def _deadline_s(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except Exception:
            return None
    return None


def _next_trial_id(controller) -> int:
    histories = getattr(controller, "histories", {}) or {}
    done = 0
    for items in histories.values():
        try:
            done += len(items)
        except Exception:
            continue
    return int(done) + 1


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    controller,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one condition-specific trial with cue, response window, and feedback."""
    trial_id = _next_trial_id(controller)
    trial_data = {"condition": condition, "trial_id": trial_id}
    response_keys = [str(k) for k in list(settings.key_list) if str(k).lower() != "space"]
    if not response_keys:
        response_keys = list(settings.key_list)

    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    cue = make_unit(unit_label="cue").add_stim(stim_bank.get(f"{condition}_cue"))
    set_trial_context(
        cue,
        trial_id=trial_id,
        phase="cue",
        deadline_s=_deadline_s(settings.cue_duration),
        valid_keys=[],
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "stage": "cue", "block_idx": block_idx},
        stim_id=f"{condition}_cue",
    )
    cue.show(
        duration=settings.cue_duration,
        onset_trigger=settings.triggers.get(f"{condition}_cue_onset"),
    ).to_dict(trial_data)

    anti = make_unit(unit_label="anticipation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        anti,
        trial_id=trial_id,
        phase="anticipation",
        deadline_s=_deadline_s(settings.anticipation_duration),
        valid_keys=[],
        block_id=block_id,
        condition_id=str(condition),
        task_factors={"condition": str(condition), "stage": "anticipation", "block_idx": block_idx},
        stim_id="fixation",
    )
    anti.show(
        duration=settings.anticipation_duration,
        onset_trigger=settings.triggers.get(f"{condition}_anti_onset"),
    ).to_dict(trial_data)

    duration = controller.get_duration(condition)
    target = make_unit(unit_label="target").add_stim(stim_bank.get(f"{condition}_target"))
    set_trial_context(
        target,
        trial_id=trial_id,
        phase="target",
        deadline_s=_deadline_s(duration),
        valid_keys=list(response_keys),
        block_id=block_id,
        condition_id=str(condition),
        task_factors={
            "condition": str(condition),
            "stage": "target",
            "block_idx": block_idx,
            "target_duration_s": float(duration),
        },
        stim_id=f"{condition}_target",
    )
    target.capture_response(
        keys=response_keys,
        duration=duration,
        onset_trigger=settings.triggers.get(f"{condition}_target_onset"),
        response_trigger=settings.triggers.get(f"{condition}_key_press"),
        timeout_trigger=settings.triggers.get(f"{condition}_no_response"),
    )
    target.to_dict(trial_data)

    make_unit(unit_label="prefeedback_fixation").add_stim(stim_bank.get("fixation")).show(
        duration=settings.prefeedback_duration
    ).to_dict(trial_data)

    hit = bool(target.get_state("hit", False))
    delta_unit = int(getattr(settings, "delta", 1))
    delta = delta_unit if hit else -delta_unit
    controller.update(hit, condition)

    hit_type = "hit" if hit else "miss"
    fb_stim = stim_bank.get(f"{condition}_{hit_type}_feedback")
    fb = make_unit(unit_label="feedback").add_stim(fb_stim).show(
        duration=settings.feedback_duration,
        onset_trigger=settings.triggers.get(f"{condition}_{hit_type}_fb_onset"),
    )
    fb.set_state(hit=hit, delta=delta).to_dict(trial_data)

    return trial_data
