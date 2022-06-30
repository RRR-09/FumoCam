import json
from asyncio import sleep as async_sleep
from time import sleep, time
from traceback import format_exc
from typing import Dict, Tuple, Union

import cv2 as cv
import numpy as np
import pytesseract
from requests import get
from selenium import webdriver

from actions import respawn_character, send_chat
from commands import ACFG, CFG
from config import OBS, ActionQueueItem
from navpoints import (  # TODO: Make this better/scalable
    comedy_to_main,
    main_to_classic,
    main_to_classic_fix_bright,
    main_to_ratcade,
    main_to_shrimp_tree,
    main_to_train,
    main_to_treehouse,
    treehouse_to_main,
)
from spawn_detection import spawn_detection_main
from utilities import (
    check_active,
    do_crash_check,
    is_process_running,
    kill_process,
    log,
    log_process,
    notify_admin,
    output_log,
    read_output_log,
    take_screenshot_binary,
)

pytesseract.pytesseract.tesseract_cmd = CFG.pytesseract_path


async def force_get_best_server() -> str:
    best_server = None
    attempts = 0
    log("Attempting to find best server to join...")
    while True:
        best_server = await get_best_server()
        if best_server:
            break
        attempts += 1
        log(f"Attempt #{attempts} to find best server failed, retrying...")
        await async_sleep(5)
    return best_server["id"]


async def check_if_should_change_servers(
    original_current_server_id: str = "N/A",
) -> Tuple[bool, str]:
    current_server_id = (
        "" if original_current_server_id == "N/A" else original_current_server_id
    )
    current_server_playing = 0
    highest_player_server_playing = 0

    log("Querying Roblox API for server list")
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public"
    try:
        response = get(url, timeout=10)
    except Exception:
        return False, "[WARN] Could not poll Roblox servers. Is Roblox down?"
    if response.status_code == 200:
        log("Finding best server and comparing to current...")

        response_result = response.json()
        servers = response_result["data"]
        if current_server_id == "N/A":
            current_server_id = ""
        for server in servers:
            server_id = server.get("id", "undefined")
            if server.get("playerTokens") is None:
                server_playing = -1
            else:
                server_playing = len(server["playerTokens"])
            if server_id == "undefined" or server_playing == -1:
                notify_admin(
                    f"Handled Error in `check_if_should_change_servers`\nServers:\n`{servers}`\nProblem:\n`{server}`"
                )
                continue

            if current_server_id == server_id:
                current_server_id = server_id
                current_server_playing = server_playing
            elif (
                "playerTokens" in server
                and server_playing > highest_player_server_playing
            ):
                highest_player_server_playing = server_playing
        log("")
        if current_server_id == "" or current_server_id == "undefined":
            if highest_player_server_playing == 0:
                return False, "[WARN] Could not poll Roblox servers. Is Roblox down?"
            return_message = (
                f"[WARN] Could not find FumoCam. Are we in a server?\n"
                f"Original Server ID: {original_current_server_id}\n"
                f"Detected Server ID: {current_server_id}"
            )
            return True, return_message
        elif (
            current_server_playing < CFG.player_switch_cap
            and (current_server_playing + CFG.player_difference_to_switch)
            < highest_player_server_playing
        ):
            difference = highest_player_server_playing - current_server_playing
            return (
                True,
                f"[WARN] There is a server with {difference} more players online.",
            )
        else:
            return False, ""
    return False, "[WARN] Could not poll Roblox servers. Is Roblox down?"


async def get_current_server_id(game_id: int = CFG.game_id) -> str:
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{game_id}/servers/Public"
    try:
        response = get(url, timeout=10)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        if len(servers) == 0:
            print("No servers found")
            return "ERROR"
        for server in servers:
            if CFG.player_id in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


