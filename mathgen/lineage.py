"""Data lineage / provenance tracking.

AGENTS.md requirement: every data file must be traceable -- who produced it,
who consumed it -- one level up and one level down.

Implementation:
  * Each artifact ``<file>`` gets a sidecar ``<file>.lineage.json`` recording how
    it was produced (tool, version, git commit, command, seed, config, sources,
    upstream inputs) and a growing list of downstream consumers.
  * A central append-only ``<lineage_dir>/manifest.jsonl`` logs every produce /
    consume event so the whole graph can be reconstructed.
  * ``trace(path)`` answers the "one level up / one level down" question.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

TOOL_NAME = "mathgen"
TOOL_VERSION = "0.1.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit() -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def sidecar_path(artifact: Path) -> Path:
    return artifact.with_name(artifact.name + ".lineage.json")


@dataclass
class ProducedBy:
    tool: str = TOOL_NAME
    version: str = TOOL_VERSION
    git_commit: Optional[str] = None
    command: List[str] = field(default_factory=list)
    seed: Optional[int] = None
    config: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    code_modules: List[str] = field(default_factory=list)
    # "up one level": files/specs this artifact was derived from.
    inputs: List[Dict[str, Any]] = field(default_factory=list)


def _append_manifest(lineage_dir: Path, event: Dict[str, Any]) -> None:
    lineage_dir.mkdir(parents=True, exist_ok=True)
    with (lineage_dir / "manifest.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def record_production(
    artifact: Path,
    produced_by: ProducedBy,
    *,
    records: int,
    lineage_dir: Optional[Path] = None,
) -> Path:
    """Write the sidecar for a freshly produced artifact and log a produce event."""
    artifact = Path(artifact)
    lineage_dir = lineage_dir or (artifact.parent / "lineage")
    if produced_by.git_commit is None:
        produced_by.git_commit = git_commit()

    doc = {
        "artifact": str(artifact),
        "sha256": sha256_of(artifact),
        "bytes": artifact.stat().st_size,
        "records": records,
        "created_at": _now(),
        "produced_by": asdict(produced_by),
        # "down one level": filled in as downstream steps consume this artifact.
        "consumed_by": [],
    }
    sc = sidecar_path(artifact)
    sc.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _append_manifest(
        lineage_dir,
        {
            "event": "produce",
            "at": doc["created_at"],
            "artifact": str(artifact),
            "sha256": doc["sha256"],
            "records": records,
            "git_commit": produced_by.git_commit,
            "sources": produced_by.sources,
            "inputs": [i.get("ref") or i for i in produced_by.inputs],
        },
    )
    return sc


def record_consumption(
    artifact: Path,
    consumer: str,
    *,
    note: str = "",
    outputs: Optional[List[str]] = None,
    lineage_dir: Optional[Path] = None,
) -> None:
    """Log that ``consumer`` used ``artifact`` (the "down one level" edge)."""
    artifact = Path(artifact)
    lineage_dir = lineage_dir or (artifact.parent / "lineage")
    at = _now()
    entry = {"consumer": consumer, "at": at, "note": note, "outputs": outputs or []}

    sc = sidecar_path(artifact)
    if sc.exists():
        doc = json.loads(sc.read_text(encoding="utf-8"))
        doc.setdefault("consumed_by", []).append(entry)
        sc.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _append_manifest(
        lineage_dir,
        {
            "event": "consume",
            "at": at,
            "artifact": str(artifact),
            "consumer": consumer,
            "note": note,
            "outputs": outputs or [],
        },
    )


def trace(artifact: Path) -> Dict[str, Any]:
    """Return one level up (producer + inputs) and one level down (consumers)."""
    artifact = Path(artifact)
    sc = sidecar_path(artifact)
    if not sc.exists():
        return {"artifact": str(artifact), "error": "no lineage sidecar found"}
    doc = json.loads(sc.read_text(encoding="utf-8"))
    pb = doc.get("produced_by", {})
    return {
        "artifact": str(artifact),
        "up": {
            "produced_by": {
                "tool": pb.get("tool"),
                "version": pb.get("version"),
                "git_commit": pb.get("git_commit"),
                "command": pb.get("command"),
                "code_modules": pb.get("code_modules"),
            },
            "inputs": pb.get("inputs", []),
        },
        "down": doc.get("consumed_by", []),
    }
