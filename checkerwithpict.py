#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import cv2
import argparse
import os
import numpy as np

import argparse
import datetime
import json
import multiprocessing
import random
import sys
import threading
import time

import numpy as np
from PIL import Image

import math
import chainer
import chainer.functions as F
from chainer import cuda
from chainer import optimizers
import random
import six
import six.moves.cPickle as pickle
from six.moves import queue

import i2vvgg

import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt

import pylab

parser = argparse.ArgumentParser(
    description='Image inspection using chainer')
parser.add_argument('source_dir', help='Path to inspection image file')
parser.add_argument('--model','-m',default='model', help='Path to model file')
parser.add_argument('--mean', default='mean.npy',
                    help='Path to the mean file (computed by compute_mean.py)')
args = parser.parse_args()

mean_image = pickle.load(open(args.mean, 'rb'))

model = pickle.load(open(args.model,'rb'))

cuda.get_device(0).use()
model.to_gpu()

size = 224
xs=[]
ys=[]
xsp=[]
ysp=[]
el=0
s=0
q=0
e=0
for i in range(24):
    for j in range(2):
        xs.append((i*100+j*50)/100.0)
        ys.append(0)
        xsp.append((i*100+j*50)/100.0)
        ysp.append(0)

for source_imgpath in os.listdir(args.source_dir):
    img = cv2.imread(args.source_dir+"/"+source_imgpath)
    height, width, depth = img.shape
    new_height = size
    new_width = size

    if height > width:
        new_width = size * width / height
    else:
        new_height = size * height / width

    crop_height_start = ( size - new_height ) / 2
    crop_height_end = crop_height_start + new_height
    crop_width_start = ( size - new_width) / 2
    crop_width_end = crop_width_start + new_width

    resized_img = cv2.resize(img, (new_width, new_height))
    cropped_img = np.zeros((size,size,3),np.uint8)
#    cropped_img.fill(255) white ver
    cropped_img[crop_height_start:crop_height_end,crop_width_start:crop_width_end] = resized_img
    x = np.ndarray((1, 3, model.insize, model.insize), dtype=np.float32)
    x[0]=(cropped_img.swapaxes(0,2)).swapaxes(1,2)
    x=cuda.to_gpu(x)
    score = model.predict(x,train=False)
    score=cuda.to_cpu(score.data)

    categories = np.loadtxt("labels.txt", str, delimiter="\t")
    prediction = zip(score[0].tolist(), categories)
    prediction.sort(cmp=lambda x, y: cmp(x[0], y[0]), reverse=True)
    top_k=1
    ys_pass=0

    for rank, (score, name) in enumerate(prediction[:top_k], start=1):
        if name == "safe":
            s+=1
            ys_pass=1*score*1*score
        elif name == "questionable":
            q+=1
            ys_pass=2*score*2*score
        elif name == "explicit":
            e+=1
            ys_pass=3*score*3*score
        else:
            el+=1
    time_m=int(source_imgpath.split(".")[0])/100000
    time_change=(time_m%100)/30*50+(time_m/100)*100
    ys[xs.index(time_change/100.0)]+=ys_pass
    ysp[xs.index(time_change/100.0)]+=1

all_score=0
all_pictures=el+s+q+e
for i in range(48):
    all_score+=ys[i]
normalize=float(all_score)/float(all_pictures)
for i in range(48):
    ys[i]/=normalize
for i in range(48):
    if ysp[i]!=0:
        ys[i]-=ysp[i]
    if ys[i]<0:
        ys[i]=0
xs.append(24)
ys.append(ys[0])
xsp.append(24)
ysp.append(ysp[0])
max=0
for i in range(48):
    if ys[i]>max:
        max=ys[i]
for i in range(24):
    for j in range(2):
        if ys[i*2+j]>max*2/3:
            print ("GekiOkoTime {:0>2}:{:0>2} ~ {:0>2}:{:0>2}".format(str(i),str(j*30),str(i),str(j*30+29)),file=sys.stderr)
plt.plot(xs, ys)
plt.plot(xsp,ysp)
plt.title("OkanGekiokoSignals")
plt.xlabel("Time")
plt.ylabel("Okan and Pictures")
plt.xlim(0,24)
plt.savefig("okanwithpict.png")

print ("safe {}/{}".format(str(s),str(el+s+q+e)),file=sys.stderr)
print ("questionable {}/{}".format(str(q),str(el+s+q+e)),file=sys.stderr)
print ("exlicit {}/{}".format(str(e),str(el+s+q+e)),file=sys.stderr)
