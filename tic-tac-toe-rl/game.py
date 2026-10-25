"""Tic-tac-toe rules. A board is a tuple of 9 cells, each ' ', 'X' or 'O' (index 0 = top-left).
X always moves first, so it's X's turn whenever both players have the same number of marks."""

EMPTY = (" ",) * 9
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(board):
    for a, b, c in LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_terminal(board):
    return winner(board) is not None or " " not in board


def to_move(board):
    return "X" if board.count("X") == board.count("O") else "O"


def legal_moves(board):
    return [i for i, c in enumerate(board) if c == " "]


def play(board, move):
    if board[move] != " ":
        raise ValueError(f"Cell {move} is already taken")
    b = list(board)
    b[move] = to_move(board)
    return tuple(b)


def all_states():
    """Every board reachable in legal play (including terminal boards)."""
    seen, stack = {EMPTY}, [EMPTY]
    while stack:
        b = stack.pop()
        if is_terminal(b):
            continue
        for m in legal_moves(b):
            nb = play(b, m)
            if nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return seen


def show(board):
    rows = [" | ".join(board[r * 3:r * 3 + 3]) for r in range(3)]
    return "\n---------\n".join(rows)
