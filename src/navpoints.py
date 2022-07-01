# TODO: Change from functions to variables (like dict or something)
from random import randint
from time import sleep

from arduino_integration import ACFG
from utilities import log, log_process


def treehouse_spawn_calibration():
    log_process("AutoNav")
    log("Treehouse Spawn -> Calibration Rock")
    ACFG.precision_look("left", 1314, raw=True)
    ACFG.move("s", 3, raw=True)
    ACFG.move("d", 3, raw=True)
    ACFG.move("w", 2.5, raw=True)

    standard_calibration()

    log_process("")
    log("")


def comedy_spawn_calibration():
    log_process("AutoNav")
    log("Comedy Machine Spawn -> Calibration Rock")
    ACFG.precision_look("right", 469, raw=True)
    ACFG.move("w", 1.6, raw=True)
    ACFG.move("a", 2.2, raw=True)
    ACFG.move("w", 2.5, raw=True)

    standard_calibration()

    log_process("")
    log("")


def main_spawn_calibration():
    log_process("AutoNav")
    log("Main Spawn -> Calibration Rock")
    ACFG.precision_look("right", 7, raw=True)
    ACFG.move("d", 0.7, raw=True)
    ACFG.move("w", 1.5, raw=True)

    standard_calibration()

    log_process("")
    log("")


def standard_calibration():
    ACFG.move("s", 0.08, raw=True)
    ACFG.move("d", 0.8, raw=True)
    ACFG.move("w", 0.8, raw=True)
    ACFG.move("a", 0.8, raw=True)
    ACFG.move("w", 0.3, raw=True)
    ACFG.move("a", 0.3, raw=True)


def main_to_shrimp_tree():
    log_process("AutoNav")
    log("-> Shrimp Tree")
    ACFG.move("s", 2, raw=True)
    ACFG.move("a", 1.9, raw=True)
    ACFG.leap(forward_time=0.5, jump_time=0.25, direction_key="s", jump_delay=0.1)
    ACFG.leap(forward_time=0.6, jump_time=0.3, direction_key="a", jump_delay=0.2)
    ACFG.leap(
        forward_time=0.65,
        jump_time=0.3,
        direction_key="d",
        jump_delay=0.1,
        diagonal_direction_key="s",
    )
    ACFG.zoom("i", 105)
    ACFG.zoom("o", 105)
    ACFG.precision_look("left", 1798, raw=True)
    log_process("")
    log("")


def main_to_ratcade():
    log_process("AutoNav")
    log("-> Ratcade")
    ACFG.move("d", 0.8, raw=True)
    ACFG.move("w", 1.2, raw=True)
    ACFG.move("a", 0.3, raw=True)
    ACFG.move("w", 2.8, raw=True)
    ACFG.move("a", 1.6, raw=True)
    ACFG.move("w", 0.95, raw=True)
    ACFG.move("d", 0.9, raw=True)
    ACFG.precision_look("left", 901, raw=True)
    ACFG.zoom("i", 105)
    ACFG.zoom("o", 105)
    ACFG.precision_look("right", 1798, raw=True)
    log_process("")
    log("")


def main_to_train():
    log_process("AutoNav")
    log("-> Train Station")
    ACFG.move("s", 2.4, raw=True)
    ACFG.move("d", 4.2, raw=True)
    ACFG.move("s", 9.8, raw=True)
    ACFG.move("a", 0.7, raw=True)
    ACFG.move("s", 0.9, raw=True)
    ACFG.leap(forward_time=0.25, jump_time=0.25, direction_key="s")
    ACFG.leap(forward_time=0.3, jump_time=0.25, direction_key="a")
    ACFG.move("w", 1.05, raw=True)
    ACFG.precision_look("right", 901, raw=True)
    ACFG.zoom("i", 105)
    ACFG.zoom("o", 105)
    ACFG.precision_look("left", 1798, raw=True)
    log_process("")
    log("")


def _main_to_classic_portal():
    # Calibration Rock
    ACFG.move("s", 2.4, raw=True)
    ACFG.move("d", 4.2, raw=True)
    ACFG.move("s", 11.5, raw=True)
    ACFG.move("a", 1.4, raw=True)
    ACFG.move("w", 1.3, raw=True)
    ACFG.move("d", 0.5, raw=True)

    # Calibration Corner 1
    ACFG.move("s", 0.3, raw=True)
    ACFG.move("a", 1.5, raw=True)
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 0.6, raw=True)
    ACFG.move("w", 0.3, raw=True)
    ACFG.move("a", 0.3, raw=True)

    # Calibration Corner 2
    ACFG.leap(forward_time=0.6, jump_time=0.25, direction_key="a")
    ACFG.leap(
        forward_time=0.3,
        jump_time=0.3,
        direction_key="a",
        diagonal_direction_key="s",
    )
    ACFG.leap(forward_time=0.8, jump_time=0.3, direction_key="s", jump_delay=0.2)
    ACFG.leap(forward_time=1, jump_time=0.5, direction_key="d", jump_delay=0.4)
    ACFG.move("s", 0.2, raw=True)
    ACFG.leap(forward_time=0.9, jump_time=0.5, direction_key="d", jump_delay=0.35)
    ACFG.move("s", 0.2, raw=True)
    ACFG.use()
    sleep(5)


