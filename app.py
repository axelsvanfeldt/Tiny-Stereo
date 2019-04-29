#!/usr/bin/env python3

import sys
import os
import re
import time
import random
import fcntl
import subprocess
import RPi.GPIO as GPIO
import RFID
import LCD
import audio

config = {
    "path": "/home/pi/TinyStereo/",
    "enable_reading": True,
    "last_read": False,
    "current_state": "read",
    "current_tag": False,
    "current_playlist": [],
    "current_track": 0,
    "current_volume": 0.6,
    "current_text": "",
    "pins": {
        "led": {
            "BCM": 14
        },
        "buttons": {
            "BCM": {
                "power": 3,
                "next": 17,
                "volume_up": 22,
                "volume_down": 27
            }
        },
        "LCD": {
            "BCM": {
                "rs": 26,
                "e": 16,
                "d4": 13,
                "d5": 6,
                "d6": 5,
                "d7": 12
            }
	    }
    }
}

def initialize():
    if lockFile():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config["pins"]["buttons"]["BCM"]["power"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config["pins"]["buttons"]["BCM"]["next"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config["pins"]["buttons"]["BCM"]["volume_up"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config["pins"]["buttons"]["BCM"]["volume_down"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config["pins"]["led"]["BCM"], GPIO.OUT)
        GPIO.output(config["pins"]["led"]["BCM"], GPIO.HIGH)
        GPIO.add_event_detect(config["pins"]["buttons"]["BCM"]["power"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        GPIO.add_event_detect(config["pins"]["buttons"]["BCM"]["next"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        GPIO.add_event_detect(config["pins"]["buttons"]["BCM"]["volume_up"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        GPIO.add_event_detect(config["pins"]["buttons"]["BCM"]["volume_down"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        LCD.initialize(config)
        displayText("Hello!")
        audio.initialize(config)
        audio.playSoundEffect(config, "power-on.wav")
        time.sleep(1)
    else:
        try:
            sys.exit(0)
        except:
            os._exit(0)

def lockFile():
    lockfile = "lock.pod"
    fd = os.open(lockfile, os.O_CREAT | os.O_TRUNC | os.O_WRONLY)
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True

def exit():
    audio.stopMusic()
    audio.playSoundEffect(config, "power-off.wav")
    displayText("Good bye!", 1)
    config["enable_reading"] = False
    GPIO.output(config["pins"]["led"]["BCM"], GPIO.LOW)
    LCD.exit()
    GPIO.cleanup()
    try:
        sys.exit(0)
    except:
        os._exit(0)   
    #subprocess.call(['shutdown', '-h', 'now'], shell=False)
    
def toggleButton(pin):
    if GPIO.input(pin) == 0:
        if pin == config["pins"]["buttons"]["BCM"]["power"]:
            exit()
        elif pin == config["pins"]["buttons"]["BCM"]["next"]:
            toggleTrack()
        elif pin == config["pins"]["buttons"]["BCM"]["volume_down"]:
            toggleVolume("decrease")
        elif pin == config["pins"]["buttons"]["BCM"]["volume_up"]:
            toggleVolume("increase")
            
def toggleVolume(action):
    config["current_volume"] = audio.toggleVolume(config, action)
    print(config["current_volume"])
    currentText = config["current_text"]
    displayVolume = str(config["current_volume"] * 10)[0:-2]
    displayText("Volume: " + displayVolume + "/10", 1)
    displayText(currentText)

def toggleTrack():
    
    if config["current_state"] == "playing":
        config["current_track"] += 1
        if config["current_track"] == len(config["current_playlist"]):
            config["current_track"] = 0
        audio.playMusic(config, config["current_playlist"], config["current_track"])
        displayTrackInfo()
    elif config["current_state"] == "write":
        enterReadState()
        
def displayText(message, duration = 0):
    config["current_text"] = LCD.displayText(config, message, duration)
        
def displayTrackInfo():
    displayText("Now playing:^Track " + str(config["current_track"] + 1) + "/" + str(len(config["current_playlist"])), 1)
    os.path.splitext("path_to_file")[0]
    fullTrack = config["current_playlist"][config["current_track"]]
    trackInfo = fullTrack.split("/")
    track = trackInfo[1].replace("_", " ")
    if trackInfo[0] != track:
        trackRegex = re.compile(re.escape(trackInfo[0]), re.IGNORECASE)
        track = trackRegex.sub("", track)
        trackRegex = re.compile(re.escape(trackInfo[0].replace(" ", "")), re.IGNORECASE)
        track = trackRegex.sub("", track)
    track = os.path.splitext(os.path.basename(track))[0].lstrip('0123456789.-_ ')
    fullTrack = trackInfo[0] + "^" + track
    displayText(fullTrack)
    
def enterReadState():
    config["current_state"] = "read"
    displayText("Tiny Stereo -^Insert music!")
    
def enterWriteState(data):
    audio.playSoundEffect(config, "beep.wav")
    allowWrite = False
    if data is None or data == "":
        allowWrite = True
    else:
        if data != "write":
            displayText("Write state:^Confirm action!")
            populatedTagInput = raw_input("The inserted tag is already populated with '" + data + "'.\nEnter Y/N to proceed: ")
            if populatedTagInput.lower() == "y":
                allowWrite = True
    if allowWrite:
        displayText("Write state:^Name the tag!")
        nameTagInput = raw_input("Populate the inserted tag with the name of your choice. Max 16 characters!\nEnter name: ")
        dataWritten = False
        endTime = time.time() + 2.5
        while time.time() < endTime:
            if dataWritten == False:
                if RFID.writeTag(nameTagInput):
                    dataWritten = True
                    audio.playSoundEffect(config, "write.wav")
                    displayText("Write state:^Success!")
    enterReadState()
    config["current_tag"] = False
        
def noTag():
    if config["last_read"] and config["current_state"] != "write":
        if time.time() - config["last_read"] > 2.5:
            audio.stopMusic("fade")
            enterReadState()
            config["current_tag"] = False
            config["last_read"] = False
            
def getPlaylist(data):
    playlist = audio.getPlaylist(config, data)
    if len(playlist):
        random.shuffle(playlist)
        config["current_playlist"] = playlist
        if audio.playMusic(config, playlist, 0):
            audio.playSoundEffect(config, "select.wav")
            config["current_state"] = "playing"
            config["current_track"] = 0
            displayTrackInfo()
        else:
            audio.playSoundEffect(config, "error.wav")
            displayText("Empty playlist!")
    else:
        #audio.playSoundEffect(config, "error.wav")
        config["current_playlist"] = []
        audio.playSoundEffect(config, "error.wav")
        displayText("Unknown tag!")
        
def getTag():
    try:
        data = RFID.readTag()
        if data == False:
            noTag()
        else:
            config["last_read"] = time.time()
            if data == config["current_tag"]:
                if config["current_state"] == "playing":
                    if audio.finishedTrack():
                        toggleTrack()
            else:
                data = str(data)
                config["current_tag"] = data
                config["current_track"] = 0
                config["current_playlist"] = []
                audio.stopMusic()
                if data == "write":
                    config["current_state"] = "write"
                    audio.c(config, "write.wav")
                    displayText("Write state:^Insert tag!")
                else:
                    if config["current_state"] == "write":
                        enterWriteState(data)
                    else:
                        if data == "":
                            audio.playSoundEffect(config, "error.wav")
                            displayText("Empty tag!")
                        else:
                            getPlaylist(data)
        time.sleep(0.5)
    except:
        pass
    
initialize()

while config["enable_reading"]:
    try:
        getTag()
    except KeyboardInterrupt:
        try:
            GPIO.cleanup()
            sys.exit(0)
        except SystemExit:
            GPIO.cleanup()
            os._exit(0)

exit()