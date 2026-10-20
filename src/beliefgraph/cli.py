"""beliefgraph CLI.

    beliefgraph providers
    beliefgraph build  snapshot.json --provider anthropic [--model M] [-o graph.json]
    beliefgraph revise snapshot.json --provider xai --model <id> [--graph graph.json]

A snapshot is JSON: {"scenario", "evidence": [{id, observed, source, text}],
"memories": [{id, text}], "policies": [{id, text}], "updates": [{id, observed, source, text}]}.
``revise`` prints the graph, how each update was read, and an action per memory
(keep / withdraw / recompute / uncertain).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from beliefgraph.core import BeliefGraph, Graph, revise
from beliefgraph.llm import KEY_ENV, OPENAI_COMPATIBLE, PROVIDERS, make_llm


def _llm(args):
    return make_llm(args.provider, model=args.model, base_url=args.base_url, budget_usd=args.budget_usd)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="beliefgraph")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("providers", help="list supported providers and their key variables")
    for name in ("build", "revise"):
        p = sub.add_parser(name)
        p.add_argument("snapshot", type=Path)
        p.add_argument("--provider", required=True, choices=PROVIDERS)
        p.add_argument("--model", default=None)
        p.add_argument("--base-url", default=None, help="for openai-compatible servers")
        p.add_argument("--budget-usd", type=float, default=1.0, help="hard cap (lyzr provider)")
        if name == "build":
            p.add_argument("-o", "--out", type=Path, default=None)
        else:
            p.add_argument("--graph", type=Path, default=None, help="reuse a graph from `build`")
    args = ap.parse_args(argv)

    if args.cmd == "providers":
        for p in PROVIDERS:
            url = OPENAI_COMPATIBLE.get(p, (None,))[0]
            print(f"{p:18s} key: {' or '.join(KEY_ENV[p]) or '(none)'}" + (f"  base: {url}" if url else ""))
        return
    view = json.loads(args.snapshot.read_text())
    llm = _llm(args)
    bg = BeliefGraph(llm)
    try:
        if args.cmd == "build":
            graph = bg.build(view)
            text = json.dumps(asdict(graph), indent=1)
            (args.out.write_text(text) if args.out else print(text))
        else:
            graph = Graph(**json.loads(args.graph.read_text())) if args.graph else bg.build(view)
            readings, errors = bg.read_updates(view)
            actions = revise(view, graph.justifications, graph.reliability, readings)
            print(json.dumps({"graph": asdict(graph), "updates": {k: asdict(v) for k, v in readings.items()},
                              "update_errors": errors,
                              "actions": {k: v.value for k, v in actions.items()
                                          if k in {m["id"] for m in view["memories"]}}}, indent=1))
    finally:
        if hasattr(llm, "close"):
            llm.close()
    print(json.dumps({"usage": llm.usage}), file=sys.stderr)


if __name__ == "__main__":
    main()
