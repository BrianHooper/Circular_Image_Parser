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
import os
from ast import literal_eval as make_tuple

def parse_svg_from_file(filename, scale):
    try:
        file = open(filename + ".txt", "r")
        lines = file.readlines()
        file.close()

        points = []
        for line in lines:
            points.append(make_tuple(line))

        parser = Parse.Parse(filename)
        color_points = parser.get_all_colors(points)

        draw_svg(filename, color_points, parser.width, parser.height, scale)
    except IOError:
        print("Error opening text file " + filename + ".txt")
        return


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


def parse_image(filename, threshold, precision, min, max, threads):
    # Open the file
    parser = Parse.Parse(filename)

    if parser.is_opened():
        # Set options for parser
        parser.threshold = threshold
        parser.precision = precision

        parser.minimum_size = min
        parser.maximum_size = max

        parser.num_threads = threads

        # Parse the image
        parser.evaluate_image()


def draw_image(filename, points, width, height):
    if filename is None or points is None:
        return

    if len(points) > 0:
        drawer = Draw
        drawer.draw_image(points, filename + "_output.png", width, height)


def draw_svg(filename, points, width, height, scale):
    if filename is None or points is None:
        return

    if len(points) > 0:
        drawer = Draw
        drawer.draw_svg(points, filename + "_output.svg", width, height, scale)


def create_image(file_name):
    filename = "images/" + file_name

    # Set this to true if the program should attempt to load a partially completed file
    load_partial = True
    if not load_partial:
        if os.path.exists(filename + ".txt"):
            os.remove(filename + ".txt")

    print("First pass")
    parse_image(filename, 6, 3, 20, 250, 4)
    parse_from_file(filename)
    print("Second pass")
    parse_image(filename, 15, 3, 10, 250, 4)
    print("Third pass")
    parse_image(filename, 25, 3, 5, 250, 4)
    print("Fourth pass")
    parse_image(filename, 80, 3, 2, 250, 4)
    parse_from_file(filename)


def main():
    for num in range(1, 16):
        create_image(str(num))



if __name__ == "__main__":
    main()
