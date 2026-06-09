#!/usr/bin/env python3
"""用修好的生成器构建一套**全局去重 + 无泄漏**的数据集（多进程并行版）。

每个 source 独立(并行)生成唯一题池(按题面去重 + validate 过滤)，按 source 互斥切成
test/val/train 写成 shard；主进程合并时再做**全局去重**：先收集 test+val 全部题面，
train 丢弃任何与 test/val 重合或 train 内重复的题 → 跨集合泄漏 = 0、集合内重复 = 0。
每条样本自带 source/difficulty，供下游"按 source 切桶"的动态课程直接用。

用法:
  python scripts/build_dataset.py --out data/clean --cap 3000 --workers 40
"""
from __future__ import annotations
import argparse, hashlib, json, os, random
import multiprocessing as mp
from pathlib import Path

from mathgen.config import GenConfig, Difficulty
from mathgen.core import json_default
from mathgen.registry import GENERATORS
from mathgen.validate import validate_sample

CFG = GenConfig(difficulty=Difficulty.MIXED)


def _qhash(s: str) -> bytes:
    return hashlib.md5(s.encode("utf-8")).digest()


def build_source_shard(args):
    """子进程：为一个 source 生成唯一池、按 source 内互斥切分、写 3 个 shard。返回统计。"""
    name, cap, attempt_mult, test_frac, val_frac, seed, shard_dir = args
    fn = GENERATORS[name]
    rng = random.Random(seed)
    seen, pool = set(), []
    attempts, max_attempts = 0, cap * attempt_mult
    while len(pool) < cap and attempts < max_attempts:
        attempts += 1
        s = fn(rng, CFG)
        ok, _ = validate_sample(s)
        if not ok:
            continue
        q = s.messages[0]["content"]
        if q in seen:
            continue
        seen.add(q)
        pool.append(s)
    random.Random(seed * 31 + 7).shuffle(pool)
    n = len(pool)
    nt = int(n * test_frac)
    nv = int(n * val_frac)
    splits = {"test": pool[:nt], "val": pool[nt:nt + nv], "train": pool[nt + nv:]}
    safe = name.replace("/", "_").replace(".", "_")
    for split, rows in splits.items():
        with (Path(shard_dir) / f"{safe}.{split}.jsonl").open("w", encoding="utf-8") as f:
            for s in rows:
                f.write(json.dumps(s.to_json_obj(), ensure_ascii=False, default=json_default) + "\n")
    return {"source": name, "unique": n, "attempts": attempts,
            "saturated": attempts >= max_attempts and n < cap,
            "train": len(splits["train"]), "val": len(splits["val"]), "test": len(splits["test"])}


def _merge(shard_dir: Path, out: Path):
    """合并 shard：test/val 各自按题面去重；train 丢弃与 test/val 重合或自身重复的题。"""
    def read_split(split):
        rows = []
        for f in sorted(shard_dir.glob(f"*.{split}.jsonl")):
            with f.open(encoding="utf-8") as fh:
                rows.extend(fh)
        return rows

    # test / val：按题面全局去重
    held_hashes = set()
    counts = {}
    for split in ("test", "val"):
        seen = set()
        kept = []
        for line in read_split(split):
            q = json.loads(line)["messages"][0]["content"]
            h = _qhash(q)
            if h in seen:
                continue
            seen.add(h)
            held_hashes.add(h)
            kept.append(line)
        path = out / ("test/id_test.jsonl" if split == "test" else "val.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            fh.writelines(kept)
        counts[split] = len(kept)

    # train：丢弃与 test/val 重合 或 train 内重复
    seen = set()
    kept = 0
    dropped_leak = 0
    with (out / "train.jsonl").open("w", encoding="utf-8") as fh:
        for line in read_split("train"):
            q = json.loads(line)["messages"][0]["content"]
            h = _qhash(q)
            if h in held_hashes:
                dropped_leak += 1
                continue
            if h in seen:
                continue
            seen.add(h)
            fh.write(line)
            kept += 1
    counts["train"] = kept
    counts["dropped_leak"] = dropped_leak
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data/clean")
    ap.add_argument("--cap", type=int, default=3000, help="每 source 唯一题上限")
    ap.add_argument("--attempt-mult", type=int, default=10)
    ap.add_argument("--test-frac", type=float, default=0.08)
    ap.add_argument("--val-frac", type=float, default=0.08)
    ap.add_argument("--seed", type=int, default=20260609)
    ap.add_argument("--workers", type=int, default=min(40, mp.cpu_count()))
    args = ap.parse_args()

    out = Path(args.out)
    shard_dir = out / "_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    for old in shard_dir.glob("*.jsonl"):
        old.unlink()

    names = list(GENERATORS)
    tasks = [(name, args.cap, args.attempt_mult, args.test_frac, args.val_frac, args.seed + i, str(shard_dir))
             for i, name in enumerate(names)]

    print(f"并行生成: {len(names)} sources × cap {args.cap}，{args.workers} workers", flush=True)
    manifest = {}
    done = 0
    with mp.Pool(args.workers) as pool:
        for st in pool.imap_unordered(build_source_shard, tasks):
            manifest[st["source"]] = st
            done += 1
            if done % 20 == 0:
                print(f"  [{done}/{len(names)}] ...", flush=True)

    print("合并 + 全局去重 ...", flush=True)
    counts = _merge(shard_dir, out)
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    small = sum(1 for v in manifest.values() if v["unique"] < args.cap)
    print("=" * 70, flush=True)
    print(f"train={counts['train']:,}  val={counts['val']:,}  test={counts['test']:,}", flush=True)
    print(f"train 因泄漏/重复丢弃: {counts['dropped_leak']}  (跨集合泄漏已清零)", flush=True)
    print(f"小空间 source(唯一题 < cap={args.cap}): {small} / {len(names)}", flush=True)
    print(f"输出 -> {out}", flush=True)


if __name__ == "__main__":
    main()
