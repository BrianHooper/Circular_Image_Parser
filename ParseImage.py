import math
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

# Open image and initialize variables
filename = 'gb.jpg'
im = Image.open(filename)
# contrast = ImageEnhance.Contrast(im)
# im = contrast.enhance(4)
# im.save("reducedImage.jpg")
im = ImageOps.posterize(im, 4)
px = im.load()
width, height = im.size

# How close the colors are to each other
# smaller = closer to each other
threshold = 25

# Distance between pixels to check
precision = 10

# Stop after no circles of at least this radius are found
minimum_size = 2

# How far to increase the radius after each search
radius_step = 2

# Rate of increase in points as search radius increases
logarithmic_coefficient = 25

special_color = (218, 235, 111)
completedimage = Image.new("RGB", (width, height), "black")


# Gets the number of search points as a factor of x
def get_num_points(x):
    return int(logarithmic_coefficient * math.log2(x) + 1)
    # return x


# Get the relative points in a circle of a specified radius
def get_relative_points(radius):
    radius = radius + 1
    quadrant = []
    angle = math.pi / (2 * radius)
    num_points = get_num_points(radius)

    for x in range(1, num_points + 1, radius_step):
        xcoord = int(round(num_points * math.cos(x * angle)))
        ycoord = int(round(num_points * math.sin(x * angle)))
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
    try:
        return px[x, y]
    except:
        print("Cant get pixel " + str(x) + ", " + str(y))


# Returns the mean difference between (r1, g1, b1) and (r2, g2, b2)
def closeness(x, y):
    try:
        a = abs(x[0] - y[0])
        b = abs(x[1] - y[1])
        c = abs(x[2] - y[2])
        mean = (a + b + c) / 3
        return int(mean)
    except:
        print(str(x) + " -- " + str(y))
        return 0


# Determines if two numbers are within the threshold of each other
def within(x, y):
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
def find_biggest_radius(x, y):
    radius = 1
    while test_radius(x, y, radius):
        radius = radius + 1
    return radius


# Locks the pixels in a specific ellipse by drawing the special color over it
def draw_special(x, y, radius):
    draw = ImageDraw.Draw(im)
    boundingbox = (x - radius, y - radius, x + radius, y + radius)
    fillcolor = (special_color[0], special_color[1], special_color[2], 255)
    draw.ellipse(boundingbox, fill=fillcolor)


# Draws an ellipse at at a specifc coordinate
def draw_color(x, y, radius, color):
    draw = ImageDraw.Draw(completedimage)
    boundingbox = (x - radius, y - radius, x + radius, y + radius)
    innerboundingbox = (x - int(radius / 1.5), y - int(radius / 1.5), x + int(radius / 1.5), y + int(radius / 1.5))
    fillcolor = (color[0], color[1], color[2], 255)
    outerfillcolor = (int(255 - (255 - color[0]) / 2), int(255 - (255 - color[1]) / 2), int(255 - (255 - color[2]) / 2), 255)
    draw.ellipse(boundingbox, fill=outerfillcolor, outline=(0, 0, 0, 255))
    draw.ellipse(innerboundingbox, fill=fillcolor)


# Determines if a color is the special color
def is_special_color(pointcolor):
    if pointcolor is None:
        return True
    if pointcolor[0] == special_color[0] and pointcolor[1] == special_color[1] and pointcolor[2] == special_color[2]:
        return True
    return False

max_radius_found = (0, 0, 100)
completed_points = []

while max_radius_found[2] > minimum_size:
    max_radius_found = (0, 0, 0)
    for xcoordinate in range(precision, width - precision, precision):
        print("Testing " + str(xcoordinate) + " max: " + str(max_radius_found))
        for ycoordinate in range(precision, height - precision, precision):
            # print("Testing (" + str(xcoordinate) + ", " + str(ycoordinate) + ") max: " + str(max_radius_found))
            current_radius = find_biggest_radius(xcoordinate, ycoordinate)
            if current_radius > max_radius_found[2]:
                max_radius_found = (xcoordinate, ycoordinate, current_radius)
    completed_points.append(max_radius_found)
    print("Found radius " + str(max_radius_found))
    draw_special(max_radius_found[0], max_radius_found[1], max_radius_found[2])
    im.save("output.jpg")
    if len(completed_points) % 20 == 0:
        threshold = threshold + 5

# Return the image to its state before the special color was drawn on it
im = Image.open(filename)
px = im.load()

# Draw the completed image
for completedpoint in completed_points:
    print(completedpoint)
    pointcolor = get_pixel(completedpoint[0], completedpoint[1])
    if not pointcolor is None:
        draw_color(completedpoint[0], completedpoint[1], completedpoint[2], pointcolor)
completedimage.save("completedimage.jpg")


