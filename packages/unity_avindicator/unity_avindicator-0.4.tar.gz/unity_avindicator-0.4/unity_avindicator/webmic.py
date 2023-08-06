#!/usr/bin/env python
'''
A/V control for System76 laptop using Unity
'''

import os

from execute import returncode

# check for the existence of /dev/video0 which is used currently for webcam
webcam = lambda: os.path.exists('/dev/video0') == False
def webcam_toggle():
    if webcam():
        returncode('sudo /sbin/modprobe uvcvideo')
    else:
        returncode('sudo /sbin/modprobe -rv uvcvideo')

# use the amixer application to glean the status of the microphone
microphone = lambda: returncode("amixer get Capture | grep Capt | grep off") == 0
microphone_toggle = lambda: returncode("amixer set Capture toggle")

def main():
    print "Mic muted ? {0}, Webcam off ? {1}".format(microphone(), webcam())

if __name__ == '__main__':
    main()
