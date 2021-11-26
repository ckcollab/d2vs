from time import sleep

from cv2 import cv2

from capture2 import map_capture, map_merge_features, map_diff


DIRECTION_NORTH_WEST = 1
DIRECTION_NORTH_EAST = 2
DIRECTION_SOUTH_EAST = 3
DIRECTION_SOUTH_WEST = 4


class Node:
    def __init__(self, x, y, diff, connections=None, unwalkable=False, is_start=False, is_end=False):
        # Sanity checks..
        # assert not is_start and connections, "Must set at least one direction, we had to have come from " \
        #                                      "somewhere?! Unless we just started, then mark is_start = True"

        assert not (is_start and is_end), "Cannot be start and end node at the same time!? or can you.. maybe!?"

        # Coords
        self.x = x
        self.y = y

        # Are we walkable? I.e., we tried to tele here and detected that tele failed.. not walkable!
        self.unwalkable = unwalkable

        # Setup connections to other nodes
        self.connections = connections or {}

        # Beginning or next to our goal?
        self.is_start = is_start
        self.is_end = is_end

        # The image of the map difference screenshot taken at this step
        self.diff = diff


def find_and_enter_warp(text, preferred_direction=DIRECTION_NORTH_WEST):
    """Flood fills area looking for warps. When a warp is found, mouse hovers over it to read
    the text. If warp text matches given text, the warp is entered."""

    """
    # "hidden" stop clause - not reinvoking for "c" or "b", only for "a".
    if matrix[x][y] == "a":  
        matrix[x][y] = "c" 
        #recursively invoke flood fill on all surrounding cells:
        if x > 0:
            floodfill(matrix,x-1,y)
        if x < len(matrix[y]) - 1:
            floodfill(matrix,x+1,y)
        if y > 0:
            floodfill(matrix,x,y-1)
        if y < len(matrix) - 1:
            floodfill(matrix,x,y+1)
    """







    """
    ##1. Take picture of current area, set start pos
    ##2. Pick a direction, starting with preferred_direction
    3. Take a picture:
        a. diff happens first to calc x/y
        a. Create `new_node` (`if counter == 0 then is_start = True`, skip rest)
        
        a. Detect if we moved at all
            - If no movement, `node.is_walkable = False`
            - Change `preferred_direction`
        a. Detect if warp is on minimap
            - If so change `preferred_direction` to point to it
        a. Detect if warp is on screen
            - Scan mouse over area to look for it and try to click 
            - Mark `node.is_end = True`
            - Return
        a. go back to start ?
    4. 
    """





    # pre, during_1, during_2 = map_capture()
    # cv2.imshow("Result", pre)
    # cv2.waitKey(0)
    # exit()







    # Start...
    counter = 0
    map = map_diff(*map_capture(), is_start=True)
    prev_node = Node(
        10_000,
        10_000,
        map,
        is_start=True,
    )

    sleep(2)

    while True:
        diff = map_diff(*map_capture())
        map, x, y = map_merge_features(map, diff)

        new_node = Node(x, y, diff)

        # if counter != 0:
        #     prev_node.connections[what direction were we coming from??]


        sleep(2)



        counter += 1

        if counter == 10:
            break

        prev_node = new_node

    cv2.imshow("Result", map)
    cv2.waitKey(0)












    # can we see a warp?
    # mouse over + check name
    # if match: enter warp, return
    # otherwise: we need to pick a direction to go and continue looking
    #   look based on preferred_direction
    #


if __name__ == "__main__":
    find_and_enter_warp("Durance of Hate Level 2", preferred_direction=DIRECTION_NORTH_EAST)
