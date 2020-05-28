import matplotlib.pyplot as plt
import time

from classes.location_grid import LocationGrid
from classes.node import informed_search


def main():
    print("Hello and welcome.\nI will be fast and concise.\nWe both know what we're here for."
          "\nThere is no validation for user input.\nI'm trusting you know what you're doing.\nFollow instructions.")

    user = float(input("\nEnter the desired grid size (stay near 0.002): "))

    loading_time = time.time()

    print("\nOpening crime_dt in the resources folder.\nReading files and generating data...")

    shapefile_path = "./../resources/crime_dt"
    lg = LocationGrid(shapefile_path, user)

    print("\nTime to read and generate data: %.3f seconds" % (time.time() - loading_time))

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

    while True:
        path = informed_search(lg,
                               (
                                   float(input("\nTime to select start and end coordinates for the search.\n"
                                               "You can use any coordinates within the graph, "
                                               "but you could also select specific x and y ticks.\n"
                                               "To select ticks, enter their order in the graph "
                                               "eg: x=0 and y=0 is the bottom left point.\n"
                                               "Remember, there is no user input validation, "
                                               "I assume you know what you're doing.\n"
                                               "Enter the starting x coordinate: ")),
                                   float(input("Enter the starting y coordinate: "))
                               ),
                               (
                                   float(input("Enter the end x coordinate: ")),
                                   float(input("Enter the end y coordinate: "))
                               ))

        if path:
            print(path)
        else:
            print("\nNo path was found between the start point and end point.")

        user = input("\nWould you like to change start again with different start and end points?"
                     "\nThe program will terminate if you continue. (y/n) ")

        if str.lower(user)[0] == "n":
            break
        elif str.lower(user)[0] != "y":
            print("I'll take that for as a no.")
            break


if __name__ == "__main__":
    main()
