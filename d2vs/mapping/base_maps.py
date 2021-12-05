import json
import os
import d2vs

from abc import ABC, abstractmethod

from cv2 import cv2

from d2vs.mapping.pathing import Node
from d2vs.mapping.pathing.node import Interactable, InteractableType


class BaseMap(ABC):
    def __init__(self):
        assert self.area_name, "You must set an area_name on each Map class"
        # assert self.pathfinder, "You must set a pathfinder on each Map class"






        # TODO: Load nodes + interactables and all that shit from json


    # @abstractmethod
    # def find_point(self, x, y):
    #     pass

    @abstractmethod
    def find_interactable(self, interactable):
        pass

    @abstractmethod
    def find_interactable_type(self, interactable_type: InteractableType):
        pass






class StaticMap(BaseMap):
    """I.e. Harrogath."""
    def __init__(self):
        super().__init__()

        assert os.path.exists(self.png_path), f"{self.area_name} png_path file ({self.png_path}) is missing"
        assert os.path.exists(self.debug_png_path), f"{self.area_name} debug_png_path ({self.debug_png_path}) is missing"
        assert os.path.exists(self.json_path), f"{self.area_name} json_path ({self.json_path}) is missing"

        # Load map png (has red circle showing start point typically)
        self.map = cv2.imread(self.png_path)

        # Nodes have keys as (x, y) tuple and values are Nodes
        self.nodes = {}

        # Quick lookup dict for interactables, keys are (x, y) as well
        self.interactables = {}

        self.start_node = None  # this is set when loading json, should always be 10_000, 10_000

        self._load_json()

    def _load_json(self):
        """This is its own method in case we need to re-load nodes from json .. maybe for testing
        or realtime recalculating nodes?"""
        data = json.loads(open(self.json_path, "r").read())

        # Loop over data once and make initial set of nodes
        for n in data["nodes"]:
            # pop data not used in class creation
            n_copy = n.copy()
            n_copy.pop("connections")
            n_copy.pop("interactables")
            node = Node(**n_copy)
            self.nodes[(node.x, node.y)] = node

            if node.is_start:
                assert self.start_node is None, "We found multiple start nodes?! tried setting it twice"
                self.start_node = node

        # Loop over data again and make connections
        for n in data["nodes"]:
            for c_x, c_y in n["connections"]:
                self.nodes[(n["x"], n["y"])].add_connection(self.nodes[(c_x, c_y)])

            for interactable_data in n["interactables"]:
                print(interactable_data)
                interactable = Interactable(**interactable_data)
                self.nodes[(n["x"], n["y"])].add_interactable(interactable)
                self.interactables[(interactable.x, interactable.y)] = interactable

    @property
    def png_path(self):
        return os.path.join(os.path.dirname(d2vs.__file__), f"mapping", "areas", "static_data", f"{self.area_name}.png")

    @property
    def debug_png_path(self):
        # return f"areas/static_data/{self.area_name}_debug.png"
        return os.path.join(os.path.dirname(d2vs.__file__), f"mapping", "areas", "static_data", f"{self.area_name}_debug.png")

    @property
    def json_path(self):
        # return f"areas/static_data/{self.area_name}.json"
        return os.path.join(os.path.dirname(d2vs.__file__), f"mapping", "areas", "static_data", f"{self.area_name}.json")

    def find_interactable_type(self, interactable_type):
        """Convenience wrapper for self.find_interactable that automatically goes to the first matching
        interactable in this area."""
        interactable = None
        for i in self.interactables.values():
            if i.interactable_type == interactable_type:
                interactable = i

        assert interactable, f"Unable to find interactable of type {interactable_type}!"

        return self.find_interactable(interactable)

    def find_interactable(self, interactable):
        explored = []
        queue = [[self.start_node]]  # TODO: start should be some kind of param?

        while queue:
            path = queue.pop(0)
            node = path[-1]

            if node not in explored:
                for conn in node.get_connections():
                    new_path = list(path)  # copy path
                    new_path.append(conn)
                    queue.append(new_path)

                    for i in conn.get_interactables():
                        if i == interactable:  # We found it! return path
                            new_path.append(interactable)
                            return new_path

                explored.append(node)



class StaticMapWithVariations(BaseMap):
    """I.e. Rogue Encampment, having many variations you can tell from some initial template.

    Another example: Halls of Pain 3 variations."""
    pass


class DynamicMap(BaseMap):
    """Start position is whereever we start scanning. Look for a goal.

    TODO: Make a DynamicMapEnclosed vs Open for like durance vs black marsh, open area vs not?
    """
    pass