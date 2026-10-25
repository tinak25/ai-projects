"""Tic-tac-toe agents: random, perfect minimax, value iteration (MDP) and tabular Q-learning.
The learning agents play X (first) against an opponent who plays O."""
import random
from collections import defaultdict
from functools import lru_cache

from game import EMPTY, all_states, is_terminal, legal_moves, play, to_move, winner


def random_agent(board, rng=random):
    return rng.choice(legal_moves(board))


@lru_cache(maxsize=None)
def minimax_value(board):
    """Game value from X's point of view with perfect play by both sides: +1 X wins, 0 draw, -1 O wins."""
    w = winner(board)
    if w:
        return 1 if w == "X" else -1
    if " " not in board:
        return 0
    values = [minimax_value(play(board, m)) for m in legal_moves(board)]
    return max(values) if to_move(board) == "X" else min(values)


def minimax_agent(board, rng=random):
    """Perfect player for whichever side is to move; breaks ties between equally good moves at random."""
    best = max if to_move(board) == "X" else min
    scored = [(minimax_value(play(board, m)), m) for m in legal_moves(board)]
    target = best(v for v, _ in scored)
    return rng.choice([m for v, m in scored if v == target])


def _reward(board):
    """Reward for X when a game ends on this board."""
    w = winner(board)
    return 1.0 if w == "X" else -1.0 if w == "O" else 0.0


class ValueIterationAgent:
    """Solves tic-tac-toe as an MDP for X against an opponent who plays uniformly at random.

    States: non-terminal boards where it's X's turn. Actions: empty cells.
    Transition: X plays, then (if the game isn't over) O picks a random empty cell.
    Reward: +1 / -1 / 0 when the game ends (win / loss / draw), 0 otherwise. Terminal value = 0,
    so each final reward is counted exactly once.
    """

    def __init__(self, gamma=1.0, tol=1e-9):
        self.gamma, self.tol = gamma, tol
        self.states = [s for s in all_states() if not is_terminal(s) and to_move(s) == "X"]
        self.V = {s: 0.0 for s in self.states}
        self.policy = {}
        self.sweeps = 0

    def _outcomes(self, s, a):
        """(probability, reward, next X-to-move state or None if terminal)."""
        after_x = play(s, a)
        if is_terminal(after_x):
            return [(1.0, _reward(after_x), None)]
        replies = legal_moves(after_x)
        out = []
        for m in replies:
            nb = play(after_x, m)
            out.append((1 / len(replies), _reward(nb), None if is_terminal(nb) else nb))
        return out

    def q(self, s, a):
        return sum(p * (r + (self.gamma * self.V[n] if n else 0.0)) for p, r, n in self._outcomes(s, a))

    def solve(self):
        while True:
            self.sweeps += 1
            delta = 0.0
            for s in self.states:
                best = max(self.q(s, a) for a in legal_moves(s))
                delta = max(delta, abs(best - self.V[s]))
                self.V[s] = best
            if delta < self.tol:
                break
        self.policy = {s: max(legal_moves(s), key=lambda a: self.q(s, a)) for s in self.states}
        return self

    def __call__(self, board, rng=random):
        return self.policy[board]


class QLearningAgent:
    """Tabular Q-learning for X. The state is the board when it's X's turn."""

    def __init__(self, alpha=0.3, gamma=0.9, epsilon=0.05, seed=0):
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.Q = defaultdict(float)
        self.rng = random.Random(seed)

    def greedy(self, board, rng=None):
        rng = rng or self.rng
        moves = legal_moves(board)
        best = max(self.Q[(board, m)] for m in moves)
        return rng.choice([m for m in moves if self.Q[(board, m)] == best])

    def act(self, board):
        if self.rng.random() < self.epsilon:
            return self.rng.choice(legal_moves(board))
        return self.greedy(board)

    def update(self, s, a, r, next_s):
        """next_s is None when the game is over, so there is nothing to bootstrap from."""
        target = r
        if next_s is not None:
            target += self.gamma * max(self.Q[(next_s, m)] for m in legal_moves(next_s))
        self.Q[(s, a)] += self.alpha * (target - self.Q[(s, a)])

    def train_episode(self, opponent=random_agent):
        """One game against the opponent. Returns the result for X: 'win', 'draw' or 'loss'."""
        s = EMPTY
        while True:
            a = self.act(s)
            after_x = play(s, a)
            if is_terminal(after_x):
                self.update(s, a, _reward(after_x), None)
                return result(after_x)
            nb = play(after_x, opponent(after_x, self.rng))
            if is_terminal(nb):
                self.update(s, a, _reward(nb), None)
                return result(nb)
            self.update(s, a, 0.0, nb)
            s = nb

    def __call__(self, board, rng=random):
        return self.greedy(board, rng)


def result(board):
    w = winner(board)
    return "win" if w == "X" else "loss" if w == "O" else "draw"


def play_match(x_agent, o_agent, games=1000, seed=0):
    """X agent vs O agent. Returns win/draw/loss shares from X's point of view."""
    rng = random.Random(seed)
    counts = {"win": 0, "draw": 0, "loss": 0}
    for _ in range(games):
        b = EMPTY
        while not is_terminal(b):
            agent = x_agent if to_move(b) == "X" else o_agent
            b = play(b, agent(b, rng))
        counts[result(b)] += 1
    return {k: v / games for k, v in counts.items()}
