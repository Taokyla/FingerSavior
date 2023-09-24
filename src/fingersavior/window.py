import ctypes
import time
import uuid
from pathlib import Path
from random import randint

import aircv as ac
import cv2
import numpy
import win32api
import win32con
import win32gui
import win32ui
from loguru import logger

from .utils import get_now


class Window(object):
    frame = None
    last_click = None

    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        # self.hWndDC = win32gui.GetDC(self.hwnd)
        self.hWndDC = win32gui.GetWindowDC(self.hwnd)
        self.hMfcDc = win32ui.CreateDCFromHandle(self.hWndDC)
        self.hMemDc = self.hMfcDc.CreateCompatibleDC()
        logger.info("load hwnd {}".format(hwnd))

    @staticmethod
    def get_all_windows(label: str) -> list[int]:
        hwnds = []

        def callback(hwnd, hwnds):
            if win32gui.GetWindowText(hwnd) == label:
                hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(callback, hwnds)
        return hwnds

    @staticmethod
    def is_admin() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def frame_shot(self):
        width, height = win32gui.GetClientRect(self.hwnd)[2:]
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(self.hMfcDc, width, height)
        self.hMemDc.SelectObject(bitmap)
        self.hMemDc.BitBlt((0, 0), (width, height), self.hMfcDc, (0, 0), win32con.SRCCOPY)
        frame = numpy.frombuffer(bitmap.GetBitmapBits(True), dtype=numpy.uint8).reshape(height, width, 4)
        self.frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        win32gui.DeleteObject(bitmap.GetHandle())

    def __del__(self):
        self.hMemDc.DeleteDC()
        self.hMfcDc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hWndDC)

    def click(self, x: int, y: int):
        logger.debug(f"click at ({x},{y})")
        long_position = win32api.MAKELONG(x, y)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)
        time.sleep(randint(85, 100) / 1000.0)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)
        self.last_click = x, y

    def find(self, img_obj, threshold=0.9):
        if self.frame is None:
            self.frame_shot()
        result = ac.find_template(self.frame, img_obj, threshold=threshold)
        return result

    def resize(self, wight=1152, height=679):
        l1, t1, r1, b1 = win32gui.GetWindowRect(self.hwnd)
        client_w, client_h = wight, height
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, l1, t1, client_w, client_h, win32con.SWP_NOZORDER)

    def take_screen_shot(self, savedir: Path = Path("save"), compression: int = 0):
        if self.frame is None:
            self.frame_shot()
        save_path = savedir.joinpath(f"{get_now()}_{uuid.uuid4().hex[:8]}")
        cv2.imwrite(save_path.as_posix(), self.frame, [int(cv2.IMWRITE_PNG_COMPRESSION), compression])
