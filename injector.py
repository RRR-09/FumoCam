import os
# multiprocess is a fork that uses Dill instead of Pickle (which caused exceptions)
import multiprocess  # pip3.9 install multiprocess

def exploit_window_checker(ret_value, potential_names):
    # requires re-import
    from time import sleep 
    import pyautogui
    import pydirectinput
    searching_for_window = True
    while searching_for_window:
        sleep(1)
        # for i in pyautogui.getAllTitles():
        #    print('"'+i+'"')
        # print("\n\n\n\n")

        for window in pyautogui.getAllWindows():
            if window.title in potential_names:
                searching_for_window = False
                ret_value.value = potential_names.index(window.title)
                while window.title in pyautogui.getAllTitles():
                    try:
                        print(f"Focusing on '{window.title}'")
                        window.focus()
                    except Exception:
                        print(f"ERROR IN FOCUSING ON '{window.title}'")
                    sleep(0.2)
                    try:
                        print(f"Activating '{window.title}'")
                        window.activate()
                    except Exception:
                        print(f"ERROR IN ACTIVATING '{window.title}'")
                    sleep(0.3)
                    pydirectinput.press("space")
                    sleep(0.3)
                break


def common(inital_load=False, lua_code="", attempts=0):
    non_fatal_error = True
    original_directory = os.getcwd()
    injector_folder = os.path.join(globals.Roblox.injector_file_path)
    os.chdir(injector_folder)
    
    potential_names = [
        "Game Process Not Found",
        "NamedPipeExist!",
        "NamedPipeDoesntExist"
    ]
    ret_value = multiprocess.Value('i', -1)
    window_checker_proc = multiprocess.Process(target=exploit_window_checker, args=(ret_value, potential_names,))
    window_checker_proc.start()
    try:
        if inital_load:
            injector_process = ["Injector.exe", "inject"]
        else:
            injector_process = ["Injector.exe", "run", lua_code]
        subprocess.check_output(, timeout=7)
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        if not inital_load:
            return False, f"Error occurred with injector:\n```{format_exc()}```"
        else:
            non_fatal_error = False
            sleep(10)
    os.chdir(original_directory)
    window_checker_proc.terminate()
    window_checker_proc.join()
    if ret_value.value != -1:
        error_result = potential_names[ret_value.value]
        print(error_result)
        if inital_load:
            if error_result == "Game Process Not Found":
                common(inital_load=True)
                non_fatal_error = False
        else:
            if error_result in ["NamedPipeDoesntExist", "Game Process Not Found"]:
                common(inital_load=True)
                if attempts > 3:
                    return False, "Failed to inject"
                common(lua_code=lua_code, attempts=attempts + 1)
    if not inital_load:
        return True
    else
        if non_fatal_error:
            inject_lua("""setfflag("AbuseReportScreenshot", "False")
            setfflag("AbuseReportScreenshotPercentage", "0")""") # Reduce chance of any exploits causing a ban
        return non_fatal_error, ""
        
    
def do_inject_lua(lua_code, attempts=0):
    original_directory = os.getcwd()
    os.chdir(globals.Roblox.injector_file_path)

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
        return False, f"Error occurred with injector:\n```{format_exc()}```"
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
            do_inject_lua(lua_code, attempts + 1)
    return True
    
def load_exploit():
    non_fatal_error, status = common(initial_load=True)
    return non_fatal_error