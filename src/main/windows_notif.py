from win32api import *
from win32gui import *
import win32con
import time
import random


class WindowsBalloonTip:

    def __init__(self, title, msg, icon_path, duration):

        message_map = {win32con.WM_DESTROY: self.OnDestroy}
        # Register the Window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar" + str(random.randint(0, 10000))
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        class_atom = RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow(class_atom, "Taskbar", style,
                                 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                 0, 0, hinst, None)
        UpdateWindow(self.hwnd)
        icon_path_name = icon_path
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hicon = LoadImage(hinst, icon_path_name,
                              win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY,
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER + 20,
                          hicon, "save-song-spotify", msg, 200, title))
        time.sleep(duration / 1000)
        DestroyWindow(self.hwnd)
        UnregisterClass(class_atom, hinst)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)


def send_notif(title, msg, icon_path, duration):
    WindowsBalloonTip(title, msg, icon_path, duration)
