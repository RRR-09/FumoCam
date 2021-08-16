import math
import os
import random
import subprocess
import threading
import time
from time import sleep
from traceback import format_exc
import winsound

import irc.bot  # pip3.9 install irc
from mss import mss  # pip3.9 install mss
# multiprocess is a fork that uses Dill instead of Pickle (which caused exceptions)
import multiprocess  # pip3.9 install multiprocess
import pyautogui  # pip3.9 install pyautogui
import pydirectinput  # pip3.9 install pydirectinput
# pip3.9 install pygetwindow (allows additional functionality in pyautogui)
import requests  # pip3.9 install requests

import globals  # globals.py
import spawn_detection
screen_res = {  # todo: Don't use globals, make class-based
    "width": pyautogui.size()[0],
    "height": pyautogui.size()[1],
    "x_multi": pyautogui.size()[0] / 2560,
    "y_multi": pyautogui.size()[1] / 1440,
}

monitor_size = mss().monitors[0]

output_log = globals.output_log


def read_output_log(file_name):
    if not os.path.exists(globals.OBS.output_folder):
        return "ERROR: Path does not exist"
    file_path = os.path.join(globals.OBS.output_folder, f"{file_name}.txt")
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception:
        print(format_exc())
        return f"ERROR: {format_exc()}"


def take_screenshot():
    global monitor_size
    file_name = f"{time.time()}.png"
    with mss() as sct:
        check_active()
        sleep(0.25)
        sct.shot(mon=-1, output=file_name)
    return file_name


def kill_process(executable="RobloxPlayerBeta.exe", force=False):
    # todo: taskkill.exe can fail, how can we kill the thing that should kill? https://i.imgur.com/jd01ZOv.png
    process_call = ["taskkill"]
    if force:
        process_call.append("/F")
    process_call.append("/IM")
    process_call.append(executable)
    subprocess.call(process_call)


def force_get_best_server():
    found_best_server = False
    while not found_best_server:
        found_best_server = get_best_server()
        if found_best_server:
            break
        sleep(5)
        log("Failed to find best server, retrying...")
    return found_best_server["id"]


def twitch_main():   # todo: Move to seperate file
    username = globals.Twitch.username
    client_id = os.getenv("TWITCH_CLIENT_ID")
    token = os.getenv("TWITCH_MAIN_OAUTH")
    channel = globals.Twitch.channel_name
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


def handle_join_new_server(crash=False):
    process_name = "Automatic Relocation System"
    action = "Detected more optimal server. Relocating."
    if crash:
        process_name = "Automatic Crash Recovery"
        action = "Detected Roblox Crash. Recovering."
    log_process(process_name)
    log(action)
    cfg = globals.Roblox
    cfg.next_possible_teleport = 0
    kill_process(force=True)
    server_id = force_get_best_server()
    sleep(1)

    log_process(f"{process_name} - Joining Server")
    join_target_server(server_id)
    output_log("change_server_status_text", "")

    log_process(f"{process_name} - Handling Spawn")
    if not server_spawn():
        return False

    log_process(f"{process_name} - Detecting Location")
    spawn_detection.main()

    log_process(f"{process_name} - Hooking into Roblox")
    log("Establishing process connection...")
    load_exploit()

    log_process(f"{process_name} - Returning to Default Position")
    log("Initiating Teleport")
    teleport(cfg.current_location, no_log=True)

    log_process("")
    log("Complete. Please use '!dev Error' if not relocated properly.")
    sleep(10)
    log_process("")
    log("")


def do_crash_check():
    crashed = False
    for window in pyautogui.getAllWindows():
        if window.title == "Crash" or window.title == "Roblox Crash" or window.title == "Crashed":    
            crashed = True
            window.close()
    if crashed:
        notify_admin("Roblox Crash")
        globals.Roblox.action_queue.append("handle_crash")
    return crashed


def crash_check_loop():
    while True:
        crashed = do_crash_check()
        if crashed:
            globals.Roblox.action_queue.append("handle_crash")
            sleep(60)
        sleep(5)


def check_active(title="Roblox", title_ending=None):
    print("check")
    active_window = pyautogui.getActiveWindow()
    if active_window is not None:
        title_active = title_ending is None and active_window.title == title
        title_ending_active = title_ending is not None and active_window.title.endswith(title_ending)
        if title_active or title_ending_active:
            print(f"{active_window.title} already active")
            return
    for window in pyautogui.getAllWindows():
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
            elif title == "Roblox" and window.height != pyautogui.size()[1]:
                while window.height != pyautogui.size()[1]:
                    pydirectinput.press("f11")
                    print("Maximizing window with F11")
                    sleep(0.3)
                check_active(title)


def send_chat(message):
    check_active()
    pyautogui.press('/')
    sleep(0.1)
    for word in globals.Roblox.censored_words:  # todo: More effective censoring
        if word in message:
            message = message.replace(word, "*" * len(word))
    pyautogui.write(message)  # todo: investigate long messages only partially coming through
    sleep(0.5)
    pydirectinput.press('enter')


def do_anti_afk():
    check_active()
    sleep(0.5)
    pydirectinput.keyDown('left')
    sleep(0.75)
    pydirectinput.keyUp('left')
    sleep(1)
    pydirectinput.keyDown('right')
    sleep(1.5)
    pydirectinput.keyUp('right')
    sleep(1)
    pydirectinput.keyDown('left')
    sleep(0.65)
    pydirectinput.keyUp('left')


def do_anti_afk_advert():
    print("DoAdvert")
    for message in globals.Roblox.advertisement:
        send_chat(message)


def anti_afk():
    cfg = globals.Roblox
    seconds_in_minute = 60
    afk_minutes = 10
    delay_duration = seconds_in_minute * afk_minutes
    while True:
        sleep(delay_duration)
        cfg.action_queue.append("anti-afk")
        sleep(delay_duration)
        cfg.action_queue.append("anti-afk")
        sleep(delay_duration)
        cfg.action_queue.append("anti-afk")
        cfg.action_queue.append("anti-afk-advert")


def rel_coord(x, y):
    global screen_res
    return round(x * screen_res["x_multi"]), round(y * screen_res["y_multi"])


