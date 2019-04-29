#!/usr/bin/env python

import MFRC522

MIFAREReader = MFRC522.MFRC522()

def authTag():
    try:
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
                MIFAREReader.MFRC522_SelectTag(uid)
                status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
                if status == MIFAREReader.MI_OK:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except:
        return False
    
def encodeTag(action, data):
    try:
        if action == "encode":
            translation = []
            dataLength = len(data)
            for i in range(0, 16):
                if i < dataLength:
                    translation.append(ord(data[i]))
                else:
                    translation.append(0)
        elif action == "decode":
            translation = ""
            for sector in data:
                if sector != 0:
                    translation += chr(sector)
        return translation
    except:
        print("ERROR: While reading encoding/decoding data from tag.")    
    

def readTag():
    try:
        if authTag():
            data = MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            data = encodeTag("decode", data)
            return data
        else:
            return False
    except:
        return False
                
def writeTag(data):
    try:
        if authTag():
            data = encodeTag("encode", data)
            if MIFAREReader.MFRC522_Write(8, data):
                print("Tag successfully programmed.")
                MIFAREReader.MFRC522_StopCrypto1()
                return True
            else:
                MIFAREReader.MFRC522_StopCrypto1()
                return False
        else:
            return False
    except:
        print("ERROR: While programming data to tag.")
        return False