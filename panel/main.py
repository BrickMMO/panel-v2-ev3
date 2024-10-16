#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent
from ev3dev2.sensor.lego import TouchSensor, ColorSensor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sound import Sound
from ev3dev2.motor import MoveTank
from time import time, sleep
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

# Initialize the EV3 sound object
ev3 = Sound()

# City Id
city_id = "1"

# Initialize motors
power_lever = LargeMotor(OUTPUT_A)
motor_B = LargeMotor(OUTPUT_B)
motor_C = LargeMotor(OUTPUT_C)
motor_D = LargeMotor(OUTPUT_D)

# Initialize sensors
cartridge = ColorSensor(INPUT_1)
switch_2 = TouchSensor(INPUT_2)
switch_3 = TouchSensor(INPUT_3)
switch_4 = TouchSensor(INPUT_4)

# Initial states
power_lever_value = "OFF"
motor_B_value = 0
motor_C_value = 0
motor_D_value = 0
cartridge_value = None
switch_2_value = "OFF"
switch_3_value = "OFF"
switch_4_value = "OFF"

def reset_power_lever():
    # Move motor to a default position by running until it stalls
    power_lever.on(SpeedPercent(-10))  # Start motor at -10% speed
    power_lever.wait_until('stalled')   # Wait until the motor stalls
    power_lever.stop(stop_action="hold")  # brake the motor after it stalls

    # Get the initial motor angle (position)
    initial_power_lever_angle = power_lever.position
    print("Initial Angle:", initial_power_lever_angle)
    power_lever.reset()

    # Move motor to a target position and reset the angle
    power_lever.on_for_degrees(SpeedPercent(10), 60, brake=True, block=True)
    print("Angle Before Reset:", power_lever.position)
    power_lever.reset()
    print("Angle After Reset:", power_lever.position)

# Function to turn power lever between 0 (OFF) and 60 (ON) degrees
def turn_power_lever(value):
    if value == "ON":
        power_lever.on_to_position(SpeedPercent(10), 60, brake=True, block=True)
        ev3.play_song((('C4', 'e'),('E4', 'e'),('G4', 'q')))
    elif value == "OFF":
        power_lever.on_to_position(SpeedPercent(-10), 0, brake=True, block=True)
        ev3.play_song((('G4', 'e'),('E4', 'e'),('C4', 'q')))

# Function to check and toggle power lever position
def power_lever_position():
    angle = power_lever.position
    print("Current Power Lever Angle: ", angle)

    # If the motor is moved away from 0, move it to 60 degrees (ON)
    if (angle >= -8 and angle <= -2) or (angle >= 2 and angle <= 15):
        turn_power_lever("ON")
        update_setting("A","ON")
        return True

    # If the motor is moved away from 60, move it back to 0 degrees (OFF)
    elif (angle >= 50 and angle <= 58) or (angle >= 64 and angle <= 68):
        turn_power_lever("OFF")
        update_setting("A","OFF")
        return False

    # Motor is either at 0 or 60 degrees
    return 59 <= angle <= 62

