from d2vs.mapping.base_maps import StaticMap
# from d2vs.mapping.pathing import StaticPather, Node


class Harrogath(StaticMap):
    area_name = "Harrogath"
    # pathfinder = StaticPather
    # threshold = .2  # when doing map diffs  TODO: use this!

    def __init__(self, *args, **kwargs):
        # self.nodes = [
        #     Node(10_000, 10_000, is_start=True)
        # ]

        # TODO: Defining nodes this way blows ass. do it via JSON!

        super().__init__(*args, **kwargs)

