from json import dumps
from time import sleep

import pyautogui
import pydirectinput
import serial  # pip install pyserial
import serial.tools.list_ports  # TODO: figure out why not the same as above

from utilities import CFG, check_active, log, log_process


class ArduinoConfig:

    interface_baudrate = 9300
    interface_timeout = 0.1
    interface = serial.Serial(baudrate=interface_baudrate, timeout=interface_timeout)
    while True:
        ports = [
            port.name
            for port in serial.tools.list_ports.comports()
            if "Arduino Leonardo" in port.description
        ]
        if len(ports) == 1:
            interface.port = ports[0]
            break
        elif len(ports) == 0:
            log("Precision chip not found by name,\nAssuming first available port")
            sleep(1)
            all_ports = serial.tools.list_ports.comports()
            if len(all_ports) > 0:
                interface.port = all_ports[0].name
                log("")
                break
            log("No ports available! Is precision chip plugged in?")
        else:
            log("More than one precision chip detected!")
        sleep(1)

    interface_ready = None

    def interface_try_open(self, do_log=False):
        try:
            self.interface.close()
        except Exception:
            print("Failed to close interface [OK]")
        try:
            self.interface.open()
            if self.interface.isOpen():
                self.interface.close()
            self.interface.open()
            if self.interface_ready is False or do_log:
                log("Intialized")
            self.interface_ready = True
        except serial.serialutil.SerialException:
            log("Failed to establish interface, retrying...")
            self.interface_ready = False

    def initalize_serial_interface(self, do_log=False):
        if do_log:
            log_process("Precision Chip Interface")
            log("Reserving precision chip interface port")
        self.interface.close()
        while not self.interface_ready:
            sleep(1)
            self.interface_try_open(do_log=do_log)
        log("")
        log_process("")

    max_serial_wait_time = 10
    tick_rate = 0.25
    screen_height_pitch_ratios = {1080: 1080 / 2.596, 720: 720 / 1.73}
    msg_letter_wait_time = 10 / 1000  # 10ms
    zoom_ratio = 0.013  # 100 = full zoom
    turn_ratio = 124.15  # 360 = 3s = 360 degrees; smaller overshoot, bigger undershoot
    move_ratio = 0.3576  # 1 unit is smallest amount (to 4 decimal places) needed to fall off diagonal spawn platform

    def arduino_interface(self, payload_object: dict, delay_time: float = 0):
        payload = dumps(payload_object, separators=(",", ":"))

        completed = False
        data = []
        max_wait_time = delay_time + self.max_serial_wait_time

        self.interface.write(bytes(payload + "\0", "utf-8"))

        for tick in range(int(max_wait_time / self.tick_rate)):
            sleep(self.tick_rate)
            line = self.interface.readline()
            if line:
                data.append(line)
                if ";Complete;" in str(line):
                    completed = True
                    break

        print(f"[Arduino Write/Read]\n{data}")
        return completed

    def jump(self, jump_time: float = 1):
        payload = {"type": "keyhold", "key": " ", "hold_time": jump_time}
        self.arduino_interface(payload, jump_time)

    def left_click(self):
        if CFG.mouse_software_emulation:
            return self.left_click_software()
        payload = {"type": "leftClick"}
        self.arduino_interface(payload, 2)  # Arbitrary max time for safety

    def left_click_software(self, do_click: bool = True):
        """
        Even pydirectinput cant click normally.
        This is a work-around that actually clicks in the area the cursor was moved.
        """
        alt_tab_duration = 0.5
        pyautogui.hotkey("alt", "tab")
        sleep(alt_tab_duration)
        pyautogui.hotkey("alt", "tab")
        sleep(alt_tab_duration * 2)
        if do_click:
            pydirectinput.click()

    def middle_click_software(self):
        """
        Even pydirectinput cant click normally.
        This is a work-around that actually clicks in the area the cursor was moved.
        """
        alt_tab_duration = 0.5
        pyautogui.hotkey("alt", "tab")
        sleep(alt_tab_duration)
        pyautogui.hotkey("alt", "tab")
        sleep(alt_tab_duration * 2)
        pydirectinput.click(button="middle")

    def leap(
        self,
        forward_time: float,
        jump_time: float,
        direction_key: str = "w",
        jump_delay: float = 0,
    ):
        payload = {
            "type": "leap",
            "forward_time": forward_time,
            "jump_time": jump_time,
            "direction_key": direction_key,
            "jump_delay": jump_delay,
        }
        self.arduino_interface(
            payload,
            max(forward_time, jump_time) + jump_delay,
        )
        sleep(0.5)

    def look(self, direction: str, amount: float, raw: bool = False):
        turn_amount = amount
        if not raw:
            turn_amount /= self.turn_ratio
        payload = {
            "type": "keyhold",
            "key": f"KEY_{direction.upper()}_ARROW",
            "hold_time": turn_amount,
        }
        self.arduino_interface(payload, turn_amount)
        sleep(0.5)

    def move(self, direction_key: str, amount: float, raw: bool = False):
        move_amount = amount
        if not raw:
            move_amount *= self.move_ratio
        payload = {"type": "keyhold", "key": direction_key, "hold_time": move_amount}
        self.arduino_interface(payload, move_amount)
        sleep(0.5)

    def moveMouseAbsolute(self, x: int, y: int):
        if CFG.mouse_software_emulation:
            return self.moveMouseAbsolute_software(x, y)
        payload = {
            "type": "resetMouse",
            "width": CFG.screen_res["width"],
            "height": CFG.screen_res["height"],
        }
        self.arduino_interface(payload, 5)  # Arbitrary max time for safety
        sleep(2)
        payload = {"type": "moveMouse", "x": x, "y": y}
        self.arduino_interface(payload, 5)  # Arbitrary max time for safety

    def moveMouseAbsolute_software(self, x: int, y: int):
        pydirectinput.moveTo(x, y)
        sleep(2)

    def moveMouseRelative(self, x: int, y: int):
        if CFG.mouse_software_emulation:
            return self.moveMouseRelative_software(x, y)
        payload = {"type": "moveMouse", "x": x, "y": y}
        self.arduino_interface(payload, 5)  # Arbitrary max time for safety

    def moveMouseRelative_software(self, x: int, y: int):
        pydirectinput.move(x, y)
        sleep(2)

    def scrollMouse(self, amount: int, down: bool = True):
        payload = {"type": "scrollMouse", "down": down}
        for scrolls in range(amount):
            self.arduino_interface(payload, 4)  # Arbitrary max time for safety

    def pitch(self, amount: float, up: bool, raw: bool = False):
        ratio = self.screen_height_pitch_ratios[CFG.screen_res["height"]]
        pitch_amount = amount
        if not raw:
            pitch_amount = round((pitch_amount / 180) * ratio, 4)

        payload = {
            "type": "resetMouse",
            "width": CFG.screen_res["width"],
            "height": CFG.screen_res["height"],
        }
        self.arduino_interface(payload, 4)  # Arbitrary max time for safety

        payload = {
            "type": "pitch",
            "up": up,
            "amount": pitch_amount,
            "width": CFG.screen_res["width"],
            "height": CFG.screen_res["height"],
        }
        self.arduino_interface(payload, 4)  # Arbitrary max time for safety

        payload = {
            "type": "moveMouse",
            "x": CFG.screen_res["width"] / 2,
            "y": CFG.screen_res["height"],
        }
        self.arduino_interface(payload, 4)  # Arbitrary max time for safety

    def keyPress(self, key: str, amount: float = 0.2):
        payload = {"type": "keyhold", "key": key, "hold_time": amount}
        self.arduino_interface(payload, amount)

    def resetMouse(self, move_to_bottom_right: bool = True):
        if CFG.mouse_software_emulation:
            if move_to_bottom_right:
                self.moveMouseAbsolute_software(
                    CFG.screen_res["width"] - 1, CFG.screen_res["height"] - 1
                )
                self.middle_click_software()
                return
            self.moveMouseAbsolute_software(1, 1)
            self.middle_click_software()
            return
        payload = {
            "type": "resetMouse",
            "width": CFG.screen_res["width"],
            "height": CFG.screen_res["height"],
        }
        self.arduino_interface(payload, 4)  # Arbitrary max time for safety
        if move_to_bottom_right:
            payload = {
                "type": "moveMouse",
                "x": CFG.screen_res["width"] - 1,
                "y": CFG.screen_res["height"] - 1,
            }
            self.arduino_interface(payload, 4)  # Arbitrary max time for safety

    def send_message(self, message: str):
        message = message[:100]  # 100 char ingame limit
        payload = {"type": "msg", "len": len(message), "msg": message}
        self.arduino_interface(payload, len(message) * self.msg_letter_wait_time)
        sleep(0.75)

    def use(self):
        payload = {"type": "keyhold", "key": "e", "hold_time": 1.5}
        self.arduino_interface(payload, payload["hold_time"])

    def zoom(self, zoom_direction_key: str, amount: float):
        zoom_direction_multiplier = 1.0 if zoom_direction_key == "o" else -1.0
        CFG.zoom_level += amount * zoom_direction_multiplier
        CFG.zoom_level = min(
            CFG.zoom_max, max(CFG.zoom_min, CFG.zoom_level)
        )  # Keep it in bounds
        print(CFG.zoom_level)

        zoom_amount = round(self.zoom_ratio * amount, 4)
        payload = {
            "type": "keyhold",
            "key": zoom_direction_key,
            "hold_time": zoom_amount,
        }
        self.arduino_interface(payload, zoom_amount)


ACFG = ArduinoConfig()


if __name__ == "__main__":
    import asyncio

    async def test():
        await check_active(force_fullscreen=False)
        sleep(0.5)
        # had_to_move, area = move_mouse_chat_cmd(,-600)
        # print(had_to_move, area)

    asyncio.get_event_loop().run_until_complete(test())
