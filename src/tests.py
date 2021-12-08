import asyncio

import pyautogui

from actions import mute_toggle
from arduino_integration import *
from commands import click_sit_button, respawn_character
from health import (change_characters, check_for_better_server,
                    click_character_in_menu, get_current_server_id,
                    join_target_server)
from twitch_integration import twitch_main
from utilities import *


def test_turn_camera(direction="left", amount=45):
    async def do_test(direction, amount):
        await check_active()
        await async_sleep(1)
        ACFG.look(direction, amount)
    asyncio.get_event_loop().run_until_complete(do_test(direction, amount))

def test_move(direction="w", amount=10):
    async def do_test(direction, amount):
        await check_active()
        await async_sleep(1)
        ACFG.move(direction, amount)
    asyncio.get_event_loop().run_until_complete(do_test(direction, amount))

def test_character_select(click_mouse=True):  # Character select OCR still needs work; guess coordinates and test
    async def do_test(click_mouse=True):
        await check_active()
        await async_sleep(1)
        await click_character_in_menu(click_mouse=click_mouse)
    asyncio.get_event_loop().run_until_complete(do_test(click_mouse=click_mouse))


def test_character_select_full(click_mouse=True):
    async def do_test(click_mouse=True):
        await check_active()
        await async_sleep(1)
        await change_characters()
    asyncio.get_event_loop().run_until_complete(do_test(click_mouse=click_mouse))
    

def test_toggle_collisions():
    check_active()
    sleep(1)
    asyncio.get_event_loop().run_until_complete(toggle_collisions())


def test_respawn(click_mouse=True):
    async def do_test(click_mouse=True):
        await check_active()
        await async_sleep(1)
        await respawn_character()
    asyncio.get_event_loop().run_until_complete(do_test(click_mouse=click_mouse))


def test_join_target_server():
    join_target_server("099cf062-e26f-4ace-b627-6ebfa2295270")


def test_get_cookies_for_browser():
    import json

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("Login to your account in the brower that opens, come back to this screen, and press enter.")
    print("Press enter to start")
    input()
    
    driver = webdriver.Chrome(CFG.browser_driver_path)
    driver.get('https://www.roblox.com/games/6238705697/Become-Fumo')
    
    input("\n\n\nPress Enter to save cookies\n\n\n\n")
    
    with open(CFG.browser_cookies_path, 'w', encoding='utf-8') as f:
        json.dump(driver.get_cookies(), f, ensure_ascii=False, indent=4)
    driver.quit()
    kill_process(CFG.browser_driver_executable_name)
    kill_process(CFG.browser_executable_name)
    
    print(f"\n\n\nCookies saved to {CFG.browser_cookies_path}, DO NOT SHARE THIS WITH ANYONE.")
    input("\nPress Enter to close.")


def test_loading_cookies_for_browser():
    import json

    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("If you completed test_get_cookies_for_browser, this should open a logged-in browser.")
    print("Press enter to start, and press enter again to terminate the browser.")
    input()
    
    with open(CFG.browser_cookies_path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={CFG.browser_profile_path}")
    driver = webdriver.Chrome(options=options, executable_path=CFG.browser_driver_path)
    driver.get(CFG.game_instances_url)
    
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    driver.execute_script("""Roblox.GameLauncher.joinGameInstance(6238705697, "099cf062-e26f-4ace-b627-6ebfa2295270")""");
    input("\n\n\nPress Enter to close\n\n\n\n")
    driver.quit()
    
       
    kill_process(CFG.browser_driver_executable_name)
    kill_process(CFG.browser_executable_name)


def test_check_for_better_server():
    print(asyncio.get_event_loop().run_until_complete(check_for_better_server()))


def test_get_current_server_id():
    print(asyncio.get_event_loop().run_until_complete(get_current_server_id()))


def test_twitch():
    twitch_main()

def test_mute(mute=None):
    asyncio.get_event_loop().run_until_complete(mute_toggle(mute=mute))


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    # If account banned
    #test_get_cookies_for_browser()
    test_loading_cookies_for_browser()
    #test_check_for_better_server()
    
    #test_mute(mute=True)
    
    #test_turn_camera(direction="right")
    #test_move()
    #sleep(5)
    #test_turn_camera("left")
    
    #test_get_cookies_for_browser()
    
    #test_twitch()
    #test_character_select()
    #test_character_select_full()
    #test_check_for_better_server()
    #test_character_select_full(click_mouse=True)
    #toggle_collisions()
    #test_toggle_collisions()
    
    #click_sit_button()
    #test_respawn()
    #test_join_target_server()
    #test_get_current_server_id()
    #error_log("test")
    #test_check_for_better_server()