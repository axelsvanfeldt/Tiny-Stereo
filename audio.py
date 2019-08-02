#!/usr/bin/env python3

import os
import pygame
import config as cfg

def initialize(vol):
    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(vol)
    except:
        print("ERROR: While initializing the audio.")
        

def getPlaylist(data):
    try:
        acceptedTracks = []
        if data == "shuffle":
            folders = os.listdir(cfg.path + "audio/music")
            for folder in folders:
                files = os.listdir(cfg.path + "audio/music/" + folder)
                acceptedTracks = validateFiles(folder, files, acceptedTracks)
        else:
            if os.path.isdir(cfg.path + "audio/music/" + data):
                files = os.listdir(cfg.path + "audio/music/" + data)
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

def playSoundEffect(vol, file):
    try:
        if os.path.exists(cfg.path + "audio/effects/" + file):
            if file.endswith('.wav') or file.endswith('.ogg'):
                soundEffect = pygame.mixer.Sound(cfg.path + "audio/effects/" + file)
                soundEffect.set_volume(vol)
                soundEffect.play()
            else:
                print("ERROR: While playing sound effect. Invalid file format!")
        else:
            print("ERROR: While playing sound effect. File not found!")
    except:
        print("ERROR: While playing sound effect.")
        
def playMusic(playlist, trackIndex):
    try:
        track = playlist[trackIndex]
        fileCount = len(playlist)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.load(cfg.path + "audio/music/" + track)
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
    
def toggleVolume(currentVolume, action):
    try:
        volume = currentVolume
        if action == "decrease" and volume >= 0.2:
            volume -= 0.1
        elif action == "increase" and volume <= 0.9:
            volume += 0.1
        pygame.mixer.music.set_volume(volume)
        playSoundEffect(volume, "beep.wav")
        return volume
    except:
        print("ERROR: While changing volume.")
        return currentVolume
    