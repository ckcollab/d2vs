from d2vs.mapping.areas import Harrogath
from d2vs.mapping.pathing.node import InteractableType


# class StaticPather:
#     """For pathfinding on static maps, like Harrogath"""
#     pass


if __name__ == "__main__":
    # from anywhere in a5 town, go to Malah

    # load a5 town nodes/interactables
    area = Harrogath()
    path = area.find_interactable_type(InteractableType.HEALER)

    print("Found path!")
    for p in path:
        print(p)
