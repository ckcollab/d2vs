from textwrap import indent


class Node:
    def __init__(self, x, y, connections=None, unwalkable=False, is_start=False, is_end=False):
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
        self.connections = connections or []

        # Beginning or next to our goal? Sometimes maybe we have no goal?
        self.is_start = is_start
        self.is_end = is_end

    # def __str__(self):
    #     s = f"({self.x}, {self.y})"
    #     if self.connections:
    #         connection_string = indent(''.join([str(c) for c in self.connections]), "\t")
    #         s += f" -> \n{connection_string}"
    #     return s


class DynamicNode(Node):
    def __init__(self, x, y, diff, **kwargs):
        super().__init__(x, y, **kwargs)

        # The image of the map difference screenshot taken at this step
        self.diff = diff
