"""Disk cache for LLM calls: a response is stored once and never re-billed on a rerun."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

_KEY_PREFIX = "bg-build-v1|bg-read-v1"


class CachedLLM:
    """Wraps an LLM callable; each response is saved under ``raw_dir`` with its usage."""

    def __init__(self, llm, raw_dir: Path):
        self.llm, self.raw_dir, self.calls = llm, Path(raw_dir), 0
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def __call__(self, system: str, message: str, note: str = "") -> str:
        # The system prompt text identifies the prompt (and its version). The key prefix is
        # frozen at the first versions' names so earlier cached responses stay valid when a
        # prompt is revised (the revised text alone changes its own calls' keys).
        key = hashlib.sha256(f"{_KEY_PREFIX}|{getattr(self.llm, 'model', '')}|{system}|{message}"
                             .encode()).hexdigest()[:16]
        path = self.raw_dir / f"{note.replace(' ', '.')}.{key}.json"
        if path.exists():
            return json.loads(path.read_text())["response"]
        t0 = time.monotonic()
        text = self.llm(system, message, note)
        seconds = round(time.monotonic() - t0, 2)
        self.calls += 1
        usage = dict(self.llm.usage[-1]) if getattr(self.llm, "usage", None) else {}
        usage["seconds"] = seconds
        path.write_text(json.dumps({"note": note, "model": getattr(self.llm, "model", ""), "response": text,
                                    "usage": usage}, indent=1, default=str))
        return text
