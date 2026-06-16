"""TypedGraph traversal helpers (spec §3.1, §10).

The typed graph is small and authored by the generator — it is the navigation
structure (Tier-A links carry the weight), not a retrieval index. We back
traversal with networkx (spec §10: "no graph DB at this scale"). `TypedGraph`
exposes `neighbors()` / `traverse()` that delegate here; keeping the algorithms
in this module preserves `schemas.py` as a pure-contract single source of truth.
"""

from __future__ import annotations

import networkx as nx

from dh.schemas import Direction, EdgeType, Node, TypedGraph


def to_networkx(g: TypedGraph) -> nx.MultiDiGraph:
    """Build a directed multigraph keyed by edge type (edge attrs preserved)."""
    G = nx.MultiDiGraph()
    for n in g.nodes:
        G.add_node(n.id, node=n)
    for e in g.edges:
        G.add_edge(e.src, e.dst, key=e.type, type=e.type,
                   confidence=e.confidence, props=e.props)
    return G


def neighbors(
    g: TypedGraph,
    node_id: str,
    edge_type: EdgeType | None = None,
    direction: Direction = "out",
) -> list[Node]:
    """Direct neighbors of `node_id` along `edge_type` (any type if None).

    `direction="out"` follows edges where `node_id` is the source; `"in"`
    follows edges where it is the destination. Results are de-duplicated and
    returned in edge-declaration order.
    """
    if direction not in ("out", "in"):
        raise ValueError(f"direction must be 'out' or 'in', got {direction!r}")
    index = {n.id: n for n in g.nodes}
    result: list[Node] = []
    seen: set[str] = set()
    for e in g.edges:
        if direction == "out" and e.src == node_id:
            other = e.dst
        elif direction == "in" and e.dst == node_id:
            other = e.src
        else:
            continue
        if edge_type is not None and e.type != edge_type:
            continue
        if other in index and other not in seen:
            seen.add(other)
            result.append(index[other])
    return result


def traverse(
    g: TypedGraph,
    node_id: str,
    edge_type: EdgeType,
    direction: Direction = "out",
    max_depth: int | None = None,
) -> list[Node]:
    """BFS reachability from `node_id` following `edge_type` only.

    Returns reachable nodes (excluding the start) in breadth-first order.
    `max_depth=None` traverses to exhaustion; cycles are handled by a visited set.
    """
    visited: set[str] = {node_id}
    frontier: list[str] = [node_id]
    order: list[Node] = []
    depth = 0
    while frontier and (max_depth is None or depth < max_depth):
        nxt: list[str] = []
        for nid in frontier:
            for nb in neighbors(g, nid, edge_type, direction):
                if nb.id not in visited:
                    visited.add(nb.id)
                    nxt.append(nb.id)
                    order.append(nb)
        frontier = nxt
        depth += 1
    return order
