from actions import *
from health import change_characters


async def click_sit_button():
    log_process("Clicking Sit button")
    await check_active()
    
    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min:
        ACFG.zoom("o", CFG.zoom_out_ui)
        need_zoom_adjust = True
    
    try:
        ratio_x, ratio_y = CFG.sit_button_position
        x = round(SCREEN_RES["width"] * ratio_x)
        y = round(SCREEN_RES["height"] * ratio_y)
        ACFG.moveMouseAbsolute(x=x, y=y)
        ACFG.left_click()
        await async_sleep(0.25)
        ACFG.resetMouse()
    except Exception:
        log("Could not find sit button on screen?")
        await async_sleep(5)
        log("")
    
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)
    log_process("")


async def force_respawn_character():
    await check_active()
    await async_sleep(0.5)
    log_process("Force-Respawning")
    await send_chat("[Respawning!]")
    await change_characters(respawn=True)
    log_process("")
