#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""pijersi_svg.py draws SVG pictures for the PIJERSI boardgame."""

import os
import sys

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


def draw_pijersi_board():
    print()
    print("draw_pijersi_board: ...")

    d = draw.Drawing(200, 100, origin='center')
    
    # Draw a rectangle
    r = draw.Rectangle(-80, -50, 40, 50, fill='#1248ff')
    r.append_title("Our first rectangle")  # Add a tooltip
    d.append(r)

    print()
    print("draw_pijersi_board: save as SVG ...")
    d.save_svg(os.path.join(_pictures_dir, 'pijersi_board.svg'))
    print("draw_pijersi_board: save as SVG done")

    print()
    print("draw_pijersi_board: save as PNG ...")
    d.save_png(os.path.join(_pictures_dir, 'pijersi_board.png'))
    print("draw_pijersi_board: save as PNG done")

    print()
    print("draw_pijersi_board: done")


def main():
    draw_pijersi_board()


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
