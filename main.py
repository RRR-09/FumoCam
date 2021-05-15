import math
import os
from pathlib import Path
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

screen_res = {
    "width": pyautogui.size()[0],
    "height": pyautogui.size()[1],
    "x_multi": pyautogui.size()[0] / 2560,
    "y_multi": pyautogui.size()[1] / 1440,
}

monitor_size = mss().monitors[0]
import globals  # globals.py

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


def kill_process(executable="RobloxPlayerBeta.exe"):
    subprocess.call(["taskkill", "/IM", executable])


def force_get_best_server():
    found_best_server = False
    while not found_best_server:
        found_best_server = get_best_server()
        if found_best_server:
            break
        sleep(5)
        log("Failed to find best server, retrying...")
    return found_best_server["id"]


def twitch_main():
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
    kill_process()
    server_id = force_get_best_server()
    sleep(1)

    log_process(f"{process_name} - Joining Server")
    join_target_server(server_id)
    output_log("change_server_status_text", "")

    log_process(f"{process_name} - Handling Spawn")
    server_spawn()

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


def crash_check_loop():
    while True:
        for window_title in pyautogui.getAllTitles():
            if window_title == "Crash" or window_title == "Roblox Crash":
                notify_admin("Roblox Crash")
                globals.Roblox.action_queue.append("handle_crash")
                sleep(60)
        sleep(5)


def check_active(title="Roblox"):
    active_window = pyautogui.getActiveWindow()
    if active_window is not None and active_window.title == title:
        return
    for window in pyautogui.getAllWindows():
        if window.title == title:
            try:
                print(f"Minimizing {title}")
                window.minimize()
            except Exception:
                print(f"ERROR IN MINIMIZING {title}")
            try:
                print(f"Focusing {title}")
                window.focus()
            except Exception:
                print(f"ERROR IN FOCUSING {title}")
            try:
                print(f"Activating {title}")
                window.activate()
            except Exception:
                print(f"ERROR IN ACTIVATING {title}")
            try:
                print(f"Maximizing {title}")
                window.maximize()
            except Exception:
                print(f"ERROR IN MAXIMIZING {title}")
            sleep(0.3)
            if title == "Roblox" and window.height != pyautogui.size()[1]:
                while window.height != pyautogui.size()[1]:
                    pydirectinput.press("f11")
                    print("Maximizing window with F11")
                    sleep(0.3)
            check_active(title)


def send_chat(message):
    check_active()
    pyautogui.press('/')
    sleep(0.1)
    for word in globals.Roblox.censored_words:
        if word in message:
            message = message.replace(word, "*" * len(word))
    pyautogui.write(message)
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


def spawn_wait_until_loaded():
    global screen_res
    check_active()
    sleep(1)
    character_select_button = None
    while character_select_button is None:  # Loading
        log("Loading into Roblox")
        winsound.Beep(40, 50)
        try:
            print("TryingToFind")
            character_select_button = pyautogui.locateOnScreen(globals.Roblox.character_select_image_path,
                                                               grayscale=True,
                                                               confidence=0.9)  # , #region=character_select_range)
        except pyautogui.ImageNotFoundException:
            character_select_button = None
        if character_select_button is not None:
            break
        sleep(1)
    return character_select_button


