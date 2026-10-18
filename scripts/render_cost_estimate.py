"""Cost estimate for rendering, built from the real prompts. Makes no model calls.

    uv run python scripts/render_cost_estimate.py

Token counts use chars / 4 for input (the usual English heuristic; ±25%). Output is
estimated from the response schema. Prices: official Gemini API pricing page, last
updated 2026-10-16 (https://ai.google.dev/gemini-api/docs/pricing). Check them again on
the day of the run.
"""

from __future__ import annotations

from beliefbench.generate import generate_suite
from beliefbench.render.prompt import SYSTEM_PROMPT, user_message

# USD per 1M tokens: (input, output). "now" = introductory, "after" = list price after
# the intro period ends (argon: after 2026-11-30; 3.8 flash: after 2026-12-31).
PRICES = {
    "gemini-4-argon": {"now": (2.00, 10.00), "after": (4.00, 20.00)},
    "gemini-3.8-flash": {"now": (0.75, 3.75), "after": (1.50, 7.50)},
}
THINKING = {"expected": 2_000, "upper": 8_000}  # per call; capped via the thinking budget setting
CALLS = {"expected": 1.3, "upper": 3.0}  # per scenario, incl. retries for invalid / rejected renderings
OUT_JSON_OVERHEAD = 1.3


def output_tokens(s) -> int:
    text = 60 * len(s.nodes) + 60 * len(s.updates)  # text + source per item, ~45 words max
    rationale = 35 * sum(len(n.justifications) for n in s.nodes if not n.is_evidence)
    return int((40 + text + rationale) * OUT_JSON_OVERHEAD)


def estimate(name: str, suite) -> list[str]:
    inp = sum((len(SYSTEM_PROMPT) + len(user_message(s))) / 4 for s in suite)
    out = sum(output_tokens(s) for s in suite)
    n = len(suite)
    lines = [f"### {name}: {n} scenarios",
             f"- per call: ~{inp / n:,.0f} input tokens, ~{out / n:,.0f} visible output tokens "
             f"(+ thinking {THINKING['expected']:,} expected / {THINKING['upper']:,} upper)",
             "", "| model | price period | expected | conservative upper bound |", "|---|---|---|---|"]
    for model, periods in PRICES.items():
        for period, (pin, pout) in periods.items():
            cost = {}
            for case in ("expected", "upper"):
                calls = CALLS[case]
                tok_in = inp * calls
                tok_out = (out + THINKING[case] * n) * calls
                cost[case] = (tok_in * pin + tok_out * pout) / 1e6
            lines.append(f"| `{model}` | {period} ${pin:.2f}/${pout:.2f} | ${cost['expected']:.2f} | ${cost['upper']:.2f} |")
    return lines


def main() -> None:
    out = estimate("A. Renderer validation pilot (seed 0, 10/family)", generate_suite(10, seed=0))
    out += [""] + estimate("B. Evaluation-pilot rendering (seed 1, 25/family) - separate budget",
                           generate_suite(25, seed=1))
    print("\n".join(out))


if __name__ == "__main__":
    main()
