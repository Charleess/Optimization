""" Find the optimal position for cameras in a museum """
import math
from time import strftime, gmtime, time
from pyscipopt import Model, quicksum

class Solver():
    def __init__(self, filename):
        self.__filename = filename
        self.positions = []
        self.parameters = {}
        self.model = None

    def __parse_file(self):
        positions = []
        parameters = {}
        with open(self.__filename, 'r') as file:
            for index, line in enumerate(file):
                if index == 0:
                    parameters["short_cam_range"] = int(line.strip().split(",")[0])
                    parameters["long_cam_range"] = int(line.strip().split(",")[1])
                if index == 1:
                    parameters["short_cam_price"] = int(line.strip().split(",")[0])
                    parameters["long_cam_price"] = int(line.strip().split(",")[1])
                if index > 1:
                    break
            for line in file.readlines()[2:]:
                positions.append(tuple(map(int, line.strip().split(","))))
        parameters["width"] = int(max([x[1] for x in positions]))
        parameters["height"] = int(max([x[0] for x in positions]))

        return positions, parameters

    def __get_centers(self, x1, y1, x2, y2, _range):
        """ Get the centers of the circles with set range and crossing the points """
        # Using (x - a)^2 + (y - b)^2 = r^2 with a, b = center(circle)
        circles = []
        # There is a weird rounding problem that creates empty lists sometimes
        # This offset is here to reduce the circle diameter and be more pessismistic
        range_offset = 0.01
        _range = _range - range_offset
        dx, dy = x2 - x1, y2 - y1
        q = math.sqrt(dx**2 + dy**2) # distance between points
        x3, y3 = (x1 + x2) / 2, (y1 + y2) / 2 # halfway point

        d = math.sqrt(_range**2 - (q / 2)**2)

        if _range + range_offset == self.parameters["short_cam_range"]:
            c1 = (1, x3 - d * dy / q, y3 + d * dx / q)
            circles.append(c1)
            c2 = (1, x3 + d * dy / q, y3 - d * dx / q)
            circles.append(c2)
        elif _range + range_offset == self.parameters["long_cam_range"]:
            c1 = (2, x3 - d * dy / q, y3 + d * dx / q)
            circles.append(c1)
            c2 = (2, x3 + d * dy / q, y3 - d * dx / q)
            circles.append(c2)

        return circles

    def __get_restricted_positions(self):
        """ Reduce the possible positions with the circle method """
        camera_positions = []

        for loc_1_index, loc_1 in enumerate(self.positions):
            x1, y1 = loc_1
            isolated = True # Account for isolated cameras
            for loc_2_index, loc_2 in enumerate(self.positions):
                x2, y2 = loc_2
                if loc_1 == loc_2:
                    continue
                squared_distance = pow((x2 - x1), 2) + pow((y2 - y1), 2)
                if squared_distance > pow(self.parameters["long_cam_range"], 2):
                    # The two locations are too far away
                    continue
                if squared_distance <= pow(self.parameters["long_cam_range"], 2):
                    # The distance is between the two ranges, only the big one is ok
                    isolated = False
                    camera_positions += \
                        self.__get_centers(x1, y1, x2, y2, self.parameters["long_cam_range"])
                if squared_distance <= pow(self.parameters["short_cam_range"], 2):
                    isolated = False
                    camera_positions += \
                        self.__get_centers(x1, y1, x2, y2, self.parameters["short_cam_range"])
            if isolated:
                camera_positions.append((1, x1, y1))

        return camera_positions

    def __initialize_model(self):
        """ Create a SCIP model """
        model = Model() # From Pyscipopt
        print("Getting restricted positions for the cameras...")
        camera_positions = self.__get_restricted_positions()

        print("Adding these positions to the model...")
        # Add the cameras
        X = dict() # Will be indexed with tuples
        for index, position in enumerate(camera_positions):
            _type, x, y = position
            X[_type, index] = model.addVar(str(_type)+','+str(x)+','+str(y), vtype='B')

        print("Adding the price constraint...")
        # Define the minimization
        price = {
            1: self.parameters["short_cam_price"],
            2: self.parameters["long_cam_price"]
        }
        model.setObjective(
            quicksum(
                X[pos[0], index] * price[pos[0]] for index, pos in enumerate(camera_positions)
            ), "minimize"
        )

        print("Adding the constraints to the model...")
        # Add the constraints on every piece
        for piece_index, piece_position in enumerate(self.positions):
            x1, y1 = piece_position
            cameras = []
            for cam_index, cam_position in enumerate(camera_positions):
                _type, x2, y2 = cam_position
                squared_distance = pow((x2 - x1), 2) + pow((y2 - y1), 2)
                if squared_distance > pow(self.parameters["long_cam_range"], 2):
                    # The two locations are too far away
                    continue
                if squared_distance <= pow(self.parameters["long_cam_range"], 2) \
                    and _type == 2:
                    cameras.append((_type, cam_index))
                if squared_distance <= pow(self.parameters["short_cam_range"], 2) \
                    and _type == 1: # Note that the camera can be on the piece
                    cameras.append((_type, cam_index))
            # One camera has to watch the piece
            model.addCons(quicksum(X[_type, cam_index] for (_type, cam_index) in cameras) >= 1)

        self.model = model
    
    def create_submission(self):
        if self.model:
            with open("submission_{}.txt".format(strftime("%Y-%m-%d", gmtime())), "w") as end:
                for var in self.model.getVars():
                    end.write(var.name + "\n")

    def solve(self):
        """ Solve the problem """
        print("Starting...")
        t1 = time()
        self.positions, self.parameters = self.__parse_file()
        self.__initialize_model()
        self.model.hideOutput()
        self.model.optimize()
        self.create_submission()
        t2 = time()
        print("Completed in {}s".format(t2-t1))


if __name__ == "__main__":
    solver = Solver("input_9.txt")
    solver.solve()