# Function to fetch initial settings from the API
def fetch_current_settings():
    request_url = "https://console.brickmmo.com/api/panel/complete/city_id/" + city_id
    try:
        request = Request(request_url, data=urlencode({"timestamp": time()}).encode("utf-8"))
        with urlopen(request, timeout=5) as response:
            # Read and decode the response once
            response_data = response.read().decode("utf-8") 
            print("Raw Response Data:", response_data)
            data = json.loads(response_data)
            
            # Check if the response contains the expected data
            if "panel" in data:
                panel_data = data['panel']
                
                # Update EV3 panel settings based on the API response
                global power_lever_value, motor_B_value, motor_C_value, motor_D_value
                global cartridge_value, switch_2_value, switch_3_value, switch_4_value

                for setting in panel_data:
                    port_id = setting['port_id']
                    value = setting['value']
                    cartridge = setting.get('cartridge')
                    # s1_value = next((setting['value'] for setting in panel_data if setting['port_id'] == 'S1'), None)
                    if port_id == 'A':
                        if power_lever_value != value:
                            turn_power_lever(value)
                            power_lever_value = value 
                            print("Power Lever initial value: " + value)
                    if cartridge_value is not None:
                        if str(cartridge_value) == cartridge:
                            if port_id == 'B':
                                motor_B_value = int(value)
                                print("Motor B value for " + cartridge + ": "+ value)
                            elif port_id == 'C':
                                motor_C_value = int(value)
                                print("Motor C value for " + cartridge + ": "+ value)
                            elif port_id == 'D':
                                motor_D_value = int(value)
                                print("Motor D value for " + cartridge + ": "+ value)
                            elif port_id == 'S2':
                                switch_2_value = value
                                print("Switch S2 value for " + cartridge + ": "+ value)
                            elif port_id == 'S3':
                                switch_3_value = value
                                print("Switch S3 value for " + cartridge + ": "+ value)
                            elif port_id == 'S4':
                                switch_4_value = value
                                print("Switch S4 value for " + cartridge + ": "+ value)
            else:
                print("Unexpected response format: ", data)
                
    except Exception as e:
        print("Error during API call:", e)


# Function to update settings via API when an action occurs on the panel
def update_setting(port_id, value, cartridge=None):
    # Handle value 0 url encoding
    if value == "0":
        value = "%30"
        
    if cartridge is not None:
        # request_url = "https://console.brickmmo.com/api/panel/update/city_id/" + city_id + "/port_id/"+ port_id + "/cartridge/" + cartridge + "/value/" + value
        request_url = "https://console.brickmmo.com/api/panel/update/city_id/" + city_id + "/port_id/"+ port_id + "/cartridge/" + cartridge + "/value/" + value +"/id/1"
    else:
        # request_url = "https://console.brickmmo.com/api/panel/update/city_id/" + city_id + "/port_id/"+ port_id + "/value/" + value
        request_url = "https://console.brickmmo.com/api/panel/update/city_id/" + city_id + "/port_id/"+ port_id + "/value/" + value +"/id/1"
        
    try:
        # Prepare the data and make a POST request
        print(request_url)
        request = Request(request_url, data=urlencode({"timestamp": time()}).encode("utf-8"))
        with urlopen(request, timeout=5) as response:
            print(response.read())
            response_data = response.read().decode("utf-8") 
            data = json.loads(response_data)
            print("Updated port " , port_id , " with value " , value , ". Response: ", data)
            response.close()

    except Exception as e:
        print("Error while updating setting for port " , port_id , " : " , e)

# Function to check the current cartridge
def check_current_cartridge():
    global cartridge_value
    current_cartridge = cartridge.color_name.upper()
    print("Current Cartridge: ", current_cartridge)
    if current_cartridge != cartridge_value and current_cartridge is not None:
        print("Cartridge has changed from ", cartridge_value, " to ", current_cartridge)
        cartridge_value = current_cartridge
        sleep(2)
        if cartridge_value != "NOCOLOR":
            update_setting("S1",str(cartridge_value))
            fetch_current_settings()
            ev3.beep()
    else:
        print("Cartridge remains the same:", current_cartridge)

# Function to handle motor value increment/decrement based on angle change
def motor_angle_to_value(prev_angle, current_angle):
    # Determine the angle change (can be positive or negative)
    angle_diff = current_angle - prev_angle

    # If the angle increased, the motor is spinning clockwise
    if angle_diff > 0:
        return 5  # Increment by 5
    # If the angle decreased, the motor is spinning counterclockwise
    elif angle_diff < 0:
        return -5  # Decrement by 5
    # No significant change in angle
    else:
        return 0

# Function to toggle switch state between ON and OFF
def toggle_switch(value):
    return "OFF" if value == "ON" else "ON"

