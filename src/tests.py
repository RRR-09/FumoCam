from health import click_character_in_menu, change_characters
from injector import *


def print_pos():
    inject_lua_file("test_print_pos")  # For getting specific position in world


def print_full_pos():
    inject_lua_file("test_print_full_pos")  # For mapping new teleport entries with pos, rot, and cam rot


def anti_gravity():
    inject_lua_file("test_adjust_gravity", desired_gravity=0.0005)  # For getting to difficult places


def silent_goto(player_name):
    inject_lua_file("test_goto_player_silent", target=player_name.lower())  # Teleporting to a player for mapping


def print_target_pos(player_name):
    inject_lua_file("test_print_target_pos", target=player_name.lower())  # Getting players' positions for mapping


def spectate_target(player_name):
    inject_lua_file("test_spectate_player", target=player_name.lower())  # To see areas we get kicked if we teleport to


def test_character_select(click_mouse=True):  # Character select OCR still needs work; guess coordinates and test
    check_active()
    sleep(1)
    click_character_in_menu(click_mouse=click_mouse)


def test_character_select_full(click_mouse=True):
    check_active()
    sleep(1)
    change_characters()
    

def test_exploit():
    load_exploit()


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    test_character_select_full(click_mouse=True)
    #test_exploit()
