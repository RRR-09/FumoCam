from actions import *
from health import change_characters


async def click_sit_button():
    log_process("Clicking Sit button")
    await check_active()
    try:
        ratio_x, ratio_y = CFG.sit_button_position
        x = round(SCREEN_RES["width"] * ratio_x)
        y = round(SCREEN_RES["height"] * ratio_y)
        pydirectinput.moveTo(x, y)
        await alt_tab_click()
    except Exception:
        log("Could not find sit button on screen?")
        await async_sleep(5)
    log_process("")


async def respawn_character():
    await check_active()
    await async_sleep(0.5)
    log_process("Respawning")
    await send_chat("[Respawning!]")
    await change_characters(respawn=True)
    log_process("")


async def zoom_camera(zoom_obj):
    zoom_direction = zoom_obj["zoom_camera_direction"]
    zoom_time = zoom_obj["zoom_camera_time"]
    await check_active()
    pydirectinput.keyDown(zoom_direction)
    await async_sleep(zoom_time/4)
    pydirectinput.keyUp(zoom_direction)
