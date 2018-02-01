import math

import numpy as np
import matplotlib.pyplot as plot

from pyscipopt import Model, quicksum

def read_input(n):
    """
    read inputs
    :param n : integer in {0, 9}, tells which input to read
    :return small_radius (int),
    :return big_radius (int),
    :return small_price (int),
    :return big_price (int),
    :return locations (set of tuple): for ex: [(4, 8), (1, 2)],
    :return width (int),
    :return height (int)
    """
    with open("./input_%s.txt" % str(n), "r") as file:
        small_radius, big_radius = tuple(map(int, file.readline().split(",")))
        small_price, big_price = tuple(map(int, file.readline().split(",")))
        locations = set(tuple(map(int, row.split(","))) for row in file.read().split("\n"))

        width = max(x[0] for x in locations)
        height = max(x[1] for x in locations)
    return small_radius, big_radius, small_price, big_price, locations, width, height

def create_camera_positions(locations, small_radius, big_radius):
    """
    Create the limited set of points for our cameras
    i_list = np.arange(0.0, float(width), 2.0)
    j_list = np.arange(0.0, float(height), 2.0)
    Above naive version doesn't scale. No surprise
    We follow the teacher tip about how to select the points for our camera
    We only keep the centers of circle (camera vision limit)
    which passed on at least two pieces of art.
    AND we had position for isolated piece of art.
    :param locations
    :param small_radius
    :param big_radius
    :return position_list : list of tuple (cam_type, pos_index(int), x, y)
    """
    camera_positions = set()
    for loc_index, location1 in enumerate(locations):
        loc1_i, loc1_j = location1
        is_isolated = True
        for location2 in locations:
            loc2_i, loc2_j = location2
            if location1 == location2:
                continue
            sd = (loc1_i-loc2_i)**2 + (loc1_j-loc2_j)**2 # square distance between loc1 and loc2
            if sd > big_radius**2:
                continue
            if sd < big_radius**2: # distance < big_radius
                is_isolated = False
                xa, ya, xb, yb = get_circle_centers(loc1_i, loc1_j, loc2_i, loc2_j, big_radius)
                camera_positions.add((2, len(camera_positions), xa, ya)) # first center point
                camera_positions.add((2, len(camera_positions), xb, yb)) # second center point
            if sd < small_radius**2: # distance < small_radius
                is_isolated = False
                xa, ya, xb, yb = get_circle_centers(loc1_i, loc1_j, loc2_i, loc2_j, small_radius)
                camera_positions.add((1, len(camera_positions), xa, ya)) # first center point
                camera_positions.add((1, len(camera_positions), xb, yb)) # second center point
        if is_isolated:
            camera_positions.add((1, len(camera_positions), loc1_i, loc1_j))
        if loc_index % 200 == 0:
            print("creating camera_positions for: ", loc_index)

    return camera_positions

def get_circle_centers(x1, y1, x2, y2, r):
    """
    Determine (xa, ya) and (xb, yb) :
    the centers of the two circles of radius l,
    passing by the points (x1, y1) and (x2, y2)
    Notation:
        - r: circle radius
        - sd: square distance between (x1, y1) and (x2, y2)
        - l: distance between (xa, ya) (resp. (xb, yb)) and the middle of (x1, y1) and (x2, y2)
    """
    r = r-0.0125
    sd = (x2-x1)**2 + (y2-y1)**2
    l = math.sqrt(r**2 - sd/4)
    d = math.sqrt(sd)
    xa = x1 + (1/2)*(x2-x1) + (l/d)*(y1-y2)
    ya = y1 + (1/2)*(y2-y1) + (l/d)*(x2-x1)

    xb = x1 + (1/2)*(x2-x1) - (l/d)*(y1-y2)
    yb = y1 + (1/2)*(y2-y1) - (l/d)*(x2-x1)

    """
    try:
        assert math.isclose((xa-x1)**2 + (ya-y1)**2, r**2, rel_tol=1e-03)
        assert math.isclose((xa-x2)**2 + (ya-y2)**2, r**2, rel_tol=1e-03)
        assert math.isclose((xb-x1)**2 + (yb-y1)**2, r**2, rel_tol=1e-03)
        assert math.isclose((xb-x2)**2 + (yb-y2)**2, r**2, rel_tol=1e-03)
    except:
        import pdb; pdb.set_trace()
    """

    return xa, ya, xb, yb