def toggle_collisions():
    global screen_res
    check_active()
    log("Opening Settings")
    sleep(0.5)
    winsound.Beep(150, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(screen_res["height"] * 0.95)  # Settings button
    pydirectinput.moveTo(button_x, button_y)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()
    winsound.Beep(100, 50)

    log("Toggling Collisions")
    sleep(0.5)
    winsound.Beep(150, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(
        screen_res["height"] * 0.40)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()
    winsound.Beep(100, 50)

    log("Closing Settings")
    sleep(0.25)
    winsound.Beep(150, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(
        screen_res["height"] * 0.30)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()
    sleep(0.25)
    winsound.Beep(100, 50)


def change_characters(character_select_button):
    global screen_res
    check_active()
    log("Opening Character Select")
    sleep(0.5)
    winsound.Beep(150, 100)
    button_x, button_y = pyautogui.center(character_select_button)
    pydirectinput.moveTo(button_x, button_y)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()
    winsound.Beep(100, 50)
    winsound.Beep(40, 25)
    winsound.Beep(40, 25)
    winsound.Beep(40, 25)
    for i in range(18):
        pyautogui.scroll(-1)
        winsound.Beep(40, 25)
        sleep(0.05)
    log("Scrolling up 10 times")
    for i in range(10):
        pyautogui.scroll(1)
        winsound.Beep(40, 25)
        sleep(0.05)

    # button_x, button_y = 
    # pydirectinput.moveTo(button_x, button_y)
    # reisen_location = None
    # while reisen_location == None:
    # try:
    # log("Trying to find character")
    # pyautogui.scroll(1)
    # reisen_location = pyautogui.locateOnScreen('reisen.png', grayscale=True, confidence=0.6)
    # except pyautogui.ImageNotFoundException:
    # reisen_location = None
    # if reisen_location != None:
    # winsound.Beep(200,75)
    # break
    # winsound.Beep(40,75)
    # sleep(0.1)
    log("Clicking Momiji")
    winsound.Beep(250, 100)
    button_x, button_y = round(screen_res["width"] * 0.5), round(
        screen_res["height"] * 0.48)  # Toggle Collisions button
    pydirectinput.moveTo(button_x, button_y)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pydirectinput.mouseDown()
    pydirectinput.mouseUp()
    winsound.Beep(100, 50)
    sleep(0.5)
    new_character_select_button = None

    log("Trying to close character select")
    while new_character_select_button is None:
        try:
            print("TryingToFind")
            new_character_select_button = pyautogui.locateOnScreen(globals.Roblox.character_select_image_path,
                                                                   grayscale=True,
                                                                   confidence=0.9)  # , #region=character_select_range)
        except pyautogui.ImageNotFoundException:
            new_character_select_button = None
        if new_character_select_button is not None:
            new_x, new_y = pyautogui.center(new_character_select_button)
            if new_y != button_y:
                winsound.Beep(150, 100)
                pydirectinput.moveTo(new_x, new_y)
                pyautogui.hotkey('alt', 'tab')
                sleep(0.15)
                pyautogui.hotkey('alt', 'tab')
                sleep(0.15)
                pydirectinput.mouseDown()
                pydirectinput.mouseUp()
                winsound.Beep(100, 50)
                break
        sleep(1)


def server_spawn():
    character_select_button = spawn_wait_until_loaded()
    sleep(5)
    toggle_collisions()
    change_characters(character_select_button)
    pydirectinput.moveTo(1, 1)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)
    pyautogui.hotkey('alt', 'tab')
    sleep(0.15)


def run_javascript_in_browser(url, js_code, esc_before_entering):
    executable_name = "chrome.exe"
    browser_path = os.path.join("C:\\", "Program Files (x86)", "Google", "Chrome", "Application", executable_name)
    if not os.path.exists(browser_path):
        browser_path = os.path.join("C:\\", "Program Files", "Google", "Chrome", "Application", executable_name)
    open_args = f"{url}"
    args = [browser_path, open_args]
    log("Launching Browser...")
    winsound.Beep(40, 25)
    log("Launched. Loading (8s)...")
    subprocess.Popen(args)
    sleep(8)
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
            if server["playing"] > highest_playercount_server["playing"]:
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


def check_if_should_change_servers(current_server_id="ERROR"):
    original_current_server_id = current_server_id
    log("Querying Roblox API for server list")
    url = f"https://games.roblox.com/v1/games/{globals.Roblox.game_id}/servers/Public?sortOrder=Asc&limit=10"
    response = requests.get(url)
    if response.status_code == 200:
        log("Finding best server and comparing to current...")

        response_result = response.json()
        servers = response_result["data"]
        highest_player_server = {"id": "", "maxPlayers": 100, "playing": 0, "fps": 59, "ping": 100}
        if current_server_id == "ERROR":
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


def get_current_server_id():
    instances_url = f"https://www.roblox.com/games/{globals.Roblox.game_id}/Become-Fumo#!/game-instances"
    file_name = f"{time.time()}.txt"
    check_js = """var gameID = "ERROR"; try { gameID = $(".rbx-game-server-item-container").first().find("[src*='""" + globals.Roblox.avatar_id + """']").parents("[data-gameid]").attr("data-gameid") } finally { const a = document.createElement("a"); const file = new Blob([gameID], {type: "text/plain"}); a.href= URL.createObjectURL(file); a.download = '""" + file_name + """'; a.click();URL.revokeObjectURL(a.href); }"""
    run_javascript_in_browser(instances_url, check_js, False)
    log("Opening Output File...")
    winsound.Beep(70, 100)
    file_path = os.path.join(Path.home(), "Downloads", file_name)
    current_server_id = "ERROR"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            current_server_id = f.read()
        if os.path.exists(file_path):
            os.remove(file_path)
    log("Returning Current Server ID...")
    winsound.Beep(70, 100)
    log("")
    return current_server_id


def discord_log(message, author, author_avatar, author_url):
    screenshot_filename = None
    if not globals.Roblox.action_running:
        screenshot_filename = take_screenshot()
    webhook_url = os.getenv("DISCORD_WEBHOOK_CHAT_CHANNEL")

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
    result = requests.post(webhook_url, json=webhook_data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"[Logged] {message}")

    # Send screenshot
    if screenshot_filename is not None:
        if os.path.exists(screenshot_filename):
            with open(screenshot_filename, "rb") as f:
                screenshot_binary = f.read()
            if os.path.exists(screenshot_filename):
                os.remove(screenshot_filename)
            requests.post(webhook_url, files={f"_{screenshot_filename}": (screenshot_filename, screenshot_binary)})
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as error:
                print(error)
            else:
                print(f"[Logged Screenshot] {message}")


def notify_admin(message):
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
    while current_server_id == "":
        log_process("Retrying better server check")
        sleep(5)
        current_server_id = get_current_server_id()
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
    inverted_direction = direction_obj["turn_camera_direction"]
    turn_time = direction_obj["turn_camera_time"]
    if inverted_direction == "left":
        direction = "right"
    elif inverted_direction == "right":
        direction = "left"
    else:
        direction = inverted_direction
        print(f"Could not invert camera direction '{inverted_direction}'!")

    check_active()
    sleep(0.5)
    pydirectinput.keyDown(direction)
    sleep(turn_time)
    pydirectinput.keyUp(direction)
    sleep(1)


def check_better_server_loop():
    while True:
        sleep(13 * 60)
        globals.Roblox.action_queue.append("check_for_better_server")


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
    event_end_time_struct = time.strptime(globals.OBS.event_end_time, "%Y-%m-%d %I:%M:%S%p")
    seconds_since_event = time.mktime(event_end_time_struct) - time.mktime(event_time_struct)
    english_time_since_event = get_english_timestamp(seconds_since_event)
    output_log("time_since_event", english_time_since_event)
    # while True:
    #    seconds_since_event = time.time() - time.mktime(event_time_struct)
    #    english_time_since_event = get_english_timestamp(seconds_since_event)
    #    with open("time_since_event.txt", "w") as f:
    #        f.write(english_time_since_event)
    #    sleep(1)


def clock_loop():
    while True:
        output_log("clock", time.strftime("%Y-%m-%d \n%I:%M:%S%p EST"))
        sleep(1)


def exploit_window_checker(ret_value, potential_names):
    from time import sleep
    import pyautogui
    import pydirectinput
    searching_for_window = True
    while searching_for_window:
        sleep(1)
        # for i in pyautogui.getAllTitles():
        #    print('"'+i+'"')
        # print("\n\n\n\n")

        for window in pyautogui.getAllWindows():
            if window.title in potential_names:
                searching_for_window = False
                ret_value.value = potential_names.index(window.title)
                while window.title in pyautogui.getAllTitles():
                    try:
                        print(f"Focusing on '{window.title}'")
                        window.focus()
                    except Exception:
                        print(f"ERROR IN FOCUSING ON '{window.title}'")
                    sleep(0.2)
                    try:
                        print(f"Activating '{window.title}'")
                        window.activate()
                    except Exception:
                        print(f"ERROR IN ACTIVATING '{window.title}'")
                    sleep(0.3)
                    pydirectinput.press("space")
                    sleep(0.3)
                break


def inject_lua(lua_code, attempts=0):
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


def load_exploit():
    print("loading exploit")
    original_directory = os.getcwd()
    injector_folder = os.path.join(globals.Roblox.injector_file_path)
    os.chdir(injector_folder)

    potential_names = [
        "Game Process Not Found",
        "NamedPipeExist!",
        "NamedPipeDoesntExist"
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
        if error_result == "Game Process Not Found":
            load_exploit()
            non_fatal_error = False
    if non_fatal_error:
        inject_lua("""setfflag("AbuseReportScreenshot", "False")
        setfflag("AbuseReportScreenshotPercentage", "0")""")
    return non_fatal_error


def test_teleport(location_name):
    winsound.Beep(40, 600)
    winsound.Beep(70, 400)
    chosen_location = globals.Roblox.teleport_locations[location_name]
    pos, rot, cam_rot = chosen_location["pos"], chosen_location["rot"], chosen_location["cam"]
    # noinspection LongLine
    inject_lua(f"""game.Players.LocalPlayer.Character:MoveTo(Vector3.new({pos}))
    game.Players.LocalPlayer.Character.PrimaryPart.CFrame = CFrame.new(game.Players.LocalPlayer.Character.PrimaryPart.Position) * CFrame.Angles({rot})
    workspace.CurrentCamera.CFrame = CFrame.new(workspace.CurrentCamera.CFrame.Position) * CFrame.Angles({cam_rot})""")
    winsound.Beep(90, 300)


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
    # noinspection LongLine
    inject_lua(f"""game.Players.LocalPlayer.Character:MoveTo(Vector3.new({pos}))
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
        # noinspection LongLine
        inject_lua(f"""game.Players.LocalPlayer.Character:MoveTo(Vector3.new({pos}))
    game.Players.LocalPlayer.Character.PrimaryPart.CFrame = CFrame.new(game.Players.LocalPlayer.Character.PrimaryPart.Position) * CFrame.Angles({rot})
    workspace.CurrentCamera.CFrame = CFrame.new(workspace.CurrentCamera.CFrame.Position) * CFrame.Angles({cam_rot})""")
    else:
        cfg.current_location = location_name
    log("", no_log)
    log_process("", no_log)
    if cfg.current_emote != "":
        send_chat(cfg.current_emote)
    return True


def print_pos():
    inject_lua(f"""
    print("\\n\\n")
    print("Position:",game.Players.LocalPlayer.Character.PrimaryPart.Position)""")


def test_cam():
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
        cfg.next_possible_teleport = 0
        cfg.action_queue.append("spectate")
        cfg.action_queue.append({"tp": cfg.current_location})


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
    # noinspection LongLine
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
                game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Could not teleport to player! (Would get stuck on roof of world)]" , "All")
                break
            else 
                game:GetService("ReplicatedStorage").DefaultChatSystemChatEvents.SayMessageRequest:FireServer("[Hello! Someone on T witch asked me to teleport to you.]" , "All")
            end
            break
        end
    end
    workspace.CurrentCamera.CameraSubject = game.Players.LocalPlayer.Character:FindFirstChildOfClass("Humanoid")
    """)
    winsound.Beep(90, 300)
    sleep(1)
    if cfg.current_emote != "":
        send_chat(cfg.current_emote)

    log("")
    log_process("")
    return True


def spectate_random():
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
    setGravity(part, 0.001)
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


class TwitchBot(irc.bot.SingleServerIRCBot):
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

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        print('Joined ' + self.channel)

    def on_pubmsg(self, c, e):
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

    def do_command(self, e, cmd, args, author):
        cfg = globals.Roblox
        c = self.connection
        is_dev = author.lower() in globals.Twitch.admins
        is_owner = author.lower() == "scary08rblx"
        if cmd == "rejoin" and is_dev:
            cfg.action_queue.append("handle_crash")
        elif (cmd == "handle_join_new_server" or cmd == "handle_crash") and is_dev:
            cfg.action_queue.append(cmd)
        elif cmd == "spectate":
            cfg.action_queue.append("spectate")
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
                if number <= 1:
                    turn_time = number
            except Exception:
                pass
            cfg.action_queue.append({"turn_camera_direction": cmd, "turn_camera_time": turn_time})
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


def commands_loop():
    cfg = globals.Roblox
    commands_list = [
        {
            "command": "!m Your Message",
            "help": "Sends \"Your Message\" in-game"
        },
        {
            "command": "!tp LocationName",
            "help": f"Teleport. \n({', '.join(cfg.teleport_locations)})"
        },
        {
            "command": "!goto PlayerName",
            "help": "Teleports to a player by that name."
        },
        {
            "command": "!spectate",
            "help": "Spectates up to 10 random players."
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
            "command": "!dev Your Message",
            "help": "Sends \"Your Message\" to devs discord account, USE IF CAM IS DOWN"
        },
    ]
    while True:
        for command in commands_list:
            output_log("commands_help_label", "")
            output_log("commands_help_title", "")
            output_log("commands_help_desc", "")

            sleep(0.25)
            current_command_in_list = f"{(commands_list.index(command) + 1)}/{len(commands_list)}"
            output_log("commands_help_label", f"TWITCH CHAT COMMANDS [{current_command_in_list}]")
            output_log("commands_help_title", command["command"])
            sleep(0.1)
            output_log("commands_help_desc", command["help"])
            sleep(10)


def process_queue():
    cfg = globals.Roblox
    while True:
        sleep(0.1)
        if cfg.action_running:
            continue
        if len(cfg.action_queue) > 0:
            action = cfg.action_queue[0]
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
                cfg.action_running = True
                check_for_better_server()
                check_active()
                cfg.action_running = False
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
            else:
                print("queue failed")

            cfg.action_queue.pop(0)
            sleep(1)


def main():
    log_process("")
    log("")
    output_log("change_server_status_text", "")

    check_active()
    thread_functions = [process_queue, check_better_server_loop, twitch_main, anti_afk, commands_loop, timer_loop,
                        clock_loop, crash_check_loop, spectate_loop]
    for thread_function in thread_functions:
        threading.Thread(target=thread_function).start()
    if "Roblox" not in pyautogui.getAllTitles():
        globals.Roblox.action_queue.append("handle_crash")


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    # load_exploit()
    main()
    # twitch_main()
    # character_select_button = spawn_wait_until_loaded()
    # change_characters(character_select_button)
    # check_for_better_server()
    # print(get_current_server_id())
    # test_cam()
    # test_teleport("miko")
    # teleport("comedy2")
