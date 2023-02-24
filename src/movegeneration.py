from typing import Dict, List, Any
import chess
import chess.polyglot
import sys
import time
from evaluate import evaluate_board, MVV_LVA, get_cnt_pieces
from endgame_tablebase import search

debug_info: Dict[str, Any] = {}

MATE_SCORE = 1000000000

table = dict()  # key:fen value: depth,value,flag
                # flag中： 0->PV node(搜索完毕) 1->Lower_bound 2->Upper_bound
table_max = 1e7     # 置换表最大容量
history = dict()  # key: move value: score
current_depth: int  # 当前迭代深度
killer = list()     # 杀手表 [depth][killer1,killer2]


def next_move(depth: int, board: chess.Board, debug=True, use_book=True) -> chess.Move:
    """
    What is the next best move?
    """
    debug_info.clear()
    debug_info["nodes"] = 0

    #   场上棋子数少于5时，检索残局库
    if use_book:
        cnt_pieces = get_cnt_pieces()
        if cnt_pieces <= 5 and cnt_pieces != 0:
            move = get_from_table(board)
            if move != chess.Move.null():
                return move

    t0 = time.time()

    # with chess.polyglot.open_reader("data/polyglot/performance.bin") as reader:
    #     for entry in reader.find_all(board):
    #         print(entry.move, entry.weight, entry.learn)

    move = negamax_root(depth, board)

    debug_info["time"] = time.time() - t0
    if debug == True:
        print(f"info {debug_info}")
    return move


def get_ordered_moves(board: chess.Board) -> List[chess.Move]:
    # 移动排序

    def orderer(move: chess.Move):
        value1 = 21000.0
        if board.is_capture(move):
            value1 += MVV_LVA(board, move)  # 考虑吃子 MVV（LVA）策略
        value2 = 0.0
        if move in history:
            value2 = history[move]  # 历史表启发
        return value1 + value2 * 0.1

    in_order = sorted(
        board.legal_moves, key=orderer, reverse=True)
    return list(in_order)


def negamax_root(depth: int, board: chess.Board) -> chess.Move:
    start = time.time()  # 记录搜索时间

    global killer   # 初始化杀手表
    killer = [[chess.Move.null() for col in range(2)] for row in range(depth)]

    # 第一次迭代，获取移动排序结果
    moves = get_ordered_moves(board)
    best_move_found = moves[0]
    # 对于剩下的迭代，按上次迭代得到的value排序
    moves_sorted = list()   # [move,value]
    for _depth in range(1, depth + 1):
        alpha = -float("inf")
        beta = float("inf")
        global current_depth
        current_depth = _depth

        if _depth != 1:  # 迭代加深
            moves_sorted.sort(key=lambda m: m[1], reverse=True)
            moves.clear()
            for i in moves_sorted:
                moves.append(i[0])
            moves_sorted.clear()

        for move in moves:
            board.push(move)
            # Checking if draw can be claimed at this level, because the threefold repetition check
            # can be expensive. This should help the bot avoid a draw if it's not favorable
            # https://python-chess.readthedocs.io/en/latest/core.html#chess.Board.can_claim_draw
            if board.can_claim_draw():  # 和棋
                value = 0.0
            else:
                value = -negamax(_depth - 1, board, -beta, -alpha)
                moves_sorted.append([move, value])
            board.pop()
            if value > alpha:
                alpha = value
                best_move_found = move
            if time.time() - start > 8:     # 8秒内给出搜索结果
                return best_move_found

    return best_move_found


