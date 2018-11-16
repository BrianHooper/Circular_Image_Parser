#!/usr/bin/env python
"""
    Converts a raster image to an ellipsified version
"""

__author__ = "Brian Hooper"
__copyright__ = "Copyright (c) 2018 Brian Hooper"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "brian_hooper@msn.com"

import Parse
import Draw
import os
import configparser
from ast import literal_eval as make_tuple


def parse_from_file(filename, extension, format, scale):
    try:
        file = open(filename + ".txt", "r")
        lines = file.readlines()
        file.close()

        points = []
        for line in lines:
            points.append(make_tuple(line))

        parser = Parse.Parse(filename, extension)
        color_points = parser.get_all_colors(points)

        return parser.width, parser.height, color_points
    except IOError:
        print("Error opening text file " + filename + ".txt")
        return 0, 0, []


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

    drawer = Draw

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
        drawer.output_background_color = make_tuple(config['DRAWING']['Background_Color'])
        drawer.outer_color_threshold = float(config['DRAWING']['Outer_Color'])
        drawer.inner_color_width = float(config['DRAWING']['Inner_Width'])
        drawer.border_width = int(config['DRAWING']['Border_Width'])
        drawer.border_color = make_tuple(config['DRAWING']['Border_Color'])
        drawer.border_radius_threshold = int(config['DRAWING']['Border_Threshold'])
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
                print("Parsing " + filename)
                for i in range(0, num_passes):
                    parse_image(filename, extension, i + 1, thresholds[i], precision[i], min_sizes[i], max_sizes[i], threads)
            if draw:
                print("Drawing " + filename)
                width, height, points = parse_from_file(filename, extension, format, scale)
                if len(points) > 0:
                    if format == "png":
                        drawer.draw_png(points, filename + "_output.png", width, height)
                    elif format == "svg":
                        pass
            print("Ellipsifying " + filename + " finished.")
        else:
            print("Error: " + file + " not found")

if __name__ == "__main__":
    main()
