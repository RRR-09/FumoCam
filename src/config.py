import json
import os
from pathlib import Path
from typing import Dict, List

from dotenv import dotenv_values, load_dotenv
from mss import mss
from pyautogui import size as get_monitor_size

load_dotenv(".env", verbose=True)


def check_dotenv():
    try:
        for dotenv_key in list(dotenv_values(".env.default").keys()):
            print(f"[DotEnv] Checking {dotenv_key}")
            if os.getenv(dotenv_key) is None:
                raise IndexError
    except Exception as e:
        print(e)
        raise Exception("Could not validate .env file! Does it exist/have all values?")


check_dotenv()


class Twitch:
    channel_name = os.getenv("TWITCH_CHAT_CHANNEL")
    username = "BecomeFumoCamBot"
    admins = ["becomefumocam", os.getenv("TWITCH_OWNER_USERNAME")]


class OBS:
    output_folder = Path.cwd().parent / "output"
    event_time = "2021-06-09 12:05:00AM"
    event_end_time = "2021-05-03 10:23:18PM"
    muted_icon_name = "muted_icon.png"


class Discord:
    webhook_username = "BecomeFumoCam"


class ActionQueueItem:
    def __init__(self, name: str, values: dict = {}):
        self.name = name
        self.values = values


class BlockedMouseRegion:
    def __init__(self, name: str, x1: int, y1: int, x2: int, y2: int):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


