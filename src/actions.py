# General use commands used frequently by other commands
import random
from winsound import Beep
from arduino_integration import *
from spawn_detection import spawn_detection_main
ACFG.initalize_serial_interface(do_log=False)


async def send_chat(message):
    await check_active()
    for word in CFG.censored_words:  # todo: More effective censoring
        if word in message:
            message = message.replace(word, "*" * len(word))
    ACFG.send_message(message)


async def do_anti_afk():
    await check_active()
    ACFG.look(direction="left", amount=45)
    await async_sleep(1)
    ACFG.look(direction="right", amount=90)
    await async_sleep(1)
    ACFG.look(direction="left", amount=45)


async def do_advert():
    for message in CFG.advertisement:
        await send_chat(message)


async def respawn_character(chat=True):
    await check_active()
    log_process("Respawning")
    if chat:
        await send_chat("[Respawning!]")
    await async_sleep(0.75)
    ACFG.keyPress('KEY_ESC')
    await async_sleep(0.5)
    ACFG.keyPress('r')
    await async_sleep(0.5)
    ACFG.keyPress('KEY_RETURN')
    await async_sleep(0.5)
    log_process("")


async def mute_toggle(mute=None):
    log_process("In-game Mute")
    desired_mute_state = not CFG.audio_muted
    if mute is not None:  # If specified, force to state
        desired_mute_state = mute
    desired_volume = 0 if desired_mute_state else 100
    log_msg = "Muting" if desired_mute_state else "Un-muting"
    log(log_msg)
    os.system(f"{str(RESOURCES_PATH / CFG.sound_control_executable_name)} /SetVolume \"{CFG.game_executable_name}\" {desired_volume}")
    
    # Kill the process no matter what, race condition for this is two songs playing (bad)
    kill_process(executable=CFG.vlc_executable_name, force=True)
    
    if desired_mute_state:  # Start playing music
        copyfile(RESOURCES_PATH / OBS.muted_icon_name, OBS.output_folder / OBS.muted_icon_name)
        subprocess.Popen(f'"{str(CFG.vlc_path / CFG.vlc_executable_name)}" --playlist-autostart --loop --playlist-tree {str(RESOURCES_PATH / "soundtracks" / "overworld")}')
        output_log("muted_status", "In-game audio muted!\nRun !mute to unmute")
        sleep(5)  # Give it time to load VLC
    else:  # Stop playing music
        try:
            if os.path.exists(OBS.output_folder / OBS.muted_icon_name):
                os.remove(OBS.output_folder / OBS.muted_icon_name)
        except OSError:
            log("Error, could not remove icon!\nNotifying admin...")
            async_sleep(2)
            notify_admin("Mute icon could not be removed")
            log(log_msg)
        output_log("muted_status", "")
    CFG.audio_muted = desired_mute_state
    
    await check_active()
    log_process("")
    log("")