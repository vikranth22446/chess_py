# -*- coding: utf-8 -*-

"""
Parent class for all pieces

Copyright © 2016 Aubhro Sengupta. All rights reserved.
"""

from abc import ABCMeta, abstractmethod
from chess_py.core.algebraic.location import Location
from chess_py.core import color
from chess_py.core.color import Color


class Piece:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, input_color, location, white_symbol, black_symbol):
        """
        Initializes a piece that is capable of moving

        :type input_color: Color
        :type location: Location
        :type white_symbol: str
        :type black_symbol: str
        """
        assert isinstance(input_color, Color)
        assert isinstance(location, Location)
        assert isinstance(white_symbol, str)
        assert isinstance(black_symbol, str)

        self.color = input_color
        self.location = location

        if self.color == color.white:
            self.symbol = white_symbol
        else:
            self.symbol = black_symbol

    def __key(self):
        return self.color, self.location

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        """
        Finds out if piece is the same type and color as self
        :type other: Piece
        """
        return type(other) is type(self) and other.color == self.color

    def __ne__(self, other):
        return not self.__eq__(other)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abstractmethod
    def possible_moves(self, position):
        pass

    def set_loc(self, moves):
        """
        Adds start_rank and start_file to moves
        :type moves list
        """
        for move in moves:
            move.start_rank = self.location.rank
            move.start_file = self.location.file
