import chess
import chess.syzygy

tablebase = chess.syzygy.Tablebase()

# 3-5子残局库
def initTablebase():
    global tablebase
    tablebase = chess.syzygy.open_tablebase("D:\PyCharm 2021.3.2\myChess\data\Syzygy Endgame Tablebases")


def search(board: chess.Board):
    global tablebase
    if tablebase is None:
        initTablebase()
    val = tablebase.get_dtz(board)
    if val is None:
        return None
    return val


# initTablebase()
# board = chess.Board("8/2K5/4B3/3N4/8/8/4k3/8 w - - 0 1")
# print(search(board))
