# The location of the script
path = "/home/pi/Tiny-Stereo/"

# GPIO setup (BCM) on the Raspberry Pi. Set "warnings" to True if you wish to render GPIO warnings.
pins = {
    "warnings": False,
    "led":  14,
    "buttons": {
        "power": 3,
        "next": 17,
        "volume_up": 22,
        "volume_down": 27
    },
    "lcd": {
        "rs": 26,
        "e": 16,
        "d4": 13,
        "d5": 6,
        "d6": 5,
        "d7": 12
    }
}