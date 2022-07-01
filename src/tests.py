import asyncio
from asyncio import sleep as async_sleep
from time import sleep

import cv2 as cv
import numpy as np
import pyautogui

from actions import mute_toggle, respawn_character
from arduino_integration import ACFG, CFG
from health import (
    change_characters,
    check_character_menu,
    check_for_better_server,
    check_if_game_loaded,
    click_character_in_menu,
    click_character_select_button,
    force_respawn_character,
    get_best_server,
    get_current_server_id,
    join_target_server,
    ocr_for_settings,
    toggle_collisions,
)
from twitch_integration import twitch_main
from utilities import check_active, kill_process, take_screenshot_binary_blocking


def test_turn_camera(direction="left", amount=45):
    async def do_test(direction, amount):
        await check_active()
        await async_sleep(1)
        ACFG.look(direction, amount)

    asyncio.get_event_loop().run_until_complete(do_test(direction, amount))


def test_turn_camera_precision(direction="left", amount=45):
    async def do_test(direction, amount):
        await check_active()
        # Main spawn calibration
        # ACFG.precision_look("right", 7, raw=True)

        # Treehouse spawn calibration
        # ACFG.precision_look("left", 1314, raw=True)

        # Comedy spawn calibration
        # ACFG.precision_look("right", 469, raw=True)

    asyncio.get_event_loop().run_until_complete(do_test(direction, amount))


def test_pitch(direction="left", amount=45):
    async def do_test(direction, amount):
        await check_active()
        ACFG.pitch(179, up=True)

    asyncio.get_event_loop().run_until_complete(do_test(direction, amount))


def test_move(direction="w", amount=10):
    async def do_test(direction, amount):
        await check_active()
        await async_sleep(1)
        ACFG.move(direction, amount)

    asyncio.get_event_loop().run_until_complete(do_test(direction, amount))


def test_character_select(
    click_mouse=True,
):  # Character select OCR still needs work; guess coordinates and test
    async def do_test(click_mouse=True):
        await check_active()
        await async_sleep(1)
        await click_character_in_menu(click_mouse=click_mouse)

    asyncio.get_event_loop().run_until_complete(do_test(click_mouse=click_mouse))


def test_character_select_full(click_mouse=True):
    async def do_test(click_mouse=True):
        await check_active()
        await async_sleep(1)
        await change_characters()

    asyncio.get_event_loop().run_until_complete(do_test(click_mouse=click_mouse))


def test_ocr_settings():
    async def test():
        await check_active(force_fullscreen=False)
        sleep(1)
        await ocr_for_settings(click_option=False)

    asyncio.get_event_loop().run_until_complete(test())


def test_ocr_character():
    async def test():
        await check_active(force_fullscreen=False)
        sleep(1)
        # await ocr_for_character(click_option=False)
        print(await check_character_menu(True))

    asyncio.get_event_loop().run_until_complete(test())


def test_character_button():
    async def test():
        await check_active(force_fullscreen=False)
        sleep(1)
        await click_character_select_button(True)

    asyncio.get_event_loop().run_until_complete(test())


def test_toggle_collisions():
    async def do_test():
        await check_active()
        await async_sleep(1)
        await toggle_collisions()

    asyncio.get_event_loop().run_until_complete(do_test())


def test_respawn(click_mouse=True):
    async def do_test(click_mouse=True):
        await check_active()
        await async_sleep(1)
        await respawn_character()

    asyncio.get_event_loop().run_until_complete(do_test(click_mouse=click_mouse))


def test_force_respawn():
    async def do_test():
        await check_active()
        await async_sleep(1)
        await force_respawn_character()

    asyncio.get_event_loop().run_until_complete(do_test())


def test_join_target_server():
    join_target_server("099cf062-e26f-4ace-b627-6ebfa2295270")


def test_get_cookies_for_browser():
    import json

    from selenium import webdriver

    print(
        "Login to your account in the brower that opens, come back to this screen, and press enter."
    )
    print("Press enter to start")
    input()

    driver = webdriver.Chrome(CFG.browser_driver_path)
    driver.get("https://www.roblox.com/games/6238705697/Become-Fumo")

    input("\n\n\nPress Enter to save cookies\n\n\n\n")

    with open(CFG.browser_cookies_path, "w", encoding="utf-8") as f:
        json.dump(driver.get_cookies(), f, ensure_ascii=False, indent=4)
    driver.quit()
    kill_process(CFG.browser_driver_executable_name)
    kill_process(CFG.browser_executable_name)

    print(
        f"\n\n\nCookies saved to {CFG.browser_cookies_path}, DO NOT SHARE THIS WITH ANYONE."
    )
    input("\nPress Enter to close.")


def test_loading_cookies_for_browser():
    import json

    from selenium import webdriver

    print(
        "If you completed test_get_cookies_for_browser, this should open a logged-in browser."
    )
    print("Press enter to start, and press enter again to terminate the browser.")
    input()

    with open(CFG.browser_cookies_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CFG.browser_profile_path}")
    driver = webdriver.Chrome(options=options, executable_path=CFG.browser_driver_path)
    driver.get(CFG.game_instances_url)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception:
            print(f"ERROR ADDING COOKIE: \n{cookie}\n")
    driver.refresh()
    script = """Roblox.GameLauncher.joinGameInstance(6238705697, "099cf062-e26f-4ace-b627-6ebfa2295270")"""
    driver.execute_script(script)
    input("\n\n\nPress Enter to close\n\n\n\n")
    driver.quit()

    kill_process(CFG.browser_driver_executable_name)
    kill_process(CFG.browser_executable_name)


