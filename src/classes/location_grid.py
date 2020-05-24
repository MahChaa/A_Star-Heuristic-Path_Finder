import shapefile as shp
import matplotlib.pyplot as plt
import numpy as np


class LocationGrid:
    def __init__(self, shapefile: str, grid_size: int = 0.002):
        self.grid_size = grid_size if grid_size <= 0.002 else 0.002

        if self.grid_size >= 0.0015:
            axis_font_size = "large"
            x_axis_angle = 45
            alignment = "right"
        elif self.grid_size >= 0.001:
            axis_font_size = "small"
            x_axis_angle = 50
            alignment = "right"
        else:
            axis_font_size = "xx-small"
            x_axis_angle = 90
            alignment = "center"

        with shp.Reader(shapefile, "r") as sf:
            self.points_x = [point.points[0][0] for point in sf.shapes()]
            self.points_y = [point.points[0][1] for point in sf.shapes()]
            self.area_coordinates = sf.bbox

        plt.axis([self.area_coordinates[0], self.area_coordinates[2], self.area_coordinates[1],
                  self.area_coordinates[3]])

        self.x_axis_ticks = np.arange(self.area_coordinates[0], self.area_coordinates[2], self.grid_size)
        self.y_axis_ticks = np.arange(self.area_coordinates[1], self.area_coordinates[3], self.grid_size)

        plt.xticks(self.x_axis_ticks, rotation=x_axis_angle, horizontalalignment=alignment,
                   size=axis_font_size)
        plt.yticks(self.y_axis_ticks, size=axis_font_size)
        plt.grid(True)
        plt.plot(self.points_x, self.points_y, "rx")

    def show(self):
        plt.show()
