#!/usr/bin/env python
"""
    Parses an image to find circles using Pillow
"""

__author__ = "Brian Hooper"
__copyright__ = "Copyright (c) 2018 Brian Hooper"
__license__ = "MIT"
__version__ = "0.2"
__email__ = "brian_hooper@msn.com"

import math
import timeit
from PIL import Image, ImageDraw
from multiprocessing import Value, Lock, Queue, Process

class Parse:
    # Input settings and image objects
    inputfilename = ""  # File to parse
    image, image_pixels = 0, 0
    width, height = 0, 0
    special_color = (218, 235, 111)  # Special color used to mark regions as complete

    # Parse settings
    threshold = 7  # How close the colors are to each other
    precision = 2  # Distance between pixels to check
    minimum_size = 1  # Stop after no circles of at least this radius are found
    maximum_size = 50 # Largest radius to find
    radius_step = 1  # How far to increase the radius after each search
    threshold_increase_frequency = 10  # Increase color threshold after this many points are found
    threshold_increase_amount = 0  # Increase color threshold by this amount

    num_threads = 108

    def __init__(self, filename):
        self.inputfilename = filename
        self.image = Image.open(filename + ".jpg")
        self.image_pixels = self.image.load()
        self.width, self.height = self.image.size


    def evaluate_image(self):
        # Truncate the log file
        try:
            file = open(self.inputfilename + ".txt", "w+")
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

    def __thread_process(self, queue, max_rad, max_x, max_y, lock):
        while queue.qsize() > 0:
            x_val = queue.get()
            for y_val in range(self.precision, self.height - self.precision, self.precision):
                lock.acquire()
                current_radius = self.__find_biggest_radius(x_val, y_val, max_rad.value)
                if current_radius > max_rad.value:
                    max_rad.value = current_radius
                    max_x.value = x_val
                    max_y.value = y_val
                lock.release()

    def __parse_image(self):
        max_rad = Value('i', 100)
        max_x = Value('i', 0)
        max_y = Value('i', 0)

        lock = Lock()
        queue = Queue()
        threads = []

        while max_rad.value > self.minimum_size:
            max_rad.value = 0
            max_x.value = 0
            max_y.value = 0

            # Find the largest circle within the color threshold on the image
            for xcoordinate in range(self.precision, self.width - self.precision, self.precision):
                queue.put(xcoordinate)

            # Start threads
            for t in range(0, self.num_threads):
                p = Process(target=self.__thread_process, args=(queue, max_rad, max_x, max_y, lock))
                p.start()
                threads.append(p)

            # Terminate threads
            for thread in threads:
                thread.join()

            max_radius_found = (max_x.value, max_y.value, max_rad.value)

            # Save the found point
            print("Found radius " + str(max_radius_found))
            self.__write_log(max_radius_found)

            # Lock pixels by drawing the circle on the canvas using the special color
            self.__draw_special(max_x.value, max_y.value, max_rad.value)
            self.image.save(self.inputfilename + "_temp.jpg")

    # Gets the color (r, g, b) tuple from a pixel located at (x, y)
    def __get_pixel(self, x, y, ):
        if x is None or y is None:
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

    def __write_log(self, point):
        file = open(self.inputfilename + ".txt", "a+")
        file.write(str(point) + "\n")
        file.close()

    def get_all_colors(self, points):
        point_color_list = []
        for point in points:
            point_color = (point, self.__get_pixel(point[0], point[1]))
            point_color_list.append(point_color)
        return point_color_list
