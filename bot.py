import os
import numpy as np
import psutil
import pyautogui

from datetime import datetime
from time import sleep, time
from threading import Thread

from pygetwindow import PyGetWindowException

from d2vs.exceptions import ChickenException, CanNoLongerBotException
from d2vs.helpers import click, shift_attack, coord_translation, slow_click
from d2vs.modules import Town, Chicken, PickIt
from d2vs.ocr import OCR
from d2vs.pickit import pick_area
from d2vs.thread_hacks import ctype_async_raise
from d2vs.window import Window

from state_checks import is_corpse_on_ground, is_at_character_select_screen, is_in_queue, is_mercenary_alive, \
    is_in_game, is_game_errored_out


class Bot:

    def __init__(self):
        OCR()  # OCR is singleton, this initializes it
        self.window = Window()

        self.modules = {
            "Town": Town(),
            "Chicken": Chicken(),
            "PickIt": PickIt(),
        }

        self.screen_scan_thread = None
        self.game_thread = None

        # Setup Hotkeys for controlling bot..
        # keyboard.add_hotkey('pause', lambda: exit(1))  # .... does not work ....

    def _screen_scan_loop(self):
        while True:
            if pyautogui.getActiveWindowTitle() != "Diablo II: Resurrected":
                sleep(.1)
                continue

            try:
                screen_data = np.array(self.window.screen)

                # This should be just about the only place we do that. Capturing the screen is relatively expensive.
                OCR().set_screen_data(screen_data)

                for name, module in self.modules.items():
                    module.on_screen_capture(screen_data)
                sleep(.01)
            except ChickenException:
                # Re-raise this chicken event in our game bot thread
                ctype_async_raise(self.game_thread.ident, ChickenException)

    def _game_loop_wrapper(self):
        """This wrapper is for catching chicken events and such..."""
        while True:
            try:
                self._game_loop()
            except ChickenException:
                print(f"Chickening @ {datetime.now():%m/%d/%Y %I:%M%p}!!!")
                pyautogui.press('esc')
                click(1275, 633, delay=.25)
            except CanNoLongerBotException as e:
                print(f"Can't bot any longer: {e}")

    def _game_loop(self):
        # make sure game started
        win = pyautogui.getWindowsWithTitle("Diablo II: Resurrected")

        if win and any(w.title == "Diablo II: Resurrected" for w in win):  # make sure it's the exact title and not some youtube video!
            # Get first window matching exact title..
            win = [w for w in win if w.title == "Diablo II: Resurrected"][0]

            try:
                win.activate()
            except PyGetWindowException:
                # wtf happened? had this error once when i interrupted bot and minimized it..
                return

            # Let screen scan fill OCR with data before we start
            sleep(1)
        else:
            # Game wasn't even open yet..
            print("Game not even started yet, starting..")
            os.startfile("C:\Program Files (x86)\Diablo II Resurrected\D2R.exe")
            sleep(10)
            pyautogui.press('space')  # intro video..
            sleep(3)
            pyautogui.press('space')  # another thing ??
            sleep(10)
            pyautogui.press('space')  # press any key to continue bullshit ...
            sleep(3)





        # sleep(1)
        # readings = OCR().read(700, 1, 2599, 750, coords_have_been_translated=False, width_ths=0.5)
        # for r in readings:
        #     print(r)
        #
        # print("---------------------------")
        #
        # readings = OCR().read(700, 1, 2599, 750, coords_have_been_translated=False, width_ths=0.8)
        # for r in readings:
        #     print(r)
        #
        # sleep(5555)










        # Is this an error window?
        if is_game_errored_out(win):
            print("Game is errored out? Restarting..")
            for proc in psutil.process_iter():
                if proc.name() in ('D2R.exe', 'BlizzardError.exe'):
                    print(f"killing {proc.name()}")
                    p = psutil.Process(proc.pid)
                    for child in p.children(recursive=True):  # or parent.children() for recursive=False
                        child.kill()
                    p.kill()

        # In queue?
        queue_check_count = 0
        while is_in_queue():
            if queue_check_count == 0:
                print("Waiting in queue!!! waiting 10 seconds to check again..")
            sleep(10)
            queue_check_count += 1

        # Back at char selection? OR maybe we're in game?
        if not is_in_game():
            char_screen_retries = 1
            while not is_at_character_select_screen() and char_screen_retries < 3:
                sleep(2 * char_screen_retries)
                char_screen_retries += 1

            if char_screen_retries >= 3:
                # TODO: Restart game here if we've tried this a few times???
                print("We're not at online char select screen yet, clicking 'Online' to try and get back..")
                click(2185, 71, delay=1)
                return

            # Start game...
            click(1059, 1285)
            click(1275, 782, delay=.1)
        else:
            # Already in game??
            # TODO: Exit game... no idea what state we're in. Go back to start ???
            pass

        # Wait until we're for sure in game..
        is_in_game_timeout_seconds = 30
        is_in_game_current_time = time()
        while not is_in_game() and time() - is_in_game_current_time < is_in_game_timeout_seconds:
            sleep(1)

        if time() - is_in_game_current_time >= is_in_game_timeout_seconds:
            # no idea what state we're in. Go back to start ???
            print("we timed out ???")
            return

        # TODO: Confirm we eventually see loading ...

        # Game started ...
        for name, module in self.modules.items():
            module.on_game_start()
        # self.modules["Town"]

        # Did we die?
        if is_corpse_on_ground():
            print("Corpse found! Picking up...")
            click(1276, 672)

        # Are we in act 4 or act 5? did we fuck up?
        # TODO: CHECK THIS!

        # Go near WP and prepare for merc check...
        """
        750, 1180
        896, 1126
        961, 1290
        """
        click(750, 1180)
        click(896, 1126, delay=1.65)

        # Is merc alive?
        if is_mercenary_alive():
            # go straight to red portal
            # print("ahoy merc nice to see ya")
            # click(999, 1286, delay=1.55)  # this goes past WP next to lil rock wall (2 clicks close together works nice for some reason ..)
            # click(1131, 1269, delay=1.45)
            click(961, 1290, delay=1.55)
            click(961, 1290, delay=0.1)  # double click is requisite for some reason to properly travel a consistent distance..

        else:
            # go to Act 4, revive merc, come back, resume path to go to red portal
            print("Merc dead! Reviving... hope I don't get stuck in act 4!")

            pyautogui.press('f7')  # telekenisis
            slow_click(1100, 916, delay=1.0, button="right")  # click wp
            # click(1100, 916, delay=.05)                     # click wp twice
            click(659, 295, delay=2.0)                        # click act 4
            click(319, 358, delay=2.5)                        # click Pandamonium Fortress
            slow_click(315, 10, delay=10.5)                   # click Tyrael

            # Search for "Resurrect: " text and click the center of it
            x1, y1 = coord_translation(512, 16)
            x2, y2 = coord_translation(1697, 699)
            resurrect_readings = OCR().read(x1, y1, x2, y2, delay=2.5, coords_have_been_translated=True)
            # print("resurrect_readings results:")
            # print(resurrect_readings)
            for (top_left, top_right, bottom_right, bottom_left), text, _ in resurrect_readings:
                if "resurrect" in text.lower():
                    center_y = int(y1 + top_left[1] + ((bottom_right[1] - top_left[1]) / 2))
                    center_x = int(x1 + top_left[0] + 6)

                    # click resurrect
                    click(center_x, center_y)

                    # ..did we not have enough gold? check if merc alive
                    sleep(1.5)
                    if not is_mercenary_alive():
                        raise CanNoLongerBotException("Can no longer bot. no mercenary :( not enough gold to revive.")
                    break

            slow_click(2125, 1059, delay=1.0)  # click wp
            click(774, 292, delay=2.5)         # click act 5
            click(322, 350, delay=1.0)         # click harrogath
            click(1135, 1014, delay=8.5)       # click next to rock wall and continue normal path

        click(1131, 1269, delay=1.45)
        click(641, 883, delay=1.4)
        pyautogui.press('f7')  # telekenisis
        slow_click(325, 500, delay=1.5, button="right")
        # slow_click(350, 400, delay=0.4, button="right")  # sometimes first one doesnt work ... click a little up
        slow_click(435, 325, delay=0.4, button="right")  # sometimes first one doesnt work ... click a lot up and to the right

        # TP to pindle
        sleep(.5)
        pyautogui.press('f5')  # teleport

        click(1400, 700, delay=1.25)  # take a quick step forward before TPing

        click(2535, 25, delay=.45, button="right")
        click(2535, 25, delay=.45, button="right")

        pyautogui.press('f2')  # set blizzard up
        click(1557, 352, delay=.45, button="right")  # blizz

        # Glacier opener
        # shift_attack(1557, 352)

        # Final attack combo
        for _ in range(2):
            shift_attack(1557, 352, duration=1.75)  # glaciers
            click(1557, 352, delay=.4, button="right")  # blizz

        # wait for merc to maybe kill cold immune guy?
        sleep(.5)

        # Read under cursor, cold immune?
        # todo..

        # Check items?
        # pyautogui.press('f5')  # teleport closer..
        # click(1775, 400, delay=.5, button="right")
        pick_area(500, 1, 2599, 750)

        # leave game...
        pyautogui.press('esc')
        click(1275, 633, delay=.5)

        # wait for next!
        sleep(22)

    def run(self):
        # daemon=True here so when we close the app this thread closes cleanly, doesn't seem to otherwise..
        # may not be helpful..
        self.screen_scan_thread = Thread(target=self._screen_scan_loop, daemon=True)
        self.screen_scan_thread.start()

        self.game_thread = Thread(target=self._game_loop_wrapper, daemon=True)
        self.game_thread.start()

        while True:
            # go forever!
            sleep(1)


bot = Bot()
bot.run()
