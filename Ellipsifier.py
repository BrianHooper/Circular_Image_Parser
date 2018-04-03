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
import configparser
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


def parse_image(filename, extension, pass_number, threshold, precision, min_size, max_size, threads):
    # Open the file
    parser = Parse.Parse(filename, extension)

    if parser.is_opened():
        # Set options for parser
        parser.threshold = threshold
        parser.precision = precision

        parser.minimum_size = min_size
        parser.maximum_size = max_size

        parser.num_threads = threads
        parser.pass_number = pass_number

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

    parse_image(filename, "jpg", 1, 6, 3, 20, 250, 4)
    parse_image(filename, "jpg", 2, 15, 3, 10, 250, 4)
    parse_image(filename, "jpg", 3, 25, 3, 5, 250, 4)
    parse_image(filename, "jpg", 4, 80, 3, 2, 250, 4)
    parse_from_file(filename)


def to_int_list(input_string):
    input_string = input_string.replace('}', '').replace('{', '').replace(' ', '').split(',')
    output_list = []
    for index in input_string:
        output_list.append(int(index))

    return output_list


def main():
    config = configparser.ConfigParser(allow_no_value=True)

    try:
        config.read_file(open('config.ini'))
    except FileNotFoundError:
        print("Cannot find config file")
        return

    try:
        files = config['FILES']
        thresholds = to_int_list(config['IMAGE SETTINGS']['Thresholds'])
        min_sizes = to_int_list(config['IMAGE SETTINGS']['Min_size'])
        max_sizes = to_int_list(config['IMAGE SETTINGS']['Max_size'])
        precision = to_int_list(config['IMAGE SETTINGS']['Precision'])
        parse = config['SETTINGS'].getboolean('Parse')
        draw = config['SETTINGS'].getboolean('Draw')
        partial = config['SETTINGS'].getboolean('LoadPartial')
        threads = int(config['SETTINGS']['Threads'])
        format = config['OUTPUT']['Format']
        scale = float(config['OUTPUT']['Scale'])
    except KeyError:
        print("Error parsing config file")
        return

    if not (len(thresholds) == len(min_sizes) == len(max_sizes) == len(precision)):
        print("Error, length of settings lists do not match")
        return

    if len(files) == 0:
        return

    num_passes = len(thresholds)

    for file in files:
        if os.path.exists(file):
            file = file.split('.')
            filename = file[0]
            extension = file[1]

            if not partial:
                if os.path.exists(filename + ".txt"):
                    os.remove(filename + ".txt")

            if parse:
                for i in range(0, num_passes):
                    parse_image(filename, extension, i + 1, thresholds[i], precision[i], min_sizes[i], max_sizes[i], threads)
            if draw:
                print("Draw")


if __name__ == "__main__":
    main()