async def check_for_better_server():
    last_check_time = time()
    output_log("last_check_for_better_server", last_check_time)
    previous_status_text = read_output_log("change_server_status_text")
    output_log("change_server_status_text", "")

    log_process("Checking for better server")
    current_server_id = await get_current_server_id()
    if current_server_id == "ERROR":
        for i in range(CFG.max_attempts_better_server):
            log_process(
                f"Attempt {i+1}/{CFG.max_attempts_better_server} failed! Retrying better server check..."
            )
            await async_sleep(10)
            current_server_id = await get_current_server_id()
            if current_server_id != "ERROR":
                break
    if current_server_id == "ERROR":
        log_process(
            f"Failed to connect to Roblox API {CFG.max_attempts_better_server} times! Skipping..."
        )
        await async_sleep(5)
        log_process("")
        return True
    if current_server_id == "N/A":
        for id in list(CFG.game_ids_other.keys()):
            current_server_id == await get_current_server_id(id)
            if current_server_id != "N/A":
                break
        if current_server_id == "N/A":
            log_process("Could not find FumoCam in any servers")
            await CFG.add_action_queue(ActionQueueItem("handle_crash"))
            return False
        else:
            log_process("")
            log("")
            return True
    (
        should_change_servers,
        change_server_status_text,
    ) = await check_if_should_change_servers(current_server_id)

    log(change_server_status_text)
    output_log("change_server_status_text", change_server_status_text)

    if not should_change_servers:
        log("PASS! Current server has sufficient players")
        log("")
        log_process("")
        return True
    elif previous_status_text != change_server_status_text:
        if "Could not find FumoCam" in change_server_status_text:
            for attempt in range(CFG.max_attempts_better_server):
                log(f"Rechecking (attempt {attempt+1}/{CFG.max_attempts_better_server}")
                current_server_id = await get_current_server_id()
                while current_server_id == "":
                    log_process("Retrying get current server check")
                    await async_sleep(5)
                    current_server_id = await get_current_server_id()
                (
                    should_change_servers,
                    change_server_status_text,
                ) = await check_if_should_change_servers(current_server_id)
                if "Could not find FumoCam" not in change_server_status_text:
                    break
            if should_change_servers:
                notify_admin(change_server_status_text)
                await CFG.add_action_queue(ActionQueueItem("handle_join_new_server"))
        else:
            await CFG.add_action_queue(ActionQueueItem("handle_join_new_server"))
    log("")
    log_process("")


async def open_roblox_with_selenium_browser(js_code: str) -> bool:
    log("Opening Roblox via Browser...")
    try:
        with open(CFG.browser_cookies_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
    except FileNotFoundError:
        print("COOKIES PATH NOT FOUND, INITIALIZE WITH TEST FIRST")
        log("")
        return False

    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CFG.browser_profile_path}")
    driver = webdriver.Chrome(
        options=options, executable_path=str(CFG.browser_driver_path)
    )
    driver.get(CFG.game_instances_url)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception:
            print(f"ERROR ADDING COOKIE: \n{cookie}\n")

    driver.refresh()
    driver.execute_script(js_code)

    sleep_time = 0.25
    success = False
    log("Verifying Roblox has opened...")
    for _ in range(int(CFG.max_seconds_browser_launch / sleep_time)):
        crashed = await do_crash_check(do_notify=False)
        active = is_process_running(CFG.game_executable_name)
        if not crashed and active:
            success = True
            break
        await async_sleep(sleep_time)
    try:
        driver.quit()
        kill_process(CFG.browser_driver_executable_name)
        kill_process(CFG.browser_executable_name)
    except Exception:
        print(format_exc())

    if not success:
        log("Failed to launch game. Notifying Dev...")
        notify_admin("Failed to launch game")
        await async_sleep(5)
        log("")
        return False
    log("")
    return True


async def join_target_server(instance_id: int):
    join_js_code = (
        f'Roblox.GameLauncher.joinGameInstance({CFG.game_id}, "{instance_id}")'
    )
    success = await open_roblox_with_selenium_browser(join_js_code)
    return success


async def get_best_server(get_worst: bool = False) -> Dict:
    server_obj = {
        "id": "",
        "maxPlayers": 100,
        "playerTokens": [] if not get_worst else [0] * 100,
        "fps": 59,
        "ping": 100,
    }
    best_server = server_obj
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public"
    response = get(url, timeout=10)
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if "playerTokens" in server:
                best_server_player_tokens = best_server.get("playerTokens", [])
                assert isinstance(best_server_player_tokens, list)  # mypy fix
                if (not get_worst) and len(server["playerTokens"]) > len(
                    best_server_player_tokens
                ):
                    best_server = server
                if get_worst and len(server["playerTokens"]) < len(
                    best_server_player_tokens
                ):
                    best_server = server
    if best_server == server_obj:
        return {}
    return best_server


