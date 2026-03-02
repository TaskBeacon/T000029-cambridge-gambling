from __future__ import annotations

from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core

from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskRunOptions,
    TaskSettings,
    context_from_config,
    count_down,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src import Controller, run_trial


def _make_qa_trigger_runtime():
    return initialize_triggers(mock=True)


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _parse_args(task_root: Path) -> TaskRunOptions:
    return parse_task_run_options(
        task_root=task_root,
        description="Run Cambridge Gambling Task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _as_float(value) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _as_int(value, default: int = 0) -> int:
    try:
        return int(round(float(value)))
    except Exception:
        return int(default)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def _summarize_trials(trials: list[dict], fallback_points: int = 100) -> dict[str, float | int]:
    if not trials:
        return {
            "quality_rate": 0.0,
            "win_rate": 0.0,
            "mean_bet_pct": 0.0,
            "mean_color_rt_ms": 0.0,
            "mean_bet_rt_ms": 0.0,
            "color_timeout_count": 0,
            "bet_timeout_count": 0,
            "net_sum": 0,
            "points_end": int(fallback_points),
            "delay_aversion": 0.0,
            "ascending_mean_bet": 0.0,
            "descending_mean_bet": 0.0,
        }

    color_timeout_count = sum(1 for row in trials if _as_bool(row.get("color_timed_out", False)))
    bet_timeout_count = sum(1 for row in trials if _as_bool(row.get("bet_timed_out", False)))

    quality_values = [row.get("chose_majority", None) for row in trials if row.get("chose_majority", None) is not None]
    quality_rate = (
        sum(1 for v in quality_values if _as_bool(v)) / len(quality_values)
        if quality_values
        else 0.0
    )

    win_values = [row.get("won", None) for row in trials if row.get("won", None) is not None]
    win_rate = (
        sum(1 for v in win_values if _as_bool(v)) / len(win_values)
        if win_values
        else 0.0
    )

    bet_values = [_as_float(row.get("bet_percent", None)) for row in trials]
    bet_values = [v for v in bet_values if v is not None]
    mean_bet_pct = _mean(bet_values)

    color_rt_values = [_as_float(row.get("color_rt_s", None)) for row in trials]
    color_rt_values = [v for v in color_rt_values if v is not None]
    mean_color_rt_ms = _mean(color_rt_values) * 1000.0 if color_rt_values else 0.0

    bet_rt_values = [_as_float(row.get("bet_rt_s", None)) for row in trials]
    bet_rt_values = [v for v in bet_rt_values if v is not None]
    mean_bet_rt_ms = _mean(bet_rt_values) * 1000.0 if bet_rt_values else 0.0

    ascending_bets: list[float] = []
    descending_bets: list[float] = []
    for row in trials:
        bet = _as_float(row.get("bet_percent", None))
        if bet is None:
            continue
        order = str(row.get("bet_order", "")).strip().lower()
        if order == "ascending":
            ascending_bets.append(bet)
        elif order == "descending":
            descending_bets.append(bet)

    ascending_mean_bet = _mean(ascending_bets)
    descending_mean_bet = _mean(descending_bets)
    delay_aversion = descending_mean_bet - ascending_mean_bet

    net_sum = sum(_as_int(row.get("net_change", 0)) for row in trials)

    points_end = int(fallback_points)
    for row in reversed(trials):
        if row.get("points_after", None) is not None:
            points_end = _as_int(row.get("points_after"), fallback_points)
            break

    return {
        "quality_rate": float(quality_rate),
        "win_rate": float(win_rate),
        "mean_bet_pct": float(mean_bet_pct),
        "mean_color_rt_ms": float(mean_color_rt_ms),
        "mean_bet_rt_ms": float(mean_bet_rt_ms),
        "color_timeout_count": int(color_timeout_count),
        "bet_timeout_count": int(bet_timeout_count),
        "net_sum": int(net_sum),
        "points_end": int(points_end),
        "delay_aversion": float(delay_aversion),
        "ascending_mean_bet": float(ascending_mean_bet),
        "descending_mean_bet": float(descending_mean_bet),
    }


def run(options: TaskRunOptions):
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))
    mode = options.mode

    ctx = None
    if mode in ("qa", "sim"):
        ctx = context_from_config(task_dir=task_root, config=cfg, mode=mode)
        sim_participant = "sim"
        if ctx.session is not None:
            sim_participant = str(ctx.session.participant_id or "sim")
        with runtime_context(ctx):
            _run_impl(mode=mode, output_dir=ctx.output_dir, cfg=cfg, participant_id=sim_participant)
    else:
        _run_impl(mode=mode, output_dir=None, cfg=cfg, participant_id="human")