def toggle_collisions():
    global screen_res
    check_active()
    log("Opening Settings")
    sleep(0.5)
    winsound.Beep(150, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(screen_res["height"] * 0.95)  # Settings button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    winsound.Beep(100, 50)

    log("Toggling Collisions")
    sleep(0.5)
    winsound.Beep(150, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(
        screen_res["height"] * 0.40)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    winsound.Beep(100, 50)

    log("Closing Settings")
    sleep(0.25)
    winsound.Beep(150, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(
        screen_res["height"] * 0.30)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    sleep(0.25)
    winsound.Beep(100, 50)


def alt_tab_click(click_mouse=True): 
    """
    Even pydirectinput cant click normally.
    This is a work-around that actually clicks in the area the cursor was moved.
    """
    alt_tab_duration = 0.3
    pyautogui.hotkey('alt', 'tab')
    sleep(alt_tab_duration)
    pyautogui.hotkey('alt', 'tab')
    sleep(alt_tab_duration)
    if click_mouse:
        pydirectinput.mouseDown()
        pydirectinput.mouseUp()


def click_character_select_button():
    sleep(0.5)
    winsound.Beep(150, 100)
    button_x, button_y = get_character_select_button_pos()
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click()
    winsound.Beep(100, 50)


def click_character_in_menu(click_mouse=True):
    log("Scrolling to bottom of list")
    for i in range(18):
        pyautogui.scroll(-1)
        winsound.Beep(40, 25)
        sleep(0.05)
    log(f"Scrolling up {globals.Roblox.character_select_scroll_up_amount} times")
    for i in range(globals.Roblox.character_select_scroll_up_amount):
        pyautogui.scroll(1)
        winsound.Beep(40, 25)
        sleep(0.05)
    log("Clicking Momiji")
    winsound.Beep(250, 100)
    button_x, button_y = round(pyautogui.size()[0] * 0.5), round(
        screen_res["height"] * globals.Roblox.character_select_screen_height_to_click)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    alt_tab_click(click_mouse=click_mouse)
    winsound.Beep(100, 50)
    sleep(0.5)


def get_character_select_button_pos():
    character_select_button = None
    for i in range(globals.Roblox.max_attempts_character_selection):
        winsound.Beep(40, 50)
        try:
            print("TryingToFind")
            character_select_button = pyautogui.locateOnScreen(globals.Roblox.character_select_image_path,
                                                               grayscale=True,
                                                               confidence=0.9)  # , #region=character_select_range)
        except pyautogui.ImageNotFoundException:
            character_select_button = None
        if character_select_button is not None:
            character_select_button = pyautogui.center(character_select_button)
            break
        sleep(1)
    return character_select_button


def click_sit_button():
    log_process("Clicking Sit button")
    check_active()
    sleep(0.5)
    winsound.Beep(150, 100)
    try:
        ratio_x, ratio_y = globals.Roblox.sit_button_position
        x = round(screen_res["width"] * ratio_x)
        y = round(screen_res["height"] * ratio_y)
        pydirectinput.moveTo(x, y)
        alt_tab_click()
        winsound.Beep(100, 50)
    except Exception:
        log("Could not find sit button on screen?")
        sleep(5)
    log_process("")
    

def change_characters():
    check_active()
    sleep(1)
    log("Opening character select")
    click_character_select_button()
    click_character_in_menu()
    log("Closing character select")
    click_character_select_button()


def server_spawn():
    sleep(5)
    log("Loading into game")
    if get_character_select_button_pos() is None:
        log("Failed to load into game.")
        sleep(5)
        notify_admin("Failed to load into game")
        globals.Roblox.action_queue.append("handle_crash")
        return False
    if globals.Roblox.disable_collisions_on_spawn:
        toggle_collisions()
    change_characters()
    pydirectinput.moveTo(1, 1)
    alt_tab_click()
    return True


def run_javascript_in_browser(url, js_code, esc_before_entering):
    # todo: Move to selenium once I figure out how generate and use cookies in a reproducible+easy way
    executable_name = "chrome.exe"
    kill_process(executable_name, force=True)
    browser_path = os.path.join("C:\\", "Program Files (x86)", "Google", "Chrome", "Application", executable_name)
    if not os.path.exists(browser_path):
        browser_path = os.path.join("C:\\", "Program Files", "Google", "Chrome", "Application", executable_name)
    open_args = f"{url}"
    args = [browser_path, open_args]
    log("Launching Browser...")
    winsound.Beep(40, 25)
    log("Launched. Loading (8s)...")
    subprocess.Popen(args)
    sleep(7)
    check_active(title_ending="Google Chrome")
    sleep(2)
    log("Closing dialogues (if present)...")
    winsound.Beep(50, 20)
    pyautogui.press("esc")
    sleep(1)
    log("Opening JS injector (6s)...")
    winsound.Beep(60, 50)
    pyautogui.hotkey('ctrl', 'shift', 'j')
    sleep(6)
    log("Injecting JS (12s)...")
    winsound.Beep(80, 50)
    pyautogui.write(js_code)
    sleep(12)
    log("Running JS (6s)...")
    winsound.Beep(70, 100)
    if esc_before_entering:
        pyautogui.press("esc")
        sleep(0.3)
    pyautogui.press("enter")
    sleep(0.3)
    pyautogui.press("enter")
    sleep(6)
    log("Closing Browser...")
    winsound.Beep(70, 100)
    kill_process(executable_name)
    sleep(2)
    winsound.Beep(70, 100)
    log("")


def join_target_server(instance_id):
    join_js_code = f"Roblox.GameLauncher.joinGameInstance({globals.Roblox.game_id}, \"{instance_id}\")"
    run_javascript_in_browser(globals.Roblox.game_instances_url, join_js_code, True)


def get_best_server():
    server_obj = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
    highest_playercount_server = server_obj
    url = f"https://games.roblox.com/v1/games/{globals.Roblox.game_id}/servers/Public?sortOrder=Asc&limit=10"
    response = requests.get(url)
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            print(server)
            if "playing" in server and server["playing"] > highest_playercount_server["playing"]:
                highest_playercount_server = server
    if highest_playercount_server == server_obj:
        return False
    return highest_playercount_server


def log(status, no_log=False):
    print(status)
    if no_log:
        return
    output_log("main_status", status)


def log_process(process, no_log=False):
    process = f"[{process}]" if process.strip() != "" else ""
    print(process)
    if no_log:
        return
    output_log("main_process", process)
    sleep(0.1)


def check_if_should_change_servers(current_server_id="N/A"):
    original_current_server_id = current_server_id
    log("Querying Roblox API for server list")
    url = f"https://games.roblox.com/v1/games/{globals.Roblox.game_id}/servers/Public?sortOrder=Asc&limit=10"
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
        print(current_server)
        for server in servers:
            print(server)
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


def check_if_in_nil_world():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{globals.Roblox.game_id_nil}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if globals.Roblox.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


def check_if_in_hinamizawa_world():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{globals.Roblox.game_id_hinamizawa}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if globals.Roblox.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


def get_current_server_id():
    current_server_id = "N/A"
    url = f"https://games.roblox.com/v1/games/{globals.Roblox.game_id}/servers/Public?sortOrder=Asc&limit=10"
    try:
        response = requests.get(url)
    except Exception:
        print(format_exc())
        return "ERROR"
    if response.status_code == 200:
        response_result = response.json()
        servers = response_result["data"]
        for server in servers:
            if globals.Roblox.player_token in server["playerTokens"]:
                current_server_id = server["id"]
                break
        if current_server_id != "ERROR":
            print(current_server_id)
        return current_server_id
    return "ERROR"


def discord_log(message, author, author_avatar, author_url):
    screenshot_filename = None
    if not globals.Roblox.action_running:
        screenshot_filename = take_screenshot()
    webhook_urls = [
        os.getenv("DISCORD_WEBHOOK_CHAT_CHANNEL"),
        os.getenv("DISCORD_WEBHOOK_CHAT_CHANNEL_FUNKY")
    ]

    webhook_data = {
        "embeds": [
            {
                "description": message,
                "author": {
                    "name": author,
                    "url": author_url,
                    "icon_url": author_avatar

                }
            }
        ]
    }

    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    screenshot_binary = None
    if screenshot_filename is not None:
        if os.path.exists(screenshot_filename):
            with open(screenshot_filename, "rb") as f:
                screenshot_binary = f.read()
            if os.path.exists(screenshot_filename):
                os.remove(screenshot_filename)
    for webhook_url in webhook_urls:
        result = requests.post(webhook_url, json=webhook_data)
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print(f"[Logged] {message}")

        # Send screenshot
        if screenshot_binary is not None:
            requests.post(webhook_url, files={f"_{screenshot_filename}": (screenshot_filename, screenshot_binary)})
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as error:
                print(error)
            else:
                print(f"[Logged Screenshot] {message}")


def notify_admin(message):  # todo: Seperate always-running process
    webhook_url = os.getenv("DISCORD_WEBHOOK_DEV_CHANNEL")
    webhook_data = {
        "content": f"<@{os.getenv('DISCORD_OWNER_ID')}>\n{message}",
        "username": globals.Discord.webhook_username
    }
    result = requests.post(webhook_url, json=webhook_data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"[Dev Notified] {message}")


def check_for_better_server():
    cfg = globals.Roblox
    last_check_time = time.time()
    output_log("last_check_for_better_server", last_check_time)
    previous_status_text = read_output_log("change_server_status_text")
    output_log("change_server_status_text", "")

    log_process("Checking for better server")
    current_server_id = get_current_server_id()
    while current_server_id == "ERROR":
        log_process("Failed! Retrying better server check")
        sleep(5)
        current_server_id = get_current_server_id()
    if current_server_id == "N/A":
        nil_world_id = check_if_in_nil_world()
        hinamizawa_world_id = check_if_in_hinamizawa_world()
        if nil_world_id == "N/A" and hinamizawa_world_id == "N/A":
            log_process("Could not find FumoCam in any servers")
            globals.Roblox.action_queue.append("handle_crash")
            return False
        else:  # other world easter egg
            log("Successfully failed! Could not find FumoCam in the realms of the living.")
            winsound.Beep(60, 2000)
            log("S#c%e!s%u^l& f!i@e%! &o#l* ^o$ f!n& @u$o%a& *n !h# $e^l!s #f ^$e #i!i$g.")
            winsound.Beep(50, 2000)
            log("!#@%&!@%%^^& $!#@&%! &@#!* ^*$ @!$& @^$@%a& *$ !@# $#^%!@ #@ ^$% #@!%$#.")
            winsound.Beep(40, 2000)
            log_process("")
            log("")
            return True
    should_change_servers, change_server_status_text = check_if_should_change_servers(current_server_id)
    log(change_server_status_text)
    output_log("change_server_status_text", change_server_status_text)
    if not should_change_servers:
        log("PASS! Current server has sufficient players")
        sleep(5)
        log("")
        log_process("")
        return True
    elif previous_status_text != change_server_status_text:
        if "Could not find FumoCam" in change_server_status_text:
            for i in range(2):
                log(f"Rechecking (attempt {i + 1}/3")
                current_server_id = get_current_server_id()
                while current_server_id == "":
                    log_process("Retrying get current server check")
                    sleep(5)
                    current_server_id = get_current_server_id()
                should_change_servers, change_server_status_text = check_if_should_change_servers(current_server_id)
                if "Could not find FumoCam" not in change_server_status_text:
                    break
            if should_change_servers:
                notify_admin(change_server_status_text)
                cfg.action_queue.append("handle_join_new_server")
        else:
            cfg.action_queue.append("handle_join_new_server")
    log("")
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


def turn_camera(direction_obj):
    direction = direction_obj["turn_camera_direction"]
    turn_time = direction_obj["turn_camera_time"]
    check_active()
    sleep(0.5)
    pydirectinput.keyDown(direction)
    sleep(turn_time)
    pydirectinput.keyUp(direction)
    sleep(1)


def check_better_server_loop():
    while True:
        globals.Roblox.action_queue.append("check_for_better_server")
        sleep(5 * 60)


def get_english_timestamp(time_var):
    original_time = time_var
    seconds_in_minute = 60
    seconds_in_hour = 60 * seconds_in_minute
    seconds_in_day = 24 * seconds_in_hour
    days = math.floor(time_var / seconds_in_day)
    time_var -= days * seconds_in_day
    hours = math.floor(time_var / seconds_in_hour)
    time_var -= hours * seconds_in_hour
    minutes = math.floor(time_var / seconds_in_minute)
    time_var -= minutes * seconds_in_minute
    seconds = round(time_var)
    # if minutes == 0:
    # return "{} second{}".format(seconds, "s" if seconds != 1 else "")
    # if hours == 0:
    #    return "{} minute{}".format(minutes, "s" if minutes != 1 else "")
    hours = math.floor(original_time / seconds_in_hour) % 24
    # if days == 0:
    #    return "{} hour{}".format(hours, "s" if hours != 1 else "")
    # return "{} day{}, {} hour{}".format(days, "s" if days != 1 else "", hours, "s" if hours != 1 else "")
    return "{}d:{}h:{}m:{}s".format(days, hours, minutes, seconds)


def timer_loop():
    event_time_struct = time.strptime(globals.OBS.event_time, "%Y-%m-%d %I:%M:%S%p")
    # event_end_time_struct = time.strptime(globals.OBS.event_end_time, "%Y-%m-%d %I:%M:%S%p")
    while globals.Roblox.event_timer_running:
        seconds_since_event = time.time() - time.mktime(event_time_struct)
        english_time_since_event = get_english_timestamp(seconds_since_event)
        output_log("time_since_event", english_time_since_event)
        sleep(1)


def clock_loop():
    while True:
        output_log("clock", time.strftime("%Y-%m-%d \n%I:%M:%S%p EST"))
        sleep(1)


def exploit_window_checker(ret_value, potential_names):
    from time import sleep
    import pyautogui
    searching_for_window = True
    while searching_for_window:
        sleep(1)
        for window in pyautogui.getAllWindows():
            if window.title in potential_names:
                searching_for_window = False
                ret_value.value = potential_names.index(window.title)
                for i in range(3):  # Attempt a maximum of 3 tries
                    if window.title not in potential_names:
                        break
                    window.close()
                    sleep(0.3)
                break


def inject_lua(lua_code, attempts=0):  # todo: Move to seperate file
    if globals.Roblox.injector_disabled:
        log("Advanced commands are currently broken, sorry!")
        sleep(5)
        log("")
        return False
    original_directory = os.getcwd()
    os.chdir(globals.Roblox.injector_file_path)

    potential_names = [
        "Game Process Not Found",
        "NamedPipeExist!",
        "NamedPipeDoesntExist"
    ]
    ret_value = multiprocess.Value('i', -1)

    window_checker_proc = multiprocess.Process(target=exploit_window_checker, args=(ret_value, potential_names,))
    window_checker_proc.start()
    try:
        subprocess.check_output(["Injector.exe", "run", lua_code], timeout=7)
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        notify_admin(f"Error occurred with injector:\n```{format_exc()}```")
    os.chdir(original_directory)
    window_checker_proc.terminate()
    window_checker_proc.join()
    if ret_value.value != -1:
        error_result = potential_names[ret_value.value]
        print(error_result)
        if error_result in ["NamedPipeDoesntExist", "Game Process Not Found"]:
            load_exploit()
            if attempts > 3:
                return False
            inject_lua(lua_code, attempts + 1)
    check_active()
    return True


def load_exploit(force=False):  # todo: Move to seperate file
    print("loading exploit")
    if globals.Roblox.injector_disabled and not force:
        log("Advanced commands are currently broken, sorry!")
        sleep(5)
        log("")
        return False
    original_directory = os.getcwd()
    injector_folder = os.path.join(globals.Roblox.injector_file_path)
    os.chdir(injector_folder)

    potential_names = [
        "Game Process Not Found",
        "NamedPipeExist!",
        "NamedPipeDoesntExist",
        "EasyExploit"
    ]
    ret_value = multiprocess.Value('i', -1)
    non_fatal_error = True

    window_checker_proc = multiprocess.Process(target=exploit_window_checker, args=(ret_value, potential_names,))
    window_checker_proc.start()
    try:
        subprocess.check_output(["Injector.exe", "inject"], timeout=7)
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        notify_admin(f"Error occurred with injector:\n```{format_exc()}```")
        log("Warning: Injector failed, this happens every 24h. Please wait for dev.")
        non_fatal_error = False
        sleep(10)
        log("")
    os.chdir(original_directory)
    window_checker_proc.terminate()
    window_checker_proc.join()

    if ret_value.value != -1:
        error_result = potential_names[ret_value.value]
        print(error_result)
        if error_result in ["Game Process Not Found", "EasyExploit", "NamedPipeDoesntExist"]:
            non_fatal_error = False
    if non_fatal_error:
        inject_lua("""setfflag("AbuseReportScreenshot", "False")
        setfflag("AbuseReportScreenshotPercentage", "0")""")
    else:
        kill_process("chrome.exe")
        globals.Roblox.injector_disabled = True
        if not force:  # We're not forcing a check from an existing injector failed loop
            notify_admin(f"Injector has been patched, navigate to location manually")
            threading.Thread(target=injector_failed_loop).start()
        log("Warning: Injector failed, this can happen every 7 days.\nYou can try moving the cam with !move.")
        sleep(10)
        log("")
        return False

    kill_process("chrome.exe")
    return non_fatal_error


def injector_failed_loop():
    gr = globals.Roblox
    gr.next_injector_check = time.time()
    while True:
        if gr.next_injector_check <= time.time():  # Time to recheck
            gr.next_injector_check = time.time() + gr.injector_recheck_seconds
            while gr.action_running or gr.action_queue:  # We have a queue or we're doing something
                sleep(0.5)  # Wait for any running action to finish
            gr.action_running = True
            log_process(f"Attempting to hook into Roblox")
            log("Re-attempting process connection...")
            output_log("injector_failure", "INJECTOR FAILED\nTP, Goto, Spectate, Tour offline Use !move\nAttempting "
                                           "again now...")
            loaded_exploit = load_exploit(force=True)
            log_process(f"")
            log("")
            if loaded_exploit:
                output_log("injector_failure", "")
                return True
            globals.Roblox.action_running = False
        time_remaining = round(gr.next_injector_check-time.time())
        friendly_time_remaining = f"{math.floor(time_remaining/60):02}:{time_remaining%60:02}"
        output_log("injector_failure", f"INJECTOR FAILED\nTP, Goto, Spectate, Tour offline. Use !move\nAttempting "
                                       f"again in {friendly_time_remaining}")
        sleep(1)


def silent_teleport(location_name):  # todo: Move tests to new file
    chosen_location = globals.Roblox.teleport_locations[location_name]
    pos, rot, cam_rot = chosen_location["pos"], chosen_location["rot"], chosen_location["cam"]
    # noinspection LongLine
    inject_lua(f"""
    game.Players.LocalPlayer.Character:SetPrimaryPartCFrame(CFrame.new(Vector3.new({pos}), game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame.LookVector))
    game.Players.LocalPlayer.Character.PrimaryPart.CFrame = CFrame.new(game.Players.LocalPlayer.Character.PrimaryPart.Position) * CFrame.Angles({rot})
    workspace.CurrentCamera.CFrame = CFrame.new(workspace.CurrentCamera.CFrame.Position) * CFrame.Angles({cam_rot})""")


def jump():
    check_active()
    sleep(0.75)
    pydirectinput.keyDown('space')
    sleep(0.25)
    pydirectinput.keyUp('space')


def respawn_character():
    check_active()
    log_process("Respawning")
    send_chat("[Respawning!]")
    sleep(0.75)
    pydirectinput.keyDown('esc')
    sleep(0.1)
    pydirectinput.keyUp('esc')
    sleep(0.5)
    pydirectinput.keyDown('r')
    sleep(0.1)
    pydirectinput.keyUp('r')
    sleep(0.5)
    pydirectinput.keyDown('enter')
    sleep(0.1)
    pydirectinput.keyUp('enter')
    sleep(0.5)
    log_process("")


def teleport(location_name, no_log=False):
    cfg = globals.Roblox

    log_process("Teleport", no_log)
    print(f"'{location_name}'")
    if location_name == "":
        log(f"Please specify a location! Use one of the locations below:\n{', '.join(cfg.teleport_locations)}")
        sleep(5)
        log_process("")
        log("")
        return False
    if location_name not in cfg.teleport_locations:
        log(f"Unknown location! Please use one of the locations below:\n{', '.join(cfg.teleport_locations)}")
        sleep(5)
        log_process("")
        log("")
        return False
    elif cfg.next_possible_teleport > time.time() and not no_log:
        log(f"Teleport on cool-down! Please wait {round(cfg.next_possible_teleport - time.time())} seconds!")
        sleep(5)
        log_process("")
        log("")
        return False
    log(f"Teleporting to: {cfg.teleport_locations[location_name]['friendly_name']}", no_log)
    sleep(0.5)
    is_comedy = location_name == "comedy2"
    if not is_comedy:
        cfg.next_possible_teleport = time.time() + 30
    if not no_log:
        send_chat(f"[Teleporting to {cfg.teleport_locations[location_name]['friendly_name']}!]")
        sleep(5)
    winsound.Beep(40, 600)
    winsound.Beep(70, 400)
    chosen_location = cfg.teleport_locations[location_name]
    pos, rot, cam_rot = chosen_location["pos"], chosen_location["rot"], chosen_location["cam"]
    # todo: Probably best to write LUA in seperate files
    # noinspection LongLine
    jump()
    inject_lua(f"""game.Players.LocalPlayer.Character:SetPrimaryPartCFrame(CFrame.new(Vector3.new({pos}), game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame.LookVector))
    game.Players.LocalPlayer.Character.PrimaryPart.CFrame = CFrame.new(game.Players.LocalPlayer.Character.PrimaryPart.Position) * CFrame.Angles({rot})
    workspace.CurrentCamera.CFrame = CFrame.new(workspace.CurrentCamera.CFrame.Position) * CFrame.Angles({cam_rot})""")
    if is_comedy:
        send_chat(random.choice(cfg.comedy_phrases))
    winsound.Beep(90, 300)
    sleep(1)
    if is_comedy:
        sleep(10)
        for i in range(5):
            log(f"Returning in {5 - i}s")
            winsound.Beep(90, 300)
            sleep(1)
        return_location = cfg.teleport_locations[cfg.current_location]
        pos, rot, cam_rot = return_location["pos"], return_location["rot"], return_location["cam"]
        # todo: Probably best to write LUA in seperate files
        # noinspection LongLine
        inject_lua(f"""game.Players.LocalPlayer.Character:SetPrimaryPartCFrame(CFrame.new(Vector3.new({pos}), game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame.LookVector))
    game.Players.LocalPlayer.Character.PrimaryPart.CFrame = CFrame.new(game.Players.LocalPlayer.Character.PrimaryPart.Position) * CFrame.Angles({rot})
    workspace.CurrentCamera.CFrame = CFrame.new(workspace.CurrentCamera.CFrame.Position) * CFrame.Angles({cam_rot})""")
    else:
        cfg.current_location = location_name
    log("", no_log)
    log_process("", no_log)
    jump()  # If knocked over, clear sitting effect
    send_chat(cfg.current_emote)
    return True


def print_pos():  # todo: Move tests to new file
    # todo: Probably best to write LUA in seperate files
    inject_lua(f"""
    print("\\n\\n")
    print("Position:",game.Players.LocalPlayer.Character.PrimaryPart.Position)""")


def test_cam():  # todo: Move tests to new file
    # todo: Probably best to write LUA in seperate files
    inject_lua(f"""
    print("\\n\\n")
    print("Position:", game.Players.LocalPlayer.Character.PrimaryPart.Position)
    print("Angles:", game.Players.LocalPlayer.Character.PrimaryPart.Rotation)
    local campos = workspace.CurrentCamera.CFrame.Position
    print("Camera Pos:", campos)
    local camx, camy, camz = (workspace.CurrentCamera.CFrame - campos):ToEulerAnglesYXZ()
    camx = math.floor(math.deg(camx)*10000)/10000
    camy = math.floor(math.deg(camy)*10000)/10000
    camz = math.floor(math.deg(camz)*10000)/10000
    print("Camera Angles:", camx, camy, camz)
    """)


def spectate_loop():
    cfg = globals.Roblox
    while True:
        sleep(15 * 60)
        if globals.Roblox.injector_disabled:
            continue
        cfg.next_possible_teleport = 0
        cfg.action_queue.append("spectate")


def goto(target):
    cfg = globals.Roblox
    log_process("Goto")
    print(f"'{target}'")
    if target == "":
        log(f"Please specify a player!")
        sleep(5)
        log_process("")
        log("")
        return False
    if cfg.next_possible_teleport > time.time():
        log(f"Teleport on cool-down! Please wait {round(cfg.next_possible_teleport - time.time())} seconds!")
        sleep(5)
        log_process("")
        log("")
        return False
    log(f"Attempting teleport to player...\n(If this doesnt work, the name was incorrect)")
    sleep(0.5)
    cfg.next_possible_teleport = time.time() + 30
    winsound.Beep(40, 600)
    winsound.Beep(70, 400)
    # todo: Probably best to write LUA in seperate files
    # noinspection LongLine
    jump()
    inject_lua(f"""
    local player_list = game.Players:GetPlayers()
    for i=1,#player_list do
        local current_player = player_list[i]
        if (string.lower(current_player.Name) == "{target.lower()}") then
            game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Teleporting to player '" .. current_player.Name .."'!]" , "All")
            wait(10)
            local original_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
            local player_pos = current_player.Character.PrimaryPart.Position
            game.Players.LocalPlayer.Character:MoveTo(player_pos)
            wait(2)
            local current_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
            if (current_pos.y > 65) then
                game.Players.LocalPlayer.Character:MoveTo(original_pos)
                game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[This player is in a location I can't teleport to!]" , "All")
                game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Can only teleport to players outside and not on objects!]" , "All")
                break
            else 
                game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Hello! Someone on T witch asked me to teleport to you.]" , "All")
            end
            break
        end
    end
    workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")
    """)

    sleep(10)  # Initial Teleport
    winsound.Beep(90, 300)
    sleep(3)  # Skybox check
    jump()  # If knocked over, clear sitting effect
    send_chat(cfg.current_emote)
    log("")
    log_process("")
    return True


def anti_gravity():
    inject_lua("""
    -- The factor by which gravity will be counteracted
local MOON_GRAVITY = 0.5
local function setGravity(part, g)
    local antiGravity = part:FindFirstChild("AntiGravity")
    if g == 1 then
        -- Standard gravity; destroy any gravity-changing force
        if antiGravity then
            antiGravity:Destroy()
        end 
    else
        -- Non-standard gravity: create and change gravity-changing force
        if not antiGravity then
            antiGravity = Instance.new("BodyForce")
            antiGravity.Name = "AntiGravity"
            antiGravity.Archivable = false
            antiGravity.Parent = part
        end
        antiGravity.Force = Vector3.new(0, part:GetMass() * workspace.Gravity * (1 - g), 0)
    end
end
local function moonGravity(part)
    setGravity(part, 0.0005)
end
local function recursiveMoonGravity(object)
    if object:IsA("BasePart") then
        moonGravity(object)
    end
    for _, child in pairs(object:GetChildren()) do
        recursiveMoonGravity(child)
    end
end
local function onDescendantAdded(object)
    if object:IsA("BasePart") then
        moonGravity(object)
    end
end
recursiveMoonGravity(workspace)
workspace.DescendantAdded:Connect(onDescendantAdded)""")


def silent_goto(target):
    inject_lua(f"""
    local player_list = game.Players:GetPlayers()
    for i=1,#player_list do
        local current_player = player_list[i]
        if (string.lower(current_player.Name) == "{target.lower()}") then
            local original_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
            local player_pos = current_player.Character.PrimaryPart.Position
            game.Players.LocalPlayer.Character:SetPrimaryPartCFrame(CFrame.new(player_pos), game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame.LookVector)
            
            
            break
        end
    end
    workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")
    """)
    
    
def silent_getpos(target):
    inject_lua(f"""
    local player_list = game.Players:GetPlayers()
    for i=1,#player_list do
        local current_player = player_list[i]
        if (string.lower(current_player.Name) == "{target.lower()}") then
            local original_pos = game.Players.LocalPlayer.Character.PrimaryPart.Position
            local player_pos = current_player.Character.PrimaryPart.Position
            print("Target:", current_player.Name)
            print("\\n\\n")
            print("Position:", current_player.Character.PrimaryPart.Position)
            print("Angles:",  current_player.PrimaryPart.Rotation)
            
            break
        end
    end
    workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")
    """)    


def spectate_target(target):

    # todo: Probably best to write LUA in seperate files
    inject_lua(f"""
    local player_list = game.Players:GetPlayers()
    for i=1,#player_list do
        local current_player = player_list[i]
        if (string.lower(current_player.Name) == "{target.lower()}") then
            pcall(function()
                print(current_player.Name)
                print(current_player.Character:FindFirstChildOfClass("Humanoid"))
                workspace.CurrentCamera.CameraSubject = current_player.Character:FindFirstChildOfClass("Humanoid")
            end)
            break
        end
    end
    """)


def spectate_random():
    if globals.Roblox.injector_disabled:
        log(f"Cannot spectate, injector functionality is currently broken!")
        return False
    cfg = globals.Roblox
    if cfg.next_possible_teleport > time.time():
        log(f"Spectate on cool-down! Please wait {round(cfg.next_possible_teleport - time.time())} seconds!")
        sleep(5)
        log_process("")
        log("")
        return False
    cfg.next_possible_teleport = time.time() + 30
    log_process("Spectating")
    log("Spectating up to 10 random players")
    send_chat("[Spectating players! Won't be able to see nearby chat. Be right back!]")

    # todo: Probably best to write LUA in seperate files
    inject_lua("""
    local function shuffle(array)
        -- fisher-yates
        local output = { }
        local random = math.random
        for index = 1, #array do
            local offset = index - 1
            local value = array[index]
            local randomIndex = offset*random()
            local flooredIndex = randomIndex - randomIndex%1
            if flooredIndex == offset then
                output[#output + 1] = value
            else
                output[#output + 1] = output[flooredIndex + 1]
                output[flooredIndex + 1] = value
            end
        end
        return output
    end
    local player_list = game.Players:GetPlayers()
    player_list = shuffle(player_list)
    for i=1,math.min(#player_list,10) do
        pcall(function()
            local current_player = player_list[i]
            print(current_player.Name)
            print(current_player.Character:FindFirstChildOfClass("Humanoid"))
            workspace.CurrentCamera.CameraSubject = current_player.Character:FindFirstChildOfClass("Humanoid")
            wait(5)
        end)
    end
    workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")
    """)
    sleep(10 * 5)
    send_chat("[I'm back! Should be finished spectating players.]")
    log_process("")
    log("")


class TwitchBot(irc.bot.SingleServerIRCBot):  # todo: Move to seperate file?
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = f"https://api.twitch.tv/kraken/users?login={channel}"
        headers = {"Client-ID": client_id, "Accept": "application/vnd.twitchtv.v5+json",
                   "Authorization": f"oauth:{token}"}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r["users"][0]["_id"]

        # Create IRC bot connection
        server = "irc.chat.twitch.tv"
        port = 6667
        print(f"Connecting to {server} on port {port}...")
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, f"oauth:{token}")], username, username)

    def on_welcome(self, c, _):
        print('Joining ' + self.channel)
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        print('Joined ' + self.channel)

    def on_pubmsg(self, _, e):
        author = "Twitch"
        for tag in e.tags:
            if tag["key"] == "display-name":
                author = tag["value"]
        author = author[:13]
        author_url = f"https://www.twitch.tv/{author.lower()}"
        author_avatar = "https://brand.twitch.tv/assets/images/black.png"
        message = e.arguments[0]
        discord_log(message, author, author_avatar, author_url)
        # If a chat message starts with an exclamation point, try to run it as a command
        if message[:1] == '!':
            original_cmd = message.split(" ")
            cmd = original_cmd[0].replace("!", "")
            args = original_cmd[1:]
            print(f"Received command: {cmd}")
            self.do_command(e, cmd, args, author)
        return

    @staticmethod
    def do_command(_, cmd, args, author):
        cfg = globals.Roblox
        is_dev = author.lower() in globals.Twitch.admins
        is_owner = author.lower() == "scary08rblx"
        if cmd == "rejoin" and is_dev:
            cfg.action_queue.append("handle_crash")
        elif (cmd == "handle_join_new_server" or cmd == "handle_crash") and is_dev:
            cfg.action_queue.append(cmd)
        elif cmd == "spectate":
            cfg.action_queue.append("spectate")
        elif cmd == "tour":
            cfg.action_queue.append("tour")
        elif cmd == "zoomin" or cmd == "zoomout":
            zoom_direction = "i" if cmd == "zoomin" else "o"
            zoom_time = 0.05
            try:
                number = float(args[0])
                if number <= 1:
                    zoom_time = number
            except Exception:
                pass
            cfg.action_queue.append({"zoom_camera_direction": zoom_direction, "zoom_camera_time": zoom_time})
        elif cmd == "left" or cmd == "right":
            turn_time = 0.1
            try:
                number = float(args[0])
                if number <= 2:
                    turn_time = number
            except Exception:
                pass
            cfg.action_queue.append({"turn_camera_direction": cmd, "turn_camera_time": turn_time})
        elif cmd == "move":
            move_time = 1
            try:
                number = float(args[1])
                if 5 >= number > 0:
                    move_time = number
            except Exception:
                pass
            try:
                cfg.action_queue.append({"movement": cmd, "move_key": args[0], "move_time": move_time, "override": is_dev})
            except Exception:
                log_process("Manual Movement")
                log("Command invalid! Check you're typing it right.")
                sleep(3)
        elif cmd == "leap":
            forward_time = 0.4
            jump_time = 0.3
            try:
                number = float(args[0])
                if 1 >= number > 0:
                    forward_time = number
            except Exception:
                pass
            try:
                number = float(args[1])
                if 1 >= number > 0:
                    jump_time = number
            except Exception:
                pass
            try:
                cfg.action_queue.append({"leap": cmd, "forward_time": forward_time, "jump_time": jump_time, "override": is_dev})
            except Exception:
                log_process("Leap")
                log("Command invalid! Check you're typing it right.")
                sleep(3)
        elif cmd == "tp":
            location = ""
            if len(args) > 0:
                location = args[0]
            if is_dev:
                cfg.next_possible_teleport = 0
            cfg.action_queue.append({"tp": location})
        elif cmd == "goto":
            player_name = ""
            if len(args) > 0:
                player_name = args[0]
            if is_dev:
                cfg.next_possible_teleport = 0
            cfg.action_queue.append({"goto": player_name})
        elif cmd == "dev":
            log("Sending warning to dev...")
            msg = " ".join(args)
            notify_admin(f"{author}: {msg}")
            sleep(5)
            log("")
        elif cmd == "click":
            cfg.action_queue.append("click")
        elif cmd == "sit":
            cfg.action_queue.append("sit")
        elif cmd == "use":
            cfg.action_queue.append("use")
        elif cmd == "grief":
            cfg.action_queue.append("grief")
        elif cmd == "respawn":
            cfg.action_queue.append("respawn")
        elif cmd == "jump":
            cfg.action_queue.append("jump")
        elif cmd == "respawn":
            cfg.action_queue.append("respawn")
        elif cmd == "m":
            msg = " ".join(args)
            if msg.startswith("[") or msg.startswith("/w"):  # Whisper functionality
                return
            elif (msg.startswith("/mute") or msg.startswith("/unmute")) and is_dev:  # Make muting dev-only
                cfg.action_queue.append({"chat": [msg]})
            elif msg.startswith("/"):
                if msg.startswith("/e"):
                    cfg.current_emote = msg
                cfg.action_queue.append({"chat": [msg]})
            elif is_dev:  # Chat with CamDev Tag
                print({"chat_with_name": ["[CamDev]:", msg]})
                cfg.action_queue.append({"chat_with_name": ["[CamDev]:", msg]})
            elif is_owner:  # Chat with BecomeFumo Owner Tag
                cfg.action_queue.append({"chat_with_name": ["[BecomeFumoDev Scary08]:", msg]})
            else:
                cfg.action_queue.append({"chat_with_name": [f"{author}:", msg]})


