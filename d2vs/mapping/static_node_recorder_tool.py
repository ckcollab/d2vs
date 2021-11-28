import keyboard

from time import sleep

import numpy as np
from cv2 import cv2

from d2vs.mapping.capture2 import map_diff, map_capture, map_merge_features
from d2vs.mapping.pathing import Node


class AutoRecorder:
    def __init__(self):
        sleep(2)  # time to load up D2 window

        self.nodes = {}

        self.map = map_diff(*map_capture(), is_start=True)
        self.start_node = Node(
            10_000,
            10_000,
            is_start=True,
        )
        self.nodes[(self.start_node.x, self.start_node.y)] = self.start_node
        # Points to last created node
        self.prev_node = self.start_node

        # Location of red dot (start) on map
        self.last_base_x, self.lase_base_y = None, None

    def record_new_node(self):
        diff = map_diff(*map_capture())
        self.map, x, y, self.last_base_x, self.lase_base_y = map_merge_features(self.map, diff)

        # TODO: sanity check, is this node too close to a previous one? may min distance is like 20 pixels?

        new_node = Node(x, y)

        self.nodes[(new_node.x, new_node.y)] = new_node

        # TODO: also connect all nodes within ??? range?
        self.prev_node.connections.append(new_node)  # connect previous to new
        self.prev_node = new_node  # new is now the old!

        print(x, y)

    def finish(self):
        # node = self.start_node
        # while True:
        #     print(node)

        # print(self.start_node)

        # todo: draw the nodes? funsies
        map_copy = self.map.copy()

        for node in self.nodes.values():
            # Go back from 10_000, 10_000 based coordinate system to 0, 0 based for drawing this on our diff
            x = node.x + self.last_base_x - 10_000
            y = node.y + self.lase_base_y - 10_000
            print(f"Drawing node from ({node.x}, {node.y}) to ({x}, {y})")
            cv2.putText(map_copy, f"({node.x}, {node.y}", (x, y - 15), 1, 1, (0x00, 0xff, 0x00))
            cv2.circle(map_copy, (x, y), 4, (0x00, 0xff, 0x00), -1)

        cv2.imshow("map with nodes", map_copy)
        cv2.waitKey(0)


if __name__ == "__main__":
    # cv2.imshow("asfd", np.array([[(255, 255, 255)]]))
    # cv2.waitKey(0)

    recorder = AutoRecorder()

    keyboard.add_hotkey("scroll lock", recorder.record_new_node)
    keyboard.add_hotkey("pause break", recorder.finish)

    # wait forever
    while True:
        sleep(.1)
