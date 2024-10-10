#!/usr/bin/env pybricks-micropython
import urequests
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction,  Button, Color
from pybricks.tools import wait
from pybricks.media.ev3dev import SoundFile

# Initialize the EV3 brick
ev3 = EV3Brick()

#City Id
city_id = 1

# Set speaker options for voice
ev3.speaker.set_speech_options(language="en-us", voice="f2", speed=30, pitch=50)
ev3.speaker.set_volume(volume=2, which='_all_')

# Initialize motors
power_lever = Motor(Port.A, Direction.CLOCKWISE)
motor_B = Motor(Port.B, Direction.CLOCKWISE)
motor_C = Motor(Port.C, Direction.CLOCKWISE)
# motor_D = Motor(Port.D, Direction.CLOCKWISE)

# Initialize sensors
cartridge = ColorSensor(Port.S1)
switch_2 = TouchSensor(Port.S2)
switch_3 = TouchSensor(Port.S3)
switch_4 = TouchSensor(Port.S4)

power_lever_value = "OFF"
motor_B_value = "0"
motor_C_value = "0"
motor_D_value = "0"
cartridge_value = None
switch_2_value = "OFF"
switch_3_value = "OFF"
switch_4_value = "OFF"

# Move motor to a default position by running until it stalls
power_lever.run_until_stalled(speed=-100, then=Stop.HOLD, duty_limit=20)
initial_power_lever_angle = power_lever.angle()

# Print initial angle for debugging
print("Initial Angle:", initial_power_lever_angle)

# Move motor to a target position and reset the angle
power_lever.run_target(speed=500, target_angle=initial_power_lever_angle + 64, then=Stop.BRAKE, wait=True)
power_lever.reset_angle(0)

# Function to turn power lever between 0 (OFF) and 60 (ON) degrees
def turn_power_lever(value):
    if value == "ON":
        # Turn lever
        power_lever.run_target(speed=500, target_angle=60, then=Stop.BRAKE, wait=True)
        # Play "ON" sound
        ev3.speaker.play_notes(['C4/8', 'E4/8', 'G4/4'], 300)
    elif value == "OFF":
        # Turn lever
        power_lever.run_target(speed=-500, target_angle=0, then=Stop.BRAKE, wait=True)
        # Play "OFF" sound
        ev3.speaker.play_notes(['G4/8', 'E4/8', 'C4/4'], 120)

# Function to check and toggle power lever position
def power_lever_position():
    angle = power_lever.angle()
    print("Current Power Lever Angle: ", angle)

    # If the motor is moved away from 0, move it to 60 degrees (ON)
    if (angle >= -8 and angle <= -3) or (angle >= 3 and angle <= 15):
        turn_power_lever("ON")
        return True

    # If the motor is moved away from 60, move it back to 0 degrees (OFF)
    elif (angle >= 50 and angle <= 57) or (angle >= 63 and angle <= 68):
        turn_power_lever("OFF")
        return False

    # Motor is either at 0 or 60 degrees
    return 59 <= angle <= 62

def convert_color_mapping(color):
    color_mapping = {
            "BLACK": Color.BLACK,
            "BLUE": Color.BLUE,
            "GREEN": Color.GREEN,
            "YELLOW": Color.YELLOW,
            "RED": Color.RED,
            "WHITE": Color.WHITE,
            "BROWN": Color.BROWN,
        }
    return color_mapping.get(color)

