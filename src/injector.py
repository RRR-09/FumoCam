import threading

import multiprocess  # multiprocess is a fork that uses Dill instead of Pickle (which caused exceptions)

from utilities import *


def exploit_window_checker(ret_value, potential_names):
    from time import sleep
    import pyautogui
    searching_for_window = True
    while searching_for_window:
        sleep(1)
        for window in pyautogui.getAllWindows():
            if window.title in potential_names:
                searching_for_window = False
                ret_value.value = potential_names.index(window.title)
                for i in range(3):  # Attempt a maximum of 3 tries
                    if window.title not in potential_names:
                        break
                    window.close()
                    sleep(0.3)
                break


def inject_lua_file(lua_file_name, attempts=0, **kwargs):
    script_path = os.path.join(RESOURCES_PATH, "lua_scripts", f"{lua_file_name}.lua")
    if not os.path.exists(script_path):
        notify_admin(f"[inject_lua_file] Lua script does not exist!\n``{script_path}``")
        return False
    try:
        with open(script_path, "r") as lua_file:
            lua_code = lua_file.read()
        if len(kwargs) > 0:
            lua_code = lua_code.format(**kwargs)
    except Exception:
        notify_admin(f"[inject_lua_file] Exception handling lua script ``{lua_file_name}``\n```{format_exc()}```")
        return False
    lua_success = inject_lua(lua_code, attempts)
    return lua_success


def inject_lua(lua_code, attempts=0):
    if CFG.injector_disabled:
        log("Advanced commands are currently broken, sorry!")
        sleep(5)
        log("")
        return False
    original_directory = os.getcwd()
    os.chdir(CFG.injector_file_path)

    potential_names = [
        "Game Process Not Found",
        "NamedPipeExist!",
        "NamedPipeDoesntExist"
    ]
    ret_value = multiprocess.Value('i', -1)

    window_checker_proc = multiprocess.Process(target=exploit_window_checker, args=(ret_value, potential_names,))
    window_checker_proc.start()
    try:
        subprocess.check_output(["Injector.exe", "run", lua_code], timeout=7)
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        notify_admin(f"Error occurred with injector:\n```{format_exc()}```")
    os.chdir(original_directory)
    window_checker_proc.terminate()
    window_checker_proc.join()
    if ret_value.value != -1:
        error_result = potential_names[ret_value.value]
        print(error_result)
        if error_result in ["NamedPipeDoesntExist", "Game Process Not Found"]:
            load_exploit()
            if attempts > 3:
                return False
            inject_lua(lua_code, attempts + 1)
    check_active()
    return True


def load_exploit(force=False):
    print("[load_exploit]")
    if CFG.injector_disabled and not force:
        log("Advanced commands are currently broken, sorry!")
        sleep(5)
        log("")
        return False
    original_directory = os.getcwd()
    injector_folder = os.path.join(CFG.injector_file_path)
    os.chdir(injector_folder)

    potential_names = [
        "Game Process Not Found",
        "NamedPipeExist!",
        "NamedPipeDoesntExist",
        "EasyExploit"
    ]
    ret_value = multiprocess.Value('i', -1)
    non_fatal_error = True

    window_checker_proc = multiprocess.Process(target=exploit_window_checker, args=(ret_value, potential_names,))
    window_checker_proc.start()
    try:
        subprocess.check_output(["Injector.exe", "inject"], timeout=7)
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        #notify_admin(f"Error occurred with injector:\n```{format_exc()}```")
        log("Warning: Injector has been temporarily removed.")
        non_fatal_error = False
        sleep(10)
        log("")
    os.chdir(original_directory)
    window_checker_proc.terminate()
    window_checker_proc.join()

    if ret_value.value != -1:
        error_result = potential_names[ret_value.value]
        print(error_result)
        if error_result in ["Game Process Not Found", "EasyExploit", "NamedPipeDoesntExist"]:
            non_fatal_error = False
    if non_fatal_error:
        inject_lua_file("injector_anti_abuse_bypass")
    else:
        kill_process("chrome.exe")
        CFG.injector_disabled = True
        if not force:  # We're not forcing a check from an existing injector failed loop
            threading.Thread(target=injector_failed_loop).start()
        log("Warning: Injector failed, this can happen every 7 days.\nYou can try moving the cam with !move.")
        sleep(10)
        log("")
        return False

    kill_process("chrome.exe")
    return non_fatal_error


def injector_failed_loop():
    CFG.next_injector_check = time.time()
    while True:
        if CFG.next_injector_check <= time.time():  # Time to recheck
            CFG.next_injector_check = time.time() + CFG.injector_recheck_seconds
            while CFG.action_running or CFG.action_queue:  # We have a queue or we're doing something
                sleep(0.5)  # Wait for any running action to finish
            CFG.action_running = True
            log_process(f"Attempting to hook into Roblox")
            log("Re-attempting process connection...")
            output_log("injector_failure", "INJECTOR FAILED\nTP, Goto, Spectate, Tour offline Use !move\nAttempting "
                                           "again now...")
            loaded_exploit = load_exploit(force=True)
            log_process(f"")
            log("")
            if loaded_exploit:
                output_log("injector_failure", "")
                return True
            CFG.action_running = False
        time_remaining = round(CFG.next_injector_check - time.time())
        friendly_time_remaining = f"{math.floor(time_remaining/60):02}:{time_remaining%60:02}"
        output_log("injector_failure", f"INJECTOR FAILED\nTP, Goto, Spectate, Tour offline. Use !move\nAttempting "
                                       f"again in {friendly_time_remaining}")
        sleep(1)
