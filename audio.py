#!/usr/bin/env python3

import os
import pygame

def initialize(config):
    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(config["current_volume"])
    except:
        print("ERROR: While initializing the audio.")
        

def getPlaylist(config, data):
    try:
        acceptedTracks = []
        if data == "shuffle":
            folders = os.listdir(config["path"] + "audio/music")
            for folder in folders:
                files = os.listdir(config["path"] + "audio/music/" + folder)
                acceptedTracks = validateFiles(folder, files, acceptedTracks)
        else:
            if os.path.isdir(config["path"] + "audio/music/" + data):
                files = os.listdir(config["path"] + "audio/music/" + data)
                acceptedTracks = validateFiles(data, files, acceptedTracks)
        return acceptedTracks
    except:
        return []

def validateFiles(folder, files, acceptedTracks):
    try:
        for file in files:
            if file.endswith('.mp3') or file.endswith('.ogg'):
                acceptedTracks.append(folder + "/" + file)
        return acceptedTracks
    except:
        return acceptedTracks

def playSoundEffect(config, file):
    try:
        if os.path.exists(config["path"] + "audio/effects/" + file):
            if file.endswith('.wav') or file.endswith('.ogg'):
                soundEffect = pygame.mixer.Sound(config["path"] + "audio/effects/" + file)
                soundEffect.set_volume(config["current_volume"])
                soundEffect.play()
            else:
                print("ERROR: While playing sound effect. Invalid file format!")
        else:
            print("ERROR: While playing sound effect. File not found!")
    except:
        print("ERROR: While playing sound effect.")
        
def playMusic(config, playlist, trackIndex):
    try:
        track = playlist[trackIndex]
        fileCount = len(playlist)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load(config["path"] + "audio/music/" + track)
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
        return True
    except:
        print("ERROR: While playing music.")
        return False
    
def stopMusic(fade = False):
    try:
        if pygame.mixer.music.get_busy():
            if fade:
                pygame.mixer.music.fadeout(1500)
            else:
                pygame.mixer.music.stop()
    except:
        print("ERROR: While stopping music.")
        
def finishedTrack():
    try:
        if pygame.mixer.music.get_busy():
            return False
        else:
            return True
    except:
        print("ERROR: While checking if track is playing.")
        return False
    
def toggleVolume(config, action):
    try:
        volume = config["current_volume"]
        if action == "decrease" and volume >= 0.2:
            volume -= 0.1
        elif action == "increase" and volume <= 0.9:
            volume += 0.1
        pygame.mixer.music.set_volume(volume)
        playSoundEffect(config, "beep.wav")
        return volume
    except:
        print("ERROR: While changing volume.")
        return config["current_volume"]
    