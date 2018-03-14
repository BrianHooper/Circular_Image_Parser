import math
from PIL import Image

# Open image and initialize variables
im = Image.open('example.jpg')
px = im.load()
threshold = 10


def get_relative_points(radius):
    radius = radius + 1
    quadrant = []
    angle = math.pi / (2 * radius)

    for x in range(1, radius + 1):
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


def get_absolute_points(points, x, y):
    absolute_points = []

    for point in points:
        absolute_points.append((x + point[0], y + point[1]))

    return absolute_points


def get_pixel(x, y):
    return px[x, y]


def closeness(x, y):
    a = abs(x[0] - y[0])
    b = abs(x[1] - y[1])
    c = abs(x[2] - y[2])
    mean = (a + b + c) / 3
    return int(mean)


def within(x, y):
    return closeness(x, y) <= threshold


# pix1 = get_pixel(4, 4)
# pix2 = get_pixel(300, 305)
# distance = closeness(pix1, pix2)
# print(within(pix1, pix2))


relative_points = get_relative_points(4)
absolute_points = get_absolute_points(relative_points, 8, 12)
for point in absolute_points:
    print(str(point[0]) + ", " + str(point[1]))
