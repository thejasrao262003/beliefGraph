"""Quantization study table: balanced accuracy per configuration on the same dossiers, restricted
to the dossiers every listed run has finished (BF16 baseline: data/beliefgraph/long-v08-gemma-4-12b-it).

    uv run python scripts/quant_table.py quant-sub-gemma-4-12b-it-fp8-dynamic ...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

METHODS = ("BeliefGraph", "LLM-direct", "LLM-RAG")


def load(run: str) -> dict:
    return json.loads((Path("data/beliefgraph") / run / "results.json").read_text())["sizes"]


def main() -> None:
    runs = ["long-v08-gemma-4-12b-it", *sys.argv[1:]]
    data = {r: load(r) for r in runs}
    keys = sorted(set.intersection(*(set(d) for d in data.values())))
    print(f"{len(keys)} dossiers in common | balanced accuracy (stale / over-invalidation)")
    print(f"{'configuration':45s} " + " ".join(f"{m:>22s}" for m in METHODS))
    for r in runs:
        cells = []
        for m in METHODS:
            fins = [data[r][k]["final"][m] for k in keys if m in data[r][k]["final"]]
            bal = [f["balanced"] for f in fins if f.get("balanced") is not None]
            st = sum(f["stale"] or 0 for f in fins) / len(fins)
            ov = sum(f["over_invalidation"] or 0 for f in fins) / len(fins)
            cells.append(f"{sum(bal) / len(bal):.3f} ({st:.2f}/{ov:.2f})")
        print(f"{r:45s} " + " ".join(f"{c:>22s}" for c in cells))


if __name__ == "__main__":
    main()
