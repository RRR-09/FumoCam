from config import *
import os
from time import sleep,time,strftime,strptime,mktime
from asyncio import sleep as async_sleep
from traceback import format_exc
import pyautogui  # pip3.9 install pygetwindow (allows additional functionality in pyautogui)
import pydirectinput
import subprocess
import requests
import math
import psutil

def check_admin_and_run():
    from sys import executable as a_executable, argv as a_argv
    from ctypes import windll as a_windll
    from traceback import format_exc as a_fe

    try:
        is_not_admin = not (a_windll.shell32.IsUserAnAdmin())
    except Exception:
        is_not_admin = True
    if is_not_admin:
        print("Packages missing, auto-installing.")
        print("Administrator access required. Acquiring...")
        try:
            run_path = ""
            for i, item in enumerate(a_argv[0:]):
                run_path += f'"{item}"'
            a_windll.shell32.ShellExecuteW(None, "runas", a_executable, run_path, None, 1)
            return False
        except Exception:
            print(a_fe())
    else:
        print("Administrator access acquired.")
        return True


def run_as_admin():
    is_admin = check_admin_and_run()
    if not is_admin:
        print("NOT ADMIN, EXITING")
        exit()


def output_log(file_name, message):
    if not os.path.exists(OBS.output_folder):
        os.mkdir(OBS.output_folder)
    file_path = os.path.join(OBS.output_folder, f"{file_name}.txt")
    with open(file_path, "w") as f:
        f.write(str(message))


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


def read_output_log(file_name):
    if not os.path.exists(OBS.output_folder):
        return "ERROR: Path does not exist"
    file_path = os.path.join(OBS.output_folder, f"{file_name}.txt")
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception:
        print(format_exc())
        return f"ERROR: {format_exc()}"


async def take_screenshot():
    file_name = f"{time()}.png"
    with mss() as sct:
        await check_active()
        await async_sleep(0.25)
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


async def check_active(title="Roblox", title_ending=None):
    print(f"[check_active] {title} | {title_ending}")
    active_window = pyautogui.getActiveWindow()
    if active_window is not None:
        title_active = title_ending is None and active_window.title == title
        title_ending_active = title_ending is not None and active_window.title.endswith(title_ending)
        if title_active or title_ending_active:
            if title == "Roblox" and active_window.height != pyautogui.size()[1]:
                print(active_window)
                while active_window.height != pyautogui.size()[1]:
                    pydirectinput.press("f11")
                    print("Maximizing window with F11")
                    await async_sleep(0.3)
                await check_active(title)
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
            print("[check_active] Switched - Waiting")
            await async_sleep(0.3)
            print("[check_active] Switched - Done Waiting")
            if title_ending is not None:
                await check_active(title_ending=title_ending)
                print("Recurse")
            elif title == "Roblox" and window.height != pyautogui.size()[1]:
                while window.height != pyautogui.size()[1]:
                    pydirectinput.press("f11")
                    print("Maximizing window with F11")
                await check_active(title)


def notify_admin(message):  # todo: Seperate always-running process
    webhook_url = os.getenv("DISCORD_WEBHOOK_DEV_CHANNEL")
    webhook_data = {
        "content": f"<@{os.getenv('DISCORD_OWNER_ID')}>\n{message}",
        "username": Discord.webhook_username
    }
    result = requests.post(webhook_url, json=webhook_data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f"[Dev Notified] {message}")


async def alt_tab_click(click_mouse=True):
    """
    Even pydirectinput cant click normally.
    This is a work-around that actually clicks in the area the cursor was moved.
    """
    alt_tab_duration = 0.3
    pyautogui.hotkey('alt', 'tab')
    await async_sleep(alt_tab_duration)
    pyautogui.hotkey('alt', 'tab')
    await async_sleep(alt_tab_duration)
    if click_mouse:
        pydirectinput.mouseDown()
        pydirectinput.mouseUp()


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


async def do_crash_check(do_notify=True):
    crashed = False
    for window in pyautogui.getAllWindows():
        if window.title == "Crash" or window.title == "Roblox Crash" or window.title == "Crashed":
            crashed = True
            window.close()
    if crashed:
        if do_notify:
            notify_admin("Roblox Crash")
        await CFG.add_action_queue("handle_crash")
    return crashed


async def discord_log(message, author, author_avatar, author_url):
    screenshot_filename = None
    if not CFG.action_running:
        screenshot_filename = await take_screenshot()
    webhook_urls = [
        os.getenv("DISCORD_WEBHOOK_CHAT_CHANNEL"),
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


def is_process_running(name):
    return len([proc for proc in psutil.process_iter() if proc.name() == "RobloxPlayerBeta.exe"]) > 0