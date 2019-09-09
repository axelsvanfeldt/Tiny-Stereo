#!/usr/bin/env python3

import sys
import os
import time
import subprocess
import RPi.GPIO as GPIO
import config as cfg
import rfid
import lcd
import audio

status = {
    "current_state": "read",
    "current_tag": False,
    "current_text": "",
    "last_read": False
}

def initialize():
    #kill tinystereo.py
    GPIO.setwarnings(cfg.pins["warnings"])
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(cfg.pins["buttons"]["power"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(cfg.pins["led"], GPIO.OUT)
    GPIO.output(cfg.pins["led"], GPIO.HIGH)
    GPIO.add_event_detect(cfg.pins["buttons"]["power"], GPIO.BOTH, callback=toggleButton, bouncetime=200)
    lcd.initialize()
    audio.initialize(0.5)
    audio.playSoundEffect(0.5, "power-on.wav")
    displayText("Write state:^Insert tag!")
    time.sleep(1)

def exit():
    audio.playSoundEffect(0.5, "power-off.wav")
    displayText("Good bye!", 1)
    GPIO.output(cfg.pins["led"], GPIO.LOW)
    lcd.exit()
    GPIO.cleanup()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    
def toggleButton(pin):
    if GPIO.input(pin) == 0:
        exit()
        
def displayText(message, duration = 0):
    status["current_text"] = lcd.displayText(status["current_text"], message, duration)
    
def enterWriteState(data):
    audio.playSoundEffect(0.5, "select.wav")
    allowWrite = False
    if data is None or data == "":
        allowWrite = True
    else:
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
                if rfid.writeTag(nameTagInput):
                    dataWritten = True
                    audio.playSoundEffect(0.5, "write.wav")
                    displayText("Write state:^Success!")
                    status["current_tag"] = data
        
def noTag():
    if status["last_read"]:
        if time.time() - status["last_read"] > 2.5:
            displayText("Write state:^Insert tag!")
            status["current_tag"] = False
            status["last_read"] = False
        
def getTag():
    try:
        data = rfid.readTag()
        if data == False:
            noTag()
        else:
            status["last_read"] = time.time()
            if data != status["current_tag"]:
                data = str(data)
                status["current_tag"] = data
                enterWriteState(data)
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