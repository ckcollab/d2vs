DIRECTION_EAST = "east"
DIRECTION_SOUTH = "south"
DIRECTION_WEST = "west"
DIRECTION_NORTH = "north"


class Node:
    def __init__(self, x, y, is_dead_end, east=None, south=None, west=None, north=None, is_start=False, is_end=False):
        self.connections = dict(east=east, south=south, west=west, north=north)
        self.is_start = is_start
        self.is_end = is_end
        self.is_dead_end = is_dead_end  # could we tele to this spot, or was this a dead end?

        assert not (is_start and is_end), "Cannot be start and end node at the same time!? or can you.. maybe!?"


def find_and_enter_warp(text, preferred_direction=DIRECTION_EAST):
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


    # can we see a warp?
    # mouse over + check name
    # if match: enter warp, return
    # otherwise: we need to pick a direction to go and continue looking
    #   look based on preferred_direction
    #
    pass
