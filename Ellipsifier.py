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
    filename = "TestImage.jpg"

    # Set options for parser
    parser = Parse.Parse()
    parser.threshold = 7
    parser.precision = 3
    parser.minimum_size = 2

    # Parse the image
    points = parser.evaluate_image(filename)

    # Draw the parsed image
    if len(points > 0):
        logfile = filename + "log.txt"
        file = open(logfile)
        for p in points:
            file.write("((" + p[0][0] + ", " + p[0][1] + ", " + p[0][2] + "),(" +
                       p[1][0] + ", " + p[1][1] + ", " + p[1][2] + "))")

        drawer = Draw
        drawer.draw_image(points, "", parser.width, parser.height)


if __name__ == "__main__":
    main()
