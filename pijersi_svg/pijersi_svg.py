#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pijersi_svg.py draws SVG pictures for the PIJERSI boardgame."""

import array
from dataclasses import dataclass
import enum
import math
import os
import sys

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
class CanvasConfig:

    board_width_cm: float = None
    board_height_cm: float = None

    board_width: float = None
    board_height: float = None

    hexagon_width: float = None
    hexagon_side: float = None
    hexagon_height: float = None
    hexagon_line_width: float = None

    hexagon_vertex_count: int = None
    hexagon_side_angle: float = None

    origin: TinyVector = None

    unit_x: TinyVector = None
    unit_y: TinyVector = None

    unit_u: TinyVector = None
    unit_v: TinyVector = None

    label_font_family: str = None
    label_font_size: int = None
    label_shift: TinyVector = None

    hexagon_opacity: float = None


def make_canvas_config():
    
    print()
    print("make_canvas_config: ...")

    # Compute the sizes in cm

    hexagon_width_cm = 3
    hexagon_side_cm = hexagon_width_cm/math.sqrt(3)
    hexagon_height_cm = 2*hexagon_side_cm
    hexagon_line_width_cm = 0.1/4

    max_horizontal_hexagon_count = 7
    max_vertical_hexagon_count = 7

    board_left_margin_cm = hexagon_width_cm/2
    board_right_margin_cm = hexagon_width_cm/2

    board_top_margin_cm = hexagon_side_cm
    board_bottom_margin_cm = hexagon_side_cm

    board_width_cm = (board_left_margin_cm +
                      max_horizontal_hexagon_count*hexagon_width_cm +
                      board_right_margin_cm)

    board_height_cm = (board_top_margin_cm +
                       (max_vertical_hexagon_count//2)*hexagon_side_cm +
                       (max_vertical_hexagon_count - max_vertical_hexagon_count//2)*hexagon_height_cm +
                       board_bottom_margin_cm)
    
    

    # Deduce other sizes in pixels

    board_width = 4096
    board_height = board_width*(board_height_cm/board_width_cm)

    hexagon_width = board_width*(hexagon_width_cm/board_width_cm)
    hexagon_side = board_width*(hexagon_side_cm/board_width_cm)
    hexagon_height = board_width*(hexagon_height_cm/board_width_cm)

    hexagon_line_width = max(
        1, board_width*(hexagon_line_width_cm/board_width_cm))

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
    label_font_family = 'Helvetica'
    label_font_size = int(hexagon_width*0.20)
    label_shift = -0.60*hexagon_side*unit_y

    # color and etc.
    hexagon_opacity = 0.20
    
    # make and return the CanvasConfig
    canvas_config = CanvasConfig(board_width_cm=board_width_cm,
                        board_height_cm=board_height_cm,

                        board_width=board_width,
                        board_height=board_height,

                        hexagon_width=hexagon_width,
                        hexagon_side=hexagon_side,
                        hexagon_height=hexagon_height,
                        hexagon_line_width=hexagon_line_width,

                        hexagon_vertex_count=hexagon_vertex_count,
                        hexagon_side_angle=hexagon_side_angle,

                        origin=origin,

                        unit_x=unit_x,
                        unit_y=unit_y,

                        unit_u=unit_u,
                        unit_v=unit_v,

                        label_font_family=label_font_family,
                        label_font_size=label_font_size,
                        label_shift=label_shift,

                        hexagon_opacity=hexagon_opacity)

    print()
    print(f"make_canvas_config: board_width_cm = {board_width_cm:.2f} ")
    print(f"make_canvas_config: board_height_cm = {board_height_cm:.2f}")
    print()
    print(f"make_canvas_config: hexagon_width_cm = {hexagon_width_cm:.2f}")
    print(f"make_canvas_config: hexagon_height_cm = {hexagon_height_cm:.2f}")
    print(f"make_canvas_config: hexagon_side_cm = {hexagon_side_cm:.2f}")

    print()
    print("make_canvas_config: done")
    return canvas_config

class Hexagon:

    @enum.unique
    class Direction(enum.IntEnum):
        PHI_090 = 0
        PHI_150 = 1
        PHI_210 = 2
        PHI_270 = 3
        PHI_330 = 4
        PHI_030 = 5
        assert PHI_090 < PHI_150 < PHI_210 < PHI_270 < PHI_330 < PHI_030

    Self = TypeVar("Self", bound="Hexagon")

    __slots__ = ('name', 'position_uv', 'ring',
                 'index', 'center', 'vertex_data')

    __all_sorted_hexagons = []
    __init_done = False
    __layout = []
    __name_to_hexagon = {}
    __position_uv_to_hexagon = {}

    all = None  # shortcut to Hexagon.get_all()

    def __init__(self, name: str, position_uv: Tuple[int, int], ring: int):

        assert name not in Hexagon.__name_to_hexagon
        assert len(position_uv) == 2
        assert position_uv not in Hexagon.__position_uv_to_hexagon
        assert len(name) == 2

        self.name = name
        self.position_uv = position_uv
        self.ring = ring
        self.index = None

        Hexagon.__name_to_hexagon[self.name] = self
        Hexagon.__position_uv_to_hexagon[position_uv] = self

        (u, v) = self.position_uv

        self.center = CANVAS_CONFIG.origin + CANVAS_CONFIG.hexagon_width * \
            (u*CANVAS_CONFIG.unit_u + v*CANVAS_CONFIG.unit_v)

        self.vertex_data = list()

        for vertex_index in range(CANVAS_CONFIG.hexagon_vertex_count):
            vertex_angle = (1/2 + vertex_index) * \
                CANVAS_CONFIG.hexagon_side_angle

            hexagon_vertex = self.center
            hexagon_vertex = hexagon_vertex + CANVAS_CONFIG.hexagon_side * \
                math.cos(vertex_angle)*CANVAS_CONFIG.unit_x
            hexagon_vertex = hexagon_vertex + CANVAS_CONFIG.hexagon_side * \
                math.sin(vertex_angle)*CANVAS_CONFIG.unit_y

            self.vertex_data.append(hexagon_vertex[0])
            self.vertex_data.append(hexagon_vertex[1])

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
        Hexagon('a1', (-1, -3), ring=0)
        Hexagon('a2', (-0, -3), ring=0)
        Hexagon('a3', (1, -3), ring=0)
        Hexagon('a4', (2, -3), ring=0)
        Hexagon('a5', (3, -3), ring=0)
        Hexagon('a6', (4, -3), ring=0)

        # Row "b"
        Hexagon('b1', (-2, -2), ring=0)
        Hexagon('b2', (-1, -2), ring=1)
        Hexagon('b3', (0, -2), ring=1)
        Hexagon('b4', (1, -2), ring=1)
        Hexagon('b5', (2, -2), ring=1)
        Hexagon('b6', (3, -2), ring=1)
        Hexagon('b7', (4, -2), ring=0)

        # Row "c"
        Hexagon('c1', (-2, -1), ring=0)
        Hexagon('c2', (-1, -1), ring=1)
        Hexagon('c3', (0, -1), ring=2)
        Hexagon('c4', (1, -1), ring=2)
        Hexagon('c5', (2, -1), ring=1)
        Hexagon('c6', (3, -1), ring=0)

        # Row "d"
        Hexagon('d1', (-3, 0), ring=0)
        Hexagon('d2', (-2, 0), ring=1)
        Hexagon('d3', (-1, 0), ring=2)
        Hexagon('d4', (0, 0), ring=3)
        Hexagon('d5', (1, 0), ring=2)
        Hexagon('d6', (2, 0), ring=1)
        Hexagon('d7', (3, 0), ring=0)

        # Row "e"
        Hexagon('e1', (-3, 1), ring=0)
        Hexagon('e2', (-2, 1), ring=1)
        Hexagon('e3', (-1, 1), ring=2)
        Hexagon('e4', (0, 1), ring=2)
        Hexagon('e5', (1, 1), ring=1)
        Hexagon('e6', (2, 1), ring=0)

        # Row "f"
        Hexagon('f1', (-4, 2), ring=0)
        Hexagon('f2', (-3, 2), ring=1)
        Hexagon('f3', (-2, 2), ring=1)
        Hexagon('f4', (-1, 2), ring=1)
        Hexagon('f5', (0, 2), ring=1)
        Hexagon('f6', (1, 2), ring=1)
        Hexagon('f7', (2, 2), ring=0)

        # Row "g"
        Hexagon('g1', (-4, 3), ring=0)
        Hexagon('g2', (-3, 3), ring=0)
        Hexagon('g3', (-2, 3), ring=0)
        Hexagon('g4', (-1, 3), ring=0)
        Hexagon('g5', (0, 3), ring=0)
        Hexagon('g6', (1, 3), ring=0)


def draw_pijersi_board():
    print()
    print("draw_pijersi_board: ...")

    # Define the board
    board = draw.Drawing(width=CANVAS_CONFIG.board_width, height=CANVAS_CONFIG.board_height,
                         origin=(-CANVAS_CONFIG.board_width/2, -CANVAS_CONFIG.board_height/2))
    board.set_render_size(
        w=f"{CANVAS_CONFIG.board_width_cm}cm", h=f"{CANVAS_CONFIG.board_height_cm}cm")

    # Draw the outer rectangle
    outer = draw.Rectangle(x=-CANVAS_CONFIG.board_width/2, y=-CANVAS_CONFIG.board_height/2,
                           width=CANVAS_CONFIG.board_width, height=CANVAS_CONFIG.board_height,
                           fill='#BF9B7A')
    board.append(outer)

    # Draw hexagons

    for abstract_hexagon in Hexagon.all:

        hexagon = draw.Lines(*abstract_hexagon.vertex_data,
                             fill=None, 
                             fill_opacity=CANVAS_CONFIG.hexagon_opacity*(1 if abstract_hexagon.ring % 2 == 0 else 0),
                             stroke='black',
                             stroke_width=CANVAS_CONFIG.hexagon_line_width,
                             close='true')

        label_location = abstract_hexagon.center + CANVAS_CONFIG.label_shift

        board.append(draw.Text(text=abstract_hexagon.name,
                               font_size=CANVAS_CONFIG.label_font_size,
                               font_family=CANVAS_CONFIG.label_font_family,
                               x=label_location[0],
                               y=label_location[1],
                               center=True,
                               fill='black'))

        board.append(hexagon)

    print()
    print("draw_pijersi_board: save as SVG ...")
    board.save_svg(os.path.join(_pictures_dir, 'pijersi_board.svg'))
    print("draw_pijersi_board: save as SVG done")

    print()
    print("draw_pijersi_board: save as PNG ...")
    board.save_png(os.path.join(_pictures_dir, 'pijersi_board.png'))
    print("draw_pijersi_board: save as PNG done")

    print()
    print("draw_pijersi_board: done")


def main():
    draw_pijersi_board()


CANVAS_CONFIG = make_canvas_config()
Hexagon.init()

if __name__ == "__main__":

    print()
    print("Hello")
    print()
    print(f"Python sys.version = {sys.version}")

    main()

    print()
    print("Bye")

    if True:
        print()
        _ = input("main: done ; press enter to terminate")
