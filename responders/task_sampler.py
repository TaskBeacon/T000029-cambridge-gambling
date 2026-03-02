from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import random as _py_random

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    """Sampler responder for Cambridge Gambling Task color+bet phases."""

    quality_rate: float = 0.8
    miss_color_rate: float = 0.05
    miss_bet_rate: float = 0.08
    risk_preference: float = 0.55
    rt_mean_s: float = 0.55
    rt_sd_s: float = 0.12
    rt_min_s: float = 0.18

    def __post_init__(self) -> None:
        self._rng: Any = None
        self.quality_rate = max(0.0, min(1.0, float(self.quality_rate)))
        self.miss_color_rate = max(0.0, min(1.0, float(self.miss_color_rate)))
        self.miss_bet_rate = max(0.0, min(1.0, float(self.miss_bet_rate)))
        self.risk_preference = max(0.0, min(1.0, float(self.risk_preference)))
        self.rt_mean_s = float(self.rt_mean_s)
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _sample_normal(self, mean: float, sd: float) -> float:
        rng = self._rng
        if hasattr(rng, "normal"):
            return float(rng.normal(mean, sd))
        return float(rng.gauss(mean, sd))

    def _sample_random(self) -> float:
        rng = self._rng
        if hasattr(rng, "random"):
            return float(rng.random())
        return float(_py_random.random())

    def _continue_action(self, valid_keys: list[str], phase: str) -> Action:
        key = "space" if "space" in valid_keys else valid_keys[0]
        rt = max(self.rt_min_s, self._sample_normal(self.rt_mean_s, self.rt_sd_s))
        return Action(
            key=key,
            rt_s=rt,
            meta={"source": "task_sampler", "phase": phase, "outcome": "continue"},
        )

    def _choose_color(self, valid_keys: list[str], factors: dict[str, Any]) -> str:
        majority_key = str(factors.get("majority_key", "")).strip().lower()
        minority_key = str(factors.get("minority_key", "")).strip().lower()

        if majority_key not in valid_keys:
            majority_key = valid_keys[0]
        if minority_key not in valid_keys:
            if len(valid_keys) > 1:
                minority_key = valid_keys[-1]
            else:
                minority_key = majority_key

        choose_majority = self._sample_random() < self.quality_rate
        return majority_key if choose_majority else minority_key

    def _choose_bet_key(self, valid_keys: list[str], factors: dict[str, Any]) -> str:
        key_map_raw = factors.get("bet_key_map", {})
        key_map: dict[str, float] = {}
        if isinstance(key_map_raw, dict):
            for k, v in key_map_raw.items():
                key = str(k).strip().lower()
                if key not in valid_keys:
                    continue
                try:
                    key_map[key] = float(v)
                except Exception:
                    continue

        if not key_map:
            for idx, key in enumerate(valid_keys):
                key_map[key] = float(idx + 1)

        options = sorted(key_map.items(), key=lambda kv: kv[1])
        if len(options) == 1:
            return options[0][0]

        mean_idx = self.risk_preference * (len(options) - 1)
        noisy_idx = mean_idx + self._sample_normal(0.0, 0.75)
        idx = int(round(noisy_idx))
        idx = max(0, min(len(options) - 1, idx))
        return options[idx][0]

    def act(self, obs: Observation) -> Action:
        valid_keys = [str(k).strip().lower() for k in list(obs.valid_keys or []) if str(k).strip()]
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})

        if self._rng is None:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "rng_missing"})

        phase = str(obs.phase or "")
        factors = dict(obs.task_factors or {})

        if phase == "color_choice":
            if self._sample_random() < self.miss_color_rate:
                return Action(key=None, rt_s=None, meta={"source": "task_sampler", "outcome": "color_timeout"})
            chosen = self._choose_color(valid_keys, factors)
            rt = max(self.rt_min_s, self._sample_normal(self.rt_mean_s, self.rt_sd_s))
            return Action(
                key=chosen,
                rt_s=rt,
                meta={"source": "task_sampler", "outcome": "choose_color"},
            )

        if phase == "bet_choice":
            if self._sample_random() < self.miss_bet_rate:
                return Action(key=None, rt_s=None, meta={"source": "task_sampler", "outcome": "bet_timeout"})
            chosen = self._choose_bet_key(valid_keys, factors)
            rt = max(self.rt_min_s, self._sample_normal(self.rt_mean_s, self.rt_sd_s))
            return Action(
                key=chosen,
                rt_s=rt,
                meta={"source": "task_sampler", "outcome": "choose_bet"},
            )

        return self._continue_action(valid_keys, phase)
