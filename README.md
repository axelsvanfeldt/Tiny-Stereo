# Tiny Stereo

Tiny Stereo is a Python project made to turn the Raspberry Pi into a miniature media player using NFC tags.

## Hardware requirements
- Raspberry Pi
- 16x2 LCD Character Display
- RFID Reader (MFRC522)
- 4 Push Switches
- 2 Potentiometers \*
- Mono amp \*\*
- Speaker \*\*

\*\* I'm using a [mono amp](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp) attached to a 4 ohm speaker to output sound, but feel free to use any sound device that works with the Pi.

## Software Requirements
- SPI-Py (https://github.com/lthiery/SPI-Py)