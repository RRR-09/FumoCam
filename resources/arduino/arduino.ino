#include <ArduinoJson.h>
#include "Keyboard.h"
#include "Mouse.h"
const unsigned char MAX_PAYLOAD_LENGTH = 200;

void setup() {
  Serial.begin(9600);
  while(!Serial) {}
  Keyboard.begin();
  Mouse.begin();
}

void smartDelay(double delay_seconds){
  const unsigned long delay_microseconds = (delay_seconds*1000000);
  while (micros() > (micros() + delay_microseconds )) {} // If about to overflow, wait
  const unsigned long time_goal = micros() + delay_microseconds;
  while (micros() < time_goal) {} // Main delay
}

void leap(StaticJsonDocument<MAX_PAYLOAD_LENGTH> payload) {
  const double jump_seconds = payload["jump_time"];
  const unsigned long jump_microseconds = (jump_seconds*1000000);
  const double forward_seconds = payload["forward_time"];
  const unsigned long forward_microseconds = (forward_seconds*1000000);

  //todo: inefficient, simplify
  if (jump_seconds > forward_seconds){
    while (micros() > (micros() + jump_seconds)) {} // If about to overflow, wait
    const unsigned long forward_goal = micros() + forward_microseconds;
    const unsigned long jump_goal = micros() + jump_microseconds;
    Keyboard.press('w');
    Keyboard.press(' ');
    while (micros() < forward_goal) {} // Forward expires first
    Keyboard.release('w'); // Release forward
    while (micros() < jump_goal) {} // Jump lasts longer
    Keyboard.release(' '); // Release jump
  } else {
    while (micros() > (micros() + forward_seconds)) {} // If about to overflow, wait
    const unsigned long jump_goal = micros() + jump_microseconds;
    const unsigned long forward_goal = micros() + forward_microseconds;
    Keyboard.press('w');
    Keyboard.press(' ');
    while (micros() < jump_goal) {} // Jump expires first
    Keyboard.release(' '); // Release jump
    while (micros() < forward_goal) {} // Forward lasts longer
    Keyboard.release('w'); // Release forward
  }
}

void keyhold(StaticJsonDocument<MAX_PAYLOAD_LENGTH> payload) {
  const char* input_key = payload["key"];
  char key = input_key[0];  
  if (!strcmp(input_key, "KEY_LEFT_ARROW")) {
    key = KEY_LEFT_ARROW;
  } else if (!strcmp(input_key, "KEY_RIGHT_ARROW")) {
    key = KEY_RIGHT_ARROW;
  }
  
  const double hold_seconds = payload["hold_time"];
  const unsigned long hold_microseconds = (hold_seconds*1000000);
  
  while (micros() > (micros() + hold_microseconds)) {} // If about to overflow, wait

  const unsigned long time_goal = micros() + hold_microseconds;
  Keyboard.press(key); // press and hold
  while (micros() < time_goal) {} // Main delay
  
  Keyboard.release(key); // release
}

void moveMouse(int amount_x, int amount_y, double move_speed) {
  int move_x_times = (abs(amount_x) / 127);
  bool left = amount_x < 0;
  int move_y_times = (abs(amount_y) / 127);
  bool up = amount_y < 0;
  signed char last_move_x = abs(amount_x) - (move_x_times * 127);
  
  Serial.print("Move X: ");
  Serial.print(((move_x_times*127) + last_move_x) * ((left) ? -1 : 1));
  if (left) {
    last_move_x = last_move_x * -1;
  }
  
  signed char last_move_y = abs(amount_y) - (move_y_times * 127);
  Serial.print("Move Y: ");
  Serial.print(((move_y_times*127) + last_move_y) * ((up) ? -1 : 1));
  if (up) {
    last_move_y = last_move_y * -1;
  }
  
  if (move_x_times != 0 || last_move_x != 0){
    for (int i = 0; i < move_x_times; i++) {
      Mouse.move((left) ? -127 : 127, 0, 0);
      smartDelay(move_speed);
    }
    Mouse.move(last_move_x, 0, 0);
    smartDelay(move_speed);
  }
  if (move_y_times != 0 || last_move_y != 0){
    for (int i = 0; i < move_y_times; i++) {
      Mouse.move(0, (up) ? -127 : 127, 0);
      smartDelay(move_speed);
    }
    Mouse.move(0, last_move_y, 0);
    smartDelay(move_speed);
  }
  smartDelay(move_speed);
  Serial.print(";MouseDone;\n");
}