def negamax(
        depth: int,
        board: chess.Board,
        alpha: float,
        beta: float,
        is_nullmove: bool = False
) -> float:
    debug_info["nodes"] += 1

    if board.is_checkmate():
        # The previous move resulted in checkmate
        return -MATE_SCORE
    # When the game is over and it's not a checkmate it's a draw
    # In this case, don't evaluate. Just return a neutral result: zero
    elif board.is_game_over():
        return 0

    if depth <= 0:  # 叶结点
        return evaluate_board(board)

    # 初始alpha、beta值
    alphaOrig = alpha
    betaOrig = beta

    # 获取当期局面散列键
    hashkey = get_hashkey(board)
    # 置换表
    if hashkey in table:
        hash_value = table.get(hashkey)
        _depth = hash_value[0]
        if _depth >= depth:
            _value = hash_value[1]
            _flag = hash_value[2]
            if _flag == 0:  # exact
                return _value
            elif _flag == 1:  # lower-bound
                alpha = max(alpha, _value)
                if alpha >= beta:
                    return beta
            elif _flag == 2:  # upper-bound
                beta = min(beta, _value)
                if alpha >= beta:
                    return alpha

    # killer move
    killer1 = killer[depth][0]
    if board.is_legal(killer1):
        board.push(killer1)
        value = -negamax(depth - 1, board, -beta, -alpha)
        board.pop()
        if value >= beta:
            return beta
    killer2 = killer[depth][1]
    if board.is_legal(killer2):
        board.push(killer2)
        value = -negamax(depth - 1, board, -beta, -alpha)
        board.pop()
        if value >= beta:
            return beta

    # null_move Pruning
    if not is_nullmove and depth > 2:  # 上一步不是空着
        null_move = chess.Move.null()
        board.push(null_move)
        value = -negamax(depth - 1 - 1, board, -beta, -beta + 1, True)
        board.pop()
        if value >= betaOrig <= MATE_SCORE:
            return betaOrig

    # move-ordering
    moves = get_ordered_moves(board)

    #  PVS and Aspiration
    best_move = moves[0]
    board.push(best_move)
    value = -negamax(depth - 1, board, -beta, -alpha)
    board.pop()
    if value > alpha:
        if value >= beta:
            record_hash(get_hashkey(board), depth, value, 1)  # beta-cutoff, lower-bound
            history[best_move] = depth ** 2 + (history[best_move] if best_move in history else 0)
            update_killer(depth, best_move)
            return beta
        alpha = value
    moves.pop(0)

    for move in moves:
        board.push(move)
        curr_move = -negamax(depth - 1, board, -alpha - 1, -alpha)  # 0窗口搜索
        if alpha < curr_move < beta:
            curr_move = -negamax(depth - 1, board, -beta, -alpha)
            alpha = curr_move
        board.pop()

        if curr_move > value:
            if curr_move >= beta:
                record_hash(get_hashkey(board), depth, alpha, 1)
                history[move] = depth ** 2 + (history[move] if move in history else 0)
                update_killer(depth, move)
                return beta
            value = curr_move
            best_move = move

    if alpha <= alphaOrig:  # all-node Upper-bound
        record_hash(get_hashkey(board), depth, value, 2)
    elif beta - alpha > 1:  # PV node exact
        record_hash(get_hashkey(board), depth, value, 0)
        history[best_move] = depth ** 2 + (history[best_move] if best_move in history else 0)
    return value


def get_hashkey(board: chess.Board):
    fen = board.fen().split()
    return fen[0] + fen[1]  # 唯一标志棋局


def record_hash(hashkey, depth, best_move, flag):  # 存入置换表
    if hashkey in table:
        _depth = table.get(hashkey)[0]
        if _depth <= depth:
            table[hashkey] = [depth, best_move, flag]
    else:
        table[hashkey] = [depth, best_move, flag]


def update_killer(depth, cutmove: chess.Move):  # 更新杀手表
    if cutmove != killer[depth][0]:
        killer[depth][1] = killer[depth][0]
        killer[depth][0] = cutmove


# 查残局库
def get_from_table(board: chess.Board) -> chess.Move:
    moves = board.legal_moves
    order_win = dict()
    order_lose = dict()
    for move in moves:
        board.push(move)
        val = search(board)
        if val is not None:
            if val > 0:
                order_win[move] = val
            else:
                order_lose[move] = val
        board.pop()
    if len(order_win) != 0:  # 能赢就赢
        return sorted(order_win.items(), key=lambda item: item[1])[0]
    elif len(order_lose) != 0:  # 不能赢尽量逼和
        return sorted(order_lose.items(), key=lambda item: item[1], reverse=True)[0]
    return chess.Move.null()
