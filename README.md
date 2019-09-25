# Tiny Stereo
Tiny Stereo is a Python project made to turn the Raspberry Pi into a miniature media player using NFC tags.

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

\* The potentiometers are optional depending on your LCD. I'm using them to control brightness and contrast of the display.

\*\* I'm using a [mono amp](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp) (so much for Tiny *Stereo*...) attached to a 4 ohm speaker to output sound, but feel free to use any sound device that works with the Pi.

## GPIO Pins
Use the following setup for the MFRC522:

| MFRC522 | Pi         |
|:-------:|:----------:|
| SDA     | GPIO8      |
| SCK     | GPIO11     |
| MOSI    | GPIO10     |
| MISO    | GPIO9      |
| IRQ     | None       |
| GND     | Ground     |
| RST     | GPIO25     |
| 3.3V    | 3V3        |

The GPIO setup of the other devices are optional, but I suggest keeping the power button connected to GPIO3 (PIN #5) if you want the power-up button to function properly.

## Installation
1. Clone or download this repository to the path of your choice.
2. Use `> sudo raspi-config` to make sure that the SPI interface on your Raspberry Pi is enabled.
3. Install the SPI-Py package from https://github.com/lthiery/SPI-Py.
4. Populate /path/to/Tiny-Stereo/audio/music with the music of your choice. Each folder you create will serve as a playlist/album.
5. Use `> python /path/to/Tiny-Stereo/write.py` and follow the instructions to pair your NFC tags with the playlists/albums you added in step 4. This step requires a monitor/remote control access as you need to see the terminal of the Pi.
6. Edit /path/to/Tiny-Stereo/config.py to match your own settings.
7. Use the method of your choice to launch the script at boot.

## Usage
`> python /path/to/Tiny-Stereo/tinystereo.py`
