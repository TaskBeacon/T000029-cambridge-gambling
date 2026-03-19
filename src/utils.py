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
        random_seed: int | None = None,
        enable_logging: bool = True,
    ):
        self.initial_points = max(1, int(initial_points))
        self.enable_logging = bool(enable_logging)

        self.rng = random.Random(random_seed)

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
            random_seed=cfg.get("random_seed", None),
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

    def next_trial_id(self) -> int:
        return int(self.trial_count_total) + 1

    def _sample_ratio(self) -> tuple[int, int]:
        return self.rng.choice(self.box_ratios)

    def _sample_majority_color(self) -> str:
        return COLOR_RED if self.rng.random() < 0.5 else COLOR_BLUE

    def _sample_token_color(self, red_boxes: int, blue_boxes: int) -> str:
        p_red = float(red_boxes) / float(max(1, red_boxes + blue_boxes))
        return COLOR_RED if self.rng.random() < p_red else COLOR_BLUE

    def build_trial(self, *, block_idx: int | None = None) -> TrialSpec:
        order = self.current_order(block_idx)
        major, minor = self._sample_ratio()
        majority_color = self._sample_majority_color()
        if majority_color == COLOR_RED:
            red_boxes, blue_boxes = major, minor
        else:
            red_boxes, blue_boxes = minor, major

        token_color = self._sample_token_color(red_boxes, blue_boxes)
        minority_color = COLOR_BLUE if majority_color == COLOR_RED else COLOR_RED
        ratio_label = f"{major}:{minor}"
        bet_options = self.bet_options if order == ORDER_ASCENDING else tuple(reversed(self.bet_options))
        red_left = self.rng.random() < 0.5

        return TrialSpec(
            order=order,
            ratio_label=ratio_label,
            red_boxes=int(red_boxes),
            blue_boxes=int(blue_boxes),
            majority_color=majority_color,
            minority_color=minority_color,
            token_color=token_color,
            bet_options=tuple(int(v) for v in bet_options),
            red_left=bool(red_left),
        )

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
