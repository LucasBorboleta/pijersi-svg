#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pijersi_svg.py draws SVG pictures for the PIJERSI boardgame."""

import array
from dataclasses import dataclass
import enum
import math
import os
import random
import sys

from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import TypeVar

import drawsvg as draw


__version__ = "1.0.0"

_COPYRIGHT_AND_LICENSE = """
PIJERSI-SVG is a Python program that draws SVG pictures for the PIJERSI boardgame.

Copyright (C) 2024 Lucas Borboleta (lucas.borboleta@free.fr).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""

_project_home = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
_pictures_dir = os.path.join(_project_home, 'pictures')

RANDOM_SEED = 20240822
random.seed(a=RANDOM_SEED)

# TROTEC LASER color codes
COLOR_TO_ENGRAVE = 'rgb(0,0,0)'
COLOR_TO_SCORE = 'rgb(255,0,0)'  # In French: marquer ou tracer
COLOR_TO_CUT_1 = 'rgb(0,0,255)'  # Cut in a first step
COLOR_TO_CUT_2 = 'rgb(51,102,153)'  # Cut in a second step

LINE_WIDTH_MAX_TO_CUT_CM = 0.1/10
LINE_WIDTH_MIN_TO_ENGRAVE_CM = 0.11/10


class Side(enum.Enum):
    NORTH = enum.auto()
    SOUTH = enum.auto()
    WEST = enum.auto()
    EAST = enum.auto()


class CubeKind(enum.Enum):
    ROCK = enum.auto()
    PAPER = enum.auto()
    SCISSORS = enum.auto()
    WISE = enum.auto()


class CubeColor(enum.Enum):
    WHITE = enum.auto()
    BLACK = enum.auto()


@dataclass
class Cube:
    kind: CubeKind = None
    color: CubeColor = None


class TinyVector:
    """Lightweight algebra on 2D vectors, inspired by numpy ndarray."""

    __slots__ = ("__x", "__y")

    def __init__(self, xy_pair=None):
        if xy_pair is None:
            self.__x = 0.
            self.__y = 0.

        else:
            self.__x = float(xy_pair[0])
            self.__y = float(xy_pair[1])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str((self.__x, self.__y))

    def __getitem__(self, key):
        if key == 0:
            return self.__x

        elif key == 1:
            return self.__y

        else:
            raise IndexError()

    def __neg__(self):
        return TinyVector((-self.__x, -self.__y))

    def __pos__(self):
        return TinyVector((self.__x, self.__y))

    def __add__(self, other):
        if isinstance(other, TinyVector):
            return TinyVector((self.__x + other.__x, self.__y + other.__y))

        elif isinstance(other, (int, float)):
            return TinyVector((self.__x + other, self.__y + other))

        else:
            raise NotImplementedError()

    def __sub__(self, other):
        if isinstance(other, TinyVector):
            return TinyVector((self.__x - other.__x, self.__y - other.__y))

        elif isinstance(other, (int, float)):
            return TinyVector((self.__x - other, self.__y - other))

        else:
            raise NotImplementedError()

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return TinyVector((self.__x*other, self.__y*other))

        else:
            raise NotImplementedError()

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return TinyVector((self.__x/other, self.__y/other))

        else:
            raise NotImplementedError()

    def __radd__(self, other):
        return self.__add__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        return self.__div__(other)

    def __rsub__(self, other):
        if isinstance(other, TinyVector):
            return TinyVector((-self.__x + other.__x, -self.__y + other.__y))

        elif isinstance(other, (int, float)):
            return TinyVector((-self.__x + other, -self.__y + other))

        else:
            raise NotImplementedError()

    def make_rotation(self, angle):
        new_x = math.cos(angle)*self.__x - math.sin(angle)*self.__y
        new_y = math.sin(angle)*self.__x + math.cos(angle)*self.__y
        return TinyVector((new_x, new_y))

    @staticmethod
    def inner(that, other):
        if isinstance(that, TinyVector) and isinstance(other, TinyVector):
            return (that.__x*other.__x + that.__y*other.__y)

        else:
            raise NotImplementedError()

    @staticmethod
    def norm(that):
        if isinstance(that, TinyVector):
            return math.sqrt(that.__x*that.__x + that.__y*that.__y)

        else:
            raise NotImplementedError()


@dataclass
class CubeConfig:

    cube_side_cm: float = None

    layout: dict = None
    row_count: int = None
    col_count: int = None

    support_width_cm: float = None
    support_height_cm: float = None
    support_color: str = None

    line_width_max_to_cut: float = None
    line_width_min_to_engrave: float = None

    support_width: float = None
    support_height: float = None
    support_cut_margin: float = None

    cube_side: float = None
    cube_cut_margin: float = None
    cube_shift: float = None
    cube_line_width: float = None

    decoration_line_width: float = None
    decoration_side: float = None



@dataclass
class BoardConfig:

    board_width_cm: float = None
    board_height_cm: float = None

    board_width: float = None
    board_height: float = None
    board_cut_margin: float = None

    line_width_max_to_cut: float = None
    line_width_min_to_engrave: float = None

    board_color: str = None

    hexagon_width: float = None
    hexagon_side: float = None
    hexagon_height: float = None
    hexagon_padding: float = None
    hexagon_line_width: float = None
    hexagon_line_color: str = None
    hexagon_opacity: float = None

    hexagon_vertex_count: int = None
    hexagon_side_angle: float = None

    origin: TinyVector = None

    unit_x: TinyVector = None
    unit_y: TinyVector = None

    unit_u: TinyVector = None
    unit_v: TinyVector = None

    label_color: str = None
    label_font_family: str = None
    label_font_size: int = None
    label_vertical_shift: TinyVector = None
    label_horizontal_shift: TinyVector = None


def make_cube_config(do_large=False):

    print()
    print("make_cube_config: ...")

    # Define the abstract layout

    layout = {}

    layout[(0, 0)] = Cube(kind=CubeKind.ROCK, color=CubeColor.BLACK)
    layout[(0, 1)] = Cube(kind=CubeKind.ROCK, color=CubeColor.BLACK)
    layout[(0, 2)] = Cube(kind=CubeKind.ROCK, color=CubeColor.BLACK)
    layout[(0, 3)] = Cube(kind=CubeKind.ROCK, color=CubeColor.BLACK)

    layout[(0, 4)] = Cube(kind=CubeKind.WISE, color=CubeColor.BLACK)
    layout[(0, 5)] = Cube(kind=CubeKind.WISE, color=CubeColor.BLACK)

    layout[(1, 0)] = Cube(kind=CubeKind.PAPER, color=CubeColor.BLACK)
    layout[(1, 1)] = Cube(kind=CubeKind.PAPER, color=CubeColor.BLACK)
    layout[(1, 2)] = Cube(kind=CubeKind.PAPER, color=CubeColor.BLACK)
    layout[(1, 3)] = Cube(kind=CubeKind.PAPER, color=CubeColor.BLACK)

    layout[(2, 0)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.BLACK)
    layout[(2, 1)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.BLACK)
    layout[(2, 2)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.BLACK)
    layout[(2, 3)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.BLACK)

    layout[(3, 0)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.WHITE)
    layout[(3, 1)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.WHITE)
    layout[(3, 2)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.WHITE)
    layout[(3, 3)] = Cube(kind=CubeKind.SCISSORS, color=CubeColor.WHITE)

    layout[(4, 0)] = Cube(kind=CubeKind.PAPER, color=CubeColor.WHITE)
    layout[(4, 1)] = Cube(kind=CubeKind.PAPER, color=CubeColor.WHITE)
    layout[(4, 2)] = Cube(kind=CubeKind.PAPER, color=CubeColor.WHITE)
    layout[(4, 3)] = Cube(kind=CubeKind.PAPER, color=CubeColor.WHITE)

    layout[(5, 0)] = Cube(kind=CubeKind.ROCK, color=CubeColor.WHITE)
    layout[(5, 1)] = Cube(kind=CubeKind.ROCK, color=CubeColor.WHITE)
    layout[(5, 2)] = Cube(kind=CubeKind.ROCK, color=CubeColor.WHITE)
    layout[(5, 3)] = Cube(kind=CubeKind.ROCK, color=CubeColor.WHITE)

    layout[(5, 4)] = Cube(kind=CubeKind.WISE, color=CubeColor.WHITE)
    layout[(5, 5)] = Cube(kind=CubeKind.WISE, color=CubeColor.WHITE)

    row_indices = list(set([row for (row, _) in layout.keys()]))
    col_indices = list(set([col for (_, col) in layout.keys()]))

    row_indices.sort()
    col_indices.sort()

    row_count = len(row_indices)
    col_count = len(col_indices)

    assert min(row_indices) == 0
    assert max(row_indices) == (row_count - 1)

    assert min(col_indices) == 0
    assert max(col_indices) == (col_count - 1)

    for row_index in range(row_count):
        for col_index in range(col_count):
            if (row_index, col_index) not in layout:
                layout[(row_index, col_index)] = None

    # Compute the sizes in cm

    if do_large:
        cube_side_cm = 2.0
    else:
        cube_side_cm = 1.6
        
    cube_cut_margin_cm = 0.1/10
    cube_shift_cm = cube_side_cm
    cube_line_width_cm = 0.1/4

    decoration_line_width_cm = 0.15
    decoration_side_cm = 0.5*cube_side_cm

    support_cut_margin_cm = 0.1/10

    support_width_cm = (support_cut_margin_cm +
                        col_count*(cube_shift_cm + cube_cut_margin_cm + cube_side_cm) +
                        cube_shift_cm +
                        support_cut_margin_cm)

    support_height_cm = (support_cut_margin_cm +
                         row_count*(cube_shift_cm + cube_cut_margin_cm + cube_side_cm) +
                         cube_shift_cm +
                         support_cut_margin_cm)

    # Deduce other sizes in pixels

    support_width = 4096
    support_height = support_width*(support_height_cm/support_width_cm)
    support_cut_margin = support_width*(support_cut_margin_cm/support_width_cm)

    cube_side = support_width*(cube_side_cm/support_width_cm)

    cube_cut_margin = support_width*(cube_cut_margin_cm/support_width_cm)

    cube_shift = support_width*(cube_shift_cm/support_width_cm)

    cube_line_width = support_width*(cube_line_width_cm/support_width_cm)
    cube_line_width = max(1, cube_line_width)

    decoration_line_width = support_width * \
        (decoration_line_width_cm/support_width_cm)
    decoration_line_width = max(1, decoration_line_width)

    decoration_side = support_width * \
        (decoration_side_cm/support_width_cm)

    line_width_max_to_cut = support_width * \
        (LINE_WIDTH_MAX_TO_CUT_CM/support_width_cm)

    line_width_min_to_engrave = support_width * \
        (LINE_WIDTH_MIN_TO_ENGRAVE_CM/support_width_cm)

    # colors
    support_color = '#BF9B7A'

    # make and return the CubeConfig
    cube_config = CubeConfig(cube_side_cm=cube_side_cm,

                             layout=layout,
                             row_count=row_count,
                             col_count=col_count,

                             support_width_cm=support_width_cm,
                             support_height_cm=support_height_cm,
                             support_color=support_color,

                             line_width_max_to_cut=line_width_max_to_cut,
                             line_width_min_to_engrave=line_width_min_to_engrave,

                             support_width=support_width,
                             support_height=support_height,
                             support_cut_margin=support_cut_margin,

                             cube_side=cube_side,
                             cube_cut_margin=cube_cut_margin,
                             cube_shift=cube_shift,
                             cube_line_width=cube_line_width,

                             decoration_line_width=decoration_line_width,
                             decoration_side=decoration_side)

    print()
    print(f"make_cube_config: cube_side_cm = {cube_side_cm:.2f} ")
    print(f"make_cube_config: cube_cut_margin_cm = {cube_cut_margin_cm:.2f}")
    print(f"make_cube_config: cube_shift_cm = {cube_shift_cm:.2f}")

    print()
    print(f"make_cube_config: row_count = {row_count} ")
    print(f"make_cube_config: row_count = {col_count} ")

    print()
    print(f"make_cube_config: support_width_cm = {support_width_cm:.2f} ")
    print(f"make_cube_config: support_height_cm = {support_height_cm:.2f}")
    print(
        f"make_cube_config: support_cut_margin_cm = {support_cut_margin_cm:.2f}")

    print()
    print("make_board_config: done")
    return cube_config


def make_board_config(do_tiny=False):

    print()
    print("make_board_config: ...")

    # Compute the sizes in cm

    hexagon_width_cm = 2*CUBE_CONFIG.cube_side_cm
    hexagon_side_cm = hexagon_width_cm/math.sqrt(3)
    hexagon_height_cm = 2*hexagon_side_cm
    hexagon_padding_cm = 0.3
    hexagon_line_width_cm = 0.1/4

    if do_tiny:
        max_horizontal_hexagon_count = 3
        max_vertical_hexagon_count = 1
    else:
        max_horizontal_hexagon_count = 7
        max_vertical_hexagon_count = 7

    board_left_margin_cm = hexagon_width_cm/2
    board_right_margin_cm = hexagon_width_cm/2

    if do_tiny:
        board_top_margin_cm = hexagon_side_cm/2
        board_bottom_margin_cm = hexagon_side_cm/2
    else:
        board_top_margin_cm = hexagon_side_cm
        board_bottom_margin_cm = hexagon_side_cm

    board_cut_margin_cm = 0.1/10

    board_width_cm = (board_cut_margin_cm +
                      board_left_margin_cm +
                      max_horizontal_hexagon_count*hexagon_width_cm +
                      board_right_margin_cm +
                      board_cut_margin_cm)

    board_height_cm = (board_cut_margin_cm +
                       board_top_margin_cm +
                       (max_vertical_hexagon_count//2)*hexagon_side_cm +
                       (max_vertical_hexagon_count - max_vertical_hexagon_count//2)*hexagon_height_cm +
                       board_bottom_margin_cm +
                       board_cut_margin_cm)

    # Deduce other sizes in pixels

    board_width = 4096
    board_height = board_width*(board_height_cm/board_width_cm)

    board_cut_margin = board_width*(board_cut_margin_cm/board_width_cm)

    hexagon_width = board_width*(hexagon_width_cm/board_width_cm)
    hexagon_side = board_width*(hexagon_side_cm/board_width_cm)
    hexagon_height = board_width*(hexagon_height_cm/board_width_cm)
    hexagon_padding = board_width*(hexagon_padding_cm/board_width_cm)

    line_width_max_to_cut = board_width * \
        (LINE_WIDTH_MAX_TO_CUT_CM/board_width_cm)

    line_width_min_to_engrave = board_width * \
        (LINE_WIDTH_MIN_TO_ENGRAVE_CM/board_width_cm)

    # Hexagon properties other than sizes
    hexagon_vertex_count = 6
    hexagon_side_angle = 2*math.pi/hexagon_vertex_count

    # Origin of both orthonormal x-y frame and oblic u-v frame
    origin = TinyVector((0, 0))

    # Unit vectors of the orthonormal x-y frame
    unit_x = TinyVector((1, 0))
    unit_y = TinyVector((0, -1))

    # Unit vectors of the oblic u-v frame
    unit_u = unit_x
    unit_v = math.cos(hexagon_side_angle)*unit_x + \
        math.sin(hexagon_side_angle)*unit_y

    # Label properties
    label_color = COLOR_TO_ENGRAVE
    label_font_family = 'Helvetica'
    label_font_size = int(hexagon_width*0.20)
    label_vertical_shift = -0.60*hexagon_side*unit_y
    label_horizontal_shift = 1.20*hexagon_side*unit_x

    # colors and etc.
    board_color = '#BF9B7A'
    # board_color = 'white'
    hexagon_opacity = 0.45
    hexagon_line_color = COLOR_TO_ENGRAVE

    hexagon_line_width = board_width*(hexagon_line_width_cm/board_width_cm)
    hexagon_line_width = max(1, hexagon_line_width)

    # make and return the BoardConfig
    board_config = BoardConfig(board_width_cm=board_width_cm,
                               board_height_cm=board_height_cm,

                               board_width=board_width,
                               board_height=board_height,
                               board_cut_margin=board_cut_margin,

                               line_width_max_to_cut=line_width_max_to_cut,
                               line_width_min_to_engrave=line_width_min_to_engrave,

                               board_color=board_color,

                               hexagon_width=hexagon_width,
                               hexagon_side=hexagon_side,
                               hexagon_height=hexagon_height,
                               hexagon_padding=hexagon_padding,
                               hexagon_line_width=hexagon_line_width,
                               hexagon_opacity=hexagon_opacity,
                               hexagon_line_color=hexagon_line_color,

                               hexagon_vertex_count=hexagon_vertex_count,
                               hexagon_side_angle=hexagon_side_angle,

                               origin=origin,

                               unit_x=unit_x,
                               unit_y=unit_y,

                               unit_u=unit_u,
                               unit_v=unit_v,

                               label_color=label_color,
                               label_vertical_shift=label_vertical_shift,
                               label_horizontal_shift=label_horizontal_shift,
                               label_font_family=label_font_family,
                               label_font_size=label_font_size)

    print()
    print(f"make_board_config: board_width_cm = {board_width_cm:.2f} ")
    print(f"make_board_config: board_height_cm = {board_height_cm:.2f}")
    print(
        f"make_board_config: board_cut_margin_cm = {board_cut_margin_cm:.2f}")
    print()
    print(f"make_board_config: hexagon_width_cm = {hexagon_width_cm:.2f}")
    print(f"make_board_config: hexagon_height_cm = {hexagon_height_cm:.2f}")
    print(f"make_board_config: hexagon_side_cm = {hexagon_side_cm:.2f}")

    print()
    print("make_board_config: done")
    return board_config


class Hexagon:

    Self = TypeVar("Self", bound="Hexagon")

    __slots__ = ('name', 'position_uv', 'ring', 'label_side',
                 'index', 'center')

    __all_sorted_hexagons = []
    __init_done = False
    __layout = []
    __name_to_hexagon = {}
    __position_uv_to_hexagon = {}

    all = None  # shortcut to Hexagon.get_all()

    def __init__(self, name: str, position_uv: Tuple[int, int], ring: int, label_side: Optional[Side] = 0):

        assert name not in Hexagon.__name_to_hexagon
        assert len(position_uv) == 2
        assert position_uv not in Hexagon.__position_uv_to_hexagon
        assert len(name) == 2

        self.name = name
        self.position_uv = position_uv
        self.ring = ring
        self.label_side = label_side
        self.index = None

        Hexagon.__name_to_hexagon[self.name] = self
        Hexagon.__position_uv_to_hexagon[position_uv] = self

        (u, v) = self.position_uv

        self.center = BOARD_CONFIG.origin + BOARD_CONFIG.hexagon_width * \
            (u*BOARD_CONFIG.unit_u + v*BOARD_CONFIG.unit_v)

    def __str__(self):
        return f"Hexagon({self.name}, {self.position_uv}, {self.index}"

    @staticmethod
    def get(name: str) -> Self:
        return Hexagon.__name_to_hexagon[name]

    @staticmethod
    def get_all() -> Sequence[Self]:
        return Hexagon.__all_sorted_hexagons

    @staticmethod
    def get_layout() -> Sequence[Sequence[str]]:
        return Hexagon.__layout

    @staticmethod
    def init():
        if not Hexagon.__init_done:
            Hexagon.__create_hexagons()
            Hexagon.__create_all_sorted_hexagons()
            Hexagon.__create_layout()
            Hexagon.__create_delta_u_and_v()
            Hexagon.__init_done = True

    @staticmethod
    def reset():
        Hexagon.__all_sorted_hexagons = []
        Hexagon.__init_done = False
        Hexagon.__layout = []
        Hexagon.__name_to_hexagon = {}
        Hexagon.__position_uv_to_hexagon = {}

    @staticmethod
    def print_hexagons():
        for hexagon in Hexagon.__all_sorted_hexagons:
            print(hexagon)

    @staticmethod
    def __create_all_sorted_hexagons():
        for name in sorted(Hexagon.__name_to_hexagon.keys()):
            Hexagon.__all_sorted_hexagons.append(
                Hexagon.__name_to_hexagon[name])

        for (index, hexagon) in enumerate(Hexagon.__all_sorted_hexagons):
            hexagon.index = index

        Hexagon.all = Hexagon.__all_sorted_hexagons

    @staticmethod
    def __create_delta_u_and_v():
        Hexagon.__delta_u = array.array('b', [+1, +1, +0, -1, -1, +0])
        Hexagon.__delta_v = array.array('b', [+0, -1, -1, +0, +1, +1])

    @staticmethod
    def __create_layout():

        Hexagon.__layout = []

        Hexagon.__layout.append((1, ["g1", "g2", "g3", "g4", "g5", "g6"]))
        Hexagon.__layout.append(
            (0, ["f1", "f2", "f3", "f4", "f5", "f6", "f7"]))
        Hexagon.__layout.append((1, ["e1", "e2", "e3", "e4", "e5", "e6"]))
        Hexagon.__layout.append(
            (0, ["d1", "d2", "d3", "d4", "d5", "d6", "d7"]))
        Hexagon.__layout.append((1, ["c1", "c2", "c3", "c4", "c5", "c6"]))
        Hexagon.__layout.append(
            (0, ["b1", "b2", "b3", "b4", "b5", "b6", "b7"]))
        Hexagon.__layout.append((1, ["a1", "a2", "a3", "a4", "a5", "a6"]))

    @staticmethod
    def __create_hexagons():

        # Row "a"
        Hexagon('a1', (-1, -3), ring=0, label_side=Side.WEST)
        Hexagon('a2', (-0, -3), ring=0)
        Hexagon('a3', (1, -3), ring=0)
        Hexagon('a4', (2, -3), ring=0)
        Hexagon('a5', (3, -3), ring=0)
        Hexagon('a6', (4, -3), ring=0, label_side=Side.EAST)

        # Row "b"
        Hexagon('b1', (-2, -2), ring=0, label_side=Side.WEST)
        Hexagon('b2', (-1, -2), ring=1)
        Hexagon('b3', (0, -2), ring=1)
        Hexagon('b4', (1, -2), ring=1)
        Hexagon('b5', (2, -2), ring=1)
        Hexagon('b6', (3, -2), ring=1)
        Hexagon('b7', (4, -2), ring=0, label_side=Side.EAST)

        # Row "c"
        Hexagon('c1', (-2, -1), ring=0, label_side=Side.WEST)
        Hexagon('c2', (-1, -1), ring=1)
        Hexagon('c3', (0, -1), ring=2)
        Hexagon('c4', (1, -1), ring=2)
        Hexagon('c5', (2, -1), ring=1)
        Hexagon('c6', (3, -1), ring=0, label_side=Side.EAST)

        # Row "d"
        Hexagon('d1', (-3, 0), ring=0, label_side=Side.WEST)
        Hexagon('d2', (-2, 0), ring=1)
        Hexagon('d3', (-1, 0), ring=2)
        Hexagon('d4', (0, 0), ring=3)
        Hexagon('d5', (1, 0), ring=2)
        Hexagon('d6', (2, 0), ring=1)
        Hexagon('d7', (3, 0), ring=0, label_side=Side.EAST)

        # Row "e"
        Hexagon('e1', (-3, 1), ring=0, label_side=Side.WEST)
        Hexagon('e2', (-2, 1), ring=1)
        Hexagon('e3', (-1, 1), ring=2)
        Hexagon('e4', (0, 1), ring=2)
        Hexagon('e5', (1, 1), ring=1)
        Hexagon('e6', (2, 1), ring=0, label_side=Side.EAST)

        # Row "f"
        Hexagon('f1', (-4, 2), ring=0, label_side=Side.WEST)
        Hexagon('f2', (-3, 2), ring=1)
        Hexagon('f3', (-2, 2), ring=1)
        Hexagon('f4', (-1, 2), ring=1)
        Hexagon('f5', (0, 2), ring=1)
        Hexagon('f6', (1, 2), ring=1)
        Hexagon('f7', (2, 2), ring=0, label_side=Side.EAST)

        # Row "g"
        Hexagon('g1', (-4, 3), ring=0, label_side=Side.WEST)
        Hexagon('g2', (-3, 3), ring=0)
        Hexagon('g3', (-2, 3), ring=0)
        Hexagon('g4', (-1, 3), ring=0)
        Hexagon('g5', (0, 3), ring=0)
        Hexagon('g6', (1, 3), ring=0, label_side=Side.EAST)


def draw_board(scale_factor=1, with_all_labels=False, without_labels=False, with_decoration=False,
               do_rendering=True, with_gradient=True, with_opacity=True, do_tiny=False, do_large=False, with_texture=False,
               with_concentrated_texture=False, with_concentric_hexas=False, hexagon_line_color=None, with_hexagon_border=True):

    print()
    print("draw_board: ...")

    global BOARD_CONFIG
    global CUBE_CONFIG
    
    assert not (do_tiny and do_large)

    if do_tiny:
        BOARD_CONFIG = make_board_config(do_tiny=True)
        Hexagon.reset()
        Hexagon.init()

    if do_large:
        CUBE_CONFIG = make_cube_config(do_large=True)
        BOARD_CONFIG = make_board_config()
        Hexagon.reset()
        Hexagon.init()

    if without_labels:
        file_name = 'pijersi_board_without_labels'

    elif with_all_labels:
        file_name = 'pijersi_board_with_all_labels'

    else:
        file_name = 'pijersi_board_with_few_labels'

    if with_decoration:
        file_name += '_with_decoration'

    if not with_gradient:
        file_name += '_without_gradient'

    if not with_opacity:
        file_name += '_without_opacity'

    if with_texture:
        file_name += '_with_texture'

    if with_concentrated_texture:
        file_name += '_with_concentrated_texture'

    if with_concentric_hexas:
        file_name += '_with_concentric_hexas'

    if not do_rendering:
        file_name = file_name.replace('pijersi_', 'pijersi_laser_')

    if do_tiny:
        file_name = file_name.replace('pijersi_', 'tiny_pijersi_')

    if do_large:
        file_name = file_name.replace('pijersi_', 'large_pijersi_')

    if scale_factor != 1:
        file_name = f"scale-{scale_factor:.2f}-{file_name}"

    if hexagon_line_color is None:
        hexagon_line_color = BOARD_CONFIG.hexagon_line_color
        gradient_color = COLOR_TO_ENGRAVE

    else:
        gradient_color = hexagon_line_color

    # Define the board
    board = draw.Drawing(width=BOARD_CONFIG.board_width, height=BOARD_CONFIG.board_height,
                         origin=(-BOARD_CONFIG.board_width/2, -BOARD_CONFIG.board_height/2), 
                         fill='none')
    board.set_render_size(
        w=f"{scale_factor*BOARD_CONFIG.board_width_cm}cm",
        h=f"{scale_factor*BOARD_CONFIG.board_height_cm}cm")

    # Draw the outer rectangle
    if do_rendering:
        outer = draw.Rectangle(x=-BOARD_CONFIG.board_width/2,
                               y=-BOARD_CONFIG.board_height/2,
                               width=BOARD_CONFIG.board_width,
                               height=BOARD_CONFIG.board_height,
                               fill=BOARD_CONFIG.board_color)

    else:
        outer = draw.Rectangle(x=-BOARD_CONFIG.board_width/2 + BOARD_CONFIG.board_cut_margin,
                               y=-BOARD_CONFIG.board_height/2 + BOARD_CONFIG.board_cut_margin,
                               width=BOARD_CONFIG.board_width - 2*BOARD_CONFIG.board_cut_margin,
                               height=BOARD_CONFIG.board_height - 2*BOARD_CONFIG.board_cut_margin,
                               #fill='white',
                               fill='none',
                               stroke=COLOR_TO_CUT_1,
                               stroke_width=BOARD_CONFIG.line_width_max_to_cut)

    board.append(outer)

    # Draw the hexagons

    for abstract_hexagon in Hexagon.all:

        if do_tiny:
            if abstract_hexagon.name not in ['d3', 'd4', 'd5']:
                continue

        hexagon_vertex_data = []
        hexagon_vertices = []

        hexagon_scale = 1 - BOARD_CONFIG.hexagon_padding/BOARD_CONFIG.hexagon_width

        for vertex_index in range(BOARD_CONFIG.hexagon_vertex_count):
            vertex_angle = (1/2 + vertex_index) * \
                BOARD_CONFIG.hexagon_side_angle


            hexagon_center = abstract_hexagon.center

            hexagon_vertex = hexagon_center

            hexagon_vertex = hexagon_vertex + hexagon_scale*BOARD_CONFIG.hexagon_side * \
                math.cos(vertex_angle)*BOARD_CONFIG.unit_x

            hexagon_vertex = hexagon_vertex + hexagon_scale*BOARD_CONFIG.hexagon_side * \
                math.sin(vertex_angle)*BOARD_CONFIG.unit_y

            hexagon_vertices.append(hexagon_vertex)

            hexagon_vertex_data.append(hexagon_vertex[0])
            hexagon_vertex_data.append(hexagon_vertex[1])

        hexagon_opacity = BOARD_CONFIG.hexagon_opacity * \
            (1 if abstract_hexagon.ring % 2 == 0 else 0.5)

        if with_gradient:
            hexagon_gradient = draw.RadialGradient(
                cx=abstract_hexagon.center[0], cy=abstract_hexagon.center[1], r=hexagon_scale*BOARD_CONFIG.hexagon_side)

            hexagon_gradient.add_stop(
                offset=0, color=gradient_color, opacity=hexagon_opacity*0.00)

            hexagon_gradient.add_stop(
                offset=1, color=gradient_color, opacity=hexagon_opacity*1.00)

            hexagon = draw.Lines(*hexagon_vertex_data,
                                 fill=hexagon_gradient,
                                 stroke=hexagon_line_color,
                                 stroke_width=BOARD_CONFIG.hexagon_line_width if with_hexagon_border else '',
                                 close=True)

        else:
            hexagon = draw.Lines(*hexagon_vertex_data,
                                 fill=None if abstract_hexagon.ring % 2 == 1 else 'black',
                                 fill_opacity=hexagon_opacity*0.5 if with_opacity else 0,
                                 stroke=hexagon_line_color,
                                 stroke_width=BOARD_CONFIG.hexagon_line_width*2,
                                 close=True)

        board.append(hexagon)

        if with_decoration and abstract_hexagon.ring % 2 == 1:

            if with_concentric_hexas:
                draw_concentric_hexas(board, hexagon_center, hexagon_vertices, hexagon_line_color=hexagon_line_color)

            elif with_concentrated_texture:
                draw_concentrated_texture(board, hexagon_center, hexagon_vertices, segment_count=600, hexagon_line_color=hexagon_line_color)

            elif with_texture:
                draw_gradient_texture(board, hexagon_center, hexagon_vertices, segment_count=800, hexagon_line_color=hexagon_line_color)

            else:
                draw_uniform_texture(board, hexagon_center, hexagon_vertices, segment_count=600, hexagon_line_color=hexagon_line_color)


        if with_decoration and abstract_hexagon.ring % 2 == 0:

            decorater_polygon_1_side_count = 12
            decorater_polygon_1_scale = 0.70

            decorater_polygon_1_vertex_data = []
            decorater_polygon_1_vertices = []

            for vertex_index in range(decorater_polygon_1_side_count):
                vertex_angle = (vertex_index)*2*math.pi / \
                    decorater_polygon_1_side_count

                decorater_polygon_1_vertex = abstract_hexagon.center

                decorater_polygon_1_vertex = decorater_polygon_1_vertex + decorater_polygon_1_scale*BOARD_CONFIG.hexagon_side * \
                    math.cos(vertex_angle)*BOARD_CONFIG.unit_x

                decorater_polygon_1_vertex = decorater_polygon_1_vertex + decorater_polygon_1_scale*BOARD_CONFIG.hexagon_side * \
                    math.sin(vertex_angle)*BOARD_CONFIG.unit_y

                decorater_polygon_1_vertex_data.append(
                    decorater_polygon_1_vertex[0])
                decorater_polygon_1_vertex_data.append(
                    decorater_polygon_1_vertex[1])

                decorater_polygon_1_vertices.append(decorater_polygon_1_vertex)

            decorater_polygon_1 = draw.Lines(*decorater_polygon_1_vertex_data,
                                           fill=None,
                                           fill_opacity=0,
                                           stroke=hexagon_line_color,
                                           stroke_width=BOARD_CONFIG.hexagon_line_width,
                                           close=True)
            board.append(decorater_polygon_1)

            for (vertex_1, vertex_2) in zip(decorater_polygon_1_vertices, decorater_polygon_1_vertices[1:] + [decorater_polygon_1_vertices[0]]):
                rotating_polygon_side_count = 6

                rotating_polygon_vertices = []
                for rotating_polygon_side_index in range(rotating_polygon_side_count):

                    if rotating_polygon_side_index == 0:
                        vector = vertex_2 - vertex_1
                        rotating_polygon_vertices.append(vertex_1)

                    else:
                        vector = vector.make_rotation(-2 *
                                                      math.pi/rotating_polygon_side_count)

                    rotating_polygon_vertices.append(
                        rotating_polygon_vertices[rotating_polygon_side_index] + vector)
                rotating_polygon_vertices.append(rotating_polygon_vertices[0])

                rotating_polygon_vertex_data = []
                for rotating_polygon_vertex in rotating_polygon_vertices:
                    rotating_polygon_vertex_data.append(
                        rotating_polygon_vertex[0])
                    rotating_polygon_vertex_data.append(
                        rotating_polygon_vertex[1])

                rotating_polygon = draw.Lines(*rotating_polygon_vertex_data,
                                              fill=None,
                                              fill_opacity=0,
                                              stroke=hexagon_line_color,
                                              stroke_width=BOARD_CONFIG.hexagon_line_width,
                                              close=True)
                board.append(rotating_polygon)


            decorater_circle_scale = 0.75
            decorater_circle_radius = decorater_circle_scale*BOARD_CONFIG.hexagon_side


            if with_concentric_hexas:
                draw_concentric_hexas(board, hexagon_center, hexagon_vertices, hexa_count=1, hexa_scale_min=0.93, hexa_scale_max=1.00,
                                      hexagon_line_color=hexagon_line_color)

            if with_concentrated_texture:
                draw_concentrated_texture(board, hexagon_center, hexagon_vertices, segment_count=500,
                                          masking_radius=decorater_circle_radius, hexagon_line_color=hexagon_line_color)

            if with_texture:

                if False:
                    decorater_circle = draw.Circle(cx=abstract_hexagon.center[0],
                                                   cy=abstract_hexagon.center[1],
                                                   r=decorater_circle_radius,
                                                   fill=None,
                                                   fill_opacity=0,
                                                   stroke=hexagon_line_color,
                                                   stroke_width=BOARD_CONFIG.hexagon_line_width,
                                                   )
                    board.append(decorater_circle)

                draw_uniform_texture(board, hexagon_center, hexagon_vertices, segment_count=1_500, masking_radius=decorater_circle_radius,
                                     hexagon_line_color=hexagon_line_color)

                draw_gradient_texture(board, hexagon_center, hexagon_vertices, segment_count=500, hexagon_line_color=hexagon_line_color)


        if without_labels:
            label_location = None

        elif with_all_labels:
            label_location = abstract_hexagon.center + BOARD_CONFIG.label_vertical_shift

        else:
            if abstract_hexagon.label_side is not None:
                if abstract_hexagon.label_side == Side.WEST:
                    label_location = abstract_hexagon.center - BOARD_CONFIG.label_horizontal_shift

                elif abstract_hexagon.label_side == Side.EAST:
                    label_location = abstract_hexagon.center + BOARD_CONFIG.label_horizontal_shift

                else:
                    label_location = None

            if do_tiny:
                if abstract_hexagon.name == 'd3':
                    label_location = abstract_hexagon.center - BOARD_CONFIG.label_horizontal_shift

                elif abstract_hexagon.name == 'd5':
                    label_location = abstract_hexagon.center + BOARD_CONFIG.label_horizontal_shift

                else:
                    label_location = None

        if label_location is not None:
            board.append(draw.Text(text=abstract_hexagon.name,
                                   font_size=BOARD_CONFIG.label_font_size,
                                   font_family=BOARD_CONFIG.label_font_family,
                                   x=label_location[0],
                                   y=label_location[1],
                                   center=True,
                                   fill=BOARD_CONFIG.label_color))

    print()
    print("draw_board: save as SVG ...")
    board.save_svg(os.path.join(_pictures_dir, f"{file_name}.svg"))
    print("draw_board: save as SVG done")

    print()
    print("draw_board: save as PNG ...")
    board.save_png(os.path.join(_pictures_dir, f"{file_name}.png"))
    print("draw_board: save as PNG done")

    if do_tiny or do_large:
        # >> reset to default
        CUBE_CONFIG = make_cube_config()
        BOARD_CONFIG = make_board_config()
        Hexagon.reset()
        Hexagon.init()

    print()
    print("draw_board: done")


def draw_concentric_hexas(board, hexagon_center, hexagon_vertices, hexa_count=12, hexa_scale_min=1/4, hexa_scale_max=1,
                          hexagon_line_color=None):

    if hexagon_line_color is None:
        hexagon_line_color = BOARD_CONFIG.hexagon_line_color


    hexagon_scale = 1 - BOARD_CONFIG.hexagon_padding/BOARD_CONFIG.hexagon_width
    hexagon_effective_side = hexagon_scale*BOARD_CONFIG.hexagon_side


    for hexa_index in range(hexa_count + 1):

        s = hexa_index/hexa_count

        fs = s**2

        hexa_scale = fs*hexa_scale_min + (1 - fs)*hexa_scale_max

        hexa_vertex_data = []
        hexa_vertices = []

        # hexa_side_count = 12
        # angle_shift = 0
        hexa_side_count = 6
        angle_shift = 0.5

        for vertex_index in range(hexa_side_count):
            vertex_angle = (vertex_index +angle_shift)*2*math.pi / \
                hexa_side_count

            hexa_vertex = hexagon_center

            hexa_vertex = hexa_vertex + hexa_scale*hexagon_effective_side * \
                math.cos(vertex_angle)*BOARD_CONFIG.unit_x

            hexa_vertex = hexa_vertex + hexa_scale*hexagon_effective_side * \
                math.sin(vertex_angle)*BOARD_CONFIG.unit_y

            hexa_vertex_data.append(
                hexa_vertex[0])
            hexa_vertex_data.append(
                hexa_vertex[1])

            hexa_vertices.append(hexa_vertex)

        hexa = draw.Lines(*hexa_vertex_data,
                                       fill=None,
                                       fill_opacity=0,
                                       stroke=hexagon_line_color,
                                       stroke_width=BOARD_CONFIG.hexagon_line_width,
                                       close=True)

        board.append(hexa)


def draw_concentrated_texture(board, hexagon_center, hexagon_vertices, segment_count=500, masking_radius=None,
                              hexagon_line_color=None):

    if hexagon_line_color is None:
        hexagon_line_color = BOARD_CONFIG.hexagon_line_color

    hexagon_side = TinyVector.norm(hexagon_vertices[0] - hexagon_center)

    for _ in range(segment_count):


        while True:
            border_points = []

            vertex_index = random.randint(0, 5)
            vertices = [hexagon_vertices[vertex_index], hexagon_vertices[(vertex_index + 1)%6]]
            p = random.uniform(0, 1)
            border_points.append( (1 - p)*vertices[0] + p*vertices[1] )

            vertex_index = (vertex_index + 3) % 6
            vertices = [hexagon_vertices[vertex_index], hexagon_vertices[(vertex_index + 1)%6]]
            p = random.uniform(0, 1)
            border_points.append( (1 - p)*vertices[0] + p*vertices[1] )

            border_side = TinyVector.norm(border_points[1] - border_points[0])

            alpha = 0.15
            beta = alpha
            t = random.betavariate(alpha=alpha, beta=beta)

            u = random.uniform(0.01, 0.06)*hexagon_side/border_side
            a = min(1, max(0, t - u/2))
            b = min(1, max(0, t + u/2))

            segment_edges = []
            segment_edges.append( (1 - a)*border_points[0] + a*border_points[1] )
            segment_edges.append( (1 - b)*border_points[0] + b*border_points[1] )

            if masking_radius is None:
                break

            else:
                validated_segment_edges = True

                for segment_edge in segment_edges:
                    segment_vector = segment_edge - hexagon_center
                    if TinyVector.norm(segment_vector) < masking_radius:
                        validated_segment_edges = False

                if validated_segment_edges:
                    break


        segment_data = []
        for segment_edge in segment_edges:
            segment_data.append(segment_edge[0])
            segment_data.append(segment_edge[1])

        segment = draw.Line(*segment_data,
                            fill=None,
                            fill_opacity=0,
                            stroke=hexagon_line_color,
                            stroke_width=BOARD_CONFIG.hexagon_line_width)

        board.append(segment)


def draw_uniform_texture(board, hexagon_center, hexagon_vertices, segment_count=500, masking_radius=None, hexagon_line_color=None):

    if hexagon_line_color is None:
        hexagon_line_color = BOARD_CONFIG.hexagon_line_color

    hexagon_side = TinyVector.norm(hexagon_vertices[0] - hexagon_center)

    for _ in range(segment_count):


        while True:
            border_points = []
            for _ in range(2):
                vertices = random.sample(hexagon_vertices, 2)
                p = random.uniform(0, 1)
                border_points.append( (1 - p)*vertices[0] + p*vertices[1] )

            border_side = TinyVector.norm(border_points[1] - border_points[0])

            t = random.uniform(0, 1)
            u = random.uniform(0.01, 0.08)*hexagon_side/border_side
            a = min(1, max(0, t - u/2))
            b = min(1, max(0, t + u/2))

            segment_edges = []
            segment_edges.append( (1 - a)*border_points[0] + a*border_points[1] )
            segment_edges.append( (1 - b)*border_points[0] + b*border_points[1] )

            if masking_radius is None:
                break

            else:
                validated_segment_edges = True

                for segment_edge in segment_edges:
                    segment_vector = segment_edge - hexagon_center
                    if TinyVector.norm(segment_vector) < masking_radius:
                        validated_segment_edges = False

                if validated_segment_edges:
                    break


        segment_data = []
        for segment_edge in segment_edges:
            segment_data.append(segment_edge[0])
            segment_data.append(segment_edge[1])

        segment = draw.Line(*segment_data,
                            fill=None,
                            fill_opacity=0,
                            stroke=hexagon_line_color,
                            stroke_width=BOARD_CONFIG.hexagon_line_width)

        board.append(segment)


def draw_gradient_texture(board, hexagon_center, hexagon_vertices, segment_count=500, hexagon_line_color=None):

    if hexagon_line_color is None:
        hexagon_line_color = BOARD_CONFIG.hexagon_line_color

    for _ in range(segment_count):

        # select a side as two consecutive vertices
        vertex_index_1 = random.randrange(6)
        vertex_index_2 = (vertex_index_1 + 1) % 6

        vertex_1 = hexagon_vertices[vertex_index_1]
        vertex_2 = hexagon_vertices[vertex_index_2]

        # select a first border_point along this side
        border_points = []
        p = random.uniform(0, 1)
        border_points.append(p*vertex_1 + (1 - p)*vertex_2)

        # the second border_point is the center of the hexagon
        border_points.append(hexagon_center)

        # define a small segment between the two border_points

        if False:
            # uniform distribution
            t = random.uniform(0, 1)

        elif False:
            # linear distribution
            f0 = 2
            f1 = 1

            u = random.uniform(0., 1.)
            t = (math.sqrt((f1**2-f0**2)*u + f0**2) - f0)/(f1-f0)

        elif True:
            # beta distribution
            alpha = 0.50
            beta = 5

            t = random.betavariate(alpha=alpha, beta=beta)

        width = random.uniform(0.02, 0.02)
        a = min(1, max(0, t - width/2))
        b = min(1, max(0, t + width/2))

        segment_edges = []

        segment_edges.append(
            border_points[0] + a*(border_points[1] - border_points[0]))

        segment_edges.append(
            border_points[0] + b*(border_points[1] - border_points[0]))

        segment_data = []
        for segment_edge in segment_edges:
            segment_data.append(segment_edge[0])
            segment_data.append(segment_edge[1])

        segment = draw.Line(*segment_data,
                            fill=None,
                            fill_opacity=0,
                            stroke=hexagon_line_color,
                            stroke_width=BOARD_CONFIG.hexagon_line_width)

        board.append(segment)


def draw_cubes_and_support(do_rendering=True, draw_support=True, draw_decorations=True, draw_cubes=True, with_negative=False):

    print()
    print("draw_cubes_and_support: ...")

    # if not do_rendering:
    #     assert draw_support != draw_decorations

    if do_rendering:
        file_name = 'pijersi_cubes'

    else:
        file_name = 'pijersi_laser_cubes'

        if draw_support:
            file_name += '_with_support'

        if draw_cubes:
                file_name += '_with_cubes'

        if draw_decorations:
            file_name += '_with_decorations'

        if with_negative:
            file_name += '_with_negative'

    # Define the support
    support = draw.Drawing(width=CUBE_CONFIG.support_width,
                           height=CUBE_CONFIG.support_height, origin=(0, 0))
    support.set_render_size(
        w=f"{CUBE_CONFIG.support_width_cm}cm", h=f"{CUBE_CONFIG.support_height_cm}cm")

    # Draw the outer rectangle
    if do_rendering:
        outer = draw.Rectangle(x=0, y=0,
                               width=CUBE_CONFIG.support_width,
                               height=CUBE_CONFIG.support_height,
                               fill=CUBE_CONFIG.support_color)

    else:
        if draw_support:
            outer = draw.Rectangle(x=CUBE_CONFIG.support_cut_margin, y=CUBE_CONFIG.support_cut_margin,
                                   width=CUBE_CONFIG.support_width - 2*CUBE_CONFIG.support_cut_margin,
                                   height=CUBE_CONFIG.support_height - 2*CUBE_CONFIG.support_cut_margin,
                                   fill='white',
                                   stroke=COLOR_TO_CUT_2,
                                   stroke_width=CUBE_CONFIG.line_width_max_to_cut)
        elif draw_decorations:
            outer = draw.Rectangle(x=0, y=0,
                                   width=CUBE_CONFIG.support_width,
                                   height=CUBE_CONFIG.support_height,
                                   fill='white',
                                   stroke='black')

    support.append(outer)

    # Draw the cubes

    for row_index in range(CUBE_CONFIG.row_count):
        for col_index in range(CUBE_CONFIG.col_count):
            abstract_cube = CUBE_CONFIG.layout[(row_index, col_index)]
            if abstract_cube is not None:

                cube_x = CUBE_CONFIG.cube_shift + col_index * \
                    (CUBE_CONFIG.cube_cut_margin +
                     CUBE_CONFIG.cube_side + CUBE_CONFIG.cube_shift)

                cube_y = CUBE_CONFIG.cube_shift + row_index * \
                    (CUBE_CONFIG.cube_cut_margin +
                     CUBE_CONFIG.cube_side + CUBE_CONFIG.cube_shift)

                if (not do_rendering) and draw_support and draw_cubes:
                    outer_cube = draw.Rectangle(x=cube_x - CUBE_CONFIG.cube_cut_margin/2,
                                                y=cube_y - CUBE_CONFIG.cube_cut_margin/2,
                                                width=CUBE_CONFIG.cube_side + CUBE_CONFIG.cube_cut_margin,
                                                height=CUBE_CONFIG.cube_side + CUBE_CONFIG.cube_cut_margin,
                                                fill='white',
                                                stroke=COLOR_TO_CUT_1,
                                                stroke_width=CUBE_CONFIG.line_width_max_to_cut)
                    support.append(outer_cube)

                draw_cube(support, abstract_cube, cube_x,
                          cube_y, do_rendering, draw_decorations, with_negative)

    print()
    print("draw_cubes_and_support: save as SVG ...")
    support.save_svg(os.path.join(_pictures_dir, f"{file_name}.svg"))
    print("draw_cubes_and_support: save as SVG done")

    print()
    print("draw_cubes_and_support: save as PNG ...")
    support.save_png(os.path.join(_pictures_dir, f"{file_name}.png"))
    print("draw_cubes_and_support: save as PNG done")

    print()
    print("draw_cubes_and_support: done")


def draw_cube(support, abstract_cube, cube_x, cube_y, do_rendering=True, draw_decorations=True, with_negative=False):

    if do_rendering or with_negative:
        cube = draw.Rectangle(x=cube_x, y=cube_y,
                              width=CUBE_CONFIG.cube_side,
                              height=CUBE_CONFIG.cube_side,
                              fill='black' if abstract_cube.color == CubeColor.BLACK else 'white')
        support.append(cube)

    if with_negative:
        if abstract_cube.color == CubeColor.BLACK:
            cube_border_line_width = CUBE_CONFIG.decoration_line_width*0.75
            cube_border_width = CUBE_CONFIG.cube_side - cube_border_line_width
            cube_border = draw.Rectangle(x=cube_x + cube_border_line_width/2, y=cube_y + cube_border_line_width/2,
                                  width=cube_border_width,
                                  height=cube_border_width,
                                  fill=None,
                                  stroke='white',
                                  stroke_width=cube_border_line_width)
            support.append(cube_border)


    if do_rendering or draw_decorations:

        if abstract_cube.kind == CubeKind.ROCK:
            draw_rock(support, abstract_cube, cube_x, cube_y, do_rendering, with_negative)

        elif abstract_cube.kind == CubeKind.PAPER:
            draw_paper(support, abstract_cube, cube_x, cube_y, do_rendering, with_negative)

        elif abstract_cube.kind == CubeKind.SCISSORS:
            draw_scissors(support, abstract_cube, cube_x, cube_y, do_rendering, with_negative)

        elif abstract_cube.kind == CubeKind.WISE:
            draw_wise(support, abstract_cube, cube_x, cube_y, do_rendering, with_negative)


def draw_rock(support, abstract_cube, cube_x, cube_y, do_rendering=True, with_negative=False):

    center_x = cube_x + CUBE_CONFIG.cube_side/2
    center_y = cube_y + CUBE_CONFIG.cube_side/2

    circle = draw.Circle(cx=center_x, cy=center_y, r=CUBE_CONFIG.decoration_side/2,
                         fill=None,
                         fill_opacity=0,
                         stroke=('white' if abstract_cube.color ==
                                 CubeColor.BLACK else 'black') if do_rendering or with_negative else 'black',
                         stroke_width=CUBE_CONFIG.decoration_line_width)

    support.append(circle)


def draw_paper(support, abstract_cube, cube_x, cube_y, do_rendering=True, with_negative=False):
    paper_x = cube_x + CUBE_CONFIG.decoration_side/2
    paper_y = cube_y + CUBE_CONFIG.decoration_side/2

    paper = draw.Rectangle(x=paper_x, y=paper_y,
                           width=CUBE_CONFIG.decoration_side,
                           height=CUBE_CONFIG.decoration_side,
                           fill=None,
                           fill_opacity=0,
                           stroke=('white' if abstract_cube.color ==
                                 CubeColor.BLACK else 'black') if do_rendering or with_negative else 'black',
                           stroke_width=CUBE_CONFIG.decoration_line_width,
                           stroke_linejoin='miter')

    support.append(paper)


def draw_scissors(support, abstract_cube, cube_x, cube_y, do_rendering=True, with_negative=False):
    for segment_index in range(2):

        segment_data = []

        if segment_index == 0:
            segment_data.append(cube_x + CUBE_CONFIG.decoration_side/2)
            segment_data.append(cube_y + CUBE_CONFIG.decoration_side/2)

            segment_data.append(cube_x + CUBE_CONFIG.decoration_side*3/2)
            segment_data.append(cube_y + CUBE_CONFIG.decoration_side*3/2)

        elif segment_index == 1:
            segment_data.append(cube_x + CUBE_CONFIG.decoration_side*3/2)
            segment_data.append(cube_y + CUBE_CONFIG.decoration_side/2)

            segment_data.append(cube_x + CUBE_CONFIG.decoration_side/2)
            segment_data.append(cube_y + CUBE_CONFIG.decoration_side*3/2)

        segment = draw.Line(*segment_data,
                            fill=None,
                            fill_opacity=0,
                            stroke=('white' if abstract_cube.color ==
                                 CubeColor.BLACK else 'black') if do_rendering or with_negative else 'black',
                            stroke_width=CUBE_CONFIG.decoration_line_width,
                            stroke_linecap='butt')

        support.append(segment)


def draw_wise(support, abstract_cube, cube_x, cube_y, do_rendering=True, with_negative=False):
    center_x = cube_x + CUBE_CONFIG.cube_side/2
    center_y = cube_y + CUBE_CONFIG.cube_side/2

    delta_x = CUBE_CONFIG.decoration_side/2
    delta_y = CUBE_CONFIG.decoration_side

    wise_data = list()

    angle_count = 100
    for angle_index in range(angle_count):
        angle_value = angle_index*2*math.pi/angle_count

        angle_sinus = math.sin(angle_value)
        angle_cosinus = math.cos(angle_value)

        x = center_x + delta_x*angle_cosinus/(1 + angle_sinus**2)
        y = center_y + delta_y*angle_cosinus * \
            angle_sinus/(1 + angle_sinus**2)

        wise_data.append(x)
        wise_data.append(y)

    wise = draw.Lines(*wise_data,
                      fill=None,
                      fill_opacity=0,
                      stroke=('white' if abstract_cube.color ==
                                 CubeColor.BLACK else 'black') if do_rendering or with_negative else 'black',
                      stroke_width=CUBE_CONFIG.decoration_line_width,
                      close=True)
    support.append(wise)


def draw_isolated_cubes(scale_factor=1):
    print()
    print("draw_isolated_cubes: ...")

    cube_dict = {}

    cube_dict['rock-black'] = Cube(kind=CubeKind.ROCK, color=CubeColor.BLACK)
    cube_dict['paper-black'] = Cube(kind=CubeKind.PAPER, color=CubeColor.BLACK)
    cube_dict['scissors-black'] = Cube(kind=CubeKind.SCISSORS,
                                       color=CubeColor.BLACK)
    cube_dict['wise-black'] = Cube(kind=CubeKind.WISE, color=CubeColor.BLACK)

    cube_dict['rock-white'] = Cube(kind=CubeKind.ROCK, color=CubeColor.WHITE)
    cube_dict['paper-white'] = Cube(kind=CubeKind.PAPER, color=CubeColor.WHITE)
    cube_dict['scissors-white'] = Cube(kind=CubeKind.SCISSORS,
                                       color=CubeColor.WHITE)
    cube_dict['wise-white'] = Cube(kind=CubeKind.WISE, color=CubeColor.WHITE)

    for (cube_name, abstract_cube) in cube_dict.items():

        support = draw.Drawing(width=CUBE_CONFIG.cube_side,
                               height=CUBE_CONFIG.cube_side, origin=(0, 0))

        support.set_render_size(w=f"{scale_factor*CUBE_CONFIG.cube_side_cm}cm",
                                h=f"{scale_factor*CUBE_CONFIG.cube_side_cm}cm")

        draw_cube(support, abstract_cube, cube_x=0, cube_y=0,
                  do_rendering=True, draw_decorations=True)

        print()
        print(f"draw_isolated_cubes: save {cube_name} as SVG ...")
        support.save_svg(os.path.join(_pictures_dir, f"{cube_name}.svg"))
        print(f"draw_isolated_cubes: save {cube_name} as SVG done")

        print()
        print(f"draw_cubes_and_support: save {cube_name} as PNG ...")
        support.save_png(os.path.join(_pictures_dir, f"{cube_name}.png"))
        print(f"draw_isolated_cubes: save {cube_name} as PNG done")

    print()
    print("draw_isolated_cubes: done")


def main():

    if False:
        draw_board(do_rendering=False, with_all_labels=False, with_decoration=True,
                   do_tiny=False, with_gradient=False, with_opacity=False)


    if False:
        draw_board(do_rendering=True, with_all_labels=False, with_decoration=True, with_gradient=False, with_opacity=False,
                   with_concentric_hexas=True)

    if False:
        draw_board(do_rendering=True, with_all_labels=False, with_decoration=True, with_gradient=False, with_opacity=False,
                   with_concentrated_texture=True)

    if False:
        # -- Simulate texture with a gradient
        draw_board(do_rendering=True, with_all_labels=False, with_decoration=True, with_gradient=False, with_opacity=False,
                   with_texture=True)

        # -- Generate accurate PNG for pijersi-certu, so use a large scale_factor
        draw_board(scale_factor=5., do_rendering=True, without_labels=True, with_decoration=True, with_gradient=False, with_opacity=False,
                   with_texture=True)


    if False:
        # -- Generate accurate PNG for pijersi-certu, so use a large scale_factor
        draw_isolated_cubes(scale_factor=18)

        draw_board(scale_factor=5., without_labels=True,
                   with_decoration=True, 
                   hexagon_line_color='#40210F',
                    with_hexagon_border=False)


    if True:
        draw_board(do_rendering=False, do_large=True, with_all_labels=False,
                   with_decoration=True, with_gradient=False, with_opacity=False, with_texture=False)

    if False:
        draw_board(do_rendering=False, with_all_labels=False,
                   with_decoration=True, do_tiny=True)

        draw_board(do_rendering=False, with_all_labels=False,
                   with_decoration=True, do_tiny=True, with_gradient=False)

        draw_board(do_rendering=False, with_all_labels=False, with_decoration=True,
                   do_tiny=True, with_gradient=False, with_opacity=False)

    if False:
        draw_board(with_all_labels=True)
        draw_board(with_all_labels=False)

        draw_board(without_labels=True)
        draw_board(without_labels=True, with_decoration=True)

        draw_board(with_all_labels=False, with_decoration=True)

        draw_board(with_all_labels=False,
                   with_decoration=True, with_gradient=False)

        draw_board(with_all_labels=False,
                   with_decoration=True, with_gradient=False, with_opacity=False)

        draw_board(do_rendering=False, with_all_labels=False,
                   with_decoration=True)

        draw_board(do_rendering=False, with_all_labels=False,
                   with_decoration=True, with_gradient=False)

        draw_board(do_rendering=False, with_all_labels=False,
                   with_decoration=True, with_gradient=False, with_opacity=False)

    if False:
        draw_cubes_and_support()

        draw_cubes_and_support(do_rendering=False, with_negative=False)
        draw_cubes_and_support(do_rendering=False, with_negative=True)

        draw_cubes_and_support(do_rendering=False, draw_support=True, draw_decorations=False, draw_cubes=False)

        draw_cubes_and_support(do_rendering=False, draw_support=True, draw_decorations=False)

        draw_cubes_and_support(do_rendering=False, draw_support=False, draw_decorations=True, with_negative=True)
        draw_cubes_and_support(do_rendering=False, draw_support=False, draw_decorations=True, with_negative=False)


CUBE_CONFIG = make_cube_config()
BOARD_CONFIG = make_board_config()

Hexagon.init()

if __name__ == "__main__":

    print()
    print("__main__: Hello")
    print()
    print(f"__main__: Python sys.version = {sys.version}")

    main()

    print()
    print("__main__: Bye")

    if True:
        print()
        _ = input("__main__: done ; press enter to terminate")
