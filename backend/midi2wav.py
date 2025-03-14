# -*- coding:utf-8 -*-
import os
import jieba
import torch
import random
PATH=r"D:\study\Graduation-Design\backend\fluidsynth\bin"
def mid2wav():
    src='static/music/'+str(random.randint(0,100000))+'.mp3'
    command='fluidsynth -ni ".fluidsynth/dgx62mbsf.sf2" "static/music/out.midi" -F '+src+ ' -r 44100'
    os.environ['Path']=(os.environ['Path']+';'+PATH)
    os.system(command)
    return src
