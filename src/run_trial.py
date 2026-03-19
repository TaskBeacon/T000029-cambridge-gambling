from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, set_trial_context


def _deadline_s(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        try:
            return float(max(value))
        except Exception:
            return None
    return None


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list:
    return list(value) if isinstance(value, (list, tuple)) else []


def _box_positions() -> list[tuple[float, float]]:
    return [(-450.0 + (100.0 * idx), 150.0) for idx in range(10)]


def _bet_positions() -> list[tuple[float, float]]:
    return [(-320.0, -70.0), (-160.0, -70.0), (0.0, -70.0), (160.0, -70.0), (320.0, -70.0)]


def _color_name(color_token: str, labels: dict[str, Any]) -> str:
    token = str(color_token).strip().lower()
    if token == "red":
        return str(labels.get("red", "red"))
    if token == "blue":
        return str(labels.get("blue", "blue"))
    return token


def _draw_boxes(unit: StimUnit, stim_bank, *, red_boxes: int, blue_boxes: int, red_left: bool) -> None:
    left_color = "red" if red_left else "blue"
    right_color = "blue" if red_left else "red"
    left_count = int(red_boxes) if red_left else int(blue_boxes)
    right_count = int(blue_boxes) if red_left else int(red_boxes)

    color_tokens = [left_color] * left_count + [right_color] * right_count
    positions = _box_positions()
    for idx in range(10):
        color_token = color_tokens[idx] if idx < len(color_tokens) else right_color
        fill_color = [0.92, 0.23, 0.23] if color_token == "red" else [0.24, 0.42, 0.95]
        unit.add_stim(
            stim_bank.rebuild(
                "box_token_template",
                text="■",
                pos=positions[idx],
                color=fill_color,
            )
        )


def _draw_bet_options(unit: StimUnit, stim_bank, bet_options: list[int], bet_keys: list[str]) -> str:
    positions = _bet_positions()
    legend_parts: list[str] = []
    for idx, pct in enumerate(bet_options):
        if idx >= len(positions) or idx >= len(bet_keys):
            break
        key = str(bet_keys[idx]).strip()
        label = f"{pct}%"
        legend_parts.append(f"{key}={label}")
        unit.add_stim(
            stim_bank.rebuild(
                "bet_option_template",
                text=label,
                pos=positions[idx],
            )
        )
    return " / ".join(legend_parts)


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
    """Run one Cambridge Gambling trial with color and bet decisions."""
    condition_name = str(condition).strip().lower()
    trial_id = int(controller.next_trial_id()) if hasattr(controller, "next_trial_id") else 1
    block_idx_val = int(block_idx) if block_idx is not None else 0

    spec = controller.build_trial(block_idx=block_idx_val)

    red_key = str(getattr(settings, "red_key", "f")).strip().lower()
    blue_key = str(getattr(settings, "blue_key", "j")).strip().lower()
    color_keys = [red_key, blue_key]

    bet_keys = [str(k).strip().lower() for k in _as_list(getattr(settings, "bet_keys", [])) if str(k).strip()]
    if not bet_keys:
        bet_keys = ["1", "2", "3", "4", "5"]

    color_labels = _as_dict(getattr(settings, "color_labels", {}))
    order_labels = _as_dict(getattr(settings, "order_labels", {}))

    fixation_duration = getattr(settings, "fixation_duration", (0.3, 0.6))
    color_deadline = float(settings.color_choice_deadline)
    bet_deadline = float(settings.bet_choice_deadline)
    feedback_duration = float(settings.feedback_duration)
    iti_duration = getattr(settings, "iti_duration", (0.3, 0.6))

    majority_key = red_key if spec.majority_color == "red" else blue_key
    minority_key = blue_key if majority_key == red_key else red_key
    order_label = str(order_labels.get(spec.order, spec.order))

    trial_data = {
        "condition": condition_name,
        "trial_id": trial_id,
        "block_id": str(block_id) if block_id is not None else "block_0",
        "block_idx": block_idx_val,
        "bet_order": str(spec.order),
        "ratio_label": str(spec.ratio_label),
        "red_boxes": int(spec.red_boxes),
        "blue_boxes": int(spec.blue_boxes),
        "majority_color": str(spec.majority_color),
        "minority_color": str(spec.minority_color),
        "token_color": str(spec.token_color),
        "red_left": bool(spec.red_left),
    }

    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    fixation = make_unit(unit_label="fixation").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        fixation,
        trial_id=trial_id,
        phase="fixation",
        deadline_s=_deadline_s(fixation_duration),
        valid_keys=[],
        block_id=trial_data["block_id"],
        condition_id=condition_name,
        task_factors={
            "stage": "fixation",
            "bet_order": spec.order,
            "ratio_label": spec.ratio_label,
            "red_boxes": spec.red_boxes,
            "blue_boxes": spec.blue_boxes,
            "block_idx": block_idx_val,
        },
        stim_id="fixation",
    )
    fixation.show(
        duration=fixation_duration,
        onset_trigger=settings.triggers.get("fixation_onset"),
    ).to_dict(trial_data)

    current_points = int(getattr(controller, "current_points", 0))
    color_choice = make_unit(unit_label="color_choice")
    color_choice.add_stim(stim_bank.get("trial_prompt"))
    color_choice.add_stim(stim_bank.get_and_format("score_text", current_points=current_points))
    color_choice.add_stim(
        stim_bank.get_and_format(
            "ratio_text",
            red_boxes=spec.red_boxes,
            blue_boxes=spec.blue_boxes,
            ratio_label=spec.ratio_label,
        )
    )
    _draw_boxes(color_choice, stim_bank, red_boxes=spec.red_boxes, blue_boxes=spec.blue_boxes, red_left=spec.red_left)
    color_choice.add_stim(
        stim_bank.get_and_format(
            "color_key_hint",
            red_key=red_key.upper(),
            blue_key=blue_key.upper(),
        )
    )
    set_trial_context(
        color_choice,
        trial_id=trial_id,
        phase="color_choice",
        deadline_s=_deadline_s(color_deadline),
        valid_keys=color_keys,
        block_id=trial_data["block_id"],
        condition_id=condition_name,
        task_factors={
            "stage": "color_choice",
            "bet_order": spec.order,
            "ratio_label": spec.ratio_label,
            "red_boxes": spec.red_boxes,
            "blue_boxes": spec.blue_boxes,
            "majority_key": majority_key,
            "minority_key": minority_key,
            "block_idx": block_idx_val,
        },
        stim_id="trial_prompt+score_text+ratio_text+box_token_template*10+color_key_hint",
    )
    color_choice.capture_response(
        keys=color_keys,
        duration=color_deadline,
        onset_trigger=settings.triggers.get("choice_onset"),
        response_trigger=None,
        timeout_trigger=settings.triggers.get("color_timeout"),
    )
    color_choice.to_dict(trial_data)

    color_response_key = str(color_choice.get_state("response", "")).strip().lower()
    color_timed_out = color_response_key not in color_keys
    if color_response_key == red_key:
        trigger_runtime.send(settings.triggers.get("choice_red"))
    elif color_response_key == blue_key:
        trigger_runtime.send(settings.triggers.get("choice_blue"))

    color_rt = color_choice.get_state("rt", None)
    color_rt_s = float(color_rt) if isinstance(color_rt, (int, float)) else None

    chosen_color = ""
    chose_majority: bool | None = None
    bet_response_key = ""
    bet_percent: int | None = None
    bet_timed_out = False
    won: bool | None = None
    net_change = 0

    if color_timed_out:
        outcome = controller.no_bet_update()
        points_after = int(outcome["points_after"])
        points_before = int(outcome["points_before"])
        bet_amount = int(outcome["bet_amount"])
        feedback_stim = stim_bank.get_and_format(
            "feedback_color_timeout",
            token_color_cn=_color_name(spec.token_color, color_labels),
            points_after=points_after,
        )
        feedback_meta = {
            "auto_bet": False,
            "feedback_type": "color_timeout",
            "bet_timeout": False,
        }
        bet_rt_s = None
    else:
        chosen_color = "red" if color_response_key == red_key else "blue"
        chose_majority = bool(chosen_color == spec.majority_color)

        display_bets = [int(v) for v in list(spec.bet_options)]
        key_count = min(len(bet_keys), len(display_bets))
        bet_keys_active = bet_keys[:key_count]
        display_bets = display_bets[:key_count]
        bet_key_map = {bet_keys_active[idx]: int(display_bets[idx]) for idx in range(len(display_bets))}

        bet_choice = make_unit(unit_label="bet_choice")
        bet_choice.add_stim(stim_bank.get_and_format("score_text", current_points=current_points))
        bet_choice.add_stim(
            stim_bank.get_and_format(
                "ratio_text",
                red_boxes=spec.red_boxes,
                blue_boxes=spec.blue_boxes,
                ratio_label=spec.ratio_label,
            )
        )
        _draw_boxes(bet_choice, stim_bank, red_boxes=spec.red_boxes, blue_boxes=spec.blue_boxes, red_left=spec.red_left)
        bet_choice.add_stim(stim_bank.get_and_format("bet_prompt", order_label=order_label))
        bet_legend = _draw_bet_options(bet_choice, stim_bank, display_bets, bet_keys_active)
        bet_choice.add_stim(stim_bank.get_and_format("bet_key_hint", bet_legend=bet_legend))
        set_trial_context(
            bet_choice,
            trial_id=trial_id,
            phase="bet_choice",
            deadline_s=_deadline_s(bet_deadline),
            valid_keys=bet_keys_active,
            block_id=trial_data["block_id"],
            condition_id=condition_name,
            task_factors={
                "stage": "bet_choice",
                "bet_order": spec.order,
                "ratio_label": spec.ratio_label,
                "red_boxes": spec.red_boxes,
                "blue_boxes": spec.blue_boxes,
                "chosen_color": chosen_color,
                "bet_key_map": bet_key_map,
                "block_idx": block_idx_val,
            },
            stim_id="score_text+ratio_text+box_token_template*10+bet_prompt+bet_option_template*5+bet_key_hint",
        )
        bet_choice.capture_response(
            keys=bet_keys_active,
            duration=bet_deadline,
            onset_trigger=settings.triggers.get("bet_onset"),
            response_trigger=None,
            timeout_trigger=settings.triggers.get("bet_timeout"),
        )
        bet_choice.to_dict(trial_data)

        bet_response_key = str(bet_choice.get_state("response", "")).strip().lower()
        bet_timed_out = bet_response_key not in bet_key_map

        if not bet_timed_out:
            key_idx = bet_keys_active.index(bet_response_key)
            trigger_runtime.send(settings.triggers.get(f"bet_key_{key_idx + 1}"))
            bet_percent = int(bet_key_map[bet_response_key])
        else:
            bet_response_key = bet_keys_active[-1]
            bet_percent = int(display_bets[-1])

        won = bool(chosen_color == spec.token_color)
        outcome = controller.apply_bet_outcome(bet_percent=int(bet_percent), won=won)
        points_before = int(outcome["points_before"])
        points_after = int(outcome["points_after"])
        bet_amount = int(outcome["bet_amount"])
        net_change = int(outcome["delta"])

        feedback_stim_name = "feedback_auto_bet" if bet_timed_out else "feedback_outcome"
        feedback_stim = stim_bank.get_and_format(
            feedback_stim_name,
            chosen_color_cn=_color_name(chosen_color, color_labels),
            token_color_cn=_color_name(spec.token_color, color_labels),
            bet_percent=int(bet_percent),
            bet_amount=bet_amount,
            net_change=net_change,
            points_after=points_after,
        )
        feedback_meta = {
            "auto_bet": bool(bet_timed_out),
            "feedback_type": feedback_stim_name,
            "bet_timeout": bool(bet_timed_out),
        }

        bet_rt = bet_choice.get_state("rt", None)
        bet_rt_s = float(bet_rt) if isinstance(bet_rt, (int, float)) else None

    feedback = make_unit(unit_label="feedback").add_stim(feedback_stim)
    set_trial_context(
        feedback,
        trial_id=trial_id,
        phase="feedback",
        deadline_s=_deadline_s(feedback_duration),
        valid_keys=[],
        block_id=trial_data["block_id"],
        condition_id=condition_name,
        task_factors={
            "stage": "feedback",
            "bet_order": spec.order,
            "ratio_label": spec.ratio_label,
            "chosen_color": chosen_color,
            "token_color": spec.token_color,
            "bet_percent": bet_percent,
            "won": won,
            "net_change": net_change,
            "color_timed_out": color_timed_out,
            "bet_timed_out": bet_timed_out,
            "block_idx": block_idx_val,
        },
        stim_id="feedback",
    )
    feedback.show(
        duration=feedback_duration,
        onset_trigger=settings.triggers.get("feedback_onset"),
    ).to_dict(trial_data)

    iti = make_unit(unit_label="iti").add_stim(stim_bank.get("fixation"))
    set_trial_context(
        iti,
        trial_id=trial_id,
        phase="iti",
        deadline_s=_deadline_s(iti_duration),
        valid_keys=[],
        block_id=trial_data["block_id"],
        condition_id=condition_name,
        task_factors={"stage": "iti", "block_idx": block_idx_val},
        stim_id="fixation",
    )
    iti.show(
        duration=iti_duration,
        onset_trigger=settings.triggers.get("iti_onset"),
    ).to_dict(trial_data)

    trial_data.update(
        {
            "color_response_key": color_response_key if not color_timed_out else "",
            "color_timed_out": bool(color_timed_out),
            "color_rt": color_rt_s,
            "color_rt_s": color_rt_s,
            "chosen_color": chosen_color if chosen_color else "none",
            "chosen_color_cn": _color_name(chosen_color, color_labels) if chosen_color else "none",
            "token_color_cn": _color_name(spec.token_color, color_labels),
            "chose_majority": chose_majority,
            "bet_response_key": bet_response_key,
            "bet_percent": int(bet_percent) if bet_percent is not None else None,
            "bet_timed_out": bool(bet_timed_out),
            "bet_rt": bet_rt_s,
            "bet_rt_s": bet_rt_s,
            "won": won,
            "net_change": int(net_change),
            "points_before": int(points_before),
            "points_after": int(points_after),
            "bet_amount": int(bet_amount),
            "feedback_auto_bet": bool(feedback_meta.get("auto_bet", False)),
            "feedback_type": str(feedback_meta.get("feedback_type", "feedback")),
        }
    )

    controller.record_trial(
        order=str(spec.order),
        ratio_label=str(spec.ratio_label),
        chosen_color=str(chosen_color),
        token_color=str(spec.token_color),
        bet_percent=int(bet_percent) if bet_percent is not None else None,
        delta=int(net_change),
        color_timed_out=bool(color_timed_out),
        bet_timed_out=bool(bet_timed_out),
    )

    return trial_data
