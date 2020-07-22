from PIL import Image, ImageFont, ImageDraw, ImageSequence

from pyftdi.spi import SpiController, SpiIOError

from luma.core.interface.serial import ftdi_spi
from luma.core.render import canvas
from luma.oled.device import ssd1322
from time import sleep

import re
import os
import sys
import time
import threading
from collections import deque

from mpd import MPDClient
import numpy as np

class Cava(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.bars = 64
        self.daemon = True
        self.command = '/usr/local/bin/cava'
        self.lock = threading.Lock()
        self.fifo = deque([ [[0]*self.bars] ], maxlen = 1)

    def get_output(self):
        with self.lock:
            try: return self.fifo.popleft()[0]
            except: pass

    def run(self):
        try:
            process = os.popen(self.command)
            while True:
                #time.sleep(0.01)
                output = process.readline().rstrip()

                if output:
                    if re.match('0;{self.bars}',output): continue
                    matched = re.findall('(\d+)',output)
                    if matched and len(matched) == self.bars:
                        for i in range(len(matched)): matched[i] = int(matched[i])
                        with self.lock: self.fifo.append([matched])

        except OSError as error:
            print("Error:", error)
            sys.exit(1)


def val_map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def sec_to_min(value):
    minute = 0
    while (value >= 60):
        value -= 60
        minute += 1
    return '{:02}'.format(minute) + ':' + '{:02}'.format(value)


visualizer = Cava()
visualizer.start()

serial = ftdi_spi('ftdi://ftdi:232h/1', gpio_CS=4, gpio_DC=6, gpio_RST=7)
serial2 = ftdi_spi('ftdi://ftdi:232h/1', gpio_CS=3, gpio_DC=6, gpio_RST=7)
device = ssd1322(serial)
device2 = ssd1322(serial2)

mpd = MPDClient()
mpd.connect('localhost', 6600)

fontMid = ImageFont.truetype('./fonts/DBSTRAIG.TTF', 12)
trkFont = ImageFont.truetype('./fonts/851Gkktt_005.ttf', 12)
albumFont = ImageFont.truetype('./fonts/PixelMplus12-Regular.ttf', 12)
faFont = ImageFont.truetype('/usr/share/fonts/TTF/fa-solid-900.ttf', 12)

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
    visualizer_outputs = visualizer.get_output()

    if visualizer_outputs:
        img = Image.new('RGBA', (256, 64), (0 ,0 ,0))
        #img.paste(gifImages[gifCounter].resize((256,64)), (0, 0))
        img.paste(gifImages[gifCounter].resize((256,144)), (0, -20))


        dim = Image.new('RGBA', img.size)
        dimDraw = ImageDraw.Draw(dim)
        dimDraw.rectangle([(0, 0), (255, 64)], fill=(0, 0, 0, 180))

        dimDraw.polygon([(65, 0), (75, 15), (75, 0)], fill=(0, 0, 0, 192))
        dimDraw.rectangle([(75,0), (255, 15)], fill=(0, 0, 0, 200))
        img = Image.alpha_composite(img, dim)


        draw = ImageDraw.Draw(img)


        #img = Image.new('RGB', (256, 64), (0, 0, 0))

        offset = 0
        falling = False

        for i in range(64):
            top = val_map(visualizer_outputs[i], 0, 1000, 63, 15)

            for j in range (63, int(top), -1):
                draw.line(((offset+i*4, j), (offset+i*4+4, j)), (int(spec_gradient[j]), int(spec_gradient[j]), int(spec_gradient[j])))
                #draw.line(((offset+i*12, j), (offset+i*12+12, j)), (int(spec_gradient[j]), int(spec_gradient[j]), int(spec_gradient[j])))
                #draw.rectangle(((offset+i*12, top), (offset+i*12+12, 63)), (128,128,128))


            if prevFallingTimer == 0:
                prevFallingTimer = time.time()

            if ((time.time() - prevFallingTimer) > 0.05):
                spectrumPeaks[i] += 1
                falling = True

            if spectrumPeaks[i] > top:
                spectrumPeaks[i] = top


            #draw.rectangle(((offset+i*12, spectrumPeaks[i]), (offset+i*12+12, spectrumPeaks[i]+1)), (255, 255, 255))
            #draw.line(((offset+i*12, spectrumPeaks[i]), (offset+i*12+12, spectrumPeaks[i])), (255, 255, 255))

        if falling:
            prevFallingTimer = time.time()

        #for i in range(0, 63, 2):
        #    draw.line(((0, i), (255, i)), (0, 0, 0))


        #for i in range(2, 255, 12):
        #    draw.line(((i, 0), (i, 63)), (0, 0, 0))


        draw.rectangle([(80, 0), (180,10)], fill=fill)
        draw.polygon([(80, 0), (65, 0), (80, 10)], fill=fill)
        draw.polygon([(195, 0), (180, 0), (180, 10)], fill=fill)
        draw.text((85, 1), 'SPECTRUM', fill=fillInverse, font=fontMid)

        device.display(img.convert('RGB'))

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

    device2.display(img)

    if prevGifTimer == 0:
        prevGifTimer = time.time()

    if ((time.time() - prevGifTimer) > 0.08):
        gifCounter += 1
        prevGifTimer = time.time()

    if gifCounter >= gifMax:
        gifCounter = 0
