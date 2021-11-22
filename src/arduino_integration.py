from utilities import *
import serial  # pip install pyserial
from time import sleep
import json


class ArduinoConfig:
    
    interface_baudrate = 9300
    interface_port = "COM3"
    interface_timeout = 0.1
    
    interface = serial.Serial(baudrate=interface_baudrate, timeout=interface_timeout)
    
    interface.port = interface_port
    interface_ready = None
    
    
    def interface_try_open(self, do_log=False):
        try:
            self.interface.close()
        except:
            pass
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
            pass

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
    screen_height_pitch_ratios = {
        1080: 1080/2.596,
        720: 720/1.73
    }
    msg_letter_wait_time = 10/1000 # 10ms
    zoom_ratio = 0.013 # 100 = full zoom
    turn_ratio = 124.15 # 360 = 3s = 360 degrees; smaller overshoot, bigger undershoot
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
        sleep(0.5)
    #leap(jump_time=1, forward_time=3)


    def look(self, direction, amount, raw=False):
        turn_amount = amount
        if not raw:
            turn_amount /= self.turn_ratio
        payload = {"type": "keyhold", "key": f"KEY_{direction.upper()}_ARROW", "hold_time": turn_amount}
        self.arduino_interface(payload, payload["hold_time"])
        sleep(0.5)
    #look("left", 90)


    def move(self, direction_key, amount, raw=False):
        move_amount = amount
        if not raw:
            move_amount *= self.move_ratio
        payload = {"type": "keyhold", "key": direction_key, "hold_time": move_amount}
        self.arduino_interface(payload, payload["hold_time"])
        sleep(0.5)
    #move("w", 2)


    def moveMouseAbsolute(self, x, y):
        payload = {"type": "resetMouse", "width": SCREEN_RES["width"], "height": SCREEN_RES["height"]}
        self.arduino_interface(payload, 5) # Arbitrary max time for safety
        sleep(2)
        payload = {"type": "moveMouse", "x": x, "y": y}
        self.arduino_interface(payload, 5) # Arbitrary max time for safety
    #moveMouseAbsolute(x=SCREEN_RES["width"]*0.5, y=SCREEN_RES["height"]*0.5)


    def moveMouseRelative(self, x, y):
        payload = {"type": "moveMouse", "x": x, "y": y}
        self.arduino_interface(payload, 5) # Arbitrary max time for safety
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

def treehouse_to_main():
    log_process("AutoNav")
    log("Treehouse -> Main")
    ACFG.move("w",3.3, raw=True)
    ACFG.move("d",0.2, raw=True)
    ACFG.look("left", 1.105, raw=True)
    log_process("")
    log("")


def comedy_to_main():
    log_process("AutoNav")
    log("Comedy Machine -> Main")
    ACFG.move("w",3.75, raw=True)
    ACFG.move("a",0.5)
    ACFG.look("right", 0.385, raw=True)
    
    log_process("")
    log("")

def main_to_shrimp_tree():
    log_process("AutoNav")
    log("Main -> Shrimp Tree")
    #If main spawn is facing North,
    #Turn to face West
    ACFG.look("left", 0.75, raw=True)
    ACFG.move("a", 1.3, raw=True) # 0.3576
    ACFG.move("w", 0.75, raw=True)
    #Right in front of first step
    ACFG.leap(0.54, 0.475)
    #Right before first tree
    ACFG.leap(0.4, 0.4)
    #Move towards edge of tree
    ACFG.move("a", 0.1, raw=True)
    #Turn towards shrimp tree
    ACFG.look("left", 1.135, raw=True)
    #Leap to Shrimp Tree
    ACFG.leap(0.6, 0.4)
    #Face South, character looking North
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
    ACFG.look("left",  1.5, raw=True)
    ACFG.leap(0.75, 0.75)
    ACFG.move("w", 0.75, raw=True)
    ACFG.leap(1, 1)
    ACFG.look("left", 0.75, raw=True)
    ACFG.move("s", 0.05, raw=True)
    ACFG.move("a", 0.075, raw=True)
    ACFG.move("s", 0.1, raw=True)
    log_process("")
    log("")
    

if __name__ == "__main__":
    ACFG.initalize_serial_interface(do_log=True)
    asyncio.get_event_loop().run_until_complete(check_active(force_fullscreen=False))
    sleep(0.5)
    
    #comedy_to_main()
    treehouse_to_main()
    #sleep(3)
    #main_to_train()
    main_to_shrimp_tree()
    #main_to_ratcade()
