""" Find the optimal position for cameras in a museum """
import math
from time import strftime, gmtime, time
from pyscipopt import Model, quicksum
import matplotlib.pyplot as plot

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
                    positions.append(tuple(map(int, line.strip().split(","))))

        # with open("test_results.txt", "w") as end:
        #     for pos in positions:
        #         x, y = pos
        #         end.write(str(x)+','+str(y)+'\n')
                
        parameters["width"] = int(max([x[1] for x in positions]))
        parameters["height"] = int(max([x[0] for x in positions]))

        print("Map is {} x {}".format(parameters["width"], parameters["height"]))
        print("There are {} pieces of art".format(len(positions)))

        return positions, parameters

    def __get_centers(self, x1, y1, x2, y2, _range):
        """ Get the centers of the circles with set range and crossing the points """
        # Using (x - a)^2 + (y - b)^2 = r^2 with a, b = center(circle)
        circles = []
        # There is a weird rounding problem that creates empty lists sometimes
        # This offset is here to reduce the circle diameter and be more pessismistic
        range_offset = 0.0015
        _range = _range - range_offset

        dx, dy = x2 - x1, y2 - y1
        q = math.sqrt(dx**2 + dy**2) # distance between points
        x3, y3 = (x1 + x2) / 2, (y1 + y2) / 2 # halfway point

        d = math.sqrt(_range**2 - (q / 2)**2)

        c1x = x3 - d * dy / q
        c1y = y3 + d * dx / q

        c2x = x3 + d * dy / q
        c2y = y3 - d * dx / q

        return c1x, c1y, c2x, c2y

    def __get_restricted_positions(self):
        """ Reduce the possible positions with the circle method """
        camera_positions = set()

        for loc_1_index, loc_1 in enumerate(self.positions):
            x1, y1 = loc_1
            isolated = True # Account for isolated pieces
            for loc_2_index, loc_2 in enumerate(self.positions):
                x2, y2 = loc_2
                if loc_1 == loc_2:
                    continue
                squared_distance = pow((x2 - x1), 2) + pow((y2 - y1), 2)
                if squared_distance >= pow(self.parameters["long_cam_range"], 2):
                    # The two locations are too far away
                    continue
                if squared_distance < pow(self.parameters["long_cam_range"], 2):
                    # The distance is between the two ranges, only the big one is ok
                    c1x, c1y, c2x, c2y = self.__get_centers(x1, y1, x2, y2, self.parameters["long_cam_range"])
                    if c1x >= 0 and c1y >= 0:
                        isolated = False
                        camera_positions.add((2, len(camera_positions), c1x, c1y))
                    if c2x >= 0 and c2y >= 0:
                        isolated = False
                        camera_positions.add((2, len(camera_positions), c2x, c2y))
                if squared_distance < pow(self.parameters["short_cam_range"], 2):
                    c1x, c1y, c2x, c2y = self.__get_centers(x1, y1, x2, y2, self.parameters["short_cam_range"])
                    if c1x >= 0 and c1y >= 0:
                        isolated = False
                        camera_positions.add((1, len(camera_positions), c1x, c1y))
                    if c2x >= 0 and c2y >= 0:
                        isolated = False
                        camera_positions.add((1, len(camera_positions), c2x, c2y))
            if isolated:
                camera_positions.add((1, len(camera_positions), x1, y1))

        return camera_positions

    def __initialize_model(self):
        """ Create a SCIP model """
        model = Model() # From Pyscipopt
        print("Getting restricted positions for the cameras...")
        camera_positions = self.__get_restricted_positions()
        print("Found {} possible positions".format(len(camera_positions)))

        print("Adding these positions to the model...")
        # Add the cameras
        X = {} # Will be indexed with tuples
        for camera_type, camera_index, x, y in camera_positions:
            X[camera_type, camera_index] = model.addVar(str(camera_type)+','+str(x)+','+str(y), vtype='B')

        print("Adding the constraints to the model...")
        # Add the constraints on every piece
        for piece_index, piece_position in enumerate(self.positions):
            cameras = set()
            x1, y1 = piece_position
            for camera_type, camera_index, x2, y2 in camera_positions:
                squared_distance = pow((float(x2) - float(x1)), 2) + pow((float(y2) - float(y1)), 2) # Distance to the piece

                if squared_distance >= pow(self.parameters["long_cam_range"], 2):
                    # The two locations are too far away
                    continue
                if squared_distance < pow(self.parameters["long_cam_range"], 2) \
                    and camera_type == 2:
                    cameras.add((camera_type, camera_index))
                if squared_distance < pow(self.parameters["short_cam_range"], 2):
                    # Note that the camera can be on the piece
                    cameras.add((camera_type, camera_index))
            # One camera has to watch the piece
            if len(cameras) == 0:
                print("WARNING - Position {},{}".format(x1, y1))
            if x1 == 301 and y1 == 628:
                print("Cameras: {}".format(cameras))
            model.addCons(
                quicksum(
                    X[camera_type, camera_index] for (camera_type, camera_index) in cameras
                ) >= 1
            )

        print("Adding the price constraint...")
        # Define the minimization
        price = {
            1: self.parameters["short_cam_price"],
            2: self.parameters["long_cam_price"]
        }

        model.setObjective(
            quicksum(
                X[camera_type, camera_index] * price[camera_type] for camera_type, camera_index, x, y in camera_positions
            ), "minimize"
        )

        self.model = model
    
    def create_submission(self):
        if self.model:
            with open("submission_{}.txt".format(strftime("%Y-%m-%d", gmtime())), "w") as end:
                for var in self.model.getVars():
                    if self.model.getVal(var):
                        end.write(var.name + "\n")

    def solve(self):
        """ Solve the problem """
        print("Starting...")
        t1 = time()
        self.positions, self.parameters = self.__parse_file()
        self.__initialize_model()
        #self.model.hideOutput()
        self.model.optimize()
        self.create_submission()
        t2 = time()
        print("Completed in {}s".format(t2-t1))

    @staticmethod
    def square_distance(x1, y1, x2, y2):
        return (x2 - x1)**2 + (y2 - y1)**2

    def print_solution(self):
        """ Display the solution """
        with open("input_9.txt", 'r') as f:
            pieces_plot = []
            for piece_position in f.readlines()[2:]:
                pieces_plot.append(plot.Circle(tuple(map(int, piece_position.strip().split(","))), 0.3, color='r'))

        with open("submission_2018-02-01.txt", 'r') as f:
            cameras_plot = []
            for var in f.readlines():
                _type, x, y = var.strip().split(",")
                if int(_type) == 1:
                    cameras_plot.append(plot.Circle((float(x), float(y)), 0.1, color='b'))
                    cameras_plot.append(plot.Circle((float(x), float(y)), 4, color='b', fill=False))
                if int(_type) == 2:
                    cameras_plot.append(plot.Circle((float(x), float(y)), 0.1, color='g'))
                    cameras_plot.append(plot.Circle((float(x), float(y)), 8, color='g', fill=False))

        fig, ax = plot.subplots()
        ax.set_xlim(0, 800)
        ax.set_ylim(0, 800)

        for ppl in pieces_plot:
            ax.add_artist(ppl)

        for cpl in cameras_plot:
            ax.add_artist(cpl)

        plot.grid(True)
        plot.show()
        fig.savefig('plot_sol.png')

    def test_solution(self, submission):
        """ Test the solution """
        self.positions, self.parameters = self.__parse_file()
        # Get the results
        with open(submission, 'r') as f:
            self.results = []
            for line in f.readlines():
                line = line.strip()
                self.results.append([
                    line.split(",")[0],
                    line.split(",")[1],
                    line.split(",")[2]
                ])
        
        for piece_index, piece_position in enumerate(self.positions):
            x1, y1 = piece_position
            monitored = False
            for result in self.results:
                if result[0] == 1 and \
                    self.square_distance(x1, y1, result[1], result[2]) <= \
                        self.parameters["short_cam_range"]**2:
                    monitored = True
                    break
                if result[0] == 2 and \
                    self.square_distance(x1, y1, result[1], result[2]) <= \
                        self.parameters["long_cam_range"]**2:
                    monitored = True
                    break
            if not monitored:
                print("Piece ({}-{}) is not monitored !".format(x1, y1))


if __name__ == "__main__":
    solver = Solver("input_9.txt")
    solver.solve()
    solver.print_solution()
    #solver.test_solution("submission_2018-02-01.txt")