import os
from asyncio import sleep as async_sleep
from math import floor
from subprocess import call as call_proc  # nosec
from time import sleep, strftime, time
from traceback import format_exc
from typing import Union

from mss import mss
from psutil import process_iter
from pydirectinput import press as press_key
from pygetwindow import getActiveWindow, getAllWindows
from requests import post
from requests.exceptions import HTTPError

from config import CFG, OBS, Discord


def check_admin_and_run() -> bool:
    from ctypes import windll as a_windll
    from sys import argv as a_argv
    from sys import executable as a_executable
    from traceback import format_exc as a_formatexc

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
            a_windll.shell32.ShellExecuteW(
                None, "runas", a_executable, run_path, None, 1
            )
        except Exception:
            print(a_formatexc())
        return False
    else:
        print("Administrator access acquired.")
        return True


def run_as_admin():
    is_admin = check_admin_and_run()
    if not is_admin:
        print("NOT ADMIN, EXITING")
        exit()


def error_log(error_msg: str, file_name: str = "_errors"):
    if not os.path.exists(OBS.output_folder):
        os.mkdir(OBS.output_folder)
    file_path = os.path.join(OBS.output_folder, f"{file_name}.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")
    entry_timestamp = strftime("%Y-%m-%d %I:%M:%S%p EST")
    entry = f"[{entry_timestamp}]\n{error_msg}\n\n\n\n"
    with open(file_path, "a") as f:
        f.write(entry)


def output_log(file_name: str, message: str):
    if not os.path.exists(OBS.output_folder):
        os.mkdir(OBS.output_folder)
    file_path = os.path.join(OBS.output_folder, f"{file_name}.txt")
    with open(file_path, "w") as f:
        f.write(str(message))


def log(status: str, no_log: bool = False):
    print(status)
    if no_log:
        return
    output_log("main_status", status)


def get_log() -> str:
    return read_output_log("main_status")


def log_process(process: str, no_log: bool = False):
    process = f"[{process}]" if process.strip() != "" else ""
    print(process)
    if no_log:
        return
    output_log("main_process", process)
    sleep(0.1)


def get_log_process() -> str:
    return read_output_log("main_process")


def read_output_log(file_name: str) -> str:
    if not os.path.exists(OBS.output_folder):
        return "ERROR: Path does not exist"
    file_path = os.path.join(OBS.output_folder, f"{file_name}.txt")
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception:
        print(format_exc())
        return f"ERROR: {format_exc()}"


async def take_screenshot() -> str:
    file_name = f"{time()}.png"
    with mss() as sct:
        await check_active()
        await async_sleep(0.25)
        sct.shot(mon=-1, output=file_name)
    return file_name


async def take_screenshot_binary():
    with mss() as sct:
        screenshot = sct.grab(CFG.screen_res["mss_monitor"])
    return screenshot


def kill_process(executable: str = "RobloxPlayerBeta.exe", force: bool = False):
    # TODO: taskkill.exe can fail, how can we kill the thing that should kill? https://i.imgur.com/jd01ZOv.png
    process_call = ["taskkill"]
    if force:
        process_call.append("/F")
    process_call.append("/IM")
    process_call.append(executable)
    call_proc(process_call)  # nosec


async def check_active(
    title: str = "Roblox", title_ending: str = None, force_fullscreen: bool = True
):
    print(f"[check_active] {title} | {title_ending}")
    active_window = getActiveWindow()
    if active_window is not None:
        title_active = title_ending is None and active_window.title == title
        title_ending_active = title_ending is not None and active_window.title.endswith(
            title_ending
        )
        if title_active or title_ending_active:
            if (
                title == "Roblox"
                and active_window.height != CFG.screen_res["height"]
                and force_fullscreen
            ):
                print(active_window)
                while active_window.height != CFG.screen_res["height"]:
                    press_key("f11")
                    print("Maximizing window with F11")
                    await async_sleep(0.3)
                await check_active(title)
            print(f"{active_window.title} already active")
            return
    for window in getAllWindows():
        title_active = title_ending is None and window.title == title
        title_ending_active = title_ending is not None and window.title.endswith(
            title_ending
        )
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
            elif (
                title == "Roblox"
                and window.height != CFG.screen_res["height"]
                and force_fullscreen
            ):
                while window.height != CFG.screen_res["height"]:
                    press_key("f11")
                    print("Maximizing window with F11")
                await check_active(title)


def notify_admin(
    message: str,
) -> bool:  # TODO: Make !dev a seperate, always-running process
    webhook_url = os.getenv("DISCORD_WEBHOOK_DEV_CHANNEL", None)
    if webhook_url is None:
        return False
    webhook_data = {
        "content": f"<@{os.getenv('DISCORD_OWNER_ID')}>\n{message}",
        "username": Discord.webhook_username,
    }
    result = post(webhook_url, json=webhook_data)
    try:
        result.raise_for_status()
    except HTTPError as err:
        print(err)
    else:
        print(f"[Dev Notified] {message}")
    return True


def get_english_timestamp(time_var: Union[float, int]) -> str:
    original_time = time_var
    seconds_in_minute = 60
    seconds_in_hour = 60 * seconds_in_minute
    seconds_in_day = 24 * seconds_in_hour
    days = floor(time_var / seconds_in_day)
    time_var -= days * seconds_in_day
    hours = floor(time_var / seconds_in_hour)
    time_var -= hours * seconds_in_hour
    minutes = floor(time_var / seconds_in_minute)
    time_var -= minutes * seconds_in_minute
    seconds = round(time_var)
    hours = floor(original_time / seconds_in_hour) % 24
    return "{}d:{}h:{}m:{}s".format(days, hours, minutes, seconds)


async def do_crash_check(do_notify=True) -> bool:
    crashed = not (is_process_running(CFG.game_executable_name))
    if not crashed:  # Check if still open, but hanged with seperate "crash" dialog
        for window in getAllWindows():
            if (
                window.title == "Crash"
                or window.title == "Roblox Crash"
                or window.title == "Crashed"
            ):
                crashed = True
                window.close()
    if crashed:
        CFG.crashed = True
        if do_notify:
            notify_admin("Roblox Crash")
    return crashed


async def discord_log(
    message: str, author: str, author_avatar: str, author_url: str
) -> bool:
    success = False
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
                    "icon_url": author_avatar,
                },
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
        if webhook_url is None:
            continue

        result = post(webhook_url, json=webhook_data)
        try:
            result.raise_for_status()
        except HTTPError as err:
            print(err)
            success = False
        else:
            print(f"[Logged] {message}")

        # Send screenshot
        if screenshot_binary is not None:
            post(
                webhook_url,
                files={
                    f"_{screenshot_filename}": (screenshot_filename, screenshot_binary)
                },
            )
            try:
                result.raise_for_status()
            except HTTPError as error:
                print(error)
                success = False
            else:
                print(f"[Logged Screenshot] {message}")
    return success


def is_process_running(name: str) -> bool:
    return len([proc for proc in process_iter() if proc.name() == name]) > 0
