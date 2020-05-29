# -------------------------------------------------------
# Assignment 1
# Written by Mahdi Chaari - 27219946
# For COMP 472 Section ABKX – Summer 2020
# --------------------------------------------------------
import shapefile as shp
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from matplotlib import colors


class LocationGrid:
    # These are private member variables that aren't initialized in the constructor
    __axis_font_size: str
    __x_axis_angle: int
    __alignment: str
    __block_graph_data: list
    __block_graph_data_formatted: list
    __blocked_blocks: list
    __invalid_coordinates: list
    __x_axis_ticks: np.ndarray
    __y_axis_ticks: np.ndarray
    __block_df: pd.DataFrame
    __crime_count: int
    __crime_mean: float
    __crime_standard_deviation: float

    def __init__(self, shapefile: str, grid_size: float = 0.002, threshold: float = 0.5):
        # All the data needed for the graphs are read here from the file
        with shp.Reader(shapefile, "r", encoding="ANSI") as sf:
            # The points are retrieved and saved to be later used to draw the scatter graph
            self.__points_x = [point.points[0][0] for point in sf.shapes()]
            self.__points_y = [point.points[0][1] for point in sf.shapes()]
            self.__area_coordinates = sf.bbox  # These are the coordinates delimiting the whole map
            # Fields are column name and records are information related to every crime eg: date, type, etc.
            fields = [x[0] for x in sf.fields][1:]
            records = [y[:] for y in sf.records()]
            points = [s.points[0] for s in sf.shapes()]  # There are the coordinates of each crime
            self.__crime_df = pd.DataFrame(columns=fields, data=records)  # DataFrame with the crime info
            self.__crime_df = self.__crime_df.assign(Coordinates=points)  # We add the crime coordinates to the df
        # The graphs to be drawn are by default in a new window
        self.windowed_graph(True)

        self.__search_path_data = []

        self.threshold = threshold
        self.grid_size = grid_size

    # This will display the block graph, the one with the crime rates
    def show_block(self) -> None:
        self.__format_axis()  # Depending on the grid size, the axis labels' style changes for clarity

        fig, block_plot = plt.subplots()

        if plt.get_backend() == "TkAgg":  # The title is only printed in windowed graphs, they overlap otherwise
            fig.suptitle("Block Graph: " + str(self.__grid_size) + " grid size; " + str(self.__threshold) +
                         " threshold")

        color_map = colors.ListedColormap(['indigo', 'yellow'])

        # quantile() is a pandas function that returns the value at a specific percentile eg: 0.5 returns the median
        # The bounds include the minimum, the threshold and the maximum.
        bounds = [0, float(self.__block_df["Crime Count"].quantile(self.__threshold)),
                  int(self.__block_df["Crime Count"].max())]
        norm = colors.BoundaryNorm(bounds, color_map.N)

        plt.grid(True, linewidth=1.5, color="k")
        # This creates the image with the crime rates, it uses a colormap and coordinates for its boundaries
        block_plot.imshow(np.array(self.__block_graph_data_formatted), cmap=color_map, norm=norm, aspect="auto",
                          extent=[self.__x_axis_ticks[0], self.__x_axis_ticks[-1] + self.__grid_size,
                                  self.__y_axis_ticks[0], self.__y_axis_ticks[-1] + self.__grid_size])

        # The red search line is only plotted when we found a shortest path,
        # the coordinates of each node in the list is used
        if self.__search_path_data:
            plt.plot([coord.coordinates[0] for coord in self.__search_path_data],
                     [coord.coordinates[1] for coord in self.__search_path_data],
                     color="red", linewidth=2)

        # This configures the x and y axis ticks before each drawing of the graph,
        # because it seems to get flushed after every call of plt.show()
        self.__set_axis_ticks()

        # We don't want the graph to block, so we can display two graphs at the same time.
        plt.show(block=False)

    # This is the function that draws the scatter plot for the positions of the crimes
    def show_scatter(self) -> None:
        self.__format_axis()

        fig, scatter_plot = plt.subplots()

        if plt.get_backend() == "TkAgg":
            fig.suptitle("Scatter Graph: " + str(self.__grid_size) + " grid size")

        # This sets the boundaries of the graph
        plt.axis([self.__area_coordinates[0], self.__area_coordinates[2], self.__area_coordinates[1],
                  self.__area_coordinates[3]])

        self.__set_axis_ticks()

        plt.grid(True)

        scatter_plot.scatter(self.__points_x, self.__points_y)

        plt.show(block=False)

    # Depending on the grid size, the axis labels are formatted differently
    def __format_axis(self) -> None:
        if self.__grid_size >= 0.0015:
            self.__axis_font_size = "large"
            self.__x_axis_angle = 45
            self.__alignment = "right"
        elif self.__grid_size >= 0.001:
            self.__axis_font_size = "small"
            self.__x_axis_angle = 50
            self.__alignment = "right"
        else:
            self.__axis_font_size = "xx-small"
            self.__x_axis_angle = 90
            self.__alignment = "center"

    # Needed before every plt.show() to draw the graphs
    def __set_axis_ticks(self) -> None:
        plt.xticks(self.__x_axis_ticks, rotation=self.__x_axis_angle, horizontalalignment=self.__alignment,
                   size=self.__axis_font_size)
        plt.yticks(self.__y_axis_ticks, size=self.__axis_font_size)

    # This will generate two lists, one with the coordinates of all the yellow blocks for the given threshold,
    # and another with all the invalid points of the map; coordinates that can't be used in the path search
    def set_coordinates_validity(self):
        threshold = float(self.__block_df["Crime Count"].quantile(self.__threshold))  # Threshold crime count
        self.__blocked_blocks = []
        self.__invalid_coordinates = []

        # block_data = [[x1, y1, x2, y2], crime_count], block_graph_data contains the crime count of every block.
        # This loop will populate blocked_blocks with only the block that have a crime count above the threshold.
        # Which means this is a list of block the search path will have to take into account.
        for block_data in self.__block_graph_data:
            if block_data[1] > threshold:
                self.__blocked_blocks.append(block_data[0])

        # Here we'll iterate though all the coordinates of the graph to see if it is adjacent to a yellow block.
        for i in range(len(self.__y_axis_ticks) + 1):
            y_coord = self.__y_axis_ticks[i] if i < len(self.__y_axis_ticks) \
                else self.__y_axis_ticks[i - 1] + self.__grid_size

            for j in range(len(self.__x_axis_ticks) + 1):
                x_coord = self.__x_axis_ticks[j] if j < len(self.__x_axis_ticks) \
                    else self.__x_axis_ticks[j - 1] + self.__grid_size
                coords = (x_coord, y_coord)
                block_adjacency_count = 0

                # If the coordinates are not on the boundary edges
                if 0 < i < len(self.__y_axis_ticks) and 0 < j < len(self.__x_axis_ticks):
                    for block in self.__blocked_blocks:
                        if x_coord in block and y_coord in block:
                            block_adjacency_count += 1

                    # If the coordinate is in between 4 yellow blocks, then it is invalid
                    if block_adjacency_count >= 4:
                        self.__invalid_coordinates.append(coords)

                # If the coordinates are on the boundary edges, except for corners
                elif (i == 0 or i == len(self.__y_axis_ticks)) != (j == 0 or j == len(self.__x_axis_ticks)):  # XOR
                    for block in self.__blocked_blocks:
                        if x_coord in block and y_coord in block:
                            block_adjacency_count += 1

                    # If the coordinates are between 2 yellow blocks, it is invalid
                    if block_adjacency_count >= 2:
                        self.__invalid_coordinates.append(coords)

                # If the coordinates are in the corners
                else:
                    for block in self.__blocked_blocks:
                        if x_coord in block and y_coord in block:
                            block_adjacency_count += 1

                    # If they're in one yellow block, it means they're invalid
                    if block_adjacency_count >= 1:
                        self.__invalid_coordinates.append(coords)

    def windowed_graph(self, val: bool) -> None:
        matplotlib.use("TkAgg" if val else "module://backend_interagg")

    @property
    def grid_size(self) -> float:
        return self.__grid_size

    @grid_size.setter
    def grid_size(self, grid_size: float) -> None:
        if hasattr(self, "grid_size") and self.__grid_size == grid_size:
            return

        self.__grid_size = grid_size

        self.__x_axis_ticks = np.arange(self.__area_coordinates[0], self.__area_coordinates[2], self.__grid_size)
        self.__y_axis_ticks = np.arange(self.__area_coordinates[1], self.__area_coordinates[3], self.__grid_size)

        self.__block_graph_data = []
        self.__block_graph_data_formatted = []

        # Won't get much into the details here, it's kind of a mess. I created this at 3 AM, it shows my confusion.
        # Either way, this populates block_graph_data with this [[x1, y1, x2, y2], crime_count].
        # At index 0 there are block coordinates and at index 1 there's the crime count for that block.
        # For every y coordinate in the graph, we iterate all x coordinates
        for j in range(len(self.__y_axis_ticks)):
            bottom_boundary = self.__y_axis_ticks[-j - 1]
            top_boundary = self.__y_axis_ticks[-j] if j != 0 else bottom_boundary + self.__grid_size

            # For all x coordinates we add a list entry to block_graph_data for a block and set its count to 0
            for i, x_coord in enumerate(self.__x_axis_ticks):
                left_boundary = x_coord
                right_boundary = self.__x_axis_ticks[i + 1] if i != len(self.__x_axis_ticks) - 1 \
                    else x_coord + self.__grid_size

                self.__block_graph_data.append([])
                self.__block_graph_data[(j * len(self.__x_axis_ticks)) + i] \
                    .append([left_boundary, bottom_boundary, right_boundary, top_boundary])
                self.__block_graph_data[(j * len(self.__x_axis_ticks)) + i] \
                    .append(0)

                # For every block, we iterate through all the crime coordinates we got and increment the block's crime
                # count for ever crime coordinate falling within the block's coordinates excluding top-right
                for point in self.__crime_df["Coordinates"]:
                    if (left_boundary <= point[0] < right_boundary) and (bottom_boundary <= point[1] < top_boundary):
                        self.__block_graph_data[(j * len(self.__x_axis_ticks)) + i][1] += 1

        # This takes the block_graph_data we just gathered creates another list where only the crime counts are present.
        # This is needed specifically for the imshow() function that will draw the block graph.
        # The list will be composed of lists of the size of the axis ticks. Basically, there's an list for every row
        # in the imshow() graph.
        for i, element in enumerate(self.__block_graph_data):
            if i % len(self.__x_axis_ticks) == 0:
                self.__block_graph_data_formatted.append([])

            self.__block_graph_data_formatted[math.floor(i / len(self.__x_axis_ticks))].append(element[1])

        # This DataFrame is used to gather the statistics necessary
        self.__block_df = pd.DataFrame(columns=["Blocks", "Crime Count"],
                                       data=self.__block_graph_data)

        self.__crime_count = self.__block_df["Crime Count"].sum()
        self.__crime_mean = self.__block_df["Crime Count"].mean()
        self.__crime_standard_deviation = self.__block_df["Crime Count"].std()

    @property
    def threshold(self) -> float:
        return self.__threshold

    @threshold.setter
    def threshold(self, threshold: float) -> None:
        self.__threshold = threshold if 0 <= threshold <= 1 else 0.5

    @property
    def blocked_blocks(self) -> list:
        return self.__blocked_blocks

    @property
    def invalid_coordinates(self) -> list:
        return self.__invalid_coordinates

    @property
    def x_axis_ticks(self) -> np.ndarray:
        return self.__x_axis_ticks

    @property
    def y_axis_ticks(self) -> np.ndarray:
        return self.__y_axis_ticks

    @property
    def crime_count(self) -> int:
        return self.__crime_count

    @property
    def crime_mean(self) -> float:
        return self.__crime_mean

    @property
    def crime_standard_deviation(self) -> float:
        return self.__crime_standard_deviation

    # The heuristic search will give this object a list of nodes that represent the shortest path
    def update_path_data(self, path: list):
        self.__search_path_data = path
