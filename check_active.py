import pygetwindow as gw
from time import sleep
global screen_height

screen_height = 1080
def check_active(title="Roblox", title_ending=None):
    print("check")
    active_window = gw.getActiveWindow()
    if active_window is not None:
        title_active = title_ending is None and active_window.title == title
        title_ending_active = title_ending is not None and active_window.title.endswith(title_ending)
        if title_active or title_ending_active:
            print(f"{active_window.title} already active")
            return
    for window in gw.getAllWindows():
        title_active = title_ending is None and window.title == title
        title_ending_active = title_ending is not None and window.title.endswith(title_ending)
        if title_active or title_ending_active:
            try:
                window.minimize()
                print(f"Minimized {window.title}")
            except Exception:
                print(f"ERROR IN MINIMIZING {window.title}")
            try:
                window.focus()
                print(f"Focused {window.title}")
            except Exception:
                print(f"ERROR IN FOCUSING {window.title}")
            try:
                window.activate()
                print(f"Activated {window.title}")
            except Exception:
                print(f"ERROR IN ACTIVATING {window.title}")
            try:
                window.maximize()
                print(f"Maximized {window.title}")
            except Exception:
                print(f"ERROR IN MAXIMIZING {window.title}")
            sleep(0.3)
            if title_ending is not None:
                check_active(title_ending=title_ending)
                print("Recurse")
            elif title == "Roblox" and window.height != screen_height:
                while window.height != screen_height:
                    pydirectinput.press("f11")
                    print("Maximizing window with F11")
                    sleep(0.3)
                check_active(title)