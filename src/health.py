from actions import *
from spawn_detection import main as cv_detect_spawn
from selenium import webdriver
import json


async def force_get_best_server():
    found_best_server = False
    while not found_best_server:
        found_best_server = await get_best_server()
        if found_best_server:
            break
        await async_sleep(5)
        log("Failed to find best server, retrying...")
    return found_best_server["id"]


async def check_if_should_change_servers(current_server_id="N/A"):
    original_current_server_id = current_server_id
    log("Querying Roblox API for server list")
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        return False, f"[WARN] Could not poll Roblox servers. Is Roblox down?"
    if response.status_code == 200:
        log("Finding best server and comparing to current...")

        response_result = response.json()
        servers = response_result["data"]
        highest_player_server = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        if current_server_id == "N/A":
            current_server = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        else:
            current_server = {"id": current_server_id, "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        for server in servers:
            if current_server["id"] == server["id"]:
                current_server = server
            elif "playing" in server and server["playing"] > highest_player_server["playing"]:
                highest_player_server = server
        log("")
        if current_server["id"] == "" or current_server["id"] == "undefined":
            if highest_player_server["playing"] == 0:
                return False, f"[WARN] Could not poll Roblox servers. Is Roblox down?"
            print(servers)
            return_message = f"[WARN] Could not find FumoCam. Are we in a server?\n" \
                             f"Original Server ID: {original_current_server_id}\n" \
                             f"Detected Server ID: {current_server['id']}"
            return True, return_message
        elif current_server["playing"] + 5 < highest_player_server["playing"]:
            difference = highest_player_server["playing"] - current_server["playing"]
            return True, f"[WARN] There is a server with {difference} more players online."
        else:
            return False, ""
    return False, f"[WARN] Could not poll Roblox servers. Is Roblox down?"


async def check_if_in_nil_world():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{CFG.game_id_nil}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if CFG.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


async def check_if_in_hinamizawa_world():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{CFG.game_id_hinamizawa}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if CFG.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


async def get_current_server_id():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        print(response_result)
        servers = response_result["data"]
        if len(servers) == 0:
            return "ERROR"
        for server in servers:
            if CFG.player_token in server["playerTokens"]:
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
    while current_server_id == "ERROR":
        log_process("Failed! Retrying better server check")
        await async_sleep(5)
        current_server_id = await get_current_server_id()
    if current_server_id == "N/A":
        nil_world_id = await check_if_in_nil_world()
        hinamizawa_world_id = await check_if_in_hinamizawa_world()
        if nil_world_id == "N/A" and hinamizawa_world_id == "N/A":
            log_process("Could not find FumoCam in any servers")
            await CFG.add_action_queue("handle_crash")
            return False
        else:  # other world easter egg
            log("Successfully failed! Could not find FumoCam in the realms of the living.")
            Beep(60, 2000)
            log("S#c%e!s%u^l& f!i@e%! &o#l* ^o$ f!n& @u$o%a& *n !h# $e^l!s #f ^$e #i!i$g.")
            Beep(50, 2000)
            log("!#@%&!@%%^^& $!#@&%! &@#!* ^*$ @!$& @^$@%a& *$ !@# $#^%!@ #@ ^$% #@!%$#.")
            Beep(40, 2000)
            log_process("")
            log("")
            return True
    should_change_servers, change_server_status_text = await check_if_should_change_servers(current_server_id)
    log(change_server_status_text)
    output_log("change_server_status_text", change_server_status_text)
    if not should_change_servers:
        log("PASS! Current server has sufficient players")
        log("")
        log_process("")
        return True
    elif previous_status_text != change_server_status_text:
        if "Could not find FumoCam" in change_server_status_text:
            for i in range(2):
                log(f"Rechecking (attempt {i + 1}/3")
                current_server_id = await get_current_server_id()
                while current_server_id == "":
                    log_process("Retrying get current server check")
                    await async_sleep(5)
                    current_server_id = await get_current_server_id()
                should_change_servers, change_server_status_text = await check_if_should_change_servers(current_server_id)
                if "Could not find FumoCam" not in change_server_status_text:
                    break
            if should_change_servers:
                notify_admin(change_server_status_text)
                await CFG.add_action_queue("handle_join_new_server")
        else:
            await CFG.add_action_queue("handle_join_new_server")
    log("")
    log_process("")


async def open_roblox_with_selenium_browser(js_code):
    log("Opening Roblox via Browser...")
    Beep(40, 25)
    try:
        with open(CFG.browser_cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
    except FileNotFoundError:
        print("COOKIES PATH NOT FOUND, INITIALIZE WITH TEST FIRST")
        log("")
        return False
    
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CFG.browser_profile_path}")
    driver = webdriver.Chrome(options=options, executable_path=CFG.browser_driver_path)
    driver.get(CFG.game_instances_url)
    
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    driver.execute_script(js_code);
    
    sleep_time = 0.25
    success = False
    log("Verifying Roblox has opened...")
    for i in range(int(CFG.max_seconds_browser_launch/sleep_time)):
        crashed = await do_crash_check(do_notify=False)
        active = is_process_running(CFG.game_executable_name)
        if not crashed and active:
            success = True
            break
        await async_sleep(sleep_time)
        Beep(40, 25)
    try:
        driver.quit()       
        kill_process(CFG.browser_driver_executable_name)
        kill_process(CFG.browser_executable_name)
    except:
        print(format_exc())
        
    if not success:
        log("Failed to launch game. Notifying Dev...")
        notify_admin("Failed to launch game")
        await async_sleep(5)
        log("")
        return False
    log("")
    return True


async def join_target_server(instance_id):
    join_js_code = f"Roblox.GameLauncher.joinGameInstance({CFG.game_id}, \"{instance_id}\")"
    success = await open_roblox_with_selenium_browser(join_js_code)
    return success


async def get_best_server():
    server_obj = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
    highest_player_count_server = server_obj
    url = f"https://games.roblox.com/v1/games/{CFG.game_id}/servers/Public?sortOrder=Asc&limit=10"
    response = requests.get(url)
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            print(server)
            if "playing" in server and server["playing"] > highest_player_count_server["playing"]:
                highest_player_count_server = server
    if highest_player_count_server == server_obj:
        return False
    return highest_player_count_server


async def click_character_select_button():
    await async_sleep(0.5)
    #Beep(150, 100)
    button_x, button_y = await get_character_select_button_pos()
    pydirectinput.moveTo(button_x, button_y)
    await alt_tab_click()
    await async_sleep(0.5)
    #Beep(100, 50)


async def scroll_to_character_in_menu():
    await async_sleep(0.5)
    log(f"Scrolling down {CFG.character_select_scroll_down_amount} times")
    for i in range(CFG.character_select_scroll_down_amount):
        pyautogui.scroll(CFG.character_select_scroll_down_scale)
        Beep(40, 25)
        await async_sleep(CFG.character_select_scroll_speed)
    log("")


async def click_character_in_menu(click_mouse=True, click_random=False):
    character_name = "Momiji" if not click_random else "a random character"
    log(f"Clicking {character_name}")
    Beep(250, 100)
    button_x, button_y = round(pyautogui.size()[0] * 0.5), round(
        SCREEN_RES["height"] * CFG.character_select_screen_height_to_click)  # Toggle Collisions button
    if click_random:
        button_y += int(SCREEN_RES["height"]*CFG.respawn_character_select_offset)
    pydirectinput.moveTo(button_x, button_y)
    await alt_tab_click(click_mouse=click_mouse)
    Beep(100, 50)
    await async_sleep(0.5)


async def get_character_select_button_pos():
    character_select_button = None
    for i in range(CFG.max_attempts_character_selection):
        Beep(40, 50)
        try:
            print("TryingToFind")
            character_select_button = pyautogui.locateOnScreen(CFG.character_select_image_path,
                                                               grayscale=True,
                                                               confidence=0.9)  # , #region=character_select_range)
        except pyautogui.ImageNotFoundException:
            character_select_button = None
        if character_select_button is not None:
            character_select_button = pyautogui.center(character_select_button)
            break
        await async_sleep(1)
    return character_select_button


async def change_characters(respawn=False):
    await check_active()
    await async_sleep(1)
    log("Opening character select")
    await click_character_select_button()
    await async_sleep(0.5)
    if respawn:
        await click_character_in_menu(click_random=True)
        respawn_delay = 12
        log(f"Waiting for {respawn_delay} seconds (or else clicking our character won't work)")
        await async_sleep(respawn_delay)
    else:
        await scroll_to_character_in_menu()
    await click_character_in_menu()
    log("Closing character select")
    await click_character_select_button()


async def server_spawn():
    await async_sleep(5)
    log("Loading into game")
    if await get_character_select_button_pos() is None:
        log("Failed to load into game.")
        await async_sleep(5)
        notify_admin("Failed to load into game")
        await CFG.add_action_queue("handle_crash")
        return False
    await async_sleep(1)
    if CFG.disable_collisions_on_spawn:
        await toggle_collisions()
    await change_characters()
    pydirectinput.moveTo(1, 1)
    await alt_tab_click()
    return True


async def handle_join_new_server(crash=False):
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

    #log_process(f"{process_name} - Detecting Location")
    #cv_detect_spawn()

    log_process("")
    log("Complete. Please use '!dev Error' if we're not in-game.")
    await async_sleep(5)
    log_process("")
    log("")
