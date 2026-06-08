"""Core sample/trace schema shared by every generator domain.

A TraceStep is one verifiable symbolic operation; a Sample bundles the
user/assistant messages, the machine-readable answer, the structured trace,
metadata, and the verification flag described in docs/des_instruct.md.

Answer format (consistent across the whole dataset, see des_instruct.md sec 4):

    <think>
    ...step by step...
    </think>
    #### \\boxed{answer}
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional


def json_default(o: Any):
    """JSON encoder fallback: render exact rationals without floating-point error."""
    if isinstance(o, Fraction):
        return int(o) if o.denominator == 1 else f"{o.numerator}/{o.denominator}"
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


@dataclass
class TraceStep:
    op: str
    text: str
    before: Optional[str] = None
    after: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


@dataclass
class Sample:
    source: str
    messages: List[Dict[str, str]]
    answer: str
    trace: List[TraceStep]
    metadata: Dict[str, Any]
    verified: bool = True

    def to_json_obj(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "messages": self.messages,
            "answer": self.answer,
            "trace": [asdict(t) for t in self.trace],
            "metadata": self.metadata,
            "verified": self.verified,
        }


def make_sample(
    source: str,
    user: str,
    trace: List[TraceStep],
    answer: str,
    metadata: Optional[Dict[str, Any]] = None,
    verified: bool = True,
) -> Sample:
    reasoning = "\n".join(step.text for step in trace)
    assistant = f"<think>\n{reasoning}\n</think>\n#### \\boxed{{{answer}}}"
    return Sample(
        source=source,
        messages=[
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ],
        answer=answer,
        trace=trace,
        metadata=metadata or {},
        verified=verified,
    )
