#!/usr/bin/env python
"""
    Converts a raster image to an ellipsified version
"""

__author__ = "Brian Hooper"
__copyright__ = "Copyright (c) 2018 Brian Hooper"
__license__ = "MIT"
__version__ = "0.2"
__email__ = "brian_hooper@msn.com"

import Parse
import Draw
from ast import literal_eval as make_tuple


def parse_from_file(filename):
    try:
        file = open(filename + ".txt", "r")
        lines = file.readlines()
        file.close()

        points = []
        for line in lines:
            points.append(make_tuple(line))

        parser = Parse.Parse(filename)
        color_points = parser.get_all_colors(points)

        draw_image(filename, color_points, parser.width, parser.height)
    except IOError:
        print("Error opening text file " + filename + ".txt")
        return


def parse_image(filename):
    # Open the file
    parser = Parse.Parse(filename)

    if parser.is_opened():
        # Set options for parser
        parser.threshold = 20
        parser.precision = 2
        parser.minimum_size = 2

        # Parse the image
        parser.evaluate_image()


def draw_image(filename, points, width, height):
    if filename is None or points is None:
        return

    if len(points) > 0:
        drawer = Draw
        drawer.draw_image(points, filename + "_output.png", width, height)


def main():
    filename = "images/" + "tinyhippo"
    parse_image(filename)
    # parse_from_file(filename)


if __name__ == "__main__":
    main()
