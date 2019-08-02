# Tiny Stereo
Tiny Stereo is a Python project made to turn the Raspberry Pi into a miniature media player using NFC tags.

...

## Software Requirements
- [SPI-Py](https://github.com/lthiery/SPI-Py)
- Some music (MP3 or Ogg)

## Hardware requirements
- 1x LCD Character Display (16x2)
- 1x RFID Reader (MFRC522)
- 4x Push Switches
- 1x LED
- 2x Potentiometers\*
- 1x Mono Amp\*\*
- 1x Speaker\*\*

* The potentiometers are optional depending on your LCD. I'm using them to control brightness and contrast of the display.

\*\* I'm using a [mono amp](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp) attached to a 4 ohm speaker to output sound, but feel free to use any sound device that works with the Pi.

## GPIO Pins
Use config.py for reference on which GPIO pins to use on the Raspberry Pi.

## Installation
1. Clone or download this repository to the path of your choice.
2. Use `> sudo raspi-config` to make sure that the SPI interface on your Raspberry Pi is enabled.
3. Install the SPI-Py package from (https://github.com/lthiery/SPI-Py).
4. Populate /path/to/Tiny-Stereo/audio/music with the music of your choice. Each folder you create will serve as a playlist/album.
5. Edit /path/to/Tiny-Stereo/config.py to match your own settings.

## Usage
...