# import keyboard
# import pyautogui
#
# from collections import defaultdict
# from datetime import datetime
# from time import sleep
#
# from d2vs.alert_helpers import send_mail
# from d2vs.constants import ITEM_TYPES
# from d2vs.helpers import coord_translation
# from d2vs.ocr import OCR
#
#
# # On load one time we read pickit from ./pickit.txt
# #
# # Once config is loaded, PICKIT_CONFIG will contain..
# #   <item name>: [<item types to pickup>]
# #
# # i.e. (ALL LOWER!)
# #   "monarch": ["unique"],
# #   "amulet": ["rare", "set", "unique"],
# PICKIT_CONFIG = defaultdict(set)
#
# try:
#     with open('pickit.txt', 'r') as f:
#         for line in f.readlines():
#             # Strip whitespace from front/back
#             line = line.lower().strip()
#             if line.startswith("#") or not line:
#                 continue
#             name, item_type = line.split(",")
#             PICKIT_CONFIG[name.strip()].add(item_type.strip())
# except FileNotFoundError:
#     raise Exception("No pickit configuration found, you must make pickit.txt in the same directory as this bot.")
#
#
# def pick_area(base_x=500, base_y=300, end_x=1900, end_y=1000, max_loops=8):
#     """
#     Picks up items from a scan area, does up to max_loops (default 8) pickup attempts
#
#     These coordinates are automatically translated from 1440p to 1080p
#
#     :param base_x:
#     :param base_y:
#     :param end_x:
#     :param end_y:
#     :param max_loops:
#     :return:
#     """
#     # Reveal items on ground and wait for it to draw to screen
#     keyboard.press('alt')
#     sleep(.1)
#
#     base_x, base_y = coord_translation(base_x, base_y)
#     end_x, end_y = coord_translation(end_x, end_y)
#
#     current_loop = 0
#     while current_loop < max_loops:
#         pyautogui.moveTo(1, 1)  # get mouse outta the way so we can see all items
#         bounded_text = OCR().read(
#             base_x,
#             base_y,
#             end_x,
#             end_y,
#             coords_have_been_translated=True,
#             # Only saving these images, typically groups items better
#             save_debug_images=current_loop == 0,  # only save first loop
#
#             # combine text found near each other at 0.8, pretty large margin
#             width_ths=0.8,
#         )
#
#         # TODO: Algorithm to detect mis-picks!
#         #   - Keep record of all items on ground
#         #   - After pickup, we should only have lost 1 item (our desired one .. maybe some left screen legitimately)
#         #   - If our item is still on ground, raise alarms? potential misspick wee woo wee woo!
#
#         # Log all items for debugging..
#         if current_loop == 0:
#             with open('pickit.log', 'a+') as f:
#                 for _, text, item_type in bounded_text:
#                     # Ignore super common things from logging
#                     if 'potion' in text.lower() or 'arrows' == text.lower() or 'bolts' == text.lower() or ' Gold' in text or 'scroll of' in text.lower():
#                         continue
#                     pickable = is_pickable(text, item_type)
#                     pickable_suffix = '***' if pickable else ''
#                     f.write(f"{datetime.now():%m/%d/%Y %I:%M%p} {text}, {item_type}{pickable_suffix}\n")
#
#                     if pickable:
#                         send_mail(f"[D2VS] Found {item_type} {text}", "Nothing much else to say chief!")
#
#
#         # Do a SECOND scan to make sure we aren't missing any potential items!
#         bounded_text += OCR().read(
#             base_x,
#             base_y,
#             end_x,
#             end_y,
#             coords_have_been_translated=True,
#
#             # combine text found near each other at a small margin, in case any items accidentally merged during scan!
#             width_ths=0.55,
#         )
#
#         any_pickable = False
#
#         for (top_left, top_right, bottom_right, bottom_left), text, item_type in bounded_text:
#             # print(f"is_pickable({text}, {item_type})??!")
#             if is_pickable(text, item_type):
#                 any_pickable = True
#                 center_x = int(base_x + top_left[0] + ((bottom_right[0] - top_left[0]) / 2))
#                 center_y = int(base_y + top_left[1] + ((bottom_right[1] - top_left[1]) / 2))
#
#                 with open('pickit.log', 'a+') as f:
#                     f.write(f"Attempting to pickup {item_type} {text} @ {center_x}, {center_y}...\n")
#
#                 print(f"Found pickable item {item_type} {text} @ {center_x}, {center_y}")
#
#                 pyautogui.click(center_x, center_y, clicks=2, interval=.01)  # 2 clicks seems to help move to it and snag it
#                 sleep(1)  # wait for pickup.. sometimes we try to re-pickup the item as it's already being picked up
#
#                 # wait for next loop (re-scan) to find next item, it may have moved!
#                 break
#
#         # OLD: We didn't see any pickable items after a couple loops, can leave
#         # if not any_pickable and current_loop >= 1:
#         # NEW: Confident in scans now, only scanning once then bailing
#         if not any_pickable:
#             break
#
#         current_loop += 1
#         sleep(.01)
#
#     keyboard.release('alt')
#
#
# def is_pickable(name, item_type):
#     """
#     Looks at our pre-loaded configuration (from pickit.txt) and returns True if the given item + type
#     is in there.
#
#     :param name: Item name
#     :param item_type: Item type ("unique", "set", "rare")
#     :return: True if this is pickable, False if it's garbo!
#     """
#     assert item_type in ITEM_TYPES, f"{item_type} is not a known item type? Expecting one of {','.join(ITEM_TYPES.keys())}"
#
#     name = name.lower()
#     item_type = item_type.lower()
#
#     return name in PICKIT_CONFIG and item_type in PICKIT_CONFIG[name]
