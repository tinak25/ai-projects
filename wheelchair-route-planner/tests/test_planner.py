import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forest_hill_map import LOCATIONS, build_segments, haversine_km  # noqa: E402
from planner import astar, dijkstra, load_forest_hill  # noqa: E402

G = load_forest_hill()
PAIRS = list(itertools.permutations(LOCATIONS, 2))


def test_map_size():
    assert len(G.edges) == 21
    assert len(build_segments()) == 30


def test_segments_never_shorter_than_straight_line():
    for a, b, length, _, _ in build_segments():
        assert length >= haversine_km(LOCATIONS[a], LOCATIONS[b])


def test_astar_matches_dijkstra_on_every_pair():
    for profile in ("shortest", "wheelchair"):
        for s, t in PAIRS:
            assert math.isclose(astar(G, s, t, profile).cost, dijkstra(G, s, t, profile).cost)


def test_astar_never_expands_more_than_dijkstra():
    for s, t in PAIRS:
        assert astar(G, s, t).expanded <= dijkstra(G, s, t).expanded


def test_heuristic_is_consistent():
    # h(a) <= cost(a, b) + h(b) for every segment and every goal
    for goal in LOCATIONS:
        h = lambda n: haversine_km(LOCATIONS[n], LOCATIONS[goal])
        for a, b, length, _, _ in build_segments():
            assert h(a) <= length + h(b) + 1e-9
            assert h(b) <= length + h(a) + 1e-9


def test_strict_profile_avoids_barriers():
    for s, t in PAIRS:
        r = astar(G, s, t, "strict")
        for a, b in zip(r.path, r.path[1:]):
            assert G.edges[a][b][1] == "normal"


def test_same_start_and_goal():
    r = astar(G, "Aqualink", "Aqualink")
    assert r.path == ["Aqualink"] and r.cost == 0
