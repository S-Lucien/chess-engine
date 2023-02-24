import chess

# this module implement's Tomasz Michniewski's Simplified Evaluation Function
# https://www.chessprogramming.org/Simplified_Evaluation_Function
# note that the board layouts have been flipped and the top left square is A1


cnt_pieces = 0

piece_value = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

pawnEvalWhite = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
pawnEvalBlack = list(reversed(pawnEvalWhite))

pawnEvalEndGameWhite = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    15, 10, 5, 10, 10, 5, 10, 15,
    25, 20, 15, 25, 25, 15, 20, 25,
    30, 25, 20, 35, 35, 20, 25, 30,
    35, 35, 35, 40, 40, 35, 35, 35,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
pawnEvalEndGameBlack = list(reversed(pawnEvalEndGameWhite))

knightEval = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishopEvalWhite = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
bishopEvalBlack = list(reversed(bishopEvalWhite))

rookEvalWhite = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
rookEvalBlack = list(reversed(rookEvalWhite))

queenEval = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

kingEvalWhite = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
kingEvalBlack = list(reversed(kingEvalWhite))

kingEvalEndGameWhite = [
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]
kingEvalEndGameBlack = list(reversed(kingEvalEndGameWhite))


def move_value(board: chess.Board, move: chess.Move, endgame: bool) -> float:
    """
    How good is a move?
    A promotion is great.
    A weaker piece taking a stronger piece is good.
    A stronger piece taking a weaker piece is bad.
    Also consider the position change via piece-square table.
    """
    if move.promotion is not None:  # 晋升 默认晋升Queen
        return 800

    _piece = board.piece_at(move.from_square)
    if _piece:
        _from_value = evaluate_piece(_piece, move.from_square, endgame)
        _to_value = evaluate_piece(_piece, move.to_square, endgame)
        position_change = _to_value - _from_value
    else:
        raise Exception(f"A piece was expected at {move.from_square}")

    capture_value = 0.0
    if board.is_capture(move):
        capture_value = MVV_LVA(board, move)

    current_move_value = capture_value + position_change

    if board.is_castling(move):  # 易位奖励25分
        return current_move_value + 25

    return current_move_value


def evaluate_capture(board: chess.Board, move: chess.Move) -> float:
    """
    Given a capturing move, weight the trade being made.
    """
    if board.is_en_passant(move):
        return piece_value[chess.PAWN]
    _to = board.piece_at(move.to_square)
    _from = board.piece_at(move.from_square)
    if _to is None or _from is None:
        raise Exception(
            f"Pieces were expected at _both_ {move.to_square} and {move.from_square}"
        )
    return piece_value[_to.piece_type] - piece_value[_from.piece_type]


def MVV_LVA(board: chess.Board, move: chess.Move) -> float:
    if board.is_en_passant(move):
        return piece_value[chess.PAWN]
    _to = board.piece_at(move.to_square)
    _from = board.piece_at(move.from_square)
    board.push(move)
    if board.is_attacked_by(not board.turn, move.to_square):  # 如果目标棋子被对方保护
        board.pop()
        return piece_value[_to.piece_type] - piece_value[_from.piece_type]
    board.pop()
    return piece_value[_to.piece_type]


def evaluate_piece(piece: chess.Piece, square: chess.Square, end_game: bool) -> int:
    piece_type = piece.piece_type
    mapping = []
    if piece_type == chess.PAWN:
        if end_game:
            mapping = (
                pawnEvalEndGameWhite
                if piece.color == chess.WHITE
                else pawnEvalEndGameBlack
            )
        else:
            mapping = pawnEvalWhite if piece.color == chess.WHITE else pawnEvalBlack
    if piece_type == chess.KNIGHT:
        mapping = knightEval
    if piece_type == chess.BISHOP:
        mapping = bishopEvalWhite if piece.color == chess.WHITE else bishopEvalBlack
    if piece_type == chess.ROOK:
        mapping = rookEvalWhite if piece.color == chess.WHITE else rookEvalBlack
    if piece_type == chess.QUEEN:
        mapping = queenEval
    if piece_type == chess.KING:
        # use end game piece-square tables if neither side has a queen
        if end_game:
            mapping = (
                kingEvalEndGameWhite
                if piece.color == chess.WHITE
                else kingEvalEndGameBlack
            )
        else:
            mapping = kingEvalWhite if piece.color == chess.WHITE else kingEvalBlack

    return mapping[square]


def evaluate_board(board: chess.Board) -> float:
    """
    Evaluates the full board and determines which player is in a most favorable position.
    The sign indicates the side:
        (+) for turn
        (-) for not_turn
    The magnitude, how big of an advantage that player has
    """
    #  评估子力差距

    global cnt_pieces

    total = 0
    end_game = False
    if cnt_pieces <= 16:
        end_game = check_end_game(board)
    cnt_pieces = 0
    bishop_turn = 0  # 是否有主教对
    bishop_notTurn = 0
    pawn_map = dict()

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        cnt_pieces += 1  # 记录场上棋子数
        ptype = piece.piece_type

        if ptype == chess.BISHOP:
            if piece.color == board.turn:
                bishop_turn += 1
            else:
                bishop_notTurn += 1
        elif ptype == chess.PAWN and piece.color == board.turn:
            pawn_map[square] = True

        value = piece_value[ptype] + evaluate_piece(piece, square, end_game)
        if end_game:  # 游戏后期马价值减少，车价值提升
            if ptype == chess.ROOK:
                value += 50
            if ptype == chess.KNIGHT:
                value -= 30
        total += value if piece.color == board.turn else -value

    # 有易位权奖励20分
    total += 20 if board.has_castling_rights(board.turn) else 0
    # 主教对奖励50分
    if bishop_turn == 2:
        total += 50
    if bishop_notTurn == 2:
        total -= 50
    total += pawn_structure(pawn_map)  # 兵结构奖励

    return total


def check_end_game(board: chess.Board) -> bool:
    """
    Are we in the end game?
    Per Michniewski:
    - Both sides have no queens or
    - Every side which has a queen has additionally no other pieces or one minorpiece maximum.
    """
    queens = 0
    minors = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.QUEEN:
            queens += 1
        if piece and (
                piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT
        ):
            minors += 1

    if queens == 0 or (queens == 2 and minors <= 1):
        return True

    return False


def pawn_structure(pawn_map: dict):
    if len(pawn_map) < 4:
        return 0
    bonus = 0
    for square in pawn_map.keys():
        if square >> 3 == 1 or square >> 3 == 6:  # 起始位置或晋升前的兵不计
            continue
        # 双兵奖励10分，孤兵惩罚20分
        if square % 8 == 0:  # A
            cnt = 0
            if (square - 7) in pawn_map:
                bonus += 10
                cnt += 1
            if (square + 9) in pawn_map:
                bonus += 10
                cnt += 1
            if cnt == 0:
                bonus -= 20
        elif (square + 1) % 8 == 0:  # H
            cnt = 0
            if (square - 9) in pawn_map:
                bonus += 10
                cnt += 1
            if (square + 7) in pawn_map:
                bonus += 10
                cnt += 1
            if cnt == 0:
                bonus -= 20
        else:
            positions = [-9, -7, 7, 9]
            cnt = 0
            for pos in positions:
                if (square + pos) in pawn_map:
                    bonus += 10
                    cnt += 1
            if cnt == 0:
                bonus -= 20

    return bonus


# 场上棋子数
def get_cnt_pieces():
    global cnt_pieces
    return cnt_pieces
