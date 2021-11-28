from d2vs.mapping.map import StaticMap
from d2vs.mapping.pathing import StaticPather, Node


class Harrogath(StaticMap):
    pathfinder = StaticPather
    nodes = [
        Node(10_000, 10_000, is_start=True)
    ]
