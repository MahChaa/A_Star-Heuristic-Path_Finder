import shapefile as shp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from classes.location_grid import LocationGrid


def main():
    shapefile_path = "./../resources/crime_dt"
    lg = LocationGrid(shapefile_path)

    with shp.Reader(shapefile_path, "r", encoding="ANSI") as sf:
        fields = [x[0] for x in sf.fields][1:]
        records = [y[:] for y in sf.records()]
        points = [s.points[0] for s in sf.shapes()]
        crime_df = pd.DataFrame(columns=fields, data=records)
        crime_df = crime_df.assign(Coordinates=points)

    block_graph_intervals = []
    block_graph_data = []

    for i, x_coord in enumerate(lg.x_axis_ticks):
        left_boundary = x_coord
        right_boundary = lg.x_axis_ticks[i + 1] if i != len(lg.x_axis_ticks) - 1 else x_coord + lg.grid_size

        for j, y_coord in enumerate(lg.y_axis_ticks):
            bottom_boundary = y_coord
            top_boundary = lg.y_axis_ticks[i + 1] if i != len(lg.y_axis_ticks) - 1 else y_coord + lg.grid_size

            block_graph_intervals.append([left_boundary, bottom_boundary, right_boundary, top_boundary])

    for i, block in enumerate(block_graph_intervals):
        block_graph_data.append(0)

        for point in crime_df["Coordinates"]:
            if (block[0] <= point[0] < block[2]) and (block[1] <= point[1] < block[3]):
                block_graph_data[i] += 1

    block_df = pd.DataFrame(columns=[str(x)[1:-2] for x in block_graph_intervals], data=np.array([block_graph_data]))

    print(block_df)


if __name__ == "__main__":
    main()
