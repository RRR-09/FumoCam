import os
from dotenv import load_dotenv  # pip3.9 install python-dotenv
load_dotenv()


def output_log(file_name, message):
    if not os.path.exists(OBS.output_folder):
        os.mkdir(OBS.output_folder)
    file_path = os.path.join(OBS.output_folder, f"{file_name}.txt")
    with open(file_path, "w") as f:
        f.write(str(message))


class Twitch:
    channel_name = "becomefumocam"
    username = "BecomeFumoBot"
    admins = ["becomefumocam", os.getenv("OWNER_USERNAME")]


class Roblox:
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
    character_select_image_path = os.path.join("resources", "character_select.png")
    
    character_select_scroll_up_amount = 10
    character_select_screen_height_to_click = 0.40
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
    current_location = "tree"
    current_emote = "/e dance3"
    event_timer_running = False
    disable_collisions_on_spawn = True
    game_id = 6238705697
    game_instances_url = "https://www.roblox.com/games/6238705697/Become-Fumo#!/game-instances"
    injector_file_path = os.path.join("resources", "injector")
    injector_attempts = 0
    injector_disabled = False
    next_possible_teleport = 0
    player_token = "BD7F4C1D8063321CDFE702866B105EFB"
    teleport_locations = {
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
        "miko": {
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


class OBS:
    output_folder = "output"
    event_time = "2021-06-09 12:05:00AM"
    event_end_time = "2021-05-03 10:23:18PM"


class Discord:
    webhook_username = "BecomeFumoCam"
