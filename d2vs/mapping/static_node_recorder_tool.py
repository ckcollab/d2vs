import json

import keyboard

from time import sleep

import numpy as np
from cv2 import cv2

from d2vs.mapping.capture2 import map_diff, map_capture, map_merge_features
from d2vs.mapping.pathing import Node
from d2vs.utils import NpEncoder


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
        diff = map_diff(*map_capture(), threshold=.15)
        self.map, x, y, self.last_base_x, self.lase_base_y = map_merge_features(self.map, diff)

        # TODO: sanity check, is this node too close to a previous one? may min distance is like 20 pixels?

        new_node = Node(x, y)

        self.nodes[(new_node.x, new_node.y)] = new_node

        # TODO: also connect all nodes within ??? range?
        self.prev_node.add_connection(new_node)  # connect previous to new
        self.prev_node = new_node  # new is now the old!

        print(x, y)

    def finish(self):
        # node = self.start_node
        # while True:
        #     print(node)

        # print(self.start_node)

        # todo: draw the nodes? funsies
        map_copy = self.map.copy()

        # lighten map color so easier to see debug shit
        map_copy[np.where((map_copy == [255, 255, 255]).all(axis=2))] = [0x70, 0x70, 0x70]

        # Delete any old green markers for "current location"
        map_copy[np.all(map_copy == [0, 255, 0], axis=-1)] = [0, 0, 0]

        for node in self.nodes.values():
            # Go back from 10_000, 10_000 based coordinate system to 0, 0 based for drawing this on our diff
            x = node.x + self.last_base_x - 10_000
            y = node.y + self.lase_base_y - 10_000
            print(f"Drawing node from ({node.x}, {node.y}) to ({x}, {y})")
            FONT_HERSHEY_COMPLEX_SMALL = 5
            cv2.putText(map_copy, f"{node.x}, {node.y}", (x - 20, y - 10), FONT_HERSHEY_COMPLEX_SMALL, .66, (0x00, 0xff, 0x00), 1)

            if node.is_start:
                color = (0x00, 0x00, 0xff)
            else:
                color = (0x00, 0xff, 0x00)

            cv2.circle(map_copy, (x, y), 3, color, -1)

            for conn in node.get_connections():
                conn_new_x = conn.x + self.last_base_x - 10_000
                conn_new_y = conn.y + self.lase_base_y - 10_000

                cv2.line(map_copy, (x, y), (conn_new_x, conn_new_y), (0x00, 0xff, 0x00))


        node_dict_data = []
        for node in self.nodes.values():
            node_data = node.to_dict()
            print(f"Adding node_data: {node_data}")
            node_dict_data.append(node_data)

        with open("areas/static_data/harrogath.json", "w") as f:
            f.write(json.dumps(node_dict_data, cls=NpEncoder))

        cv2.imshow("map with nodes", map_copy)
        cv2.waitKey(0)











        # TODO: OUTPUT JSON?!















if __name__ == "__main__":
    # cv2.imshow("asfd", np.array([[(255, 255, 255)]]))
    # cv2.waitKey(0)

    recorder = AutoRecorder()

    keyboard.add_hotkey("scroll lock", recorder.record_new_node)
    keyboard.add_hotkey("pause break", recorder.finish)

    # wait forever
    while True:
        sleep(.1)
