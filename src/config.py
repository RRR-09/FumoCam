import json
import os
import sqlite3
from pathlib import Path
from re import compile as re_compile
from time import time
from typing import Dict, List

from dotenv import dotenv_values, load_dotenv
from mss import mss
from pyautogui import size as get_monitor_size

# TODO: This is a mess of config vars, utility functions, and statelike variables. Cleanup needed

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

    chat_bracket_like_chars = ["|", "!", "l", "I"]
    chat_bracket_like_chars_left = chat_bracket_like_chars + ["[", "{", "("]
    chat_bracket_like_chars_right = chat_bracket_like_chars + ["]", "}", ")"]
    chat_db = sqlite3.connect(OBS.output_folder / "chat_messages.sqlite")
    chat_db_cursor = chat_db.cursor()
    chat_db_tables = [
        "CREATE TABLE messages(time REAL, time_friendly TEXT, author TEXT, message TEXT, author_confidence REAL)",
        "CREATE TABLE interactions("
        "time REAL, time_friendly TEXT, author TEXT, message TEXT, response TEXT, author_confidence REAL)",
    ]
    try:
        for query in chat_db_tables:
            chat_db_cursor.execute(query)
    except Exception:  # nosec
        pass  # TODO: figure out db-exists exception

    chat_block_functions = ["anti_afk"]
    chat_cleared_after_response = (
        True  # False when sending OCR messages and haven't send /clear
    )
    chat_dimensions = screen_res["mss_monitor"].copy()
    chat_dimensions["top"] = int(screen_res["height"] * 0.05)
    chat_dimensions["width"] = int(screen_res["width"] * 0.29)
    chat_dimensions["height"] = int(screen_res["height"] * 0.22)
    chat_fuzzy_threshold = (
        0.80  # Minimum similarity ratio to consider a message as already-captured
    )
    chat_idle_time_required = 30  # Seconds with no activity to activate
    chat_ignore_functions = [
        "ocr_chat",
        "check_for_better_server",
        "activate_ocr",
    ]
    chat_last_non_idle_time = time()
    chat_message_corrections = {"[e": "/e"}
    chat_messages_in_memory: List[Dict] = []
    chat_ocr_active = False
    chat_ocr_activation_queued = False  # True when ocr_active False, but queued
    chat_ocr_ready = True  # Ready for another OCR loop (False when OCR loop running)
    chat_start_ocr_time = time()

    character_select_button_position = {"x": screen_res["center_x"], "y": 40}
    character_select_scroll_position = {
        "x": screen_res["center_x"],
        "y": screen_res["center_y"],
    }
    character_select_scroll_down_amount = 0
    character_select_scroll_down_scale = -200
    character_select_screen_height_to_click = 0
    character_select_scroll_speed = 0.2

    character_select_initial = "Alice"
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
        character_select_screen_height_to_click = prev_char_select[
            "desired_character_height"
        ]
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
    max_attempts_game_loaded = 50
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
    respawn_character_select_offset = 0.1

    regex_alpha = re_compile("[^a-zA-Z]")

    settings_menu_image_path = os.path.join(resources_path, "gear.jpg")
    settings_menu_width = 0.3
    settings_menu_grief_text = "grief"
    settings_menu_grief_label = "Anti-Grief"

    settings_menu_positions = {}
    settings_menu_positions_path = OBS.output_folder / "settings_menu_positions.json"
    try:
        with open(settings_menu_positions_path, "r") as f:
            settings_menu_positions = json.load(f)
    except Exception:
        print(f"{settings_menu_positions_path} malformed or missing")

    settings_button_position = {
        "x": screen_res["center_x"],
        "y": screen_res["height"] - 40,
    }
    settings_menu_max_find_attempts = 3
    settings_menu_find_threshold = 0.50
    settings_menu_max_click_attempts = 2
    settings_menu_button_height = 0.065
    settings_menu_ocr_max_attempts = 2

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
    twitch_chatters_path = OBS.output_folder / "twitch_chatters.json"
    try:
        with open(twitch_chatters_path, "r") as f:
            twitch_chatters_list = json.load(f)
            twitch_chatters = set(twitch_chatters_list)
    except Exception:
        print(f"{twitch_chatters_path} malformed or missing")

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

    # Window area for settings menu
    window_settings = screen_res["mss_monitor"].copy()
    window_settings_horizontal_offset = int(0.13 * screen_res["width"])
    window_settings["left"] += window_settings_horizontal_offset
    window_settings["width"] -= window_settings_horizontal_offset * 2
    window_settings_vertical_offset = int(0.15 * screen_res["height"])
    window_settings["top"] += window_settings_vertical_offset
    window_settings["height"] -= window_settings_vertical_offset * 2

    # Window area for character select
    window_character = screen_res["mss_monitor"].copy()
    window_character_horizontal_offset = int(0.33 * screen_res["width"])
    window_character["left"] += window_character_horizontal_offset
    window_character["width"] -= window_character_horizontal_offset * 2
    window_character_top_offset = int(0.31 * screen_res["height"])
    window_character["top"] += window_character_top_offset
    window_character_bottom_offset = int(0.14 * screen_res["height"])
    window_character["height"] -= (
        window_character_top_offset + window_character_bottom_offset
    )

    # Window area for backpack
    window_backpack = screen_res["mss_monitor"].copy()
    window_backpack_horizontal_offset = int(0.14 * screen_res["width"])
    window_backpack["left"] += window_backpack_horizontal_offset
    window_backpack["width"] -= window_backpack_horizontal_offset * 2
    window_backpack_vertical_offset = int(0.137 * screen_res["height"])
    window_backpack["top"] += window_backpack_vertical_offset
    window_backpack["height"] -= window_backpack_vertical_offset * 2

    # Window area for white pixels on UI element to indicate fully loaded
    window_ui_loaded = screen_res["mss_monitor"].copy()
    window_ui_loaded_horizontal_offset = int(screen_res["center_x"]) - 5
    window_ui_loaded["left"] += window_ui_loaded_horizontal_offset
    window_ui_loaded["width"] -= window_ui_loaded_horizontal_offset * 2
    window_ui_loaded_vertical_offset = int(0.045 * screen_res["height"])
    window_ui_loaded["top"] += window_ui_loaded_vertical_offset
    window_ui_loaded["height"] = window_ui_loaded_vertical_offset + 2

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
