import os
from dotenv import load_dotenv  # pip3.9 install python-dotenv
from pyautogui import size as get_monitor_size
from pyautogui import position as get_mouse_position
from mss import mss
from pathlib import Path
from shutil import copyfile
import json
import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.path.join("C:\\", "Program Files", "Tesseract-OCR", "tesseract.exe")

load_dotenv()
RESOURCES_PATH = Path.cwd().parent / "resources"
SCREEN_RES = {  # todo: Don't use globals, make class-based
    "width": get_monitor_size()[0],
    "height": get_monitor_size()[1],
    "x_multi": get_monitor_size()[0] / 2560,
    "y_multi": get_monitor_size()[1] / 1440,
    "center_x_float": get_monitor_size()[0]/2,
    "center_y_float": get_monitor_size()[1]/2,
    "center_x": int(get_monitor_size()[0]/2),
    "center_y": int(get_monitor_size()[1]/2),
}
MONITOR_SIZE = mss().monitors[0]


class Twitch:
    channel_name = "becomefumocam"
    username = "BecomeFumoCamBot"
    admins = ["becomefumocam", os.getenv("OWNER_USERNAME")]
    


class OBS:
    output_folder = Path.cwd().parent / "output"
    event_time = "2021-06-09 12:05:00AM"
    event_end_time = "2021-05-03 10:23:18PM"
    muted_icon_name = "muted_icon.png"


class Discord:
    webhook_username = "BecomeFumoCam"