# Function to fetch initial settings from the API
def fetch_current_settings():
    #DO NOT USE HTTPS
    url = "http://670422dcab8a8f89273310ce.mockapi.io/api/panel" # Replace with actual API URL
    
    try:
        response = urequests.get(url)

        # Check if the response is a redirect (status code 3xx)
        if 300 <= response.status_code < 400:
            # Extract the new location from the headers
            new_url = response.headers.get('Location')
            print("Redirected to: ", new_url)
            response = urequests.get(new_url)

        # Parse and process the response
        print("Complete API Response: ", response.json())
        panel_data = response.json()[0]['panel']
        print("Fetched Initial Panel Settings: ", panel_data)

        # Update EV3 panel settings based on the API response
        global power_lever_value, motor_B_value, motor_C_value, motor_D_value, cartridge_value, switch_2_value, switch_3_value, switch_4_value
        for setting in panel_data:
            port_id = setting['port_id']
            value = setting['value']
            cartridge = setting.get('cartridge')
            # Process the values accordingly, for example:
            if port_id == 'A':
                if power_lever_value != value :
                    turn_power_lever(value)
                    power_lever_value = value 
                    print("Power Lever initial value: " + value)
                    
            if cartridge_value == convert_color_mapping(cartridge):
                if port_id == 'B':
                    motor_B_value = value
                    print("Motor B value for " + cartridge + ": "+ value)
                elif port_id == 'C':
                    motor_C_value = value
                    print("Motor C value for " + cartridge + ": "+ value)
                elif port_id == 'D':
                    motor_D_value = value
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
        response.close()

    except Exception as e:
        print("Error during API call:", e)


# Function to update settings via API when an action occurs on the panel
def update_setting(port_id, value):
    url = "http://console.brickmmo.com:7777/api/panel/update/city_id/" + city_id + "/port_id/"+ port_id + "/value/" + value
    try:
        response = urequests.post(url)
        print("Updated port " , port_id , " with value " , value , ". Response: ", response.text)
        response.close()

    except Exception as e:
        print("Error while updating setting for port " , port_id , " : " , e)

# function to check cartridge
def check_current_cartridge():
    global cartridge_value
    current_cartridge = cartridge.color()
    print("Current Cartridge: ", current_cartridge)
    # Fetch settings only if the cartridge value has changed
    if current_cartridge != cartridge_value and current_cartridge != None:
        print("Cartridge has changed from ", cartridge_value, " to ", current_cartridge)
        cartridge_value = current_cartridge
        # Delay for cartridge change
        wait(2000)
        fetch_current_settings()
    else:
        print("Cartridge remains the same:", current_cartridge)
    
# New function to handle switch press and cartridge check
def handle_panel_interactions(current_cartridge):
    # Check if cartridge is BLUE and handle switch presses
    if current_cartridge == Color.BLUE:
        if switch_2.pressed():
            print("Switch 2 is pressed with BLUE cartridge!")
            ev3.speaker.beep()
            update_setting('BLUE','S2', 'ON')

        if switch_3.pressed():
            print("Switch 3 is pressed with BLUE cartridge!")
            ev3.speaker.beep()
            update_setting('BLUE','S3', 'ON')

        if switch_4.pressed():
            print("Switch 4 is pressed with BLUE cartridge!")
            ev3.speaker.beep()
            update_setting('BLUE','S4', 'ON')

    # Check if cartridge is RED and handle switch presses
    elif current_cartridge == Color.RED:
        if switch_2.pressed():
            print("Switch 2 is pressed with RED cartridge!")
            ev3.speaker.beep()
            update_setting('RED','S2', 'OFF')

        if switch_3.pressed():
            print("Switch 3 is pressed with RED cartridge!")
            ev3.speaker.beep()
            update_setting('RED','S3', 'OFF')

        if switch_4.pressed():
            print("Switch 4 is pressed with RED cartridge!")
            ev3.speaker.beep()
            update_setting('RED','S4', 'OFF')

    # Add more conditions for other cartridges if needed
    else:
        print("No recognized cartridge inserted.")


# Main loop to check motor switch and sensor state
def main():
    ev3.speaker.beep()  # Start signal
    fetch_current_settings()

    while True:
        # Check power lever position and toggle between ON and OFF
        motor_on = power_lever_position()
        
        # If the motor is ON, check the current cartridge and switch presses
        if motor_on:
            check_current_cartridge()
            handle_panel_interactions(cartridge_value)

        # Small delay to avoid overloading the CPU
        wait(1500)

# Entry point of the program
if __name__ == "__main__":
    main()