def world_tour():
    interval = globals.Roblox.seconds_per_tour_location
    locations = globals.Roblox.teleport_locations
    send_chat(f"[Going on tour. Try and keep up! I'll be back here in {len(locations)*interval} seconds.]")
    log_process("World Tour")
    sleep(5)
    locations_list = list(locations.keys())
    for index in range(len(locations_list)): 
        if globals.Roblox.injector_disabled:
            break
        location_key = locations_list[index]
        location = locations[location_key]
        log(f"Touring {location['friendly_name']} ({index+1}/{len(locations_list)})")
        globals.Roblox.next_possible_teleport = 0
        jump()
        silent_teleport(location_key)
        sleep(interval)
        
    if globals.Roblox.injector_disabled:
        crashed = do_crash_check()
        if crashed or "Roblox" not in pyautogui.getAllTitles():
            globals.Roblox.action_queue.append("handle_crash")
    globals.Roblox.next_possible_teleport = 0
    teleport(globals.Roblox.current_location, no_log=True)
    globals.Roblox.next_possible_teleport = time.time() + 30
    log("")
    log_process("")
    send_chat(f"[I'm back from my tour!]")


def commands_loop():
    cfg = globals.Roblox
    commands_list = [
        {
            "command": "!m Your Message",
            "help": "Sends \"Your Message\" in-game"
        },
        {
            "help": f"Teleport. \n({', '.join(cfg.teleport_locations)})",
            "command": "!tp LocationName",
            "injector_status_required": True,
            "time": 20
        },
        {
            "command": "!goto PlayerName",
            "help": "Teleports to a player by that name.",
            "injector_status_required": True
        },
        {
            "command": "!spectate",
            "help": "Spectates up to 10 random players.",
            "injector_status_required": True
        },
        {
            "command": "!tour",
            "help": "Goes on a tour to all known locations.",
            "injector_status_required": True
        },
        {
            "command": "!left 0.2 or !right 0.2",
            "help": "Turn camera left or right for 0.2s"
        },
        {
            "command": "!zoomin 0.1 or !zoomout 0.1",
            "help": "Zoom camera in or out for 0.1s"
        },
        {
            "command": "!sit",
            "help": "Clicks the sit button"
        },
        {
            "command": "!dev Your Message",
            "help": "EMERGENCY ONLY, Sends \"Your Message\" to devs discord account"
        },
        {
            "command": "!move w 5",
            "help": "Moves forwards for 5 seconds",
            "injector_status_required": False
        },
        {
            "command": "!leap 0.7 0.5",
            "help": "At the same time, moves forwards for 0.7s and jumps for 0.5s",
            "injector_status_required": False
        },
        {
            "command": "!jump",
            "help": "Jumps. Helpful if stuck on something.",
            "injector_status_required": False
        },
        {
            "command": "!grief",
            "help": "Toggles anti-grief.",
            "injector_status_required": False
        },
        {
            "command": "!respawn",
            "help": "Respawns. Helpful if completely stuck.",
            "injector_status_required": False
        },
        {
            "command": "!use",
            "help": "Presses \"e\".",
            "injector_status_required": False
        },
        {
            "command": "!sit",
            "help": "Clicks the sit button.",
            "injector_status_required": False
        },
    ]
    while True:
        new_commands_list = []
        for cmd in commands_list:
            if "injector_status_required" in cmd:
                # If the injector needs to be ON for this but its OFF
                if cmd["injector_status_required"] and globals.Roblox.injector_disabled:
                    continue
                # If the injector needs to be OFF for this but its ON
                if not cmd["injector_status_required"] and not globals.Roblox.injector_disabled:
                    continue
            new_commands_list.append(cmd)
        for command in new_commands_list:
            output_log("commands_help_label", "")
            output_log("commands_help_title", "")
            output_log("commands_help_desc", "")

            sleep(0.25)
            current_command_in_list = f"{(new_commands_list.index(command) + 1)}/{len(new_commands_list)}"
            output_log("commands_help_label", f"TWITCH CHAT COMMANDS [{current_command_in_list}]")
            output_log("commands_help_title", command["command"])
            sleep(0.1)
            output_log("commands_help_desc", command["help"])
            if "time" in command:
                sleep(int(command["time"]))
                continue
            sleep(5)


