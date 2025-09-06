# Pico Display & Capacitive Button Project

This is a MicroPython project for the Raspberry Pi Pico that demonstrates how to control an ST7789 SPI display and interact with a capacitive touch button.

## Features

- Drives a 160x128 ST7789 SPI display in landscape mode.
- Toggles the onboard LED with each press of a capacitive touch button.
- Displays a large, scrolling message ("LED ON" or "LED OFF") on the screen.
- Cycles through a set of background colors (blue, red, green, magenta) with each button press.
- The screen holds the new background color after the text animation finishes, waiting for the next input.

## Hardware Requirements

- Raspberry Pi Pico or Pico W
- ST7789 IPS Display (e.g., 1.14 inch, 160x128, SPI)
- Capacitive Touch Button (e.g., a TTP223 module)
- Jumper wires

## Wiring

### ST7789 Display

| Display Pin | Pico Pin | Description      |
|-------------|----------|------------------|
| VCC         | 3V3 (OUT)| Power            |
| GND         | GND      | Ground           |
| SCL/SCK     | GP18     | SPI Clock        |
| SDA/MOSI    | GP19     | SPI Data Out     |
| RES/RST     | GP20     | Reset            |
| DC          | GP21     | Data/Command     |
| CS          | GP17     | Chip Select      |
| BLK/BL      | GP22     | Backlight Control|

### Capacitive Touch Button

| Button Pin | Pico Pin | Description      |
|------------|----------|------------------|
| VCC        | 3V3 (OUT)| Power            |
| GND        | GND      | Ground           |
| SIG/OUT    | GP0      | Signal Output    |

*Note: The script uses `GP0` for the button. You can change this pin in the code if needed.*

## How to Use

1.  Flash the latest version of MicroPython onto your Raspberry Pi Pico.
2.  Copy the `test_display_color.py` file to the Pico's filesystem (e.g., using Thonny IDE).
3.  Connect the hardware as described in the wiring section.
4.  Run the script from a MicroPython REPL (like in Thonny).
5.  Touch the capacitive button to see the LED and the display react.