class MainBotConfig:
    action_queue = []
    action_running = False
    advertisement = [
        "This bot is live on T witch! Go to the roblox profile for a link or Google",
        '"BecomeFumoCam"!'
    ]
    audio_muted = False
    
    twitch_blacklist = []
    twitch_blacklist_path = OBS.output_folder / 'twitch_blacklist.json'
    try:
        with open(str(twitch_blacklist_path), "r") as f:
            twitch_blacklist = json.load(f)
    except:
        print(f"{twitch_blacklist_path} malformed or missing")
    
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
    browser_driver_path = RESOURCES_PATH / browser_driver_executable_name
    browser_executable_name = "chrome.exe"
    browser_profile_path = RESOURCES_PATH / ".browser_profile"
    Path(browser_profile_path).mkdir(parents=True, exist_ok=True)
    browser_cookies_path = browser_profile_path / "browser_cookies.json"
    
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
        character_select_screen_height_to_click = prev_char_select["desired_character_height"] / SCREEN_RES["height"]
        character_select_scroll_down_amount = prev_char_select["scroll_amount"]
    except:
        print(f"{OBS.output_folder / 'character_select.json'} malformed or missing")
    
    
    chat_name_sleep_factor = 0.05  # Seconds to wait per char in users name before sending their message
    chat_bypasses = {}  # Bypass filters for harmless words
    
    crashed = False
    
    collisions_disabled = True
    current_emote = "/e dance3"
    event_timer_running = False
    epoch_time = 1616817600
    disable_collisions_on_spawn = True
    game_executable_name = "RobloxPlayerBeta.exe"
    game_id = 6238705697
    game_id_nil = 7137029060
    game_id_hinamizawa = 6601613056
    game_id_lenen = 8129913919
    game_instances_url = "https://www.roblox.com/games/6238705697/Become-Fumo#!/game-instances"
    max_attempts_character_selection = 30
    max_attempts_sit_button = 3
    max_seconds_browser_launch = 20
    max_attempts_better_server = 20
    mouse_software_emulation = True
    mouse_blocked_regions = [
        {"name": "Chat", "x1": 0, "y1": 0, "x2":340, "y2":240},
        {"name": "Character Select", "x1": 420, "y1": 0, "x2":850, "y2":80},
        {"name": "Settings/Bottom-Right Buttons", "x1": 0, "y1": 580, "x2":1280, "y2":720},
        {"name": "Leaderboard", "x1": 1100, "y1": 0, "x2":1280, "y2":720},
        
    ]
    nav_locations = {
        "shrimp": {"name": "Shrimp Tree"},
        "ratcade": {"name": "Ratcade"},
        "train": {"name": "Train Station"},
        "classic": {"name": "'BecomeF umo: Classic' Portal"},
        "treehouse": {"name": "Funky Treehouse"}
    }
    nav_post_zoom_in = {
        "treehouse": 50,
        "train": 0,
    }
    player_token = "BD7F4C1D8063321CDFE702866B105EFB"  # F_umoCam02
    #player_token = "877C2AD2DB86BC486676330B47AFD9F8"  # F_umoCamBeta01
    #player_token = "D5E4A52E9B12F1E36D7269325943AE35"   # BecomeF_umoCam
    #player_token = "A9AFD097DCB5C13B801697A4104C3A61"   # F_umoCam04
    #player_token = "CD456AA86FE893389524D51774A0916D"    # F_umoCam05
    respawn_character_select_offset = -0.1    
    
    settings_menu_image_path = os.path.join(RESOURCES_PATH, "gear.jpg")
    settings_menu_width = 0.3
    settings_menu_grief_text = "Anti-Grief"
    settings_menu_max_find_attempts = 3
    settings_menu_find_threshold = 0.70
    settings_menu_max_click_attempts = 10
    settings_menu_button_height = 0.065
    settings_menu_ocr_max_attempts = 3
    
    sit_button_position = (0.79, 0.89)
    sitting_status = False
    
    sound_control_executable_name = "SoundVolumeView.exe"
    vlc_path = Path("C:\\", "Program Files", "VideoLAN", "VLC")
    vlc_executable_name = "vlc.exe"
    
    vip_twitch_names = ["ceatidk", "initialo", "dedegiko", "maplemedictv", "becomefumocam"]
    
    zoom_default = 30
    zoom_level = 50  # TODO: validate this is roughly correct on spawn
    zoom_max = 100
    zoom_min = 0
    zoom_ui_min = 30  # If lower, zoom out when interacting with UI (No CV needed, just get out of first person)
    zoom_out_ui = 10  # Amount to zoom out for safety when interacting with UI (No CV needed, just get out of first person)
    zoom_ui_min_cv = 50  # If lower, zoom out when interacting with UI (Computervision)
    zoom_out_ui_cv = 50  # Amount to zoom out for safety when interacting with UI (Computervision)
    
    commands_list = [
        {
            "command": "!m Your Message",
            "help": "Sends \"Your Message\" in-game"
        },
        {
            "command": "!left 90 or !right 360",
            "help": "Turn camera x degrees left or right"
        },
        {
            "command": "!up 45 or !down 180",
            "help": "Turn camera x degrees up or down"
        },
        {
            "command": "!zoomin 100 or !zoomout 100",
            "help": "Zoom camera in or out 100%"
        },
        {
            "command": "!dev Your Message",
            "help": "EMERGENCY ONLY, Sends \"Your Message\" to devs discord account"
        },
        {
            "command": "!move w 10",
            "help": "Moves forwards # FumoCam units. Max 10. (!move a, !move d, !move s)"
        },
        {
            "command": "!nav LocationName",
            "help": f"AutoNavigates to a location. ({', '.join(list(nav_locations.keys()))})"
        },
        {
            "command": "!leap 0.7 0.5",
            "help": "At the same time, moves forwards for 0.7s and jumps for 0.5s"
        },
        {
            "command": "!jump",
            "help": "Jumps. Helpful if stuck on something."
        },
        {
            "command": "!grief",
            "help": "Toggles anti-grief."
        },
        {
            "command": "!respawn",
            "help": "Respawns using Roblox respawn. Use !respawnforce if completely stuck."
        },
        {
            "command": "!respawnforce",
            "help": "Respawns. Helpful if completely stuck."
        },
        {
            "command": "!use",
            "help": "Presses \"e\"."
        },
        {
            "command": "!sit",
            "help": "Clicks the sit button."
        },
        {
            "command": "!mute",
            "help": "Music will still play, but toggles mute in-game sound effects."
        },
        {
            "command": "!click",
            "help": "Clicks wherever the mouse is on screen."
        },
        {
            "command": "!mouse -30 50",
            "help": "FROM SCREEN CENTER, moves mouse 30 pixels left, 50 pixels down."
        },
        {
            "command": "!backpack",
            "help": "Toggles the backpack."
        },
        {
            "command": "!item 1",
            "help": "(OPEN BACKPACK FIRST), Clicks item 1 (goes up to 8)"
        },
        {
            "command": "!hidemouse",
            "help": "Moves mouse off-screen."
        },
    ]


CFG = MainBotConfig()  # Instantiate the config for use between files

async def initial_add_action_queue(item):
    print(f"Attempted to add action queue item too early!")
    print(item)

CFG.add_action_queue = initial_add_action_queue