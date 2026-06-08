"""mathgen: programmatic, verifiable, difficulty-controlled math SFT data generator."""

from mathgen.config import Difficulty, GenConfig
from mathgen.core import Sample, TraceStep, make_sample

__all__ = ["Difficulty", "GenConfig", "Sample", "TraceStep", "make_sample"]
__version__ = "0.1.0"
