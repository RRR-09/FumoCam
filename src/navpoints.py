# TODO: Change from functions to variables (like dict or something)
from time import sleep

from arduino_integration import ACFG
from utilities import log, log_process


def treehouse_to_main():
    log_process("AutoNav")
    log("Treehouse -> Main")
    ACFG.move("w", 3.3, raw=True)
    ACFG.move("d", 0.2, raw=True)
    ACFG.look("left", 1.10, raw=True)
    log_process("")
    log("")


def comedy_to_main():
    log_process("AutoNav")
    log("Comedy Machine -> Main")
    ACFG.move("w", 3.75, raw=True)
    ACFG.move("a", 0.5)
    ACFG.look("right", 0.3875, raw=True)

    log_process("")
    log("")


def main_to_shrimp_tree():
    log_process("AutoNav")
    log("Main -> Shrimp Tree")
    # If main spawn is facing North,
    # Turn to face West
    ACFG.look("left", 0.75, raw=True)
    ACFG.move("a", 1.3, raw=True)  # 0.3576
    ACFG.move("w", 0.75, raw=True)
    # Right in front of first step
    ACFG.leap(0.54, 0.475)
    # Right before first tree
    ACFG.leap(0.4, 0.4)
    # Move towards edge of tree
    ACFG.move("a", 0.1, raw=True)
    # Turn towards shrimp tree
    ACFG.look("left", 1.135, raw=True)
    # Leap to Shrimp Tree
    ACFG.leap(0.6, 0.4)
    # Face South, character looking North
    ACFG.look("right", 0.385, raw=True)
    ACFG.move("a", 0.07, raw=True)
    ACFG.move("s", 0.07, raw=True)
    ACFG.move("d", 0.07, raw=True)
    log_process("")
    log("")


def main_to_ratcade():
    log_process("AutoNav")
    log("Main -> Ratcade")
    ACFG.move("a", 1.5, raw=True)
    ACFG.move("w", 5, raw=True)
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("w", 0.9, raw=True)
    ACFG.move("d", 2, raw=True)
    ACFG.move("w", 0.075, raw=True)
    ACFG.move("a", 0.075, raw=True)
    ACFG.move("s", 0.075, raw=True)
    ACFG.look("right", 0.75, raw=True)
    log_process("")
    log("")


def main_to_train():
    log_process("AutoNav")
    log("Main -> Train Station")
    ACFG.move("a", 0.25, raw=True)
    ACFG.move("s", 4.5, raw=True)
    ACFG.move("d", 1.525, raw=True)
    ACFG.move("s", 2.9, raw=True)
    ACFG.move("d", 1, raw=True)
    ACFG.move("s", 2, raw=True)
    ACFG.move("d", 0.6, raw=True)
    ACFG.look("left", 1.5, raw=True)
    ACFG.leap(0.75, 0.75)
    ACFG.move("w", 0.75, raw=True)
    ACFG.leap(1, 1)
    ACFG.look("left", 0.75, raw=True)
    ACFG.move("s", 0.05, raw=True)
    ACFG.move("a", 0.075, raw=True)
    ACFG.move("s", 0.1, raw=True)
    log_process("")
    log("")


def main_to_classic():
    log_process("AutoNav")
    log("Main -> BecomeFumo Classic Portal")
    ACFG.move("a", 0.25, raw=True)
    ACFG.move("s", 4.5, raw=True)
    ACFG.move("d", 1.75, raw=True)
    ACFG.move("s", 2.6, raw=True)
    ACFG.move("a", 1, raw=True)
    ACFG.move("s", 2.55, raw=True)
    ACFG.move("d", 1, raw=True)
    ACFG.move("s", 2.5, raw=True)
    ACFG.leap(forward_time=0.3, jump_time=0.25, direction_key="s")

    ACFG.move("d", 0.5, raw=True)
    ACFG.move("s", 0.3, raw=True)

    ACFG.leap(forward_time=0.3, jump_time=0.3, direction_key="s")
    ACFG.move("d", 0.2, raw=True)
    ACFG.move("s", 0.275, raw=True)
    ACFG.leap(forward_time=0.625, jump_time=0.5, direction_key="s")
    ACFG.leap(forward_time=1, jump_time=0.2, direction_key="d", jump_delay=0.35)
    ACFG.move("s", 0.225, raw=True)
    ACFG.leap(forward_time=0.8, jump_time=0.4, direction_key="d", jump_delay=0.3)
    ACFG.use()
    sleep(5)
    ACFG.move("w", 1.8, raw=True)
    ACFG.move("d", 0.125, raw=True)
    ACFG.move("w", 2.275, raw=True)
    ACFG.look("right", 0.375, raw=True)
    ACFG.move("s", 0.075, raw=True)
    ACFG.move("d", 0.06, raw=True)

    log_process("")
    log("")


def main_to_treehouse():
    log_process("AutoNav")
    log("Main -> Funky Treehouse")
    ACFG.move("a", 1.5, raw=True)
    ACFG.move("w", 3, raw=True)
    ACFG.move("a", 1, raw=True)
    ACFG.move("w", 1.5, raw=True)
    ACFG.move("a", 1.1, raw=True)
    ACFG.move("s", 1, raw=True)
    ACFG.leap(forward_time=1, jump_time=1, direction_key="s")
    ACFG.move("s", 0.5, raw=True)
    ACFG.move("d", 0.5, raw=True)
    ACFG.move("w", 0.3, raw=True)
    ACFG.move("d", 0.2, raw=True)
    ACFG.leap(forward_time=0.305, jump_time=0.3, direction_key="w")
    ACFG.move("d", 0.2, raw=True)
    ACFG.leap(forward_time=0.6, jump_time=0.3, direction_key="s", jump_delay=0.15)

    ACFG.move("w", 0.125, raw=True)
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="d", jump_delay=0.1)
    ACFG.move("d", 0.125, raw=True)
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="d")
    ACFG.move("s", 0.5, raw=True)
    ACFG.leap(forward_time=0.2, jump_time=0.2, direction_key="s")
    ACFG.move("a", 0.1, raw=True)
    ACFG.move("s", 0.15, raw=True)
    ACFG.move("a", 0.8, raw=True)
    ACFG.move("w", 0.125, raw=True)
    ACFG.leap(forward_time=0.3, jump_time=0.15, direction_key="d")
    ACFG.move("d", 1.7, raw=True)
    ACFG.move("w", 0.5, raw=True)
    ACFG.move("a", 0.5, raw=True)

    ACFG.move("s", 0.41, raw=True)
    ACFG.move("d", 0.55, raw=True)
    ACFG.leap(forward_time=0.4, jump_time=0.75, direction_key="a")
    ACFG.leap(forward_time=0.2, jump_time=0.3, direction_key="d", jump_delay=0.1)

    ACFG.move("s", 0.075, raw=True)
    ACFG.move("a", 0.05, raw=True)
