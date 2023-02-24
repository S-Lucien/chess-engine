import sys
import chess
import argparse
from movegeneration import next_move


def talk():
    """
    The main input/output loop.
    This implements a slice of the UCI protocol.
    """
    board = chess.Board()
    depth = get_depth()

    while True:
        msg = input()
        command(depth, board, msg)


def command(depth: int, board: chess.Board, msg: str):
    """
    Accept UCI commands and respond.
    The board state is also updated.
    """
    msg = msg.strip()
    tokens = msg.split(" ")
    while "" in tokens:
        tokens.remove("")

    if msg == "quit":
        sys.exit()

    if msg == "uci":
        print("id name SeRipple")
        print("id author SuYipeng")
        print()
        print("option name Move Overhead type spin default 1000 min 0 max 2000")
        print("option name Threads type spin default 1 min 1 max 2")
        print("option name Hash type spin default 256 min 1 max 1024")  # 16
        print("uciok")

        return

    if msg == "isready":
        print("readyok")
        return

    if msg == "ucinewgame":
        return

    if msg.startswith("position"):
        if len(tokens) < 2:
            return

        # Set starting position
        if tokens[1] == "startpos":
            board.reset()
            moves_start = 2
        elif tokens[1] == "fen":
            fen = " ".join(tokens[2:8])
            board.set_fen(fen)
            moves_start = 8
        else:
            return

        # Apply moves
        if len(tokens) <= moves_start or tokens[moves_start] != "moves":
            return

        for move in tokens[(moves_start+1):]:
            board.push_uci(move)

    if msg == "d":
        # Non-standard command, but supported by Stockfish and helps debugging
        print(board)
        print(board.fen())

    if msg[0:2] == "go":
        _move = next_move(depth, board)
        print(f"bestmove {_move}")
        return


def get_depth() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", default=8, help="provide an integer (default: 6)")
    args = parser.parse_args()
    return max([1, int(args.depth)])
