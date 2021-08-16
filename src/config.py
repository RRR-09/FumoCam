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
    avatar_id = "d20920201dc57c8502a910185c3076ad"  # Fumocam 2
    # avatar_id = "abf177b3d6d7f87381f59e50ee08ad99" Fumocam 1
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

    character_select_scroll_up_amount = 10
    character_select_screen_height_to_click = 0.20
    chat_name_sleep_factor = 0.05  # Seconds to wait per char in users name before sending their message
    comedy_phrases = [
        "Peak comedy incoming",
        "This is going to be funny",
        "Wee! c:",
        "That's one small step for fumo, one giant leap for fumo cam",
        "Incoming fumo asteroid",
        "FORE!",
        "Awoo incoming!",
        "To infumoty and beyond!",
        "If I'm using CM3K, does that make me Comedy Machine 4000?",
        "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "Orbital fumocam",
        "It's no trebuchet but it'll do"
    ]
    current_location = "easteregg"
    current_emote = "/e dance3"
    event_timer_running = False
    disable_collisions_on_spawn = True
    game_id = 6238705697
    game_id_nil = 7137029060
    game_id_hinamizawa = 6601613056
    game_instances_url = "https://www.roblox.com/games/6238705697/Become-Fumo#!/game-instances"
    injector_file_path = os.path.join(RESOURCES_PATH, "injector")
    injector_attempts = 0
    injector_disabled = False
    injector_recheck_seconds = 30 * 60
    max_attempts_character_selection = 30
    max_attempts_sit_button = 3
    next_possible_teleport = 0
    player_token = "BD7F4C1D8063321CDFE702866B105EFB"
    seconds_per_tour_location = 7
    sit_button_position = (0.79, 0.89)
    teleport_locations = {
        # "velvet": {
        # "pos": "-3404.589, -82.86, 26.134",
        # "rot": "0, math.rad(0), 0",
        # "cam": "math.rad(20), math.rad(120), 0",
        # "friendly_name": "Velvet Room",
        # },
        "easteregg": {
            "pos": "24.709, 10.702, 80.479",
            "rot": "math.rad(180), math.rad(-51), math.rad(180)",
            "cam": "math.rad(10), math.rad(50), 0",
            "friendly_name": "Fumocam Easter Egg",
        },
        "tree2": {
            "pos": "-67.394, 12.613, -224.721",
            "rot": "math.rad(0), math.rad(45), math.rad(0)",
            "cam": "math.rad(30), math.rad(-135), 0",
            "friendly_name": "Trees near Train",
        },
        "lobster": {
            "pos": "0.227, -12, -52.868",
            "rot": "math.rad(-180), math.rad(45), math.rad(180)",
            "cam": "math.rad(-30), math.rad(-35), 0",
            "friendly_name": "Lobster Room",
        },
        "funky": {
            "pos": "-52.267967224121, 1, 60.158397674561",
            "rot": "0, math.rad(90), 0",
            "cam": "math.rad(8), math.rad(-90), 0",
            "friendly_name": "Funky Room",
        },
        "secret": {
            "pos": "-46.992160797119, -3.3972184658051, -60.269630432129",
            "rot": "0, math.rad(45), 0",
            "cam": "math.rad(20), math.rad(-125), 0",
            "friendly_name": "Secret Chair Room",
        },
        "miko2": {
            "pos": "16.568878173828, -0.59699988365173, -108.66677856445",
            "rot": "0, math.rad(0), 0",
            "cam": "math.rad(20), math.rad(120), 0",
            "friendly_name": "Miko Borgar Interior",
        },
        "jungle2": {
            "pos": "39.32, 8.6, -156.57",
            "rot": "0, math.rad(180), 0",
            "cam": "math.rad(0), math.rad(0), 0",
            "friendly_name": "Jungle",
        },
        "jungle1": {
            "pos": "33.164390563965, 26.33, -179.29165649414",
            "rot": "0, math.rad(-47), 0",
            "cam": "math.rad(20), math.rad(141), 0",
            "friendly_name": "Jungle Tree",
        },
        "train": {
            "pos": "-57.425586700439, 5.3103098869324, -157.5",
            "rot": "0, math.rad(180), 0",
            "cam": "math.rad(-10), math.rad(0), 0",
            "friendly_name": "Train Station",
        },
        "treehouse": {
            "pos": "36.4470062, 41.9251442, 47.5567894",
            "rot": "0, math.rad(0), 0",
            "cam": "math.rad(24), math.rad(155), 0",
            "friendly_name": "Treehouse",
        },
        "bonfire": {
            "pos": "-48.0837212, -3.39721847, 9.8922472",
            "rot": "0, math.rad(153), 0",
            "cam": "math.rad(-16.1963), math.rad(-26.5195), 0",
            "friendly_name": "Bonfire",
        },
        "comedy1": {
            "pos": "-59.9171944, 22.7805653, -44.7005348",
            "rot": "0, math.rad(135), 0",
            "cam": "math.rad(-37.6182), math.rad(-46.4159), 0",
            "friendly_name": "Top of 'Comedy Machine 3000'",
        },
        "comedy2": {
            "pos": "-57.5851326, 15.2805653, -39.5438385",
            "rot": "0, math.rad(90), 0",
            "cam": "math.rad(0), math.rad(-90), 0",
            "friendly_name": "Comedy Machine, wee",
        },
        "miko1": {
            "pos": "-20.65061, -3.39721847, -109.600708",
            "rot": "0, math.rad(90), 0",
            "cam": "math.rad(-8.9949), math.rad(-51.2586), 0",
            "friendly_name": "Miko Borgar Windows",
        },
        "mikoroof": {
            "pos": "26.721, 8.103, -92.448",
            "rot": "0, math.rad(-90), 0",
            "cam": "math.rad(16), math.rad(114), 0",
            "friendly_name": "'Miko Borgar' Rooftop",
        },
        "cave": {
            "pos": "47.640686, -1.01810837, 43.9505501",
            "rot": "0, math.rad(-135), 0",
            "cam": "math.rad(-21.8371), math.rad(44.1698), 0",
            "friendly_name": "The Cave",
        },
        "pond": {
            "pos": "-71.2607193, 1.65747952, -110.610229",
            "rot": "0, math.rad(62), 0",
            "cam": "math.rad(29.1522), math.rad(-119.8305), 0",
            "friendly_name": "Fishing Pond",
        },
        "tree": {
            "pos": "16.2970638, 9.94406033, -36.5782738",
            "rot": "0, math.rad(180), 0",
            "cam": "math.rad(-29.1523), math.rad(0), 0",
            "friendly_name": "Central Trees",
        },
        "funny": {
            "pos": "60.8279991, 1.37292504, -7.6749382",
            "rot": "0, math.rad(90), 0",
            "cam": "math.rad(0), math.rad(-90), 0",
            "friendly_name": "'funny' Statue",
        },
    }
    tick_rate = 0.25
    tick_rate_blocked = 0.1


CFG = MainBotConfig()  # Instantiate the config for use between files
