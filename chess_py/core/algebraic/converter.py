# -*- coding: utf-8 -*-

"""
Methods that take external input and attempt
to turn them into usable commands.

Copyright © 2016 Aubhro Sengupta. All rights reserved.
"""

from chess_py.core import color
from chess_py.core.algebraic import notation_const
from chess_py.core.algebraic.location import Location
from chess_py.core.algebraic.move import Move
from chess_py.pieces.bishop import Bishop
from chess_py.pieces.king import King
from chess_py.pieces.pawn import Pawn
from chess_py.pieces.queen import Queen
from chess_py.pieces.rook import Rook
from chess_py.pieces.knight import Knight


def incomplete_alg(algebraic_string, input_color):
    """
    Converts a string written in short algebraic form into a potentially
    legal move

    pawn move e4
    piece move Nf3
    pawn capture exd5
    piece capture Qxf3
    Castle 00 or 000
    pawn promotion e8=Q

    :type algebraic_string: str
    :type input_color: Color
    """
    def edge_rank():
        if input_color == color.white:
            return 0
        return 7

    def set_rank(index):
        """
        Returns rank given index
        :type index: int
        :rtype int
        """
        return int(algebraic_string[index]) - 1

    def set_file(index):
        """
        Returns file given index
        :type index: int
        :rtype int
        """
        return ord(algebraic_string[index]) - 97

    def set_piece(index, loc):
        """
        Returns specific piece given index of piece.
        :type index: int
        :type loc Location
        """
        piece = algebraic_string[index].strip()
        piece = piece.upper()

        if piece == 'R':
            return Rook(input_color, loc)

        if piece == 'N':
            return Knight(input_color, loc)

        if piece == 'B':
            return Bishop(input_color, loc)

        if piece == 'Q':
            return Queen(input_color, loc)

        if piece == 'K':
            return King(input_color, loc)
        return None

    def is_kingside(): return algebraic_string == "00"

    def is_queenside(): return algebraic_string == "000"

    end_loc = Location(edge_rank(), 6)

    # King side castle
    if is_kingside():
        return Move(end_loc,
                    piece=King(input_color, Location(edge_rank(), 4)),
                    status=notation_const.KING_SIDE_CASTLE,
                    start_rank=edge_rank(),
                    start_file=4)

    # Queen side castle
    elif is_queenside():
        end_loc = Location(edge_rank(), 2)
        move = Move(end_loc=end_loc,
                    piece=King(input_color, Location(edge_rank(), 4)),
                    status=notation_const.QUEEN_SIDE_CASTLE,
                    start_rank=edge_rank(),
                    start_file=4)

        return move

    # Pawn movement
    elif len(algebraic_string) == 2:
        end_loc = Location(set_rank(1), set_file(0))

        return Move(end_loc, piece=Pawn(input_color, end_loc), status=notation_const.MOVEMENT)

    # Non-pawn Piece movement
    elif len(algebraic_string) == 3:
        end_loc = Location(set_rank(2), set_file(1))
        if set_piece(0, end_loc) is not None:
            return Move(end_loc, piece=set_piece(0, end_loc), status=notation_const.MOVEMENT)
        else:
            return None

    # Multiple options
    elif len(algebraic_string) == 4:

        # Capture
        if algebraic_string[1].upper() == "X":
            """
            ex Nxf3
            """
            # If this is a pawn capture
            if not algebraic_string[0].isupper():

                end_loc = Location(set_rank(3), set_file(2))
                return Move(end_loc,
                            piece=Pawn(input_color, end_loc),
                            status=notation_const.CAPTURE,
                            start_file=set_file(0))

            elif algebraic_string[0].isupper():
                end_loc = Location(set_rank(3), set_file(2))
                return Move(end_loc,
                            piece=set_piece(0, end_loc),
                            status=notation_const.CAPTURE)

            # Pawn Promotion
            elif algebraic_string[2] == "=":
                end_loc = Location(set_rank(1), set_file(0))
                return Move(end_loc,
                            piece=Pawn(input_color, end_loc),
                            status=notation_const.PROMOTE,
                            promoted_to_piece=set_piece(3, end_loc))

            # Non-pawn Piece movement with file specified
            elif algebraic_string[1].isupper():
                end_loc = Location(set_rank(3), set_file(2))
                return Move(end_loc,
                            piece=set_piece(1, end_loc),
                            status=notation_const.MOVEMENT,
                            start_file=set_file(0))

    # Multiple options
    elif len(algebraic_string) == 5:

        # Non-pawn Piece movement with rank and file specified
        if algebraic_string[2].isupper():
            end_loc = Location(set_rank(4), set_file(3))
            return Move(end_loc,
                        piece=set_piece(2, end_loc),
                        status=notation_const.MOVEMENT,
                        start_file=set_file(0),
                        start_rank=set_rank(1))

    elif len(algebraic_string) == 6:
        """
        exd8=Q
        """
        # Pawn promote with capture
        end_loc = Location(set_rank(3), set_file(2))
        return Move(end_loc,
                    piece=Pawn(input_color, end_loc),
                    status=notation_const.MOVEMENT,
                    start_file=set_file(0),
                    promoted_to_piece=set_piece(5, end_loc))

    else:
        return None


