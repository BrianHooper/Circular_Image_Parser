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


def main():
    filename = "tinybee.jpg"

    # Set options for parser
    parser = Parse.Parse()
    parser.threshold = 30
    parser.precision = 2
    parser.minimum_size = 2

    # Parse the image
    points = parser.evaluate_image(filename)

    # Draw the parsed image
    if len(points) > 0:
        logfile = "log.txt"
        file = open(logfile, "w+")
        for p in points:
            file.write("((" + str(p[0][0]) + ", " + str(p[0][1]) + ", " + str(p[0][2]) + "),(" +
                       str(p[1][0]) + ", " + str(p[1][1]) + ", " + str(p[1][2]) + "))\n")

        drawer = Draw
        drawer.draw_image(points, "output.png", parser.width, parser.height)


if __name__ == "__main__":
    main()