def classic_portal_to_slide():
    ACFG.move("w", 1.8, raw=True)
    ACFG.move("d", 0.125, raw=True)
    ACFG.move("w", 2.270, raw=True)
    ACFG.precision_look("left", 901 + (901 / 2), raw=True)
    ACFG.zoom("i", 105)
    ACFG.zoom("o", 105)
    ACFG.precision_look("left", 1798, raw=True)


def main_to_classic():
    log_process("AutoNav")
    log("-> BecomeFumo Classic Portal")
    _main_to_classic_portal()
    classic_portal_to_slide()
    log_process("")
    log("")


def main_to_classic_fix_bright():
    log_process("AutoNav")
    log("-> BecomeFumo Classic Portal\n(And back out)")
    _main_to_classic_portal()
    ACFG.use()
    log_process("")
    log("")


def main_to_treehouse_bench():
    log_process("AutoNav")
    log("-> Treehouse Bench")
    ACFG.move("d", 0.8, raw=True)
    ACFG.move("w", 1.2, raw=True)
    ACFG.move("a", 0.3, raw=True)
    ACFG.move("w", 2.8, raw=True)
    ACFG.move("a", 3.9, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.move("d", 0.7, raw=True)

    # Calibration corner before vines
    ACFG.move("w", 0.3, raw=True)
    ACFG.move("a", 0.3, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.leap(forward_time=0.25, jump_time=0.4, direction_key="s")
    ACFG.move("s", 0.6, raw=True)
    ACFG.move("d", 0.6, raw=True)

    # Calibration corner above vines
    ACFG.move("a", 0.2, raw=True)
    ACFG.move("w", 0.27, raw=True)
    ACFG.leap(forward_time=0.9, jump_time=0.4, direction_key="d")
    ACFG.move("s", 0.3, raw=True)
    ACFG.leap(forward_time=0.9, jump_time=0.4, direction_key="s")
    ACFG.move("d", 0.3, raw=True)
    ACFG.leap(forward_time=1.2, jump_time=0.9, direction_key="d", jump_delay=0.3)
    ACFG.move("a", 0.1, raw=True)
    ACFG.move("w", 0.3, raw=True)
    ACFG.leap(forward_time=0.5, jump_time=0.5, direction_key="s")
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 0.9, raw=True)


def treehouse_bench_calibration():
    log_process("AutoNav")
    log("Treehouse Spawn-> Treehouse Bench")
    ACFG.precision_look("left", 1314, raw=True)
    ACFG.move("w", 0.65, raw=True)
    ACFG.move("a", 1, raw=True)


def treehouse_bench_to_treehouse():
    log("Treehouse Bench -> Funky Treehouse")

    ACFG.leap(forward_time=0.65, jump_time=0.5)
    ACFG.leap(forward_time=1, jump_time=0.2, direction_key="d")
    ACFG.move("w", 0.5)
    ACFG.move("a", 0.8)
    # ACFG.move("s", 1)
    # ACFG.move("d", 1.6)
    # ACFG.leap(forward_time=0.6, jump_time=0.7, direction_key="a")
    # sleep(1)
    # ACFG.leap(forward_time=0.4, jump_time=0.4, direction_key="d", jump_delay=0.1)
    ACFG.move("s", 0.41, raw=True)
    ACFG.move("d", 0.55, raw=True)
    ACFG.leap(forward_time=0.4, jump_time=0.75, direction_key="a")
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="d", jump_delay=0.1)
    ACFG.precision_look("left", 1798, raw=True)
    ACFG.zoom("i", 105)
    ACFG.zoom("o", 105)
    ACFG.precision_look("left", 1798, raw=True)

    log_process("")
    log("")


def main_to_beach():
    log_process("AutoNav")
    log("-> Beach")

    main_to_beach_portal()

    log("-> Beach\n(Going through twice to clear portal-lock bug)")
    sleep(5)
    ACFG.use()
    log("-> Beach")
    sleep(5)
    ACFG.use()
    sleep(5)

    if randint(0, 100) > 75:  # nosec
        beach_portal_easter_egg()
    else:
        beach_portal_to_dock()

    log_process("")
    log("")


def main_to_beach_portal():
    ACFG.move("s", 2, raw=True)
    ACFG.move("a", 6, raw=True)
    ACFG.move("w", 9, raw=True)
    ACFG.move("s", 1.3, raw=True)
    ACFG.leap(forward_time=0.6, jump_time=0.25, direction_key="d", jump_delay=0.1)
    ACFG.use()


def beach_portal_easter_egg():
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 1.8, raw=True)
    ACFG.move("s", 4.4, raw=True)
    ACFG.zoom("i", 50)
    ACFG.use()
    ACFG.send_message("[Fun slide!]")
    sleep(5)
    ACFG.jump()
    ACFG.move("w", 2.5, raw=True)
    ACFG.move("s", 0.2, raw=True)
    ACFG.send_message("[Awoo swim.]")
    sleep(2.5)
    ACFG.zoom("o", 60)
    ACFG.move("d", 0.7, raw=True)
    ACFG.move("w", 0.8, raw=True)
    ACFG.move("d", 0.6, raw=True)
    ACFG.move("s", 1, raw=True)


def beach_portal_to_dock():
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("a", 1.8, raw=True)
    ACFG.move("s", 3.1, raw=True)
    ACFG.move("d", 1.1, raw=True)
    ACFG.move("s", 1, raw=True)
