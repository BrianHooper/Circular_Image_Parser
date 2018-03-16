#!/usr/bin/env python
"""
    Draws circles on an image using
"""

__author__ = "Brian Hooper"
__copyright__ = "Copyright (c) 2018 Brian Hooper"
__license__ = "MIT"
__version__ = "0.2"
__email__ = "brian_hooper@msn.com"

import gizeh

# Drawing settings
outputbackgroundcolor = (0, 0, 0)  # Background color of the final image
outer_color_threshold = 2  # How much lighter to color the outer region of the circle
inner_color_width = 2 / 3  # Percentage of the circle taken up by the inner circle
border_width = 2  # Thickness of the border
border_color = (0, 0, 0)  # Color of the border

def draw_image(points, filename, width, height):
    surface = gizeh.Surface(width=width, height=height, bg_color=outputbackgroundcolor)
    for point in points:
        x = point[0][0]
        y = point[0][1]

        # Draw the outer color
        radius = point[0][2]
        outer_color = ((255 - (point[1][0] / outer_color_threshold)) / 255,
                       (255 - (point[1][1] / outer_color_threshold)) / 255,
                       (255 - (point[1][2] / outer_color_threshold)) / 255)
        circle = gizeh.circle(r=radius, xy=[x, y], fill=outer_color,
                              stroke_width=border_width, stroke=border_color)
        circle.draw(surface)

        # Draw the inner color
        inner_color = (point[1][0] / 255,
                       point[1][1] / 255,
                       point[1][2] / 255)
        radius = int(2 * (radius / 3))
        circle = gizeh.circle(r=radius, xy=[x, y], fill=inner_color)
        circle.draw(surface)

    surface.write_to_png(filename)
