"""Wheelchair-aware route planning with A* and Dijkstra (uniform cost search).

Costs are in "effort-km": a segment's length multiplied by a terrain factor.
A factor of float("inf") makes that terrain impassable.
"""
import heapq
import math
from dataclasses import dataclass, field

from forest_hill_map import LOCATIONS, build_segments, haversine_km

# Terrain cost multipliers for each routing profile
PROFILES = {
    "shortest": {"normal": 1.0, "steep": 1.0, "narrow": 1.0},              # distance only
    "wheelchair": {"normal": 1.0, "steep": 3.0, "narrow": 2.0},            # avoid barriers where reasonable
    "strict": {"normal": 1.0, "steep": math.inf, "narrow": math.inf},      # never use barriers
}
WHEELCHAIR_SPEED_KMH = 5.0


@dataclass
class Graph:
    coords: dict
    edges: dict = field(default_factory=dict)   # node -> {neighbour: (length_km, terrain)}

    def add(self, a, b, length, terrain):
        self.edges.setdefault(a, {})[b] = (length, terrain)
        self.edges.setdefault(b, {})[a] = (length, terrain)


def load_forest_hill():
    g = Graph(coords=dict(LOCATIONS))
    for a, b, length, terrain, _ in build_segments():
        g.add(a, b, length, terrain)
    return g


@dataclass
class Result:
    path: list
    cost: float          # effort-km under the chosen profile
    distance: float      # actual km travelled
    expanded: int        # nodes taken off the frontier and expanded


def _search(graph, start, goal, profile, heuristic):
    factors = PROFILES[profile] if isinstance(profile, str) else profile
    frontier = [(heuristic(start), 0.0, 0, start)]
    best_g = {start: 0.0}
    parent = {start: None}
    closed = set()
    tie = 0
    expanded = 0
    while frontier:
        _, g, _, node = heapq.heappop(frontier)
        if node in closed:
            continue
        if node == goal:
            path = [node]
            while parent[path[-1]] is not None:
                path.append(parent[path[-1]])
            path.reverse()
            dist = sum(graph.edges[a][b][0] for a, b in zip(path, path[1:]))
            return Result(path, g, dist, expanded)
        closed.add(node)
        expanded += 1
        for nb, (length, terrain) in graph.edges[node].items():
            step = length * factors[terrain]
            if math.isinf(step) or nb in closed:
                continue
            new_g = g + step
            if new_g < best_g.get(nb, math.inf):
                best_g[nb] = new_g
                parent[nb] = node
                tie += 1
                heapq.heappush(frontier, (new_g + heuristic(nb), new_g, tie, nb))
    return Result([], math.inf, math.inf, expanded)   # no route


def dijkstra(graph, start, goal, profile="wheelchair"):
    """Uniform cost search: A* with a zero heuristic."""
    return _search(graph, start, goal, profile, lambda n: 0.0)


def straight_line_heuristic(graph, goal):
    """Admissible and consistent: every segment is at least as long as the straight line between
    its ends, and every terrain factor is >= 1, so this never overestimates the remaining cost."""
    target = graph.coords[goal]
    return lambda n: haversine_km(graph.coords[n], target)


def astar(graph, start, goal, profile="wheelchair", heuristic=None):
    h = heuristic or straight_line_heuristic(graph, goal)
    return _search(graph, start, goal, profile, h)


def describe(graph, result, profile="wheelchair"):
    """Human-readable route summary with per-segment terrain warnings."""
    if not result.path:
        return "No accessible route found."
    if len(result.path) == 1:
        return f"You are already at {result.path[0]}."
    lines = [f"Route ({profile} profile): " + " -> ".join(result.path),
             f"Distance: {result.distance:.2f} km, about {result.distance / WHEELCHAIR_SPEED_KMH * 60:.0f} min"]
    for a, b in zip(result.path, result.path[1:]):
        length, terrain = graph.edges[a][b]
        warn = {"steep": "  ! steep ramp", "narrow": "  ! narrow footpath"}.get(terrain, "")
        lines.append(f"  {a} -> {b}: {length:.2f} km{warn}")
    return "\n".join(lines)
