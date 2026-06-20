from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from psychopy import logging

COLOR_RED = "red"
COLOR_BLUE = "blue"
ORDER_ASCENDING = "ascending"
ORDER_DESCENDING = "descending"
DEFAULT_BET_OPTIONS = (5, 25, 50, 75, 95)
DEFAULT_RATIO_PAIRS = ((9, 1), (8, 2), (7, 3), (6, 4))
DEFAULT_BLOCK_ORDER = (ORDER_ASCENDING, ORDER_DESCENDING)


@dataclass(frozen=True)
class TrialSpec:
    order: str
    ratio_label: str
    red_boxes: int
    blue_boxes: int
    majority_color: str
    minority_color: str
    token_color: str
    bet_options: tuple[int, ...]
    red_left: bool


class Controller:
    """Cambridge Gambling Task controller for trial sampling and point updates."""

    def __init__(
        self,
        initial_points: int = 100,
        box_ratios: list[list[int]] | tuple[tuple[int, int], ...] | None = None,
        bet_options: list[int] | tuple[int, ...] | None = None,
        block_order: list[str] | tuple[str, ...] | None = None,
        enable_logging: bool = True,
    ):
        self.initial_points = max(1, int(initial_points))
        self.enable_logging = bool(enable_logging)

        self.box_ratios = self._normalize_ratios(box_ratios)
        self.bet_options = self._normalize_bet_options(bet_options)
        self.block_order = self._normalize_block_order(block_order)

        self.current_points = int(self.initial_points)
        self.block_idx = -1
        self.trial_count_total = 0
        self.trial_count_block = 0

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "Controller":
        cfg = dict(config or {})
        return cls(
            initial_points=cfg.get("initial_points", 100),
            box_ratios=cfg.get("box_ratios", None),
            bet_options=cfg.get("bet_options", None),
            block_order=cfg.get("block_order", None),
            enable_logging=bool(cfg.get("enable_logging", True)),
        )

    @staticmethod
    def _normalize_ratios(value: Any) -> tuple[tuple[int, int], ...]:
        if not isinstance(value, (list, tuple)):
            return tuple(DEFAULT_RATIO_PAIRS)

        clean: list[tuple[int, int]] = []
        for pair in value:
            if not isinstance(pair, (list, tuple)) or len(pair) < 2:
                continue
            try:
                a = int(round(float(pair[0])))
                b = int(round(float(pair[1])))
            except Exception:
                continue
            if a <= 0 or b <= 0:
                continue
            total = a + b
            if total <= 0:
                continue
            # CGT uses 10 boxes; normalize any valid pair to preserve ratio shape.
            if total != 10:
                scale = 10.0 / float(total)
                a = max(1, int(round(a * scale)))
                b = max(1, int(round(b * scale)))
                drift = (a + b) - 10
                if drift != 0:
                    if a >= b:
                        a = max(1, a - drift)
                    else:
                        b = max(1, b - drift)
                if (a + b) != 10:
                    continue
            major, minor = (a, b) if a >= b else (b, a)
            clean.append((major, minor))

        return tuple(clean) if clean else tuple(DEFAULT_RATIO_PAIRS)

    @staticmethod
    def _normalize_bet_options(value: Any) -> tuple[int, ...]:
        if not isinstance(value, (list, tuple)):
            return tuple(DEFAULT_BET_OPTIONS)

        clean: list[int] = []
        for raw in value:
            try:
                pct = int(round(float(raw)))
            except Exception:
                continue
            if 1 <= pct <= 95:
                clean.append(pct)

        # Remove duplicates while preserving order.
        seen: set[int] = set()
        uniq: list[int] = []
        for pct in clean:
            if pct in seen:
                continue
            seen.add(pct)
            uniq.append(pct)

        if len(uniq) < 3:
            return tuple(DEFAULT_BET_OPTIONS)
        return tuple(sorted(uniq))

    @staticmethod
    def _normalize_block_order(value: Any) -> tuple[str, ...]:
        if not isinstance(value, (list, tuple)):
            return tuple(DEFAULT_BLOCK_ORDER)

        clean: list[str] = []
        for raw in value:
            token = str(raw).strip().lower()
            if token in {ORDER_ASCENDING, ORDER_DESCENDING}:
                clean.append(token)

        if not clean:
            return tuple(DEFAULT_BLOCK_ORDER)
        return tuple(clean)

    def start_block(self, block_idx: int) -> None:
        self.block_idx = int(block_idx)
        self.trial_count_block = 0

    def current_order(self, block_idx: int | None = None) -> str:
        idx = self.block_idx if block_idx is None else int(block_idx)
        if idx < 0:
            idx = 0
        return self.block_order[idx % len(self.block_order)]

    def apply_bet_outcome(self, *, bet_percent: int, won: bool) -> dict[str, int]:
        points_before = int(self.current_points)
        pct = max(1, min(95, int(bet_percent)))
        bet_amount = int(round(points_before * (float(pct) / 100.0)))
        if points_before > 0 and bet_amount <= 0:
            bet_amount = 1

        delta = bet_amount if bool(won) else -bet_amount
        points_after = max(0, points_before + delta)
        self.current_points = int(points_after)

        return {
            "points_before": int(points_before),
            "bet_amount": int(bet_amount),
            "delta": int(delta),
            "points_after": int(points_after),
        }

    def no_bet_update(self) -> dict[str, int]:
        points = int(self.current_points)
        return {
            "points_before": int(points),
            "bet_amount": 0,
            "delta": 0,
            "points_after": int(points),
        }

    def record_trial(
        self,
        *,
        order: str,
        ratio_label: str,
        chosen_color: str,
        token_color: str,
        bet_percent: int | None,
        delta: int,
        color_timed_out: bool,
        bet_timed_out: bool,
    ) -> None:
        self.trial_count_total += 1
        self.trial_count_block += 1

        if self.enable_logging:
            logging.data(
                "[CGT] "
                f"block={self.block_idx} "
                f"trial_block={self.trial_count_block} "
                f"trial_total={self.trial_count_total} "
                f"order={order} ratio={ratio_label} "
                f"chosen={chosen_color or 'none'} token={token_color or 'none'} "
                f"bet={bet_percent if bet_percent is not None else 'none'} "
                f"delta={int(delta)} points={self.current_points} "
                f"color_timeout={bool(color_timed_out)} bet_timeout={bool(bet_timed_out)}"
            )


