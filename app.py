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
import config as cfg
import LCD
import audio

status = {
    "enable_reading": True,
    "last_read": False,
    "current_state": "read",
    "current_tag": False,
    "current_playlist": [],
    "current_track": 0,
    "current_volume": 0.6,
    "current_text": ""
}

def initialize():
    if lockFile():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(cfg.pins["buttons"]["power"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(cfg.pins["buttons"]["next"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(cfg.pins["buttons"]["volume_up"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(cfg.pins["buttons"]["volume_down"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(cfg.pins["led"], GPIO.OUT)
        GPIO.output(cfg.pins["led"], GPIO.HIGH)
        GPIO.add_event_detect(cfg.pins["buttons"]["power"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        GPIO.add_event_detect(cfg.pins["buttons"]["next"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        GPIO.add_event_detect(cfg.pins["buttons"]["volume_up"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        GPIO.add_event_detect(cfg.pins["buttons"]["volume_down"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
        LCD.initialize()
        displayText("Hello!")
        audio.initialize(status["current_volume"])
        audio.playSoundEffect(status["current_volume"], "power-on.wav")
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
    audio.playSoundEffect(status["current_volume"], "power-off.wav")
    displayText("Good bye!", 1)
    GPIO.output(cfg.pins["led"], GPIO.LOW)
    LCD.exit()
    GPIO.cleanup()
    subprocess.call(['shutdown', '-h', 'now'], shell=False)
    
def toggleButton(pin):
    if GPIO.input(pin) == 0:
        if pin == cfg.pins["buttons"]["power"]:
            exit()
        elif pin == cfg.pins["buttons"]["next"]:
            toggleTrack()
        elif pin == cfg.pins["buttons"]["volume_down"]:
            toggleVolume("decrease")
        elif pin == cfg.pins["buttons"]["volume_up"]:
            toggleVolume("increase")
            
def toggleVolume(action):
    status["current_volume"] = audio.toggleVolume(status["current_volume"], action)
    currentText = status["current_text"]
    displayVolume = str(status["current_volume"] * 10)[0:-2]
    displayText("Volume: " + displayVolume + "/10", 1)
    displayText(currentText)

def toggleTrack():
    
    if status["current_state"] == "playing":
        status["current_track"] += 1
        if status["current_track"] == len(status["current_playlist"]):
            status["current_track"] = 0
        audio.playMusic(status["current_playlist"], status["current_track"])
        displayTrackInfo()
    elif status["current_state"] == "write":
        enterReadState()
        
def displayText(message, duration = 0):
    status["current_text"] = LCD.displayText(status["current_text"], message, duration)
        
def displayTrackInfo():
    displayText("Now playing:^Track " + str(status["current_track"] + 1) + "/" + str(len(status["current_playlist"])), 1)
    os.path.splitext("path_to_file")[0]
    fullTrack = status["current_playlist"][status["current_track"]]
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
    status["current_state"] = "read"
    displayText("Tiny Stereo -^Insert music!")
    
def enterWriteState(data):
    audio.playSoundEffect(status["current_volume"], "beep.wav")
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
                    audio.playSoundEffect(status["current_volume"], "write.wav")
                    displayText("Write state:^Success!")
    enterReadState()
    status["current_tag"] = False
        
def noTag():
    if status["last_read"] and status["current_state"] != "write":
        if time.time() - status["last_read"] > 2.5:
            audio.stopMusic("fade")
            enterReadState()
            status["current_tag"] = False
            status["last_read"] = False
            
def getPlaylist(data):
    playlist = audio.getPlaylist(data)
    if len(playlist):
        random.shuffle(playlist)
        status["current_playlist"] = playlist
        if audio.playMusic(playlist, 0):
            audio.playSoundEffect(status["current_volume"], "select.wav")
            status["current_state"] = "playing"
            status["current_track"] = 0
            displayTrackInfo()
        else:
            audio.playSoundEffect(status["current_volume"], "error.wav")
            displayText("Empty playlist!")
    else:
        #audio.playSoundEffect(status["current_volume"], "error.wav")
        status["current_playlist"] = []
        audio.playSoundEffect(status["current_volume"], "error.wav")
        displayText("Unknown tag!")
        
def getTag():
    try:
        data = RFID.readTag()
        if data == False:
            noTag()
        else:
            status["last_read"] = time.time()
            if data == status["current_tag"]:
                if status["current_state"] == "playing":
                    if audio.finishedTrack():
                        toggleTrack()
            else:
                data = str(data)
                status["current_tag"] = data
                status["current_track"] = 0
                status["current_playlist"] = []
                audio.stopMusic()
                if data == "write":
                    status["current_state"] = "write"
                    audio.c("write.wav")
                    displayText("Write state:^Insert tag!")
                else:
                    if status["current_state"] == "write":
                        enterWriteState(data)
                    else:
                        if data == "":
                            audio.playSoundEffect(status["current_volume"], "error.wav")
                            displayText("Empty tag!")
                        else:
                            getPlaylist(data)
        time.sleep(0.5)
    except:
        pass
    
initialize()

while status["enable_reading"]:
    try:
        getTag()
    except KeyboardInterrupt:
        try:
            GPIO.cleanup()
            sys.exit(0)
        except SystemExit:
            GPIO.cleanup()
            os._exit(0)