def test_check_for_better_server():
    print(asyncio.get_event_loop().run_until_complete(check_for_better_server()))


def test_get_current_server_id():
    print(asyncio.get_event_loop().run_until_complete(get_current_server_id()))


def test_twitch():
    twitch_main()


def test_mute(mute=None):
    asyncio.get_event_loop().run_until_complete(mute_toggle(mute=mute))


def test_get_player_token():
    async def test():
        total_diffs = []
        print(
            "This will use log in to the least popular server in an attempt to get your token.\n"
            "If someone else joins before you do, it will be impossible to tell, so the program will retry.\n"
            "It's recommended to run this 2 or 3 times to make sure we deduced the right token."
        )
        input("Press enter to begin.")

        while True:
            server_before_join = await get_best_server(get_worst=True)
            print(server_before_join)
            print(f"[DEBUG] BEFORE:\n{server_before_join['playerTokens']}\n")
            await join_target_server(server_before_join["id"])
            game_loaded = await check_if_game_loaded()
            if not game_loaded:
                raise Exception("Could not load into game!")
            await async_sleep(1)
            server_after_join = await get_best_server(get_worst=True)

            if server_after_join["id"] != server_before_join["id"]:
                print("Ideal servers became different, retrying...")
                total_diffs = []
            else:
                print(f"[DEBUG] AFTER:\n{server_after_join['playerTokens']}\n")
                current_diffs = []
                for id in server_after_join["playerTokens"]:
                    if id not in server_before_join["playerTokens"]:
                        current_diffs.append(id)

                for id in total_diffs:
                    if id not in current_diffs:
                        total_diffs.remove(id)
                    else:
                        current_diffs.remove(id)

                total_diffs = current_diffs

            kill_process(force=True)
            print(f"[DEBUG] Diffs: {total_diffs}")
            if len(total_diffs) == 1:
                break
            wait_time = 20
            print(f"[DEBUG] Waiting {wait_time}s to avoid ratelimit/inaccuracy...")
            await async_sleep(wait_time)

        print(f'\n\n\n\n\nYOUR ID IS: "{total_diffs[0]}"')

    asyncio.get_event_loop().run_until_complete(test())


def test_window_area():
    async def test():
        await check_active(force_fullscreen=False)
        sleep(1)

        monitor = CFG.screen_res["mss_monitor"].copy()

        # SETTINGS
        # horizontal_offset = int(0.13 * CFG.screen_res["width"])
        # monitor["left"] += horizontal_offset
        # monitor["width"] -= horizontal_offset * 2
        # vertical_offset = int(0.15 * CFG.screen_res["height"])
        # monitor["top"] += vertical_offset
        # monitor["height"] -= vertical_offset * 2

        # CHARACTER SELECT
        # horizontal_offset = int(0.33 * CFG.screen_res["width"])
        # monitor["left"] += horizontal_offset
        # monitor["width"] -= horizontal_offset * 2
        # top_offset = int(0.31 * CFG.screen_res["height"])
        # monitor["top"] += top_offset
        # bottom_offset = int(0.14 * CFG.screen_res["height"])
        # monitor["height"] -= top_offset + bottom_offset

        # BACKPACK
        # horizontal_offset = int(0.14 * CFG.screen_res["width"])
        # monitor["left"] += horizontal_offset
        # monitor["width"] -= horizontal_offset * 2
        # vertical_offset = int(0.137 * CFG.screen_res["height"])
        # monitor["top"] += vertical_offset
        # monitor["height"] -= vertical_offset * 2

        # CHARACTER SELECT WHITESPACE
        horizontal_offset = int(CFG.screen_res["center_x"]) - 5
        monitor["left"] += horizontal_offset
        monitor["width"] -= horizontal_offset * 2
        vertical_offset = int(0.045 * CFG.screen_res["height"])
        monitor["top"] += vertical_offset
        monitor["height"] = vertical_offset + 2

        print(monitor)
        screenshot = np.array(take_screenshot_binary_blocking(monitor))
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGBA2RGB)

        color_threshold = cv.inRange(screenshot, (236, 235, 253), (255, 255, 255))
        screenshot[color_threshold > 0] = (255, 255, 255)

        white_pixels = np.sum(screenshot == 255)
        non_white_pixels = np.sum(screenshot != 255)
        total_pixels = white_pixels + non_white_pixels
        percentage = white_pixels / total_pixels
        ui_loaded = percentage > 0.7
        print(ui_loaded)

        cv.imshow("screen", screenshot)
        cv.imwrite("test_screenshot.jpg", screenshot)
        cv.waitKey(0)

    asyncio.get_event_loop().run_until_complete(test())


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    # If account banned
    test_get_cookies_for_browser()
    # test_character_select_full()
    # test_toggle_collisions()

    # test_pitch()
    # test_loading_cookies_for_browser()
    # test_get_player_token()

    # test_window_area()

    # test_mute(mute=True)

    # test_turn_camera(direction="right")
    # test_move()
    # sleep(5)
    # test_turn_camera("left")

    # test_get_cookies_for_browser()

    # test_twitch()
    # test_character_select()
    # test_character_select_full()
    # test_check_for_better_server()
    # test_character_select_full(click_mouse=True)
    # test_force_respawn()
    # test_toggle_collisions()
    # test_ocr_settings()
    # test_ocr_character()
    # test_character_button()

    # click_sit_button()
    # test_respawn()
    # test_join_target_server()
    # test_get_current_server_id()
    # error_log("test")
    # test_check_for_better_server()
