import os
from dotenv import load_dotenv  # pip3.9 install python-dotenv
from pyautogui import size as get_monitor_size
from mss import mss
from pathlib import Path

load_dotenv()
RESOURCES_PATH = Path.cwd().parent / "resources"
SCREEN_RES = {  # todo: Don't use globals, make class-based
    "width": get_monitor_size()[0],
    "height": get_monitor_size()[1],
    "x_multi": get_monitor_size()[0] / 2560,
    "y_multi": get_monitor_size()[1] / 1440,
}
MONITOR_SIZE = mss().monitors[0]


class Twitch:
    channel_name = "becomefumocam"
    username = "BecomeFumoBot"
    admins = ["becomefumocam", os.getenv("OWNER_USERNAME")]


class OBS:
    output_folder = Path.cwd().parent / "output"
    event_time = "2021-06-09 12:05:00AM"
    event_end_time = "2021-05-03 10:23:18PM"


class Discord:
    webhook_username = "BecomeFumoCam"


class MainBotConfig:
    action_queue = []
    action_running = False
    advertisement = [
        "This bot is live on T witch! Go to the roblox profile for a link or Google",
        '"BecomeFumoCam"!'
    ]
    censored_words = [  # todo: Attempt to inject into chat censor API
        "gay",
        "nigger",
        "nheggar",
        "ninggrer",
        "fhucqing",
        "simp",
        "s!mp",
        "jjgay",
        "niggaHomosexual",
    ]
    character_select_image_path = os.path.join(RESOURCES_PATH, "character_select.png")
    character_select_scroll_down_amount = 14
    character_select_scroll_down_scale = -200
    character_select_screen_height_to_click = 0.58
    character_select_scroll_speed = 0.2
    
    chat_name_sleep_factor = 0.05  # Seconds to wait per char in users name before sending their message
    
    browser_driver_executable_name = "chromedriver.exe"
    browser_driver_path = RESOURCES_PATH / browser_driver_executable_name
    browser_executable_name = "chrome.exe"
    browser_profile_path = RESOURCES_PATH / ".browser_profile"
    Path(browser_profile_path).mkdir(parents=True, exist_ok=True)
    browser_cookies_path = browser_profile_path / "browser_cookies.json"
    
    
    current_emote = "/e dance3"
    event_timer_running = False
    disable_collisions_on_spawn = True
    game_executable_name = "RobloxPlayerBeta.exe"
    game_id = 6238705697
    game_id_nil = 7137029060
    game_id_hinamizawa = 6601613056
    game_instances_url = "https://www.roblox.com/games/6238705697/Become-Fumo#!/game-instances"
    max_attempts_character_selection = 30
    max_attempts_sit_button = 3
    max_seconds_browser_launch = 5
    player_token = "BD7F4C1D8063321CDFE702866B105EFB"
    respawn_character_select_offset = -0.1
    sit_button_position = (0.79, 0.89)
    tick_rate = 0.25
    tick_rate_blocked = 0.1


CFG = MainBotConfig()  # Instantiate the config for use between files