async def check_character_menu(is_open):
    # Check for either a known character visible on first spawn, or our desired character
    # One of those two should always be visible on character select between routines
    print("check_character_menu")
    open_status_initial = await ocr_for_character(
        CFG.character_select_initial, click_option=False
    )
    print(f"open_status_initial: {open_status_initial}")
    if open_status_initial != is_open:
        open_status_other = await ocr_for_character(
            CFG.character_select_desired, click_option=False
        )
        print(f"open_status_other: {open_status_other}")
        return open_status_other == is_open

    return open_status_initial == is_open


async def click_character_select_button(check_open_state: Union[bool, None] = None):
    await async_sleep(0.5)

    button_x, button_y = (
        CFG.character_select_button_position["x"],
        CFG.character_select_button_position["y"],
    )

    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()

    if check_open_state is not None:
        log(
            f"Checking that character select is {'open' if check_open_state else 'closed'}"
        )
        await async_sleep(2)
        success = False
        for _ in range(CFG.character_select_max_close_attempts):
            if await check_character_menu(check_open_state):
                success = True
                break
            else:
                ACFG.moveMouseAbsolute(x=button_x, y=button_y)
                ACFG.left_click()

        if not success:
            log("Unable to toggle character menu!\nNotifying dev...")
            notify_admin(
                "Failed to find toggle character menu in `click_character_select_button` loop"
            )
            sleep(2)
        log("")
    else:
        await async_sleep(0.5)


async def ocr_for_character(character: str = "", click_option: bool = True) -> bool:
    desired_character = (
        CFG.character_select_desired.lower() if not character else character.lower()
    )

    await async_sleep(0.5)

    ocr_data = {}
    last_ocr_text = None
    times_no_movement = 0
    found_character = False
    scroll_amount = 0
    for attempts in range(CFG.character_select_max_scroll_attempts):
        if click_option:
            log(
                f"Scanning list for '{desired_character.capitalize()}'"
                f" ({attempts}/{CFG.character_select_max_scroll_attempts})"
            )
        for _ in range(CFG.character_select_scan_attempts):  # Attempt multiple OCRs
            screenshot = np.array(await take_screenshot_binary(CFG.window_character))

            gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
            gray, img_bin = cv.threshold(gray, 240, 255, cv.THRESH_BINARY)
            gray = cv.bitwise_not(img_bin)
            kernel = np.ones((2, 1), np.uint8)
            img = cv.erode(gray, kernel, iterations=1)
            img = cv.dilate(img, kernel, iterations=1)

            ocr_data = pytesseract.image_to_data(
                img, config="--oem 1", output_type=pytesseract.Output.DICT
            )
            ocr_data["text"] = [word.lower() for word in ocr_data["text"]]
            print(ocr_data["text"])
            for entry in ocr_data["text"]:
                if desired_character in entry:
                    if click_option:
                        found_character = True
                        break
                    else:
                        return True
            if found_character:
                break
            sleep(0.1)

        if click_option and found_character:
            break
        elif not click_option and not found_character:
            return False  # Do not scroll

        if last_ocr_text == ocr_data["text"]:
            times_no_movement += 1
        else:
            times_no_movement = 0
            last_ocr_text = ocr_data["text"]

        if times_no_movement > 3:
            break  # We reached the bottom of the list, OCR isnt changing

        ACFG.scrollMouse(1, down=True)
        scroll_amount += 1
        sleep(0.4)

    if not found_character:
        if click_option:
            log(
                f"Failed to find '{desired_character.capitalize()}'.\n Notifying Dev..."
            )
            notify_admin(f"Failed to find `{desired_character}`")
            sleep(5)
        return False

    # We found the character, lets click it
    ocr_index = ocr_data["text"].index(desired_character)
    desired_character_height = int(
        ocr_data["top"][ocr_index] + (ocr_data["height"][ocr_index] / 2)
    )
    desired_character_height += CFG.window_character["top"]
    with open(OBS.output_folder / "character_select.json", "w") as f:
        json.dump(
            {
                "scroll_amount": scroll_amount,
                "desired_character_height": desired_character_height,
            },
            f,
        )

    CFG.character_select_screen_height_to_click = desired_character_height

    CFG.character_select_scroll_down_amount = scroll_amount
    ACFG.moveMouseAbsolute(
        x=CFG.screen_res["center_x"], y=int(desired_character_height)
    )
    sleep(0.5)
    ACFG.left_click()
    sleep(0.5)
    return True