def do_process_queue():  # todo: Investigate benefits of multithreading over single-threaded/async
    cfg = globals.Roblox
    if len(cfg.action_queue) > 0:
        action = cfg.action_queue[0]
        print("running Action Queue")
        print(cfg.action_queue)
        if action == "anti-afk":
            cfg.action_running = True
            do_anti_afk()
            cfg.action_running = False
        elif action == "anti-afk-advert":
            cfg.action_running = True
            do_anti_afk_advert()
            cfg.action_running = False
        elif "turn_camera_direction" in action:
            cfg.action_running = True
            turn_direction = action['turn_camera_direction']
            turn_time = action['turn_camera_time']
            log_process(f"{turn_direction.upper()} for {turn_time}s")
            turn_camera(action)
            log_process("")
            cfg.action_running = False
        elif "zoom_camera_direction" in action:
            cfg.action_running = True
            zoom_direction = "in" if action['zoom_camera_direction'] == "i" else "out"
            zoom_time = action['zoom_camera_time']
            log_process(f"Zooming {zoom_direction} for {zoom_time}s")
            zoom_camera(action)
            log_process("")
            cfg.action_running = False
        elif action == "check_for_better_server":
            crashed = do_crash_check()
            if not crashed:
                check_for_better_server()
                check_active()
            else:
                cfg.action_queue.insert(0, "handle_crash")
        elif "chat_with_name" in action:
            name = action["chat_with_name"][0]
            send_chat(name)
            sleep(len(name) * 0.05)
            print(name)
            msgs = action["chat_with_name"][1:]
            for msg in msgs:
                send_chat(msg)
        elif "chat" in action:
            for message in action["chat"]:
                send_chat(message)
        elif action == "handle_crash":
            cfg.action_running = True
            handle_join_new_server(crash=True)
            cfg.action_running = False
        elif action == "handle_join_new_server":
            cfg.action_running = True
            handle_join_new_server()
            cfg.action_running = False
        elif "tp" in action:
            cfg.action_running = True
            teleport(action["tp"])
            check_active()
            cfg.action_running = False
        elif "goto" in action:
            cfg.action_running = True
            goto(action["goto"])
            check_active()
            cfg.action_running = False
        elif action == "spectate":
            cfg.action_running = True
            spectate_random()
            check_active()
            cfg.action_running = False
        elif action == "tour":
            cfg.action_running = True
            world_tour()
            check_active()
            cfg.action_running = False
        elif action == "click":
            cfg.action_running = True
            alt_tab_click()
            cfg.action_running = False
        elif action == "sit":
            cfg.action_running = True
            click_sit_button()
            cfg.action_running = False
        elif action == "use":
            cfg.action_running = True
            log_process("Pressing Use (e)")
            if not globals.Roblox.injector_disabled:
                log("Manual control not allowed when injector is working!")
                sleep(5)
            else:
                check_active()
                pydirectinput.keyDown("e")
                sleep(1)
                pydirectinput.keyUp("e")
            log_process("")
            log("")
            cfg.action_running = False
        elif action == "grief":
            cfg.action_running = True
            if not globals.Roblox.injector_disabled:
                log("Anti-Grief toggling not allowed when injector is working!")
                sleep(5)
            else:
                toggle_collisions()
                pydirectinput.moveTo(1, 1)
                alt_tab_click()
            log_process("")
            log("")
            cfg.action_running = False
        elif action == "respawn":
            cfg.action_running = True
            if not globals.Roblox.injector_disabled:
                log("Respawning character not allowed when injector is working!")
                sleep(5)
            else:
                respawn_character()
            log_process("")
            log("")
            cfg.action_running = False
        elif action == "jump":
            cfg.action_running = True
            jump()
            cfg.action_running = False
        elif "movement" in action:
            cfg.action_running = True
            log_process("Manual Movement")
            if not globals.Roblox.injector_disabled and not action["override"]:
                log("Manual movement not allowed when injector is working!")
                sleep(5)
                log_process("")
                log("")
            valid_keys = {"w": "Forward", "a": "Left", "s": "Backwards", "d": "Right"}
            key = action["move_key"].lower()
            if key not in valid_keys.keys():
                log(f"Not a valid movement! ({','.join(valid_keys)})")
                sleep(5)
                log("")
                log_process("")
                cfg.action_running = False
                cfg.action_queue.pop(0)
                return False
            time_to_press = action["move_time"]
            log(f"Moving {valid_keys[key]} for {time_to_press}s")
            check_active()
            sleep(0.75)
            pydirectinput.keyDown(key)
            sleep(time_to_press)
            pydirectinput.keyUp(key)            
            log("")
            log_process("")
            cfg.action_running = False
        elif "leap" in action:
            cfg.action_running = True
            log_process("Leap Forward")
            if not globals.Roblox.injector_disabled and not action["override"]:
                log("Manual movement not allowed when injector is working!")
                sleep(5)
                log_process("")
                log("")
            time_forward = action["forward_time"]
            time_jump = action["jump_time"]
            log(f"Moving forward for {time_forward}s and jumping for {time_jump}s")
            check_active()
            sleep(0.75)
            pydirectinput.keyDown("w")
            pydirectinput.keyDown("space")
            if time_forward > time_jump:
                sleep(time_jump)
                pydirectinput.keyUp("space")
                sleep(time_forward-time_jump)
                pydirectinput.keyUp("w")
            else:
                sleep(time_forward)
                pydirectinput.keyUp("w")
                sleep(time_jump-time_forward)
                pydirectinput.keyUp("space")
            log("")
            log_process("")
            cfg.action_running = False
        else:
            print("queue failed")

        cfg.action_queue.pop(0)


def process_queue_loop():
    while True:
        sleep(0.1)
        if globals.Roblox.action_running:
            continue
        do_process_queue()
        sleep(0.25)


def main():
    log_process("")
    log("")
    output_log("change_server_status_text", "")
    output_log("injector_failure", "")
    crashed = do_crash_check()
    if crashed or "Roblox" not in pyautogui.getAllTitles():
        globals.Roblox.action_queue.append("handle_crash")
        do_process_queue()
    else:
        check_active()
        load_exploit()
    print("Starting Threads")
    thread_functions = [process_queue_loop, check_better_server_loop, twitch_main, anti_afk, commands_loop, timer_loop,
                        clock_loop, crash_check_loop, spectate_loop]
    for thread_function in thread_functions:
        threading.Thread(target=thread_function).start()
    print("Done Main")


def test_character_select(click_mouse=True):  # todo: Move tests to new file
    check_active()
    sleep(1)
    click_character_in_menu(click_mouse=click_mouse)


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    main()
    # test_character_select(click_mouse=True)
