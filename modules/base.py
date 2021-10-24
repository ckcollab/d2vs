from abc import ABC, abstractmethod


class BaseModule(ABC):



    # @abstractmethod
    def on_screen_capture(self, screen_data):
        pass

    def on_game_start(self):
        pass

    # @abstractmethod
    # def on_memory_read(self):
    #     pass
