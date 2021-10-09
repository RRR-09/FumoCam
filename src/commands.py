from actions import *
from health import change_characters


def click_sit_button():
    log_process("Clicking Sit button")
    check_active()
    sleep(0.5)
    Beep(150, 100)
    try:
        ratio_x, ratio_y = CFG.sit_button_position
        x = round(SCREEN_RES["width"] * ratio_x)
        y = round(SCREEN_RES["height"] * ratio_y)
        pydirectinput.moveTo(x, y)
        alt_tab_click()
        Beep(100, 50)
    except Exception:
        log("Could not find sit button on screen?")
        sleep(5)
    log_process("")


def respawn_character():
    check_active()
    log_process("Respawning")
    send_chat("[Respawning!]")
    change_characters(respawn=True)
    log_process("")


def zoom_camera(zoom_obj):
    zoom_direction = zoom_obj["zoom_camera_direction"]
    zoom_time = zoom_obj["zoom_camera_time"]
    check_active()
    sleep(0.5)
    pydirectinput.keyDown(zoom_direction)
    sleep(zoom_time)
    pydirectinput.keyUp(zoom_direction)
    sleep(0.5)