void resetMouse(StaticJsonDocument<MAX_PAYLOAD_LENGTH> payload) {
  const int screen_width = payload["width"];
  const int screen_height = payload["height"];
  const double move_speed = 0.02;
  moveMouse((screen_width+1)*-1, (screen_height+1)*-1, move_speed); // Reset to top left
}

void moveMouseAction(StaticJsonDocument<MAX_PAYLOAD_LENGTH> payload) {
  int amount_x = payload["x"];
  int amount_y = payload["y"];
  const double move_speed = 0.02;
  moveMouse(amount_x, amount_y, move_speed); // Reset to top left
}

void leftClick() {
  Mouse.click();
}

void pitch(StaticJsonDocument<MAX_PAYLOAD_LENGTH> payload) {
  const bool up = payload["up"];
  int amount = (up) ? payload["amount"].as<int>() : payload["amount"].as<int>() * -1; // Pull mouse down to move camera to top-down view
  const int screen_width = payload["width"];
  const int screen_height = payload["height"];
  
  const double move_speed = 0.02;
  const double delay_speed = 0.4;
  moveMouse(screen_width/2, screen_height/2, move_speed); // Move to center
  smartDelay(delay_speed);
  Mouse.press(MOUSE_RIGHT);
  smartDelay(delay_speed);
  moveMouse(0, amount, move_speed);
  smartDelay(delay_speed);
  Mouse.release(MOUSE_RIGHT);
}

void chat(StaticJsonDocument<MAX_PAYLOAD_LENGTH> payload) {  
  const int msg_len = payload["len"];
  const char* msg = payload["msg"];
  Keyboard.write('/');
  delay(50);
  for(int i = 0; i < msg_len; i++) {
    Keyboard.write(msg[i]);
    delay(10);
  }
  delay(50);
  Keyboard.write(KEY_RETURN);
}

void loop() {
  if (Serial.available() > 0) {
    // Read serial input
    char payload_string[MAX_PAYLOAD_LENGTH];
    unsigned char payload_pos = 0;
    unsigned char failures = 0;
    Serial.print(";Serial Start;");
    while (true){
      int payload_byte = Serial.read();
      if (payload_byte == -1){
        if (failures > 254){
          Serial.print(";Serial Read Error;");
          break;
        }
        failures++;
        continue;
      }
      failures = 0;
      char payload_char = (char)payload_byte;
      if (payload_char != '\0' && (payload_pos < MAX_PAYLOAD_LENGTH - 1))
      {
        Serial.print(payload_char);
        payload_string[payload_pos] = payload_char;
        payload_pos++;
      } else {
        Serial.print(";NullTerm;");  
        payload_string[payload_pos] = '\0';
        break;
      }
    }
    Serial.print(";Serial End;");

    //Parse serial input
    StaticJsonDocument<MAX_PAYLOAD_LENGTH+100> parsed_payload;
    DeserializationError err = deserializeJson(parsed_payload, payload_string);
    if (err) {
      Serial.print(F("deserializeJson() failed with code "));
      Serial.print(err.f_str());
      Serial.print(";Complete;");
      return;
    }
    
    //Run requested process
    char* type = parsed_payload["type"];
    if (!strcmp(type, "keyhold")) {
      keyhold(parsed_payload);
    } else if (!strcmp(type, "msg")) {
      chat(parsed_payload);
    } else if (!strcmp(type, "pitch")) {
      pitch(parsed_payload);
    } else if (!strcmp(type, "resetMouse")) {
      resetMouse(parsed_payload);
    } else if (!strcmp(type, "moveMouse")) {
      moveMouseAction(parsed_payload);
    } else if (!strcmp(type, "leftClick")) {
      leftClick();
    } else if (!strcmp(type, "leap")) {
      leap(parsed_payload);
    } else {
      Serial.print("Unknown type: ");
      Serial.print(type);
    }
    Serial.print(";Complete;");
  }
}
