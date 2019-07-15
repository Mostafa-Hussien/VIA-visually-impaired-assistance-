from sys import byteorder
from array import array
from struct import pack
import speech_recognition as sr
import pyaudio
import wave
import datetime
import pygame
import pyttsx3
import os
from PIL import Image,ImageEnhance
import numpy as np
import cv2
from skimage import data
from skimage.filters import threshold_otsu, threshold_adaptive
from pytesseract import image_to_string

from time import sleep


THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

engine = pyttsx3.init()
engine.setProperty('rate', 150)



def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in range(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*RATE))])
    return r

def listen():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r



def ocr():
     
    text1="hi"
    while 1:
        
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print ('Say Something!')
            engine.say('Say Something!')
            engine.runAndWait()
            audio = r.listen(source)
            print ('Done!')
               
        
        text = r.recognize_google(audio)
       
        r=[text]
        a=['start']
        b=['next']
        c=['close']

        if r==a :
            print("enjoy your book")
            #tracing
            engine.say('enjoy your book')
            engine.runAndWait()
            from picamera import PiCamera
            camera = PiCamera()
            camera.brightness = 50
            camera.resolution = (2592, 1944)
            camera.framerate = 15

            camera.start_preview()
            sleep(5)
            camera.capture('image.jpg')
            camera.stop_preview()


            img = np.array(Image.open('2.jpg'))
            img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            img = cv2.bilateralFilter(img,9,75,75)
            #ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY)
            gray1=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            print("done")
            

            text1 = image_to_string(gray1)
            print(text1)

            
           
        elif r==b:
            print("next page")
            engine.say('next page')
            engine.runAndWait()
           

            camera.brightness = 50
            camera.resolution = (2592, 1944)
            camera.framerate = 15

            camera.start_preview()
            sleep(5)
            camera.capture('image.jpg')
            camera.stop_preview()
           


            img = np.array(Image.open('3.jpg'))
            img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            img = cv2.bilateralFilter(img,9,75,75)
            #ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY)
            gray1=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            print("done")
         

            text1 = text1+image_to_string(gray1)
            print(text1)
           
        elif r==c :
            print("reader closed")
            return text1
            engine.say('reader closed')
            engine.runAndWait()
            break
        else:
            print (text)
            print ('unknown command')
            engine.say('unknown command')
            engine.runAndWait()
            
