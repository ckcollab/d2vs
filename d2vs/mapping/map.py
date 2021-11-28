class BaseMap:
    def __init__(self):
        assert self.pathfinder, "You must set a pathfinder on each Map class"


class StaticMap(BaseMap):
    """I.e. Harrogath."""
    pass


class StaticMapWithVariations(BaseMap):
    """I.e. Rogue Encampment, having many variations you can tell from some initial template.

    Another example: Halls of Pain 3 variations."""
    pass


class DynamicMap(BaseMap):
    """Start position is whereever we start scanning. Look for a goal.

    TODO: Make a DynamicMapEnclosed vs Open for like durance vs black marsh, open area vs not?
    """
    pass