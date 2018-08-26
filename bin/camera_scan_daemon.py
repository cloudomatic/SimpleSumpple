#!/usr/bin/python

import datetime

camera_list=["10.0.0.2", "10.0.0.3"]


def scan_loop():
  log("scan_loop()")
  for camera in camera_list:
    log("scanning camera at address: " + camera)
    


  
def log(message):
  print "SimpleSumpple: " + '{:%Y.%m.%d %H:%M:%S}'.format(datetime.datetime.now()) + ": " + message

if __name__ == "__main__":
  scan_loop()
