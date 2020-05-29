import shapefile as shp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from matplotlib import colors


class LocationGrid:
    __axis_font_size: str
    __x_axis_angle: int
    __alignment: str

    def __init__(self, shapefile: str, grid_size: int = 0.002):
        self.grid_size = grid_size

        with shp.Reader(shapefile, "r", encoding="ANSI") as sf:
            self.points_x = [point.points[0][0] for point in sf.shapes()]
            self.points_y = [point.points[0][1] for point in sf.shapes()]
            self.area_coordinates = sf.bbox

            fields = [x[0] for x in sf.fields][1:]
            records = [y[:] for y in sf.records()]
            self.points = [s.points[0] for s in sf.shapes()]
            self.crime_df = pd.DataFrame(columns=fields, data=records)
            self.crime_df = self.crime_df.assign(Coordinates=self.points)

        self.block_graph_intervals = []
        self.block_graph_data = []
        self.block_graph_data_formatted = []

        self.x_axis_ticks = np.arange(self.area_coordinates[0], self.area_coordinates[2], self.grid_size)
        self.y_axis_ticks = np.arange(self.area_coordinates[1], self.area_coordinates[3], self.grid_size)

        for j in range(0, len(self.y_axis_ticks)):
            bottom_boundary = self.y_axis_ticks[-j - 1]
            top_boundary = self.y_axis_ticks[-j] if j != 0 else bottom_boundary + self.grid_size

            for i, x_coord in enumerate(self.x_axis_ticks):
                left_boundary = x_coord
                right_boundary = self.x_axis_ticks[i + 1] if i != len(self.x_axis_ticks) - 1 \
                    else x_coord + self.grid_size

                self.block_graph_intervals.append([left_boundary, bottom_boundary, right_boundary, top_boundary])

        for i, block in enumerate(self.block_graph_intervals):
            self.block_graph_data.append(0)

            for point in self.crime_df["Coordinates"]:
                if (block[0] <= point[0] < block[2]) and (block[1] <= point[1] < block[3]):
                    self.block_graph_data[i] += 1

        for i, block in enumerate(self.block_graph_intervals):
            if i % len(self.x_axis_ticks) == 0:
                self.block_graph_data_formatted.append([])
            self.block_graph_data_formatted[math.floor(i / len(self.x_axis_ticks))].append(0)

            for point in self.crime_df["Coordinates"]:
                if (block[0] <= point[0] < block[2]) and (block[1] <= point[1] < block[3]):
                    self.block_graph_data_formatted[math.floor(i / len(self.x_axis_ticks))][
                        i % len(self.x_axis_ticks)] += 1

        self.block_df = pd.DataFrame(columns=[str(x)[1:-2] for x in self.block_graph_intervals],
                                     data=np.array([self.block_graph_data]))

    def show_block(self, threshold: float = 0.5):
        self.__format_axis()

        fig, block_plot = plt.subplots()

        color_map = colors.ListedColormap(['blue', 'red'])
        bounds = [0, float(self.block_df.quantile(threshold if 0 <= threshold <= 1 else 0.5, axis=1)),
                  int(self.block_df.max(axis=1))]
        norm = colors.BoundaryNorm(bounds, color_map.N)

        block_plot.imshow(np.array(self.block_graph_data_formatted), cmap=color_map, norm=norm, aspect="auto",
                          extent=[self.area_coordinates[0], self.area_coordinates[2],
                                  self.area_coordinates[1], self.area_coordinates[3]])

        self.__set_axis_ticks()

        plt.show()

    def show_scatter(self):
        self.__format_axis()

        fig, scatter_plot = plt.subplots()

        plt.axis([self.area_coordinates[0], self.area_coordinates[2], self.area_coordinates[1],
                  self.area_coordinates[3]])

        self.__set_axis_ticks()

        scatter_plot.scatter(self.points_x, self.points_y)

        plt.show()

    def __format_axis(self) -> None:
        if self.grid_size >= 0.0015:
            self.__axis_font_size = "large"
            self.__x_axis_angle = 45
            self.__alignment = "right"
        elif self.grid_size >= 0.001:
            self.__axis_font_size = "small"
            self.__x_axis_angle = 50
            self.__alignment = "right"
        else:
            self.__axis_font_size = "xx-small"
            self.__x_axis_angle = 90
            self.__alignment = "center"

    def __set_axis_ticks(self) -> None:
        plt.xticks(self.x_axis_ticks, rotation=self.__x_axis_angle, horizontalalignment=self.__alignment,
                   size=self.__axis_font_size)
        plt.yticks(self.y_axis_ticks, size=self.__axis_font_size)