# Function to handle switch and motor interactions for different cartridges
def handle_panel_interactions():
    global power_lever_value, motor_B_value, motor_C_value, motor_D_value
    global cartridge_value, switch_2_value, switch_3_value, switch_4_value
    
    # Track previous motor positions to calculate change in angles
    prev_motor_B_angle = motor_B.position
    prev_motor_C_angle = motor_C.position
    prev_motor_D_angle = motor_D.position
    
    color_name = cartridge_value
    
    # Check cartridge and handle interactions
    if color_name != "NOCOLOR" and color_name != None:
        # Handle switch S2
        if switch_2.is_pressed:
            switch_2_value = toggle_switch(switch_2_value)
            print("Switch 2 is pressed with", color_name, "cartridge! Value:", switch_2_value)
            ev3.beep()
            update_setting('S2', switch_2_value,color_name)

        # Handle switch S3
        if switch_3.is_pressed:
            switch_3_value = toggle_switch(switch_3_value)
            print("Switch 3 is pressed with", color_name, "cartridge! Value:", switch_3_value)
            ev3.beep()
            update_setting('S3', switch_3_value,color_name)

        # Handle switch S4
        if switch_4.is_pressed:
            switch_4_value = toggle_switch(switch_4_value)
            print("Switch 4 is pressed with", color_name, "cartridge! Value:", switch_4_value)
            ev3.beep()
            update_setting('S4', switch_4_value,color_name)

        # Handle motor B
        current_motor_B_angle = motor_B.position
        angle_change_B = motor_angle_to_value(prev_motor_B_angle, current_motor_B_angle)
        motor_B_value += angle_change_B
        if angle_change_B != 0 and (motor_B_value >=0 and motor_B_value <= 100):
            motor_B_value = max(0, min(100, motor_B_value))
            print("Motor B value updated for", color_name, ":", motor_B_value)
            update_setting('B', str(motor_B_value), color_name)
            ev3.beep() if angle_change_B > 0 else ev3.beep(args='-r 2')
        elif motor_B_value < -5 or motor_B_value > 105:
            motor_B_value = 0 if motor_B_value < -5 else 100

        # Handle motor C
        current_motor_C_angle = motor_C.position
        angle_change_C = motor_angle_to_value(prev_motor_C_angle, current_motor_C_angle)
        motor_C_value += angle_change_C
        if angle_change_C != 0 and motor_C_value >=0 and motor_C_value <= 100:
            motor_C_value = max(0, min(100, motor_C_value))
            print("Motor C value updated for", color_name, ":", motor_C_value)
            update_setting('C', str(motor_C_value), color_name)
            ev3.beep() if angle_change_C > 0 else ev3.beep(args='-r 2')
        elif motor_C_value < -5 or motor_C_value > 105:
            motor_C_value = 0 if motor_C_value < -5 else 100
       
        # # Handle motor D
        current_motor_D_angle = motor_D.position
        angle_change_D = motor_angle_to_value(prev_motor_D_angle, current_motor_D_angle)
        motor_D_value += angle_change_D
        if angle_change_D != 0 and motor_D_value >=0 and motor_D_value <= 100:
            motor_D_value = max(0, min(100, motor_D_value))
            print("Motor D value updated for", color_name, ":", motor_D_value)
            update_setting('D', str(motor_D_value), color_name)
            ev3.beep() if angle_change_D > 0 else ev3.beep(args='-r 2')
        elif motor_D_value < -5 or motor_D_value > 105:
            motor_D_value = 0 if motor_D_value < -5 else 100
            
            
        prev_motor_B_angle = current_motor_B_angle
        prev_motor_C_angle = current_motor_C_angle
        prev_motor_D_angle = current_motor_D_angle

    else:
        print("No recognized cartridge inserted.")


# Main loop to check motor, switch, and sensor state
def main():
    
    reset_power_lever()
    ev3.beep()  # Start signal
    
    fetch_current_settings()

    while True:
        motor_on = power_lever_position()
        
        # If the motor is ON, check the current cartridge and switch presses
        if motor_on:
            check_current_cartridge()
            handle_panel_interactions()

        # Small delay to avoid overloading the CPU
        sleep(0.2)

# Entry point of the program
if __name__ == "__main__":
    main()
