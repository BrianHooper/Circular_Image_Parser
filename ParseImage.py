import math
import timeit
import gizeh
import Parse
from PIL import Image, ImageDraw

# Filenames and image settings
inputfilename = "bee.jpg"
tempfilename = "temp.jpg"
outputfilename = "output.png"
outputbackgroundcolor = (0, 0, 0)
special_color = (218, 235, 111)

# How close the colors are to each other
# smaller = closer to each other
threshold = 7

# Distance between pixels to check
precision = 2

# Stop after no circles of at least this radius are found
minimum_size = 1

# How far to increase the radius after each search
radius_step = 1


# Get the relative points in a circle of a specified radius
def get_relative_points(radius):
    if radius <= 1:
        return []

    radius = radius + 1
    quadrant = []
    angle = math.pi / (2 * radius)

    for x in range(1, radius + 1, radius_step):
        xcoord = int(round(radius * math.cos(x * angle)))
        ycoord = int(round(radius * math.sin(x * angle)))
        quadrant.append((xcoord, ycoord))

    points = []

    for point in quadrant:
        points.append((point[0], point[1]))
        points.append((point[0], (point[1] * -1)))
        points.append(((point[0] * -1), point[1]))
        points.append(((point[0] * -1), (point[1] * -1)))

    return points


# Convert relative points to absolute points based on an (x, y) point
def get_absolute_points(points, x, y):
    absolute_points = []

    for point in points:
        absolute_points.append((x + point[0], y + point[1]))

    return absolute_points


# Gets the color (r, g, b) tuple from a pixel located at (x, y)
def get_pixel(x, y):
    if x is None or y is None:
        return 255, 255, 255
    return px[x, y]


# Returns the mean difference between (r1, g1, b1) and (r2, g2, b2)
def closeness(x, y):
    if x is None or y is None:
        return 255
    a = abs(x[0] - y[0])
    b = abs(x[1] - y[1])
    c = abs(x[2] - y[2])
    mean = (a + b + c) / 3
    return int(mean)


# Determines if two numbers are within the threshold of each other
def within(x, y, threshold):
    return closeness(x, y) <= threshold


# Returns true if the (x, y) coordinates are within the bounds of the image
def on_image(x, y):
    if x < 0 or y < 0:
        return False
    if x > width - 1 or y > height - 1:
        return False
    return True


# Returns true if the a circle of a specified radius located at (x, y) is outside the bounds of the image
def radius_off_image(x, y, radius):
    if (x - radius) < 0 or (y - radius) < 0:
        return True
    if (x + radius) > width or (y + radius) > height:
        return True
    return False


# Tests if a circle of a given radius is within the color threshold
def test_radius(x, y, radius):
    if radius_off_image(x, y, radius):
        return False
    relative_points = get_relative_points(radius)
    absolute_points = get_absolute_points(relative_points, x, y)

    center = get_pixel(x, y)
    for point in absolute_points:
        if not on_image(point[0], point[1]):
            return False
        pointcolor = get_pixel(point[0], point[1])
        if pointcolor is None:
            return False
        if is_special_color(pointcolor):
            return False
        if not within(center, pointcolor):
            return False
    return True


# Searches for the largest circle centered at point (x, y) is entirely within the color threshold
def find_biggest_radius(x, y, starting_radius):
    radius = starting_radius - 1
    while test_radius(x, y, radius):
        radius = radius + 1
    return radius


# Locks the pixels in a specific ellipse by drawing the special color over it
def draw_special(x, y, radius):
    draw = ImageDraw.Draw(im)
    boundingbox = (x - radius, y - radius, x + radius, y + radius)
    fillcolor = (special_color[0], special_color[1], special_color[2], 255)
    draw.ellipse(boundingbox, fill=fillcolor)


# Determines if a color is the special color
def is_special_color(pointcolor):
    if pointcolor is None:
        return True
    if pointcolor[0] == special_color[0] and pointcolor[1] == special_color[1] and pointcolor[2] == special_color[2]:
        return True
    return False

def parse_image(threshold):
    completed_points = []
    while max_radius_found[2] > minimum_size:
        max_radius_found = (0, 0, 0)
        for xcoordinate in range(precision, width - precision, precision):
            for ycoordinate in range(precision, height - precision, precision):
                current_radius = find_biggest_radius(xcoordinate, ycoordinate, max_radius_found[2])
                if current_radius > max_radius_found[2]:
                    max_radius_found = (xcoordinate, ycoordinate, current_radius)
        completed_point = (max_radius_found, get_pixel(max_radius_found[0], max_radius_found[1]))
        completed_points.append(completed_point)
        print("Found radius " + str(max_radius_found))
        draw_special(max_radius_found[0], max_radius_found[1], max_radius_found[2])
        im.save(tempfilename)
        if len(completed_points) % 10 == 0:
            threshold = threshold + 15
    return completed_points

def draw_image(completed_points):
    surface = gizeh.Surface(width=width, height=height, bg_color=outputbackgroundcolor)
    for finished_point in completed_points:
        circle_radius = finished_point[0][2]
        circle_x = finished_point[0][0]
        circle_y = finished_point[0][1]
        red = finished_point[1][0] / 255
        green = finished_point[1][1] / 255
        blue = finished_point[1][2] / 255
        color = (round(red + (1 - red) / 2, 1), round(green + (1 - green) / 2, 1), round(blue + (1 - blue) / 2, 1))
        circle = gizeh.circle(r=circle_radius, xy=[circle_x, circle_y], fill=color, stroke_width=2, stroke=(0, 0, 0))
        circle.draw(surface)
        red = round(finished_point[1][0] / 255, 1)
        green = round(finished_point[1][1] / 255, 1)
        blue = round(finished_point[1][2] / 255, 1)
        circle_radius = int(2 * (circle_radius / 3))
        circle = gizeh.circle(r=circle_radius, xy=[circle_x, circle_y], fill=(red, green, blue))
        circle.draw(surface)
    surface.write_to_png(outputfilename)

im = Image.open(inputfilename)
px = im.load()
width, height = im.size

start = timeit.default_timer()
points = parse_image(threshold)
draw_image(points)
stop = timeit.default_timer()
num_pixels = 0
for point in points:
    circle_pixels = math.pi * point[2] * point[2]
    num_pixels = num_pixels + circle_pixels
print("Calculated " + str(len(points)) + " circles encompassing " +
      str(num_pixels) + " pixels in " + str(stop - start) + " time.")

xvs = Parse()
