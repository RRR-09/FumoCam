import serial  # pip install pyserial
from time import sleep
import json
from config import *


class ArduinoConfig:
    port = "COM3"
    baudrate = 115200
    interface_timeout = 0.1
    interface = serial.Serial(port=port, baudrate=baudrate, timeout=interface_timeout)
    max_serial_wait_time = 10
    tick_rate = 0.25
    screen_height_pitch_ratios = {
        1080: 1080/2.596,
        720: 720/1.73
    }
    msg_letter_wait_time = 10/1000 # 10ms
    zoom_ratio = 0.013 # 100 = full zoom
    turn_ratio = 120 # 360 = 3s = 360 degrees
    move_ratio = 0.3576 # 1 unit is smallest amount (to 4 decimal places) needed to consistently fall off diagonal spawn platform

    def arduino_interface(self, payload, delay_time=0):
        payload = json.dumps(payload, separators=(',', ':'))
        
        completed = False
        data = []
        max_wait_time = delay_time+self.max_serial_wait_time
        
        self.interface.write(bytes(payload+"\0", "utf-8"))
        
        for tick in range(int(max_wait_time/self.tick_rate)):
            sleep(self.tick_rate)
            line = self.interface.readline()
            if line:
                data.append(line)
                if ";Complete;" in str(line):
                    completed = True
                    break
        
        print(f"[Arduino Write/Read]\n{data}")
        return completed


    def jump(self, jump_time=1):
        payload = {"type": "keyhold", "key": ' ', "hold_time": jump_time}
        self.arduino_interface(payload, payload["hold_time"])
    #jump(1)


    def left_click(self):
        payload = {"type": "leftClick"}
        self.arduino_interface(payload, 2) # Arbitrary max time for safety
    #left_click()


    def leap(self, forward_time, jump_time):
        payload = {"type": "leap", "forward_time": forward_time, "jump_time": jump_time}
        self.arduino_interface(payload, max(payload["forward_time"], payload["jump_time"]))
    #leap(jump_time=1, forward_time=3)


    def look(self, direction, amount):
        turn_amount = round(amount/self.turn_ratio, 4)
        payload = {"type": "keyhold", "key": f"KEY_{direction.upper()}_ARROW", "hold_time": turn_amount}
        self.arduino_interface(payload, payload["hold_time"])
    #look("left", 90)


    def move(self, direction_key, amount):
        move_amount = round(amount*self.move_ratio, 4)
        payload = {"type": "keyhold", "key": direction_key, "hold_time": move_amount}
        self.arduino_interface(payload, payload["hold_time"])
    #move("w", 2)


    def moveMouseAbsolute(self, x, y):
        payload = {"type": "resetMouse", "width": SCREEN_RES["width"], "height": SCREEN_RES["height"]}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
        sleep(1)
        payload = {"type": "moveMouse", "x": x, "y": y}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
    #moveMouseAbsolute(x=SCREEN_RES["width"]*0.5, y=SCREEN_RES["height"]*0.5)


    def moveMouseRelative(self, x, y):
        payload = {"type": "moveMouse", "x": x, "y": y}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
    #moveMouse(x=0, y=SCREEN_RES["height"]*0.34)


    def scrollMouse(self, amount, down=True):
        payload = {"type": "scrollMouse", "down": down}
        for i in range(amount):
            self.arduino_interface(payload, 4) # Arbitrary max time for safety    
    #scrollMouse(4)

    def pitch(self, amount, up):
        ratio = self.screen_height_pitch_ratios[SCREEN_RES["height"]]
        pitch_amount = round((amount/180)*ratio, 4)
        
        payload = {"type": "resetMouse", "width": SCREEN_RES["width"], "height": SCREEN_RES["height"]}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
        
        payload = {"type": "pitch", "up": up, "amount": pitch_amount, "width": SCREEN_RES["width"], "height": SCREEN_RES["height"]}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
        
        payload = {"type": "moveMouse", "x": SCREEN_RES["width"]/2, "y": SCREEN_RES["height"]}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
    #pitch(180, up=False)


    def keyPress(self, key, amount=0.2):
        payload = {"type": "keyhold", "key": key, "hold_time": amount}
        self.arduino_interface(payload, payload["hold_time"])
    #move("w", 2)

    def resetMouse(self, move_to_bottom_left=True):
        payload = {"type": "resetMouse", "width": SCREEN_RES["width"], "height": SCREEN_RES["height"]}
        self.arduino_interface(payload, 4) # Arbitrary max time for safety
        if move_to_bottom_left:
            payload = {"type": "moveMouse", "x": SCREEN_RES["width"]-1, "y": SCREEN_RES["height"]-1}
            self.arduino_interface(payload, 4) # Arbitrary max time for safety
    #resetMouse()

    def send_message(self, message):
        message = message[:100] # 100 char ingame limit
        payload = {"type": "msg", "len": len(message), "msg": message}
        self.arduino_interface(payload, payload["len"]*self.msg_letter_wait_time)
        sleep(0.75)
    #send_message("Long test message to test accuracy of typing Long test message to test accuracy of typing Long testt")


    def use(self):
        payload = {"type": "keyhold", "key": 'e', "hold_time": 1.5}
        self.arduino_interface(payload, payload["hold_time"])
    #use()


    def zoom(self, zoom_direction_key, amount):
        zoom_amount = round(self.zoom_ratio * amount, 4)
        payload = {"type": "keyhold", "key": zoom_direction_key, "hold_time": zoom_amount}
        self.arduino_interface(payload, payload["hold_time"])
    #zoom("o", 25)

ACFG = ArduinoConfig()

