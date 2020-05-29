import math
import queue as Q
import time

from classes.location_grid import LocationGrid


# This is the node we'll use to represent a valid coordinate on the map
class Node:
    def __init__(self, previous, coordinates: tuple):
        self.previous = previous  # This is to create a path history, like a linked list
        self.coordinates = coordinates
        self.f = 0
        self.g = 0
        self.h = 0

    # This is a like a toString() function
    def __repr__(self) -> str:
        return str(self.coordinates)

    # Comparison function
    def __lt__(self, other) -> bool:
        return self.f < other.f

    # Equality function
    def __eq__(self, other) -> bool:
        return self.coordinates == other.coordinates


# This is the heuristic search function, it requires the map, and coordinates
def informed_search(graph: LocationGrid, start_coords: tuple, end_coords: tuple) -> list:
    # A priority queue is more practical than alist
    open_list = Q.PriorityQueue()
    closed_list = []

    # Somewhat of a validation of the passed coordinates
    start_coords = check_coordinates_validity(start_coords, graph)
    end_coords = check_coordinates_validity(end_coords, graph)

    # The passed coordinates and actual coordinates may vary, so we confirm the used coordinates with the user
    print("\nUsing starting coordinates: " + str(start_coords))
    print("\nUsing end coordinates: " + str(end_coords))

    if start_coords in graph.invalid_coordinates or end_coords in graph.invalid_coordinates:
        print("\nDue to blocks, no path was found. Please change the points and try again.")
        return []

    initial_node = Node(None, start_coords)
    final_node = Node(None, end_coords)
    current_node: Node
    path = []

    search_time = time.time()

    open_list.put_nowait(initial_node)

    # This is the search loop
    while open_list.qsize() > 0:
        current_node = open_list.get_nowait()

        # We put the node we just got from the open list in the closed list to remember we visited it already
        closed_list.append(current_node)

        # We test the node for goal condition
        if current_node == final_node:
            # The current node is the final node, so we get it's g as the actual total cost
            print("\nThe cost of the shortest path: " + str(current_node.g))

            # We append the goal node and all the nodes that came before it to the path
            while current_node != initial_node:
                path.append(current_node)

                current_node = current_node.previous

            # The initial node was a condition to know when to stop the loop, we add it after
            path.append(initial_node)

            # Since we added the nodes to the path list from the final node to the initial node, we return the path in
            # reverse order to make its order become from initial to final node
            return path[::-1]

        (x_coord, y_coord) = current_node.coordinates

        # Get a list of all possible directions to explore next
        possible_moves = find_valid_moves(x_coord, y_coord, graph)

        # We create a node for every point we can explore next
        for move in possible_moves:
            next_node = Node(current_node, move)

            move_cost = get_move_cost(current_node.coordinates, next_node.coordinates, graph)

            # Check if it was visited before so we can ignore it if it was
            if next_node not in closed_list:
                # This basically calculates the flight distance between the next node and the final node (straight line)
                next_node.h = math.hypot(next_node.coordinates[0] - final_node.coordinates[0],
                                         next_node.coordinates[1] - final_node.coordinates[1])
                next_node.g = current_node.g + move_cost
                next_node.f = next_node.h + next_node.g

                # We loop the open list for duplicates if the open list isn't empty, otherwise we add the next
                # node to the list directly
                if open_list.qsize() > 0:
                    exists = False
                    for node in open_list.queue:
                        if next_node == node:
                            exists = True

                            # If the node is already in the open list, we add it only if its f is lower
                            if next_node.f < node.f:
                                open_list.put_nowait(next_node)
                                break

                    # If its f isn't lower and is already in the list we ignore it
                    if not exists:
                        open_list.put_nowait(next_node)
                else:
                    open_list.put_nowait(next_node)

        # We check for the run time to interrupt when necessary
        if time.time() - search_time > 10:
            print("\nTime is up. The optimal path was not found.")
            return []

    # The open list emptied and we haven't found a path
    print("\nDue to blocks, no path was found. Please change the points and try again.")
    return []


