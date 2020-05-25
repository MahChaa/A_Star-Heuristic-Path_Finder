from classes.location_grid import LocationGrid


def main():
    shapefile_path = "./../resources/crime_dt"
    lg = LocationGrid(shapefile_path)

    lg.show_block()
    lg.show_scatter()


if __name__ == "__main__":
    main()
