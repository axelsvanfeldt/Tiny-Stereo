#!/usr/bin/env python3

import sys
import os
import re
import time
import random
import fcntl
import subprocess
import RPi.GPIO as GPIO
import config as cfg
import rfid
import lcd
import audio

status = {
    "current_state": "read",
    "current_tag": False,
    "current_playlist": [],
    "current_track": 0,
    "current_volume": 0.5,
    "current_text": "",
    "last_read": False
}

def initialize():
    if lockFile():
        GPIO.setwarnings(cfg.pins["warnings"])
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
        lcd.initialize()
        displayText("Tiny Stereo -^Insert tag!")
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
    audio.stopMusic(True)
    audio.playSoundEffect(status["current_volume"], "power-off.wav")
    displayText("Good bye!", 1)
    time.sleep(1.5)
    GPIO.output(cfg.pins["led"], GPIO.LOW)
    lcd.exit()
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
        
def displayText(message, duration = 0):
    status["current_text"] = lcd.displayText(status["current_text"], message, duration)
        
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
    displayText("Tiny Stereo -^Insert tag!")
        
def noTag():
    if status["last_read"]:
        if time.time() - status["last_read"] > 2.5:
            audio.stopMusic("fade")
            status["current_tag"] = False
            status["last_read"] = False
            enterReadState()
            
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
        status["current_playlist"] = []
        audio.playSoundEffect(status["current_volume"], "error.wav")
        displayText("Unknown tag!")
        
def getTag():
    try:
        data = rfid.readTag()
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
                if data == "":
                    audio.playSoundEffect(status["current_volume"], "error.wav")
                    displayText("Empty tag!")
                else:
                    getPlaylist(data)
        time.sleep(0.5)
    except:
        pass
    
initialize()

while True:
    try:
        getTag()
    except KeyboardInterrupt:
        try:
            GPIO.cleanup()
            sys.exit(0)
        except SystemExit:
            GPIO.cleanup()
            os._exit(0)
