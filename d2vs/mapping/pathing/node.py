import json
from enum import Enum, auto


class InteractableType(Enum):
    WAYPOINT = auto()
    WARP = auto()
    HEALER = auto()
    REPAIRER = auto()


class Interactable:
    """Appears near a node, not a "walkable point" but something you interact with typically.

    Examples:
        - Red Portal
        - Malah (the Act 5 healer)
    """
    def __init__(self, x, y, name, interactable_type: InteractableType):
        self.x = x
        self.y = y
        self.name = name

        assert interactable_type in InteractableType.__members__.values(), f"{interactable_type} not in InteractableTypes, " \
                                                                           f"known options are {InteractableType.__members__.values()}"
        self.interactable_type = interactable_type

    def to_dict(self):
        """for json serialization"""
        return {
            "x": self.x,
            "y": self.y,
            "name": self.name or "",
            "interactable_type": self.interactable_type.name,
        }


class Node:
    def __init__(self, x, y, unwalkable=False, is_start=False, is_end=False):
        # Sanity checks..
        # assert not is_start and connections, "Must set at least one direction, we had to have come from " \
        #                                      "somewhere?! Unless we just started, then mark is_start = True"

        assert not (is_start and is_end), "Cannot be start and end node at the same time!? or can you.. maybe!?"

        # Coords
        self.x = x
        self.y = y

        # Are we walkable? I.e., we tried to tele here and detected that tele failed.. not walkable!
        self.unwalkable = unwalkable

        # Setup connections (list of x, y tuples) to other nodes
        self._connections = {}

        # Things you can interact with near this node..
        self._interactables = {}

        # Beginning or next to our goal? Sometimes maybe we have no goal?
        self.is_start = is_start
        self.is_end = is_end

    def __str__(self):
        return f"{self.x}, {self.y}"

    def to_dict(self):
        """for json serialization"""
        return {
            "x": self.x,
            "y": self.y,
            "unwalkable": self.unwalkable,
            "connections": [(x, y) for x, y in self._connections.keys()],
            "interactables": [(x, y) for x, y in self._interactables.keys()],
            "is_start": self.is_start,
            "is_end": self.is_end,
        }

    def get_connections(self):
        return self._connections.values()

    def add_connection(self, node):
        assert (node.x, node.y) not in self._connections, "Cannot add existing connection to node?!"
        self._connections[(node.x, node.y)] = node

    def get_interactables(self):
        return self._interactables.values()

    def add_interactable(self, interactable):
        assert (interactable.x, interactable.y) not in self._connections, "Cannot add existing interactable to node?!"
        self._interactables[(interactable.x, interactable.y)] = interactable


class DynamicNode(Node):
    def __init__(self, x, y, diff, **kwargs):
        super().__init__(x, y, **kwargs)

        # The image of the map difference screenshot taken at this step
        self.diff = diff
