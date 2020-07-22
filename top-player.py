from PIL import Image, ImageFont, ImageDraw, ImageSequence

from pyftdi.spi import SpiController, SpiIOError

from luma.core.interface.serial import ftdi_spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from time import sleep

import urllib
import json
import re
import os
import sys
import time
import threading
from collections import deque

from mpd import MPDClient
import numpy as np

def val_map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def sec_to_min(value):
    minute = 0
    while (value >= 60):
        value -= 60
        minute += 1
    return '{:02}'.format(minute) + ':' + '{:02}'.format(value)


covid_url = 'https://app.sabae.cc/api/covid19japan.json'
covid_buffer = urllib.request.urlopen(covid_url)
corona_data = json.load(covid_buffer)

serial = ftdi_spi('ftdi://ftdi:232h/1', gpio_CS=3, gpio_DC=6, gpio_RST=7)
serial2 = ftdi_spi('ftdi://ftdi:232h/1', gpio_CS=4, gpio_DC=6, gpio_RST=7)
device = ssd1322(serial)
device2 = ssd1322(serial2)

mpd = MPDClient()
mpd.connect('localhost', 6600)

fontMid = ImageFont.truetype('./fonts/DBSTRAIG.TTF', 12)
trkFont = ImageFont.truetype('./fonts/851Gkktt_005.ttf', 12)
albumFont = ImageFont.truetype('./fonts/PixelMplus12-Regular.ttf', 12)
faFont = ImageFont.truetype('/usr/share/fonts/TTF/fa-solid-900.ttf', 12)

largeNumberFont = ImageFont.truetype('./fonts/851Gkktt_005.ttf', 18)

gif = Image.open('./gifs/giphy.gif')

#gif = Image.open('./gifs/okabe.gif')
#gif = Image.open('./gifs/kbyd.gif')
#gif = Image.open('./gifs/divergence.gif')
#gif = Image.open('./gifs/tsukihi.gif')
#gif = Image.open('./gifs/pinball.gif')

spec_gradient = np.linspace(0, 192, 64)
#spec_gradient = np.linspace(0, 224, 64)

specGifImages = []
gifImages = []

for i, f in enumerate(ImageSequence.Iterator(gif)):
    gifImages.append(f.copy())

gifCounter = 0
gifMax = len(gifImages)

fill = (255, 255, 255)
fillInverse = (0, 0, 0)

prevGifTimer = 0
prevFallingTimer = 0

spectrumPeaks = np.full(64, 63)

