import network
import time

ssid = "VM1402096"
password = "password"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Espera a conexão ser estabelecida
max_wait = 10
while max_wait > 0:
    if wlan.isconnected():
        print("Conectado!")
        print("Endereço IP:", wlan.ifconfig()[0])
        break
    max_wait -= 1
    time.sleep(1)

if not wlan.isconnected():
    print("Falha na conexão Wi-Fi.")

from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

print("LED starts flashing...")
while True:
    try:
        pin.toggle()
        sleep(1) # sleep 1sec
    except KeyboardInterrupt:
        break
pin.off()
print("Finished.")