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
output_background_color = (0, 0, 0)  # Background color of the final image
outer_color_threshold = 1  # How much lighter to color the outer region of the circle
inner_color_width = 2 / 3  # Percentage of the circle taken up by the inner circle
border_width = 2  # Thickness of the border
border_color = (0, 0, 0)  # Color of the border
border_radius_threshold = 4  # Don't draw the border if the radius is less than this


def draw_image(points, filename, width, height):
    if len(points) == 0 or len(filename) == 0 or width == 0 or height == 0:
        return

    # Load the surface for drawing
    surface = gizeh.Surface(width=width, height=height, bg_color=output_background_color)
    for point in points:
        x = point[0][0]
        y = point[0][1]

        # Draw the outer color
        radius = point[0][2]
        outer_color = (((point[1][0] + (255 - point[1][0]) / 2) / 255),
                       ((point[1][1] + (255 - point[1][1]) / 2) / 255),
                       ((point[1][2] + (255 - point[1][2]) / 2) / 255))

        # Don't draw the border if the radius is smaller than the threshold
        if radius < border_radius_threshold:
            border = 0
        else:
            border = border_width

        # Draw the outer color and border
        circle = gizeh.circle(r=radius, xy=[x, y], fill=outer_color,
                              stroke_width=border, stroke=border_color)
        circle.draw(surface)

        # Draw the inner color
        inner_color = (point[1][0] / 255,
                       point[1][1] / 255,
                       point[1][2] / 255)
        radius = int(2 * (radius / 3))
        circle = gizeh.circle(r=radius, xy=[x, y], fill=inner_color)
        circle.draw(surface)

    # Save the completed image
    surface.write_to_png(filename)
