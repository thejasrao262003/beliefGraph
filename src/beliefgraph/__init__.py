"""BeliefGraph: build an AND/OR justification graph from an assistant's memory text, then
revise stored conclusions selectively when evidence changes.

    graph = BeliefGraph(llm).build(view)          # LLM: OR-of-AND justifications per memory
    readings = BeliefGraph(llm).read_updates(view) # LLM: what each update does, how reliable
    actions = revise(view, graph, readings)        # TMS propagation: keep / withdraw / recompute / uncertain

``view`` is a memory snapshot: evidence (id, observed date, source, text), memories
(id, text), policies (id, text) and updates (id, observed date, source, text). It is the
benchmark's system view, but nothing here depends on the benchmark.
"""

from beliefgraph.core import BeliefGraph, DecomposedBeliefGraph, Graph, UpdateReading, revise

__all__ = ["BeliefGraph", "DecomposedBeliefGraph", "Graph", "UpdateReading", "revise"]