def _run_impl(*, mode: str, output_dir: Path | None, cfg: dict, participant_id: str):
    if mode == "qa":
        subject_data = {"subject_id": "qa"}
    elif mode == "sim":
        subject_data = {"subject_id": participant_id}
    else:
        subform = SubInfo(cfg["subform_config"])
        subject_data = subform.collect()

    settings = TaskSettings.from_dict(cfg["task_config"])
    if mode in ("qa", "sim") and output_dir is not None:
        settings.save_path = str(output_dir)

    settings.add_subinfo(subject_data)

    if mode == "qa" and output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        settings.res_file = str(output_dir / "qa_trace.csv")
        settings.log_file = str(output_dir / "qa_psychopy.log")
        settings.json_file = str(output_dir / "qa_settings.json")

    settings.triggers = cfg["trigger_config"]
    if mode in ("qa", "sim"):
        trigger_runtime = _make_qa_trigger_runtime()
    else:
        trigger_runtime = initialize_triggers(cfg)

    win, kb = initialize_exp(settings)

    stim_bank = StimBank(win, cfg["stim_config"])
    if mode not in ("qa", "sim"):
        stim_bank = stim_bank.convert_to_voice("instruction_text")
    stim_bank = stim_bank.preload_all()

    settings.controller = cfg["controller_config"]
    settings.save_to_json()
    controller = Controller.from_dict(settings.controller)

    trigger_runtime.send(settings.triggers.get("exp_onset"))

    instr = StimUnit("instruction_text", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get("instruction_text")
    )
    if mode not in ("qa", "sim"):
        instr.add_stim(stim_bank.get("instruction_text_voice"))
    instr.wait_and_continue()

    all_data: list[dict] = []
    total_blocks = int(getattr(settings, "total_blocks", 1))
    for block_i in range(total_blocks):
        controller.start_block(block_i)
        if mode not in ("qa", "sim"):
            count_down(win, 3, color="black")

        block = (
            BlockUnit(
                block_id=f"block_{block_i}",
                block_idx=block_i,
                settings=settings,
                window=win,
                keyboard=kb,
            )
            .generate_conditions()
            .on_start(lambda b: trigger_runtime.send(settings.triggers.get("block_onset")))
            .on_end(lambda b: trigger_runtime.send(settings.triggers.get("block_end")))
            .run_trial(
                partial(
                    run_trial,
                    stim_bank=stim_bank,
                    controller=controller,
                    trigger_runtime=trigger_runtime,
                    block_id=f"block_{block_i}",
                    block_idx=block_i,
                )
            )
            .to_dict(all_data)
        )

        block_summary = _summarize_trials(block.get_all_data(), fallback_points=int(controller.current_points))

        if block_i < (total_blocks - 1):
            StimUnit("block", win, kb, runtime=trigger_runtime).add_stim(
                stim_bank.get_and_format(
                    "block_break",
                    block_num=block_i + 1,
                    total_blocks=total_blocks,
                    points_end=block_summary["points_end"],
                    block_net=block_summary["net_sum"],
                    quality_rate=block_summary["quality_rate"],
                    win_rate=block_summary["win_rate"],
                    mean_bet_pct=block_summary["mean_bet_pct"],
                    mean_color_rt_ms=block_summary["mean_color_rt_ms"],
                    mean_bet_rt_ms=block_summary["mean_bet_rt_ms"],
                    color_timeout_count=block_summary["color_timeout_count"],
                    bet_timeout_count=block_summary["bet_timeout_count"],
                    delay_aversion=block_summary["delay_aversion"],
                )
            ).wait_and_continue()

    overall = _summarize_trials(all_data, fallback_points=int(controller.current_points))

    StimUnit("goodbye", win, kb, runtime=trigger_runtime).add_stim(
        stim_bank.get_and_format(
            "good_bye",
            total_trials=len(all_data),
            points_end=overall["points_end"],
            net_total=overall["net_sum"],
            quality_rate=overall["quality_rate"],
            win_rate=overall["win_rate"],
            mean_bet_pct=overall["mean_bet_pct"],
            mean_color_rt_ms=overall["mean_color_rt_ms"],
            mean_bet_rt_ms=overall["mean_bet_rt_ms"],
            color_timeout_count=overall["color_timeout_count"],
            bet_timeout_count=overall["bet_timeout_count"],
            delay_aversion=overall["delay_aversion"],
            ascending_mean_bet=overall["ascending_mean_bet"],
            descending_mean_bet=overall["descending_mean_bet"],
        )
    ).wait_and_continue(terminate=True)

    trigger_runtime.send(settings.triggers.get("exp_end"))

    pd.DataFrame(all_data).to_csv(settings.res_file, index=False)

    trigger_runtime.close()
    core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = _parse_args(task_root)
    run(options)


if __name__ == "__main__":
    main()
