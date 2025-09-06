from machine import Pin
import time
import network

# --- WiFi Configuration ---
ssid = "VM1402096"
password = "password"

# --- Pin Configuration ---
led = Pin("LED", Pin.OUT)
# NOTE: Change '0' to the GPIO pin number your button is connected to.
# Using an internal pull-down resistor, so a press reads as 1.
button = Pin(0, Pin.IN, Pin.PULL_DOWN)

# --- Connect to WiFi ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connection with a timeout
max_wait = 10
print("Connecting to WiFi...")
while max_wait > 0:
    # Check status: 0=link-down, 1=link-join, 2=link-no-ip, 3=link-up
    # <0 are errors. We wait until the status is >= 3 or an error occurs.
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)

# Handle the connection result
if wlan.isconnected():
    print("Connected!")
    print("IP Address:", wlan.ifconfig()[0])
else:
    print("Connection failed.")

# --- Main Loop ---
print("Starting main loop. Press the button to toggle the LED.")
last_button_state = 0 # Assume the button is not pressed initially
while True:
    try:
        current_button_state = button.value()
        # Check if the button was pressed (state change from 0 to 1) to avoid multiple triggers
        if current_button_state == 1 and last_button_state == 0:
            print("Button pressed, toggling the LED.")
            led.toggle()
            time.sleep(0.2) # Debounce delay to avoid multiple triggers

        last_button_state = current_button_state

    except KeyboardInterrupt:
        break

led.off()
print("Finished.")