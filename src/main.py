import matplotlib.pyplot as plt
import time

from classes.location_grid import LocationGrid


def main():
    start_time = time.time()

    print("Hello and welcome.\nI will be fast and concise.\nWe both know what we're here for."
          "\nThere is no validation for user input.\nI'm trusting you know what you're doing.\nFollow instructions.")

    user = float(input("\nEnter the desired grid size (stay near 0.002): "))

    print("\nOpening crime_dt in the resources folder.\nReading files and generating data...")

    shapefile_path = "./../resources/crime_dt"
    lg = LocationGrid(shapefile_path, user)

    print("\nTime to read and generate data: %.3f seconds" % (time.time() - start_time))

    while True:
        user = float(input("\nEnter the desired threshold for the block graph (between 0 and 1): "))
        lg.threshold = user

        lg.show_scatter()

        lg.show_block()

        print("\nYou will have to close the graph windows to continue.")

        plt.show(block=True)

        user = input("\nWould you like to change the grid size and print the new graphs?"
                     "\nYou will not be able to change the grid size and threshold anymore if you continue. (y/n) ")

        if str.lower(user)[0] == "n":
            break
        elif str.lower(user)[0] != "y":
            print("I'll take that for as a no.")
            break

        user = float(input("\nEnter the desired grid size (stay near 0.002): "))

        loading_time = time.time()

        print("Generating data from grid size...")

        lg.grid_size = user

        print("\nTime to generate data: %.3f seconds" % (time.time() - loading_time))

    lg.windowed_graph(False)

    lg.show_scatter()

    lg.show_block()


if __name__ == "__main__":
    main()
