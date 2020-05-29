# -------------------------------------------------------
# Assignment 1
# Written by Mahdi Chaari - 27219946
# For COMP 472 Section ABKX – Summer 2020
# --------------------------------------------------------
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

    # A while loop is used to allow the users to create and many graphs they they want
    while True:
        user = float(input("\nEnter the desired threshold for the block graph (between 0 and 1): "))
        lg.threshold = user

        lg.show_scatter()

        lg.show_block()

        print("\nAverage crime count per grid square: " + str(lg.crime_mean))
        print("Crime count standard deviation: " + str(lg.crime_standard_deviation))

        print("\nYou will have to close the graph windows to continue.")

        plt.show(block=True)  # We have to block like this to prevent the graph windows from closing instantly

        user = input("\nWould you like to change the grid size and print the new graphs?"
                     "\nYou will not be able to change the grid size and threshold anymore if you decline. (y/n) ")

        # Very basic user input interpretation
        # If the user doesn't input a word starting with y, then it is assumed a no was input and the loop is broken
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

    lg.set_coordinates_validity()  # Make the necessary calculations for the search to be done eg: invalid_coordinates

    lg.windowed_graph(False)  # The next graphs won't be windowed so the user won't have to close them to continue

    lg.show_scatter()

    lg.show_block()

    lg.windowed_graph(True)  # The next graph is going to be the found path, so it is better windowed

    print("\nTime to select start and end coordinates for the search.")

    while True:
        start_x = float(input("\nYou can use any coordinates within the graph, "
                              "but you could also select specific x and y ticks.\n"
                              "To select ticks, enter their order in the graph "
                              "eg: x=0 and y=0 is the bottom left point.\n"
                              "Remember, there is no user input validation, "
                              "I assume you know what you're doing.\n"
                              "Enter the starting x coordinate: "))
        start_y = float(input("Enter the starting y coordinate: "))
        end_x = float(input("Enter the end x coordinate: "))
        end_y = float(input("Enter the end y coordinate: "))

        loading_time = time.time()

        path = informed_search(lg, (start_x, start_y), (end_x, end_y))

        print("\nTime to find shortest path: %.3f seconds" % (time.time() - loading_time))

        if path:
            lg.update_path_data(path)   # We share the list of nodes that link start and end points so it can be showed
            lg.show_block()

            print("\nYou will have to close the graph window to continue.")
            plt.show(block=True)

        user = input("\nWould you like to change start again with different start and end points?"
                     "\nThe program will terminate if you decline. (y/n) ")

        if str.lower(user)[0] == "n":
            break
        elif str.lower(user)[0] != "y":
            print("I'll take that for as a no.")
            break

    print("\nThank you for using this program.\nIt's time to terminate.")


if __name__ == "__main__":
    main()