while True:
    song = mpd.currentsong()
    status = mpd.status()
    img = Image.new('RGBA', (256, 64), (0 ,0 ,0))

    img.paste(gifImages[gifCounter].resize((256,144)), (0, -20))
    #img.paste(gifImages[gifCounter].resize((256,144)), (0, -40))


    timeData = status['time'].split(":")
    time_label = sec_to_min(int(timeData[0])) + '/' + sec_to_min(int(timeData[1]))

    dim = Image.new('RGBA', img.size)
    dimDraw = ImageDraw.Draw(dim)
    dimDraw.rectangle([(0, 0), (255, 64)], fill=(0, 0, 0, 180))
    dimDraw.polygon([(65, 0), (75, 15), (75, 0)], fill=(0, 0, 0, 192))
    dimDraw.rectangle([(75,0), (255, 15)], fill=(0, 0, 0, 200))

    img = Image.alpha_composite(img, dim)

    try:
        cover = Image.open('/tmp/cover.jpg')
        img.paste(cover.resize((64,64)), (0, 0))
    except:
        pass


    img = img.convert('RGB')
    draw = ImageDraw.Draw(img)

    #draw.text((70, 0), song['title'], fill=fill, font=fontMid)
    #draw.text((70, 13), song['artist'], fill=fill, font=fontMid)

    #draw.line([(65, 0), (70, 15)], fill=fill)
    #draw.polygon([(65, 0), (75, 15), (75, 0)], fill=fill)
    #draw.rectangle([(75,0), (246, 15)], fill=fill)
    #draw.rectangle([(75,0), (255, 15)], fill=fill)
    #draw.polygon([(246, 15), (255, 0), (246, 0)], fill=fill)

    draw.text((69, 35), time_label, fill=fill, font=trkFont)

    draw.rectangle([(218, 50), (256,64)], fill=fill)
    draw.polygon([(208, 64), (218, 50), (218, 64)], fill=fill)
    #draw.text((180, 52), '{:>8}'.format(status['bitrate'] + 'kbps'), fill=fillInverse, font=fontMid)

    if (status['random'] == '1'):
        draw.text((222, 51), '', fill=fillInverse, font=faFont)
    else:
        draw.text((222, 51), '', fill=(128, 128, 128), font=faFont)

    if (status['repeat'] == '1'):
        draw.text((240, 51), '', fill=fillInverse, font=faFont)
    else:
        draw.text((240, 51), '', fill=(128, 128, 128), font=faFont)

    #draw.text((215, 52), 'MP3', fill=(128, 128, 128), font=fontMid)

    #if status['state'] == 'pause':
    #    draw.text((80, 1), '', fill=fill, font=faFont)
    #else:
    #    draw.text((80, 1), '', fill=fill, font=faFont)


    #draw.text((95, 2), '{:<10}'.format('Now Playing'), fill=fill, font=fontMid)
    #draw.text((77, 1), '', fill=fill, font=faFont)
    #draw.text((90, 3), 'MPD', fill=fill, font=fontMid)
    #draw.text((77, 2), '{:<12}'.format(song['album'][0:10]), fill=fill, font=albumFont)


    #draw.text((200, 3), '', fill=fill, font=faFont)
    #draw.text((215, 4), '{:>4}'.format(status['volume'] + '%'), fill=fill, font=fontMid)

    draw.text((69, 1), '', fill=fill, font=faFont)
    draw.text((84, 1), song['title'], fill=fill, font=albumFont)

    draw.text((71, 18), '', fill=fill, font=faFont)

    if 'artist' in song:
        draw.text((84, 18), song['artist'], fill=fill, font=albumFont)
    else:
        draw.text((84, 18), "Unknown", fill=fill, font=albumFont)

    #draw.text((69, 35), '', fill=fill, font=faFont)
    #draw.text((84, 35), song['album'], fill=fill, font=albumFont)


    trk = 'TRK.'+str((int(status['song'])+1))+'/'+status['playlistlength']
    draw.text((69, 50), trk, fill=fill, font=trkFont)

    device.display(img)

    if prevGifTimer == 0:
        prevGifTimer = time.time()

    if ((time.time() - prevGifTimer) > 0.08):
        gifCounter += 1
        prevGifTimer = time.time()

    if gifCounter >= gifMax:
        gifCounter = 0


    img = Image.new('RGB', (256, 64), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), 'COVID-19 Japan/Anti-Coronavirus Dashboard', fill=fill)

    draw.line(((0,10), (256, 10)), fill=fill)

    draw.text((0, 15), "Active", fill=fill, font=trkFont)
    draw.text((0, 23), "cases", fill=fill, font=trkFont)
    draw.text((55, 18), "/"+str(corona_data["ncurrentpatients"]), fill=fill, font=largeNumberFont)


    draw.text((0, 38), "Total", fill=fill, font=trkFont)
    draw.text((0, 48), "deaths", fill=fill, font=trkFont)
    draw.text((55, 40), "/"+str(corona_data["ndeaths"]), fill=fill, font=largeNumberFont)


    draw.text((135, 15), "PCR confirmed", fill=fill, font=trkFont)
    draw.text((135, 25), "/"+str(corona_data["npatients"]), fill=fill, font=trkFont)


    draw.text((125, 38), "Total discharged", fill=fill, font=trkFont)
    draw.text((125, 48), "patients", fill=fill, font=trkFont)
    draw.text((200, 50), "/"+str(corona_data['nexits']), fill=fill, font=trkFont)

    device2.display(img)
