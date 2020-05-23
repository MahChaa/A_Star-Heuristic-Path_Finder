import shapefile as shp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from classes.location_grid import LocationGrid


def main():
    shapefile_path = "./../resources/crime_dt"
    df = None

    with shp.Reader(shapefile_path, "r", encoding="ANSI") as sf:
        fields = [x[0] for x in sf.fields][1:]
        records = [y[:] for y in sf.records()]
        #records = sf.records()
        points = [s.points[0] for s in sf.shapes()]
        df = pd.DataFrame(columns=fields, data=records)
        df = df.assign(Coordinates=points)

    lg = LocationGrid(shapefile_path)
    lg.show()


if __name__ == "__main__":
    main()