def _sample_cgt_trial(
    *,
    rng: random.Random,
    order: str,
    box_ratios: tuple[tuple[int, int], ...],
    bet_options: tuple[int, ...],
) -> TrialSpec:
    major, minor = rng.choice(box_ratios)
    majority_color = COLOR_RED if rng.random() < 0.5 else COLOR_BLUE
    if majority_color == COLOR_RED:
        red_boxes, blue_boxes = major, minor
    else:
        red_boxes, blue_boxes = minor, major

    p_red = float(red_boxes) / float(max(1, red_boxes + blue_boxes))
    token_color = COLOR_RED if rng.random() < p_red else COLOR_BLUE
    minority_color = COLOR_BLUE if majority_color == COLOR_RED else COLOR_RED
    ordered_bets = bet_options if order == ORDER_ASCENDING else tuple(reversed(bet_options))

    return TrialSpec(
        order=order,
        ratio_label=f"{major}:{minor}",
        red_boxes=int(red_boxes),
        blue_boxes=int(blue_boxes),
        majority_color=majority_color,
        minority_color=minority_color,
        token_color=token_color,
        bet_options=tuple(int(v) for v in ordered_bets),
        red_left=bool(rng.random() < 0.5),
    )


def generate_cgt_conditions(
    n_trials: int,
    condition_labels: list[Any] | None = None,
    *,
    seed: int = 0,
    block_idx: int = 0,
    box_ratios: Any = None,
    bet_options: Any = None,
    block_order: Any = None,
) -> list[tuple[Any, ...]]:
    """Build concrete Cambridge Gambling trial specs during block scheduling."""
    labels = [str(label).strip().lower() for label in (condition_labels or ["gambling"])]
    if not labels:
        labels = ["gambling"]
    ratios = Controller._normalize_ratios(box_ratios)
    bets = Controller._normalize_bet_options(bet_options)
    orders = Controller._normalize_block_order(block_order)
    order = orders[int(block_idx) % len(orders)]
    rng = random.Random(int(seed))

    scheduled: list[tuple[Any, ...]] = []
    for trial_index in range(int(n_trials)):
        condition_name = labels[trial_index % len(labels)]
        spec = _sample_cgt_trial(rng=rng, order=order, box_ratios=ratios, bet_options=bets)
        scheduled.append(
            (
                condition_name,
                spec.order,
                spec.ratio_label,
                spec.red_boxes,
                spec.blue_boxes,
                spec.majority_color,
                spec.minority_color,
                spec.token_color,
                spec.bet_options,
                spec.red_left,
            )
        )
    return scheduled


def cgt_condition_to_trial_spec(condition: Any) -> tuple[str, TrialSpec]:
    """Decode a scheduled Cambridge Gambling condition tuple."""
    if isinstance(condition, (tuple, list)) and len(condition) >= 10:
        (
            condition_name,
            order,
            ratio_label,
            red_boxes,
            blue_boxes,
            majority_color,
            minority_color,
            token_color,
            bet_options,
            red_left,
        ) = condition[:10]
        return str(condition_name).strip().lower(), TrialSpec(
            order=str(order),
            ratio_label=str(ratio_label),
            red_boxes=int(red_boxes),
            blue_boxes=int(blue_boxes),
            majority_color=str(majority_color),
            minority_color=str(minority_color),
            token_color=str(token_color),
            bet_options=tuple(int(v) for v in bet_options),
            red_left=bool(red_left),
        )
    raise ValueError(f"Expected scheduled CGT condition tuple, got {condition!r}")


def box_positions() -> list[tuple[float, float]]:
    return [(-450.0 + (100.0 * idx), 150.0) for idx in range(10)]


def bet_positions() -> list[tuple[float, float]]:
    return [(-320.0, -70.0), (-160.0, -70.0), (0.0, -70.0), (160.0, -70.0), (320.0, -70.0)]


def add_boxes(unit: Any, stim_bank: Any, *, red_boxes: int, blue_boxes: int, red_left: bool) -> None:
    left_color = COLOR_RED if red_left else COLOR_BLUE
    right_color = COLOR_BLUE if red_left else COLOR_RED
    left_count = int(red_boxes) if red_left else int(blue_boxes)
    right_count = int(blue_boxes) if red_left else int(red_boxes)

    color_tokens = [left_color] * left_count + [right_color] * right_count
    positions = box_positions()
    for idx in range(10):
        color_token = color_tokens[idx] if idx < len(color_tokens) else right_color
        fill_color = [0.92, 0.23, 0.23] if color_token == COLOR_RED else [0.24, 0.42, 0.95]
        unit.add_stim(
            stim_bank.rebuild(
                "box_token_template",
                text="â– ",
                pos=positions[idx],
                color=fill_color,
            )
        )


def add_bet_options(unit: Any, stim_bank: Any, bet_options: list[int], bet_keys: list[str]) -> str:
    positions = bet_positions()
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
