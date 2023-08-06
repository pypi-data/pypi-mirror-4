#!/usr/bin/env python
# encoding=utf-8
import sys
import signal
import readline
from dictionary import Dictionary 

def sigHandler(signum, frame):
    sys.stdout.write('\nbye~')
    sys.exit()
    

signal.signal(signal.SIGINT, sigHandler)
signal.signal(signal.SIGHUP, sigHandler)
signal.signal(signal.SIGTERM, sigHandler)

myDict = Dictionary()

while True:
    word = raw_input(">> ").strip()
    res = myDict.lookUp(word)
    if res == []: 
        sys.stdout.write('Not found...')
    else: 
        try:
            for i in myDict.lookUp(word): print i
        except Exception:
            del(myDict)
    sys.stdout.write('------------------------------------------')
