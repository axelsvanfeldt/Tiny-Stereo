#!/usr/bin/env python3

import time
import unidecode
import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
import config as cfg

lcd = False

def initialize():
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        global lcd
        lcd = CharLCD(cols=16, rows=2, pin_rs=cfg.pins["LCD"]["BCM"]["rs"], pin_e=cfg.pins["LCD"]["BCM"]["e"], pins_data=[cfg.pins["LCD"]["BCM"]["d4"], cfg.pins["LCD"]["BCM"]["d5"], cfg.pins["LCD"]["BCM"]["d6"], cfg.pins["LCD"]["BCM"]["d7"]], numbering_mode=GPIO.BCM)
        lcd.clear()
        time.sleep(0.01)
        print("LCD successfully initialized.")
    except:
        print("ERROR: While initializing the LCD.")

def displayText(currentText, message, duration):
    try:
        if lcd:
            if message != currentText:
                messageRows = message.split("^")
                rowCount = len(messageRows)
                fixedMessage = ""
                for i in range(0, rowCount):
                    if len(messageRows[i]) > 16:
                        if messageRows[i][13] == " ":
                            messageRows[i] = messageRows[i][0:13] + "..."
                        else:
                            messageRows[i] = messageRows[i][0:14] + ".."
                    if i == 0 and rowCount == 2:
                        messageRows[i] = messageRows[i] + "\r\n"
                    fixedMessage = fixedMessage + messageRows[i]
                fixedMessage = fixedMessage.replace("_", " ")
                fixedMessage = unicode(fixedMessage, "utf-8")
                fixedMessage = unidecode.unidecode(fixedMessage)
                lcd.clear()
                time.sleep(0.01)
                lcd.write_string(fixedMessage)
                if duration:
                    time.sleep(duration)
                else:
                    time.sleep(0.01)
                print("LCD successfully displayed: " + message)
            return message
        else:
            print("ERROR: While displaying text to the LCD. LCD not initialized!")
            return currentText
    except:
        print("ERROR: While displaying text to the LCD.")
        return currentText

def clearText():
    try:
        if lcd:
            lcd.clear()
            time.sleep(0.01)
        else:
            print("ERROR: While clearing text from the LCD. LCD not initialized!")
    except:
        print("ERROR: While clearing text from the LCD.")
        
def exit():
    clearText()
    GPIO.cleanup()