import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import (QLearningAgent, ValueIterationAgent, minimax_agent, minimax_value,  # noqa: E402
                    play_match, random_agent)
from game import EMPTY, all_states, is_terminal, play, to_move, winner  # noqa: E402

VI = ValueIterationAgent().solve()


def board(s):
    return tuple(s.replace(".", " "))


def test_rules():
    assert winner(board("XXX......")) == "X"
    assert winner(board("O...O...O")) == "O"
    assert winner(board("XOXXOOOXX")) is None and is_terminal(board("XOXXOOOXX"))
    assert to_move(EMPTY) == "X" and to_move(play(EMPTY, 4)) == "O"


def test_state_count():
    assert len(all_states()) == 5478


def test_perfect_play_is_a_draw():
    assert minimax_value(EMPTY) == 0


def test_minimax_never_loses():
    assert play_match(minimax_agent, random_agent, 2000, seed=1)["loss"] == 0
    assert play_match(random_agent, minimax_agent, 2000, seed=2)["win"] == 0


def test_values_are_bounded():
    assert all(-1 <= v <= 1 for v in VI.V.values())


def test_value_iteration_wins_and_blocks():
    assert VI(board("XX..O.O..")) == 2               # complete the top row
    assert VI(board("X.X.OO...")) == 1               # win beats blocking
    assert VI(board("OO..X...X")) == 2               # block O's top row (no win available)


def test_q_learning_learns():
    agent = QLearningAgent(seed=0)
    for _ in range(20000):
        agent.train_episode()
    agent.epsilon = 0
    assert play_match(agent, random_agent, 2000, seed=3)["win"] > 0.9