class MainBotConfig:
    resources_path = Path.cwd().parent / "resources"
    screen_res = {  # todo: Don't use globals, make class-based
        "width": get_monitor_size()[0],
        "height": get_monitor_size()[1],
        "x_multi": get_monitor_size()[0] / 2560,
        "y_multi": get_monitor_size()[1] / 1440,
        "center_x_float": get_monitor_size()[0] / 2,
        "center_y_float": get_monitor_size()[1] / 2,
        "center_x": int(get_monitor_size()[0] / 2),
        "center_y": int(get_monitor_size()[1] / 2),
        "mss_monitor": mss().monitors[-1],
    }

    action_queue: List[ActionQueueItem] = []
    action_running = False
    advertisement = [
        "This bot is live on T witch! Go to its Roblox profile for a link, or Google:",
        '"BecomeFumosCam"',
    ]
    audio_muted = False
    backpack_button_position = (0.87, 0.89)
    backpack_item_positions = {
        1: {"x": 0.26, "y": 0.35},
        2: {"x": 0.41, "y": 0.35},
        3: {"x": 0.56, "y": 0.35},
        4: {"x": 0.71, "y": 0.35},
        5: {"x": 0.26, "y": 0.6},
        6: {"x": 0.41, "y": 0.6},
        7: {"x": 0.56, "y": 0.6},
        8: {"x": 0.71, "y": 0.6},
    }
    backpack_open = False
    browser_driver_executable_name = "chromedriver.exe"
    browser_driver_path = resources_path / browser_driver_executable_name
    browser_executable_name = "chrome.exe"
    browser_profile_path = resources_path / ".browser_profile"
    Path(browser_profile_path).mkdir(parents=True, exist_ok=True)
    browser_cookies_path = browser_profile_path / "browser_cookies.json"

    censored_words = [  # TODO: Attempt to inject into chat censor API
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
    character_select_image_path = os.path.join(resources_path, "character_select.png")
    character_select_scroll_down_amount = 0
    character_select_scroll_down_scale = -200
    character_select_screen_height_to_click = 0
    character_select_scroll_speed = 0.2

    character_select_desired = "Momiji"
    character_select_width = 0.28
    character_select_button_height = 0.035
    character_select_scan_attempts = 3
    character_select_max_scroll_attempts = 100
    character_select_max_close_attempts = 10
    character_select_max_click_attempts = 10

    try:
        with open(OBS.output_folder / "character_select.json", "r") as f:
            prev_char_select = json.load(f)
        character_select_screen_height_to_click = (
            prev_char_select["desired_character_height"] / screen_res["height"]
        )
        character_select_scroll_down_amount = prev_char_select["scroll_amount"]
    except Exception:
        print(f"{OBS.output_folder / 'character_select.json'} malformed or missing")

    chat_name_sleep_factor = (
        0.05  # Seconds to wait per char in users name before sending their message
    )

    crashed = False

    collisions_disabled = True
    current_emote = "/e dance3"
    event_timer_running = False
    epoch_time = 1616817600
    disable_collisions_on_spawn = True
    game_executable_name = "RobloxPlayerBeta.exe"
    game_id = 6238705697
    game_ids_other: Dict[int, str] = {  # Do not check for better servers in these
        7137029060: "Nil",
        6601613056: "Hinamizawa",
        8129913919: "Lenen",
    }
    game_instances_url = (
        "https://www.roblox.com/games/6238705697/Become-Fumo#!/game-instances"
    )

    help_url = os.getenv("HELP_URL")

    max_attempts_better_server = 20
    max_attempts_character_selection = 30
    max_attempts_game_loaded = 20
    max_attempts_sit_button = 3
    max_seconds_browser_launch = 20

    mouse_software_emulation = True
    mouse_blocked_regions = [
        BlockedMouseRegion(name="Chat", x1=0, y1=0, x2=340, y2=240),
        BlockedMouseRegion(name="Character Select", x1=420, y1=0, x2=850, y2=80),
        BlockedMouseRegion(
            name="Settings/Bottom-Right Buttons", x1=0, y1=580, x2=1280, y2=720
        ),
        BlockedMouseRegion(name="Leaderboard", x1=1100, y1=0, x2=1280, y2=720),
    ]
    mouse_blocked_safety_padding = 10
    nav_locations = {
        "shrimp": {"name": "Shrimp Tree"},
        "ratcade": {"name": "Ratcade"},
        "train": {"name": "Train Station"},
        "classic": {"name": "'BecomeF umo: Classic' Portal"},
        "treehouse": {"name": "Funky Treehouse"},
    }
    nav_post_zoom_in = {
        "treehouse": 50,
        "train": 0,
    }
    player_id = os.getenv("PLAYER_ID")
    player_switch_cap = 50
    player_difference_to_switch = 20
    pytesseract_path = os.path.join(
        "C:\\", "Program Files", "Tesseract-OCR", "tesseract.exe"
    )
    respawn_character_select_offset = -0.1

    settings_menu_image_path = os.path.join(resources_path, "gear.jpg")
    settings_menu_width = 0.3
    settings_menu_grief_text = "Anti-Grief"
    settings_menu_max_find_attempts = 3
    settings_menu_find_threshold = 0.70
    settings_menu_max_click_attempts = 10
    settings_menu_button_height = 0.065
    settings_menu_ocr_max_attempts = 3

    sit_button_position = (0.79, 0.89)
    sitting_status = False

    twitch_blacklist = []
    twitch_blacklist_path = OBS.output_folder / "twitch_blacklist.json"
    try:
        with open(str(twitch_blacklist_path), "r") as f:
            twitch_blacklist = json.load(f)
    except Exception:
        print(f"{twitch_blacklist_path} malformed or missing")

    twitch_chatters = set()
    try:
        with open(OBS.output_folder / "twitch_chatters.json", "r") as f:
            twitch_chatters = json.load(f)
    except Exception:
        print(f"{OBS.output_folder / 'twitch_chatters.json'} malformed or missing")

    updates_url = os.getenv("HASHNODE_UPDATES_URL")

    sound_control_executable_name = "SoundVolumeView.exe"
    vlc_path = Path("C:\\", "Program Files", "VideoLAN", "VLC")
    vlc_executable_name = "vlc.exe"

    vip_twitch_names = [
        "ceatidk",
        "initialo",
        "dedegiko",
        "maplemedictv",
        "becomefumocam",
    ]

    zoom_default: float = 30
    zoom_level: float = 50  # TODO: validate this is roughly correct on spawn
    zoom_max: float = 100
    zoom_min: float = 0
    zoom_ui_min: float = 30  # If lower, zoom out when interacting with UI (No CV needed, just get out of first person)
    zoom_out_ui: float = 10  # Amount to zoom out when interacting with UI (No CV needed, just get out of first person)
    zoom_ui_min_cv: float = (
        50  # If lower, zoom out when interacting with UI (Computervision)
    )
    zoom_out_ui_cv: float = (
        50  # Amount to zoom out for safety when interacting with UI (Computervision)
    )

    async def add_action_queue(self, item: ActionQueueItem):
        print("Attempted to add action queue item too early!")
        print(item)


CFG = MainBotConfig()  # Instantiate the config for use between files