async def click_character_in_menu(click_random: bool = False):
    character_name = (
        CFG.character_select_desired if not click_random else "a random character"
    )
    log(f"Clicking {character_name}")

    button_x, button_y = (
        round(CFG.screen_res["width"] * 0.5),
        CFG.character_select_screen_height_to_click,
    )
    if click_random:
        button_y -= int(CFG.screen_res["height"] * CFG.respawn_character_select_offset)
    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()
    await async_sleep(0.5)


async def change_characters(respawn: bool = False):
    await check_active()
    await async_sleep(1)
    log("Opening character select")

    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min_cv:
        ACFG.zoom("o", CFG.zoom_out_ui_cv)
        need_zoom_adjust = True

    await click_character_select_button(check_open_state=True)
    sleep(1)
    if respawn:
        await click_character_in_menu(click_random=True)
        respawn_delay = 12
        log(
            f"Waiting for {respawn_delay} seconds (or else clicking our character won't work)"
        )
        await async_sleep(respawn_delay)
        await click_character_in_menu()
    else:
        print("Beginning scroll")
        ACFG.moveMouseAbsolute(
            x=int(CFG.character_select_scroll_position["x"]),
            y=int(CFG.character_select_scroll_position["y"]),
        )
        ACFG.mouse_alt_tab()
        await ocr_for_character()
    sleep(1)
    await async_sleep(1)  # I have no idea what causes less errors
    log("Closing character select")
    await async_sleep(0.5)
    sleep(0.5)
    await click_character_select_button(check_open_state=False)
    sleep(1)
    await async_sleep(0.5)
    ACFG.resetMouse()
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)


async def check_ui_loaded():
    screenshot = np.array(await take_screenshot_binary(CFG.window_ui_loaded))
    screenshot = cv.cvtColor(screenshot, cv.COLOR_RGBA2RGB)

    color_threshold = cv.inRange(screenshot, (236, 235, 253), (255, 255, 255))
    screenshot[color_threshold > 0] = (255, 255, 255)

    white_pixels = np.sum(screenshot == 255)
    non_white_pixels = np.sum(screenshot != 255)
    total_pixels = white_pixels + non_white_pixels
    percentage = white_pixels / total_pixels
    ui_loaded = percentage > 0.7
    return ui_loaded


async def check_if_game_loaded() -> bool:
    game_loaded = False
    log("Loading into game")

    for attempt in range(CFG.max_attempts_game_loaded):
        if await check_ui_loaded():
            game_loaded = True
            break
        log(f"Loading into game (Check #{attempt}/{CFG.max_attempts_game_loaded})")
        await async_sleep(1)

    if not game_loaded:
        log("Failed to load into game.")
        notify_admin("Failed to load into game")
        await async_sleep(5)
        await CFG.add_action_queue(ActionQueueItem("handle_crash"))
        log("")
        return False
    log("")
    return True


async def server_spawn() -> bool:
    game_loaded = await check_if_game_loaded()
    if not game_loaded:
        return False

    if CFG.disable_collisions_on_spawn:
        CFG.collisions_disabled = False
        await toggle_collisions()

    await change_characters()

    ACFG.resetMouse()

    await auto_nav("shrimp", do_checks=False)

    return True


async def handle_join_new_server(crash=False):
    CFG.crashed = True  # Just in case
    process_name = "Automatic Relocation System"
    action = "Detected more optimal server. Relocating."
    if crash:
        process_name = "Automatic Crash Recovery"
        action = "Detected Roblox Crash. Recovering."
    log_process(process_name)
    log(action)
    kill_process(force=True)
    server_id = await force_get_best_server()
    await async_sleep(1)

    log_process(f"{process_name} - Joining Server")
    success = await join_target_server(server_id)
    if not success:
        return False
    output_log("change_server_status_text", "")

    log_process(f"{process_name} - Handling Spawn")
    if not await server_spawn():
        return False

    log_process("")
    log("Complete. Please use '!dev Error' if we're not in-game.")
    await async_sleep(5)
    CFG.crashed = False
    log_process("")
    log("")