def make_legal(move, position):
    """
    Returns the corresponding move from
    all_possible_moves in Board

    :type move: Move
    :type position: Board
    :rtype: Move
    """
    assert isinstance(move, Move)
    for test_move in position.all_possible_moves(move.color):

        if move.status == notation_const.START_LOC_SPECIFIED:
            if move.end_loc == test_move.end_loc and \
                            move.start_rank ==test_move.start_rank and \
                            move.start_file == test_move.start_file:
                return test_move
            else:
                continue
        # Checks for basic equality of essential elements
        if move == test_move:

            if move.status == notation_const.KING_SIDE_CASTLE or \
                    move.status == notation_const.QUEEN_SIDE_CASTLE:
                return test_move

            if move.start_rank is not None and move.start_rank is not test_move.start_rank:
                continue

            if move.start_file is not None and move.start_file is not test_move.start_file:
                continue

            if move.promoted_to_piece is not None and move.promoted_to_piece is not test_move.promoted_to_piece:
                continue

            return test_move

    return None


def short_alg(algebraic_string, input_color, position):
    """
    Converts a string of short algebraic notation into a
    legal move using current position. If conversion fails,
    None is returned.

    pawn move e4
    piece move Nf3
    pawn capture exd5
    piece capture Qxf3
    Castle 00 or 000
    pawn promotion e8=Q

    :type algebraic_string: str
    :type input_color: Color
    :type position: Board
    """
    return make_legal(incomplete_alg(algebraic_string, input_color), position)

def long_alg(alg_str, position):
    """
    Initializes a move from long algebraic notation

    :type alg_str: str
    :type position: Board
    :rtype: Move
    """
    end = Location.init_alg(alg_str[2] + alg_str[3])
    start = Location.init_alg(alg_str[0] + alg_str[1])

    if position.piece_at_square(start) is not None:
        piece = position.piece_at_square(start)
    else:
        raise Exception("Invalid move input")

    pr_piece = None
    if len(alg_str) == 5:
        if alg_str[4] == "Q":
            pr_piece = Queen(piece.color, end)
        elif alg_str[4] == "R":
            pr_piece = Rook(piece.color, end)
        elif alg_str[4] == "B":
            pr_piece = Bishop(piece.color, end)
        elif alg_str[4] == "N":
            pr_piece = Knight(piece.color, end)
        else:
            raise Exception("Invalid move input")

    return make_legal(Move(end_loc=end,
                           piece=piece,
                           status=notation_const.START_LOC_SPECIFIED,
                           start_rank=start.rank,
                           start_file=start.file,
                           promoted_to_piece=pr_piece), position)
