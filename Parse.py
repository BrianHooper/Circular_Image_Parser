#!/usr/bin/env python
"""
    Parses an image to find circles using Pillow
"""

__author__ = "Brian Hooper"
__copyright__ = "Copyright (c) 2018 Brian Hooper"
__license__ = "MIT"
__version__ = "0.2"
__email__ = "brian_hooper@msn.com"

import queue
import math
import timeit
import multiprocessing
from PIL import Image, ImageDraw


class Parse:
    __opened = False

    # Input settings and image objects
    input_filename = ""  # File to parse
    image, image_pixels = 0, 0
    width, height = 0, 0
    special_color = (218, 235, 111)  # Special color used to mark regions as complete

    # Parse settings
    threshold = 7  # How close the colors are to each other
    precision = 10  # Distance between pixels to check
    minimum_size = 1  # Stop after no circles of at least this radius are found
    maximum_size = 150  # Largest radius to find
    radius_step = 1  # How far to increase the radius after each search
    threshold_increase_frequency = 10  # Increase color threshold after this many points are found
    threshold_increase_amount = 0  # Increase color threshold by this amount

    num_threads = 2

    def __init__(self, filename):
        self.input_filename = filename
        try:
            self.image = Image.open(filename + ".jpg")
            self.image_pixels = self.image.load()
            self.width, self.height = self.image.size
            self.__opened = True
        except IOError:
            print("Error opening " + filename + ".jpg")

    def is_opened(self):
        return self.__opened

    def evaluate_image(self):
        # Don't try and evaluate if there is no image loaded
        if not self.__opened:
            print("Error, no file opened.")
            return

        # Truncate the log file
        try:
            file = open(self.input_filename + ".txt", "w+")
            file.write("")
            file.close()
        except IOError:
            pass

        # Parse the image
        start = timeit.default_timer()  # Timer
        self.__parse_image()
        stop = timeit.default_timer()  # Timer

        # Calculate some information about the process
        print("Calculated in " + str(int(stop - start)) + " second(s).")

    def __thread_process(self, process_id, q, max_rad, max_x, max_y, lock, found_by):
        # Continue reading x values from the queue until it is empty
        while q.qsize() > 0:
            try:
                x_val = q.get(timeout=2)
                # Check each y value
                for y_val in range(self.precision, self.height - self.precision, self.precision):
                    # Find the largest radius at the current x, y location
                    current_radius = self.__find_biggest_radius(x_val, y_val, max_rad.value)

                    # Update the max radius if the current radius is larger than the previous max
                    lock.acquire()
                    try:
                        if current_radius > max_rad.value:
                            max_rad.value = current_radius
                            max_x.value = x_val
                            max_y.value = y_val
                            found_by.value = process_id
                    finally:
                        lock.release()
            except queue.Empty:
                continue

    def __parse_image(self):
        # For multiprocessing
        multi_context = multiprocessing.get_context("fork")
        lock = multi_context.Lock()
        q = multi_context.Queue()

        # Set up variables for maximum radius
        max_rad = multi_context.Value('i', 100)
        max_x = multi_context.Value('i', 0)
        max_y = multi_context.Value('i', 0)
        found_by = multi_context.Value('i', 0)

        while max_rad.value > self.minimum_size:
            # Clear previous value for maximum radius
            max_rad.value = 0
            max_x.value = 0
            max_y.value = 0

            # Find the largest circle within the color threshold on the image
            for xcoordinate in range(self.precision, self.width - self.precision, self.precision):
                q.put(xcoordinate)

            threads = []
            # Start threads
            for t in range(0, self.num_threads):
                p = multi_context.Process(target=self.__thread_process,
                                          args=(t, q, max_rad, max_x, max_y, lock, found_by))
                p.start()
                threads.append(p)

            # Terminate threads
            for thread in threads:
                thread.join()

            # Update maximum radius
            max_radius_found = (max_x.value, max_y.value, max_rad.value)

            # Save the found point
            print("Found radius " + str(max_radius_found) + " by process " + str(found_by.value))
            self.__write_log(max_radius_found)

            # Lock pixels by drawing the circle on the canvas using the special color
            self.__draw_special(max_x.value, max_y.value, max_rad.value)
            self.image.save(self.input_filename + "_temp.jpg")

    # Gets the color (r, g, b) tuple from a pixel located at (x, y)
    # Returns (255, 255, 255) if the pixel or image is invalid
    def __get_pixel(self, x, y):
        if x is None or y is None or self.image_pixels is None:
            return 255, 255, 255
        return self.image_pixels[x, y]

    # Get the relative points in a circle of a specified radius
    def __get_relative_points(self, radius):
        if radius <= 1:
            return []

        # Number of points to calculate within one quadrant
        radius = radius + 1
        quadrant = []
        angle = math.pi / (2 * radius)

        # Calculate relative locations of each point within the quadrant
        for x in range(1, radius + 1, self.radius_step):
            xcoord = int(round(radius * math.cos(x * angle)))
            ycoord = int(round(radius * math.sin(x * angle)))
            quadrant.append((xcoord, ycoord))

        # Calculate each relative point within the edge of the circle
        points = []
        for point in quadrant:
            points.append((point[0], point[1]))
            points.append((point[0], (point[1] * -1)))
            points.append(((point[0] * -1), point[1]))
            points.append(((point[0] * -1), (point[1] * -1)))
        return points

    # Convert relative points to absolute points based on an (x, y) point
    def __get_points(self, x, y, radius):
        relative_points = self.__get_relative_points(radius)
        absolute_points = []

        for relative_point in relative_points:
            absolute_points.append((x + relative_point[0], y + relative_point[1]))

        return absolute_points

    # Returns the mean difference between (r1, g1, b1) and (r2, g2, b2)
    @staticmethod
    def __closeness(x, y):
        # If either value is None, return greatest possible difference
        if x is None or y is None:
            return 255

        a = abs(x[0] - y[0])
        b = abs(x[1] - y[1])
        c = abs(x[2] - y[2])
        mean = (a + b + c) / 3
        return int(mean)

    # Determines if two numbers are within the threshold of each other
    def __within(self, x, y):
        return self.__closeness(x, y) <= self.threshold

    # Returns true if the (x, y) coordinates are within the bounds of the image
    def __on_image(self, x, y):
        if x < 0 or y < 0:
            return False
        if x > self.width - 1 or y > self.height - 1:
            return False
        return True

    # Returns true if the a circle of a specified radius located at (x, y) is outside the bounds of the image
    def __radius_off_image(self, x, y, radius):
        if (x - radius) < 0 or (y - radius) < 0:
            return True
        if (x + radius) > self.width or (y + radius) > self.height:
            return True
        return False

    # Tests if a circle of a given radius is within the color threshold
    def __test_radius(self, x, y, radius):
        if self.__radius_off_image(x, y, radius):
            return False
        if radius > self.maximum_size:
            return False
        absolute_points = self.__get_points(x, y, radius)

        center = self.__get_pixel(x, y)
        for point in absolute_points:
            if not self.__on_image(point[0], point[1]):
                return False
            pointcolor = self.__get_pixel(point[0], point[1])
            if pointcolor is None:
                return False
            if self.__is_special_color(pointcolor):
                return False
            if not self.__within(center, pointcolor):
                return False
        return True

    # Searches for the largest circle centered at point (x, y) is entirely within the color threshold
    def __find_biggest_radius(self, x, y, starting_radius):
        radius = starting_radius
        while self.__test_radius(x, y, radius):
            radius = radius + 1
        return radius

    # Locks the pixels in a specific ellipse by drawing the special color over it
    def __draw_special(self, x, y, radius):
        draw = ImageDraw.Draw(self.image)
        boundingbox = (x - radius, y - radius, x + radius, y + radius)
        fillcolor = (self.special_color[0], self.special_color[1], self.special_color[2], 255)
        draw.ellipse(boundingbox, fill=fillcolor)

    # Determines if a color is the special color
    def __is_special_color(self, pointcolor):
        if pointcolor is None:
            return True
        if pointcolor[0] == self.special_color[0] and \
                pointcolor[1] == self.special_color[1] and \
                pointcolor[2] == self.special_color[2]:
            return True
        return False

    # Appends the point to the end of the log file
    def __write_log(self, point):
        if point is None:
            return

        file = open(self.input_filename + ".txt", "a+")
        file.write(str(point) + "\n")
        file.close()

    # Gets the colors for a list of pixels
    def get_all_colors(self, points):
        # if points is None or len(points) == 0 or self.image_pixels is None:
        #     return

        point_color_list = []
        for point in points:
            point_color = (point, self.__get_pixel(point[0], point[1]))
            point_color_list.append(point_color)
        return point_color_list
