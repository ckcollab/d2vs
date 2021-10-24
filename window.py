import ctypes
import os
from collections import namedtuple
from ctypes import windll, wintypes

import win32api
import win32con
import win32gui
import win32process
from PIL import Image


class BaseError(Exception):
    def __init__(self, message, data=None):
        self.message = message
        self.data = data

    def __str__(self):
        if self.data:
            return '{}, data: {}'.format(self.message, self.data)
        return self.message

    def __repr__(self):
        return repr(self.message)


class WindowsAppNotFoundError(BaseError):
    pass


# https://msdn.microsoft.com/en-us/library/windows/desktop/dd183376(v=vs.85).aspx
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]


def find_process_id(exe_file):
    exe_file = os.path.normpath(exe_file).lower()
    command = "wmic process get processid,commandline"
    for line in os.popen(command).read().lower().splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.split()
        pid = line[-1]
        cmd = " ".join(line[:-1])
        if not cmd:
            continue
        elif cmd.startswith("'") or cmd.startswith('"'):
            pos = cmd.find(cmd[0], 1)
            cmd = cmd[1:pos]
        else:
            cmd = cmd.split()[0]

        if exe_file == cmd:
            return int(pid)


Rect = namedtuple('Rect', ('left', 'top', 'right', 'bottom'))
Size = namedtuple('Size', ('width', 'height'))


class Window(object):
    """A interface of windows' window display zone.

    Args:
        window_name: the text on window border
        exe_file: the path to windows executable
        exclude_border: count the border in display zone or not.
            Default is True.

    Attributes:
        screen: a PIL Image object of current display zone.
        rect: (left, top, right, bottom) of the display zone.
        size: (width, height) of the display zone.

    Methods:
        norm_position((x,y)) --> (x0, y0)
            normalize coordinates relative to window's rect.
    """

    def __init__(self, window_name=None, exe_file=None, exclude_border=True):
        hwnd = 0

        # first check window_name
        if window_name is not None:
            hwnd = win32gui.FindWindow(None, window_name)
            if hwnd == 0:
                def callback(h, extra):
                    if window_name in win32gui.GetWindowText(h):
                        extra.append(h)
                    return True

                extra = []
                win32gui.EnumWindows(callback, extra)
                if extra: hwnd = extra[0]
            if hwnd == 0:
                raise WindowsAppNotFoundError("Windows Application <%s> not found!" % window_name)

        # check exe_file by checking all processes current running.
        elif exe_file is not None:
            pid = find_process_id(exe_file)
            if pid is not None:
                def callback(h, extra):
                    if win32gui.IsWindowVisible(h) and win32gui.IsWindowEnabled(h):
                        _, p = win32process.GetWindowThreadProcessId(h)
                        if p == pid:
                            extra.append(h)
                        return True
                    return True

                extra = []
                win32gui.EnumWindows(callback, extra)
                # TODO: get main window from all windows.
                if extra: hwnd = extra[0]
            if hwnd == 0:
                raise WindowsAppNotFoundError("Windows Application <%s> is not running!" % exe_file)

        # if window_name & exe_file both are None, use the screen.
        if hwnd == 0:
            hwnd = win32gui.GetDesktopWindow()

        self.hwnd = hwnd
        self.exclude_border = exclude_border

    @property
    def rect(self):
        hwnd = self.hwnd
        if not self.exclude_border:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        else:
            _left, _top, _right, _bottom = win32gui.GetClientRect(hwnd)
            left, top = win32gui.ClientToScreen(hwnd, (_left, _top))
            right, bottom = win32gui.ClientToScreen(hwnd, (_right, _bottom))
        return Rect(left, top, right, bottom)

    @property
    def size(self):
        left, top, right, bottom = self.rect
        return Size(right - left, bottom - top)

    def norm_position(self, pos):
        left, top, right, bottom = self.rect
        _left, _top = pos
        x, y = _left - left, _top - top
        if _left > right:
            x = -1
        if _top > bottom:
            y = -1
        return (x, y)

    @property
    def screen(self):
        """PIL Image of current window screen. (the window must be on the top)
        reference: https://msdn.microsoft.com/en-us/library/dd183402(v=vs.85).aspx"""
        # opengl windows cannot get from it's hwnd, so we use the screen
        hwnd = win32gui.GetDesktopWindow()

        # get window size and offset
        left, top, right, bottom = self.rect
        width, height = right - left, bottom - top

        # the device context of the window
        hdcwin = win32gui.GetWindowDC(hwnd)
        # make a temporary dc
        hdcmem = win32gui.CreateCompatibleDC(hdcwin)
        # make a temporary bitmap in memory, this is a PyHANDLE object
        hbmp = win32gui.CreateCompatibleBitmap(hdcwin, width, height)
        # select bitmap for temporary dc
        win32gui.SelectObject(hdcmem, hbmp)
        # copy bits to temporary dc
        win32gui.BitBlt(hdcmem, 0, 0, width, height,
                        hdcwin, left, top, win32con.SRCCOPY)
        # check the bitmap object infomation
        bmp = win32gui.GetObject(hbmp)

        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = bmp.bmWidth
        bi.biHeight = bmp.bmHeight
        bi.biPlanes = bmp.bmPlanes
        bi.biBitCount = bmp.bmBitsPixel
        bi.biCompression = 0  # BI_RGB
        bi.biSizeImage = 0
        bi.biXPelsPerMeter = 0
        bi.biYPelsPerMeter = 0
        bi.biClrUsed = 0
        bi.biClrImportant = 0

        # calculate total size for bits
        pixel = bmp.bmBitsPixel
        size = ((bmp.bmWidth * pixel + pixel - 1) / pixel) * 4 * bmp.bmHeight
        buf = (ctypes.c_char * int(size))()

        # read bits into buffer
        windll.gdi32.GetDIBits(hdcmem, hbmp.handle, 0, bmp.bmHeight, buf, ctypes.byref(bi), win32con.DIB_RGB_COLORS)

        # make a PIL Image
        img = Image.frombuffer('RGB', (bmp.bmWidth, bmp.bmHeight), buf, 'raw', 'BGRX', 0, 1)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        # cleanup
        win32gui.DeleteObject(hbmp)
        win32gui.DeleteObject(hdcmem)
        win32gui.ReleaseDC(hwnd, hdcwin)

        return img

    def _screenshot(self, filepath):
        dirpath = os.path.dirname(os.path.abspath(filepath))
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        self.screen.save(filepath)

    # @property
    # def screen_cv2(self):
    #     """cv2 Image of current window screen"""
    #     pil_image = self.screen.convert('RGB')
    #     cv2_image = np.array(pil_image)
    #     pil_image.close()
    #     # Convert RGB to BGR
    #     cv2_image = cv2_image[:, :, ::-1]
    #     return cv2_image

    # def _screenshot_cv2(self, filepath):
    #     dirpath = os.path.dirname(os.path.abspath(filepath))
    #     if not os.path.exists(dirpath):
    #         os.makedirs(dirpath)
    #     cv2.imwrite(filepath, self.screen_cv2)

    def set_foreground(self):
        win32gui.SetForegroundWindow(self.hwnd)

    def _input_left_mouse(self, x, y):
        left, top, right, bottom = self.rect
        width, height = right - left, bottom - top
        if x < 0 or x > width or y < 0 or y > height:
            return

        win32gui.SetForegroundWindow(self.hwnd)
        pos = win32gui.GetCursorPos()
        win32api.SetCursorPos((left + x, top + y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.Sleep(100)  # ms
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        win32api.Sleep(100)  # ms
        # win32api.SetCursorPos(pos)
