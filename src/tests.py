from health import click_character_in_menu, change_characters, join_target_server, check_for_better_server, get_current_server_id
from actions import toggle_collisions
from commands import click_sit_button, respawn_character
from utilities import *
import pyautogui
from twitch_integration import twitch_main
import asyncio

def test_character_select(click_mouse=True):  # Character select OCR still needs work; guess coordinates and test
    check_active()
    sleep(1)
    click_character_in_menu(click_mouse=click_mouse)


def test_character_select_full(click_mouse=True):
    check_active()
    sleep(1)
    change_characters()
    

def test_toggle_collisions():
    check_active()
    sleep(1)
    toggle_collisions()


def test_respawn(click_mouse=True):
    check_active()
    sleep(1)
    respawn_character()


def test_join_target_server():
    join_target_server("099cf062-e26f-4ace-b627-6ebfa2295270")


def test_get_cookies_for_browser():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import json
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
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import json
    print("If you completed test_get_cookies_for_browser, this should open a logged-in browser.")
    print("Press enter to start, and press enter again to terminate the browser.")
    input()
    
    with open(CFG.browser_cookies_path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    driver = webdriver.Chrome(CFG.browser_driver_path)
    driver.get('https://www.roblox.com/games/6238705697/Become-Fumo')
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    driver.execute_script("""Roblox.GameLauncher.joinGameInstance(6238705697, "099cf062-e26f-4ace-b627-6ebfa2295270")""");
    input("\n\n\nPress Enter to close\n\n\n\n")
    driver.quit()
    
       
    kill_process(CFG.browser_driver_executable_name)
    kill_process(CFG.browser_executable_name)


def test_check_for_better_server():
    print(check_for_better_server())


def test_get_current_server_id():
    
    print(asyncio.get_event_loop().run_until_complete(get_current_server_id()))


def test_twitch():
    twitch_main()


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    
    #test_get_cookies_for_browser()
    #test_twitch()
    
    #test_check_for_better_server()
    #test_character_select_full(click_mouse=True)
    #toggle_collisions()
    #click_sit_button()
    #test_respawn()
    #test_join_target_server()
    test_get_current_server_id()
    #test_get_cookies_for_browser()
    #test_loading_cookies_for_browser()