async def auto_nav(
    location: str, do_checks: bool = True, slow_spawn_detect: bool = True
):
    log_process("AutoNav")
    if do_checks:
        await check_active(force_fullscreen=False)
        await async_sleep(0.5)
        location_name = CFG.nav_locations.get(location, {}).get("name", "ERROR")
        if location_name == "fixbright":
            location_name = "Classic Portal, to fix screen brightness"
        await send_chat(f"[AutoNavigating to {location_name}!]")
        if not CFG.collisions_disabled:
            log("Disabling collisions")
            await toggle_collisions()
            await async_sleep(0.5)
        await async_sleep(1)
        log("Respawning")
        await respawn_character(notify_chat=False)
        await async_sleep(7)
    log("Zooming out to full scale")
    ACFG.zoom(zoom_direction_key="o", amount=105)

    spawn = spawn_detection_main(CFG.resources_path, slow=slow_spawn_detect)
    if spawn == "ERROR":
        log("Failed to detect spawn!\n Notifying Dev...")
        notify_admin("Failed to find spawn in `auto_nav`")
        sleep(5)
        return

    if spawn == "comedy_machine":
        comedy_to_main()
    elif spawn == "tree_house":
        treehouse_to_main()
    await async_sleep(1)
    if location == "shrimp":
        main_to_shrimp_tree()
    elif location == "ratcade":
        main_to_ratcade()
    elif location == "train":
        main_to_train()
    elif location == "classic":
        main_to_classic()
    elif location == "treehouse":
        main_to_treehouse()
    elif location == "fixbright":
        main_to_classic_fix_bright()
    log("Zooming in to normal scale")
    default_zoom_in_amount = CFG.zoom_max - CFG.zoom_default
    zoom_in_amount = CFG.nav_post_zoom_in.get(location, default_zoom_in_amount)
    ACFG.zoom(zoom_direction_key="i", amount=zoom_in_amount)
    log(
        f"Complete! This is experimental, so please re-run \n'!nav {location}' if it didn't work."
    )
    await async_sleep(3)


async def check_settings_menu(is_open):
    open_status = await ocr_for_settings(
        CFG.settings_menu_grief_text, click_option=False
    )
    return open_status == is_open


async def click_settings_button(check_open_state: Union[bool, None] = None) -> bool:
    await async_sleep(0.5)

    # Bottom center of screen
    button_x, button_y = (
        CFG.settings_button_position["x"],
        CFG.settings_button_position["y"],
    )

    ACFG.moveMouseAbsolute(x=button_x, y=button_y)
    ACFG.left_click()

    if check_open_state is not None:
        log(
            f"Checking that settings menu is {'open' if check_open_state else 'closed'}"
        )
        await async_sleep(2)
        success = False
        for i in range(CFG.settings_menu_max_click_attempts):
            settings_menu_at_desired = await check_settings_menu(check_open_state)
            if settings_menu_at_desired:
                success = True
                break
            else:
                ACFG.moveMouseAbsolute(x=button_x, y=button_y)
                ACFG.left_click()
                await async_sleep(2)

        if not success:
            log("Unable to toggle settings menu!")
            await async_sleep(2)
        log("")
    else:
        await async_sleep(0.5)
    return True


