"""Difficulty levels and generator configuration."""

from __future__ import annotations

import random
from dataclasses import dataclass


class Difficulty:
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    MIXED = "mixed"

    ALL = (EASY, MEDIUM, HARD)


@dataclass
class GenConfig:
    difficulty: str = Difficulty.MIXED


def pick_difficulty(rng: random.Random, cfg: GenConfig) -> str:
    if cfg.difficulty != Difficulty.MIXED:
        return cfg.difficulty
    return rng.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
