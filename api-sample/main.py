#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent
from ev3dev2.sound import Sound

from time import time, sleep
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

# Initialize the EV3 sound object
ev3 = Sound()

# City Id
city_id = "1"

# Initialize motors
motor_A = LargeMotor(OUTPUT_A)

# Function to fetch initial settings from the API
def fetch_setting():

    global city_id

    print("fetch_setting")

    request_url = "https://console.brickmmo.com/api/panel/details/port_id/s2/cartridge/BLUE/city_id/" + city_id

    try:
        request = Request(request_url, data=urlencode({"timestamp": time()}).encode("utf-8"))
        with urlopen(request, timeout=5) as response:

            # Read and decode the response once
            response_data = response.read().decode("utf-8") 
            print("Raw Response Data:", response_data)
            data = json.loads(response_data)

            print(data['value'])

            if(data['value'] == 'ON'):
                motor_A.on(50, 50)

            else:
                motor_A.stop()

            
            sleep(1)
                
    except Exception as e:
        print("Error during API call:", e)



# Main loop to check motor, switch, and sensor state
def main():
    
    while True:
        
        ev3.beep()

        fetch_setting()

        sleep(1)

# Entry point of the program
if __name__ == "__main__":
    main()