# noinspection DuplicatedCode
# This function takes a starting coordinate and return a list of all valid neighbouring coordinates
def find_valid_moves(x_coord, y_coord, graph) -> list:
    possible_moves = []

    # If the starting coordinates are not on the boundary edges, we look in all 8 directions
    # For every direction, we check if the point is not in the invalid_coordinates list
    if x_coord != graph.x_axis_ticks[0] and x_coord != graph.x_axis_ticks[-1] + graph.grid_size \
            and y_coord != graph.y_axis_ticks[0] and y_coord != graph.y_axis_ticks[-1] + graph.grid_size:
        # Top move
        if (x_coord, y_coord + graph.grid_size) not in graph.invalid_coordinates:
            adjacent_blocks = 0

            # If the source AND target points are adjacent to two different yellow blocks, the the move is illegal
            # because that would mean it is crossing between two yellow blocks
            # This rule applies to all vertical or horizontal moves
            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and y_coord + graph.grid_size in block:
                    adjacent_blocks += 1

                    if adjacent_blocks >= 2:
                        break

            if adjacent_blocks < 2:
                possible_moves.append((x_coord, y_coord + graph.grid_size))

        # Top-Right move
        if (x_coord + graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
            valid = True

            # If the source AND target points are adjacent to the same yellow block, then the move is illegal
            # A diagonal move is never adjacent to the same block unless it was crossed over
            # This rule applies to all diagonal moves
            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and x_coord + graph.grid_size in block \
                        and y_coord + graph.grid_size in block:
                    valid = False
                    break

            if valid:
                possible_moves.append((x_coord + graph.grid_size, y_coord + graph.grid_size))

        # Right move
        if (x_coord + graph.grid_size, y_coord) not in graph.invalid_coordinates:
            adjacent_blocks = 0

            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and x_coord + graph.grid_size in block:
                    adjacent_blocks += 1

                    if adjacent_blocks >= 2:
                        break

            if adjacent_blocks < 2:
                possible_moves.append((x_coord + graph.grid_size, y_coord))

        # Bottom-Right move
        if (x_coord + graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
            valid = True

            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and x_coord + graph.grid_size in block \
                        and y_coord - graph.grid_size in block:
                    valid = False
                    break

            if valid:
                possible_moves.append((x_coord + graph.grid_size, y_coord - graph.grid_size))

        # Bottom move
        if (x_coord, y_coord - graph.grid_size) not in graph.invalid_coordinates:
            adjacent_blocks = 0

            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and y_coord - graph.grid_size in block:
                    adjacent_blocks += 1

                    if adjacent_blocks >= 2:
                        break

            if adjacent_blocks < 2:
                possible_moves.append((x_coord, y_coord - graph.grid_size))

        # Bottom-Left move
        if (x_coord - graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
            valid = True

            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and x_coord - graph.grid_size in block \
                        and y_coord - graph.grid_size in block:
                    valid = False
                    break

            if valid:
                possible_moves.append((x_coord - graph.grid_size, y_coord - graph.grid_size))

        # Left move
        if (x_coord - graph.grid_size, y_coord) not in graph.invalid_coordinates:
            adjacent_blocks = 0

            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and x_coord - graph.grid_size in block:
                    adjacent_blocks += 1

                    if adjacent_blocks >= 2:
                        break

            if adjacent_blocks < 2:
                possible_moves.append((x_coord - graph.grid_size, y_coord))

        # Top-Left move
        if (x_coord - graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
            valid = True

            for block in graph.blocked_blocks:
                if x_coord in block and y_coord in block and x_coord - graph.grid_size in block \
                        and y_coord + graph.grid_size in block:
                    valid = False
                    break

            if valid:
                possible_moves.append((x_coord - graph.grid_size, y_coord + graph.grid_size))

    # If the source coordinates are along the boundary edges, but not in corners
    # We will check only at 3 direction depending on which side the point is on
    elif (x_coord == graph.x_axis_ticks[0] or x_coord == graph.x_axis_ticks[-1] + graph.grid_size) \
            != (y_coord == graph.y_axis_ticks[0] or y_coord == graph.y_axis_ticks[-1] + graph.grid_size):
        # Bottom edge
        if y_coord == graph.y_axis_ticks[0]:
            # Top-Left move
            if (x_coord - graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord - graph.grid_size in block \
                            and y_coord + graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord - graph.grid_size, y_coord + graph.grid_size))
            # Top move
            # Here we do not check adjacency count because if the source point was adjacent to two yellow blocks,
            # it would be in the invalid coordinates list
            # This applies to vertical and horizontal movements from the edges of the map
            if (x_coord, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                possible_moves.append((x_coord, y_coord + graph.grid_size))

            # Top-Right move
            if (x_coord + graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord + graph.grid_size in block \
                            and y_coord + graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord + graph.grid_size, y_coord + graph.grid_size))

        # Top boundary edge
        elif y_coord == graph.y_axis_ticks[-1] + graph.grid_size:
            # Bottom-Right move
            if (x_coord + graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord + graph.grid_size in block \
                            and y_coord - graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord + graph.grid_size, y_coord - graph.grid_size))

            # Bottom move
            if (x_coord, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                possible_moves.append((x_coord, y_coord - graph.grid_size))

            # Bottom-Left move
            if (x_coord - graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord - graph.grid_size in block \
                            and y_coord - graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord - graph.grid_size, y_coord - graph.grid_size))

        # Left boundary edge
        elif x_coord == graph.x_axis_ticks[0]:
            # Top-Right move
            if (x_coord + graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord + graph.grid_size in block \
                            and y_coord + graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord + graph.grid_size, y_coord + graph.grid_size))

            # Right move
            if (x_coord + graph.grid_size, y_coord) not in graph.invalid_coordinates:
                possible_moves.append((x_coord + graph.grid_size, y_coord))

            # Bottom-Right move
            if (x_coord + graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord + graph.grid_size in block \
                            and y_coord - graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord + graph.grid_size, y_coord - graph.grid_size))

        # Right boundary edge
        else:
            # Bottom-Left move
            if (x_coord - graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord - graph.grid_size in block \
                            and y_coord - graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord - graph.grid_size, y_coord - graph.grid_size))

            # Left move
            if (x_coord - graph.grid_size, y_coord) not in graph.invalid_coordinates:
                possible_moves.append((x_coord - graph.grid_size, y_coord))

            # Top-Left move
            if (x_coord - graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                valid = True

                for block in graph.blocked_blocks:
                    if x_coord in block and y_coord in block and x_coord - graph.grid_size in block \
                            and y_coord + graph.grid_size in block:
                        valid = False
                        break

                if valid:
                    possible_moves.append((x_coord - graph.grid_size, y_coord + graph.grid_size))

    # If the source coordinates are in one of the corners.
    # Corners have only one movement option.
    # We do need to check for adjacency because if they were adjacent to a single yellow block,
    # they would be in the invalid coordinates list
    else:
        # Bottom-Left corner
        if x_coord == graph.x_axis_ticks[0] and y_coord == graph.y_axis_ticks[0]:
            # Top-Right move
            if (x_coord + graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                possible_moves.append((x_coord + graph.grid_size, y_coord + graph.grid_size))

        # Top-Left corner
        elif x_coord == graph.x_axis_ticks[0] and y_coord == graph.y_axis_ticks[-1] + graph.grid_size:
            # Bottom-Right move
            if (x_coord + graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                possible_moves.append((x_coord + graph.grid_size, y_coord - graph.grid_size))

        # Bottom-Right corner
        elif x_coord == graph.x_axis_ticks[-1] + graph.grid_size and y_coord == graph.y_axis_ticks[0]:
            # Top-Left move
            if (x_coord - graph.grid_size, y_coord + graph.grid_size) not in graph.invalid_coordinates:
                possible_moves.append((x_coord - graph.grid_size, y_coord + graph.grid_size))

        # Top-Right corner
        elif x_coord == graph.x_axis_ticks[-1] + graph.grid_size \
                and y_coord == graph.y_axis_ticks[-1] + graph.grid_size:
            # Bottom-Left move
            if (x_coord - graph.grid_size, y_coord - graph.grid_size) not in graph.invalid_coordinates:
                possible_moves.append((x_coord - graph.grid_size, y_coord - graph.grid_size))

    return possible_moves


# Gets a source coordinates, target coordinates, and the map.
# Returns the cost of the move
# Here we already know the move is valid
def get_move_cost(source, target, graph) -> float:
    # If the source and the target have the same x or the same y, the move is either vertical or horizontal
    if source[0] == target[0] or source[1] == target[1]:
        # We iterate through all the yellow blocks
        for block in graph.blocked_blocks:
            # If we find one that is adjacent to the source AND target point, then the move was along a yellow block
            if source[0] in block and source[1] in block and target[0] in block and target[1] in block:
                return 1.3
        return 1
    else:
        return 1.5


# noinspection DuplicatedCode
# This is used to return adjusted coordinates from user input.
# The assignment required that a coordinate inside one grid become the lowest coordinates in that grid
def check_coordinates_validity(coords: tuple, graph) -> tuple:
    x_coord = coords[0]
    y_coord = coords[1]
    # We change the axis here to include an additional tick that is not displayed din the graph
    x_axis = list(graph.x_axis_ticks) + [graph.x_axis_ticks[-1] + graph.grid_size]
    y_axis = list(graph.y_axis_ticks) + [graph.y_axis_ticks[-1] + graph.grid_size]

    # The user can enter an index instead of a coordinate, but it has to be within positive or negative range
    if -len(graph.x_axis_ticks) <= x_coord < len(x_axis):
        x_coord = x_axis[int(x_coord)]

    # If coordinate doesn't fall exactly within an axis tick
    elif x_coord not in x_axis:
        # Out of range coordinates are defaulted to maximum or minimum coordinate tick
        if x_coord < x_axis[0]:
            x_coord = x_axis[0]
        elif x_coord > x_axis[-1]:
            x_coord = x_axis[-1]
        # We compare the coordinate with each tick until it is smaller than the tick, we then know that the lowest tick
        # that coordinate can take precedes the higher ticker we just iterated to
        else:
            for i, tick in enumerate(x_axis):
                if x_coord < tick:
                    x_coord = x_axis[i - 1]
                    break

    # The same thing is done for the y coordinate
    if -len(y_axis) <= y_coord < len(y_axis):
        y_coord = y_axis[int(y_coord)]

    elif y_coord not in y_axis:
        if y_coord < y_axis[0]:
            y_coord = y_axis[0]
        elif y_coord > y_axis[-1]:
            y_coord = y_axis[-1]
        else:
            for i, tick in enumerate(y_axis):
                if y_coord < tick:
                    y_coord = y_axis[i - 1]
                    break

    return x_coord, y_coord