def create_model(small_radius, big_radius, small_price, big_price, locations):
    """
    Create the model
    :param small_radius (int),
    :param big_radius (int),
    :param small_price (int),
    :param big_price (int),
    :param locations (list of tuple): for ex: [(4, 8), (1, 2)],
    :param width (int),
    :param height (int)
    :return a model, ready to be solved.
    """
    model = Model()

    # Variables : a binary variable for every locations and camera types
    # For now, we get the half integer location
    x = {}

    camera_positions = create_camera_positions(locations, small_radius, big_radius)

    for k, pos_index, i, j in camera_positions:
        name = str(k)+','+str(i)+','+str(j)
        x[k, pos_index] = model.addVar(name, vtype='B')
    print("Optimal position (ie variable number): ", len(camera_positions))

    # Constraints :
    # Each art piece is monitored, ie its distance from the nearest camera is less than the radius
    for loc_index, location in enumerate(locations):
        loc_i, loc_j = location
        pos_list = set()
        for k, pos_index, i, j in camera_positions:
            sd = (i-loc_i)**2 + (j-loc_j)**2
            if sd > big_radius**2:
                continue
            if sd < big_radius**2 and k == 2: # distance < big_radius
                pos_list.add((k, pos_index))
            if sd < small_radius**2 and k == 1: # distance < small_radius
                pos_list.add((k, pos_index))
        model.addCons(quicksum(x[k, pos_index] for (k, pos_index) in pos_list) >= 1)

        if loc_index % 200 == 0:
            print("creating constraints for: ", loc_index)

    # Cost function
    price = (0, small_price, big_price)
    model.setObjective(
        quicksum(x[k, pos_index]*price[k] for k, pos_index, i, j in camera_positions),
        "minimize")

    return model

if __name__ == '__main__':
    N = 9
    SMALL_RADIUS, BIG_RADIUS, SMALL_PRICE, BIG_PRICE, LOCATIONS, WIDTH, HEIGHT = read_input(N)

    print("Locations: ", len(LOCATIONS), ", Width: ", WIDTH, ", Height: ", HEIGHT)

    MODEL = create_model(SMALL_RADIUS, BIG_RADIUS, SMALL_PRICE, BIG_PRICE, LOCATIONS)

    print("Model created. Let solve it.")
    MODEL.hideOutput()
    MODEL.optimize()

    # Print/Plot the result
    with open('./museum_problem/sol_%s.txt' % N, 'w') as sol_file:
        for var in MODEL.getVars():
            if MODEL.getVal(var):
                sol_file.write(var.name+"\n")

    loc_circles = []
    for loc in LOCATIONS:
        loc_circles.append(plot.Circle(loc, 0.3, color='r'))

    cam_circles = []
    for var in MODEL.getVars():
        if MODEL.getVal(var):
            cam_type, x, y = var.name.split(",")
            cam_type = int(cam_type)
            x = float(x)
            y = float(y)
            if cam_type == 1:
                cam_circles.append(plot.Circle((x, y), 0.1, color='b'))
                cam_circles.append(plot.Circle((x, y), SMALL_RADIUS, color='b', fill=False))
            if cam_type == 2:
                cam_circles.append(plot.Circle((x, y), 0.1, color='g'))
                cam_circles.append(plot.Circle((x, y), BIG_RADIUS, color='g', fill=False))

    fig, ax = plot.subplots()
    ax.set_xlim(0, max(WIDTH, HEIGHT))
    ax.set_ylim(0, max(WIDTH, HEIGHT))
    for loc_circle in loc_circles:
        ax.add_artist(loc_circle)

    for cam_circle in cam_circles:
        ax.add_artist(cam_circle)

    plot.grid(True)
    fig.savefig('./museum_problem/plot_sol_%s.png' % N)
    print("Optimal value: %f" % MODEL.getObjVal())
    plot.show()
    