async def ocr_for_settings(option: str = "", click_option: bool = True) -> bool:
    desired_option = (CFG.settings_menu_grief_text if not option else option).lower()
    desired_label = (CFG.settings_menu_grief_label if not option else option).lower()

    ocr_data = {}
    found_option = False
    for attempts in range(CFG.settings_menu_ocr_max_attempts):  # Attempt multiple OCRs
        if not click_option:
            log(
                f"Finding '{desired_label.capitalize()}' (Attempt #{attempts}/{CFG.settings_menu_ocr_max_attempts})"
            )
        screenshot = np.array(await take_screenshot_binary(CFG.window_settings))

        menu_green = {
            "upper_bgra": np.array([212, 255, 158, 255]),
            "lower_bgra": np.array([163, 196, 133, 255]),
        }
        green_mask = cv.inRange(
            screenshot, menu_green["lower_bgra"], menu_green["upper_bgra"]
        )
        screenshot[green_mask > 0] = (255, 255, 255, 255)

        menu_red = {
            "upper_bgra": np.array([79, 79, 255, 255]),
            "lower_bgra": np.array([63, 63, 214, 255]),
        }
        red_mask = cv.inRange(
            screenshot, menu_red["lower_bgra"], menu_red["upper_bgra"]
        )
        screenshot[red_mask > 0] = (255, 255, 255, 255)

        gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)  # PyTesseract
        _, thresh = cv.threshold(gray, 240, 255, cv.THRESH_BINARY)
        thresh_not = cv.bitwise_not(thresh)
        kernel = np.ones((2, 1), np.uint8)
        img = cv.erode(thresh_not, kernel, iterations=1)
        img = cv.dilate(img, kernel, iterations=1)

        ocr_data = pytesseract.image_to_data(
            img, config="--oem 1", output_type=pytesseract.Output.DICT
        )
        ocr_data["text"] = [word.lower() for word in ocr_data["text"]]
        print(ocr_data["text"])
        for entry in ocr_data["text"]:
            if desired_option in entry:
                desired_option = entry
                if click_option:
                    log("Found option, clicking")
                    found_option = True
                    break
                else:
                    return True
        if found_option:
            break
        await async_sleep(0.25)

    if not found_option:
        if click_option:
            log(f"Failed to find '{desired_label.capitalize()}'.\n Notifying Dev...")
            notify_admin(f"Failed to find `{desired_option}`")
            await async_sleep(5)
        return False
    else:
        # We found the option
        print(ocr_data)
        ocr_index = ocr_data["text"].index(desired_option)

        option_top = ocr_data["top"][ocr_index]
        option_y_center = ocr_data["height"][ocr_index] / 2
        option_y_pos = option_top + option_y_center
        # The top-offset of our capture window + the found pos of the option
        desired_option_y = int(CFG.window_settings["top"] + option_y_pos)

        option_left = ocr_data["left"][ocr_index]
        option_x_center = ocr_data["width"][ocr_index] / 2
        option_x_pos = option_left + option_x_center
        # The left-offset of our capture window + the found pos of the option
        desired_option_x = int(CFG.window_settings["left"] + option_x_pos)

    # Click the option
    ACFG.moveMouseAbsolute(x=int(desired_option_x), y=int(desired_option_y))
    await async_sleep(0.5)
    ACFG.left_click()
    await async_sleep(0.5)
    return True


async def toggle_collisions() -> bool:
    log_process(
        f"{'Enabling' if CFG.collisions_disabled else 'Disabling'} Grief Collisions"
    )
    log("Opening Settings")
    await check_active(force_fullscreen=False)
    await async_sleep(1)

    need_zoom_adjust = False
    if CFG.zoom_level < CFG.zoom_ui_min_cv:
        ACFG.zoom("o", CFG.zoom_out_ui_cv)
        need_zoom_adjust = True

    if not await click_settings_button(check_open_state=True):
        notify_admin("Failed to open settings")
        log("")
        log_process("")
        if need_zoom_adjust:
            ACFG.zoom("i", CFG.zoom_out_ui_cv)
        return False

    log(f"Finding {CFG.settings_menu_grief_label} option")
    await async_sleep(1)
    if not await ocr_for_settings():
        notify_admin("Failed to click settings option")
        log("")
        log_process("")
        if need_zoom_adjust:
            ACFG.zoom("i", CFG.zoom_out_ui_cv)
        return False

    CFG.collisions_disabled = not (CFG.collisions_disabled)
    collisions_msg = (
        "" if CFG.collisions_disabled else "[WARN] Griefing/Collisions enabled!"
    )
    output_log("collisions", collisions_msg)

    log("Closing Settings")
    await async_sleep(0.25)
    if not await click_settings_button(check_open_state=False):
        notify_admin("Failed to close settings")
        log("")
        log_process("")
        if need_zoom_adjust:
            ACFG.zoom("i", CFG.zoom_out_ui_cv)
        return False
    log("")
    log_process("")
    ACFG.resetMouse()
    if need_zoom_adjust:
        ACFG.zoom("i", CFG.zoom_out_ui_cv)
    return True


async def force_respawn_character():
    await check_active()
    await async_sleep(0.5)
    log_process("Force-Respawning")
    await send_chat("[Respawning!]")
    await change_characters(respawn=True)
    log_process("")


if __name__ == "__main__":
    import asyncio

    async def test():
        await check_active(force_fullscreen=False)
        sleep(0.5)
        await auto_nav("treehouse", do_checks=False, slow_spawn_detect=False)

    asyncio.get_event_loop().run_until_complete(test())
