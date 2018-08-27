#!/usr/bin/python

import datetime, time, os, sys

# This is the lsit of "known" cameras.  If IP addresses are not known, put in all "suspected" addresses.
#   TO DO:  Change this to a subnet to scan
camera_list=["10.0.0.2", "10.0.0.3"]

# The list of cameras that are active, i.e. up and running
active_cameras=[]

# The timestamp in absolute seconds when the network of cameras was scanned for active cameras
last_scan_for_active_cameras=0

# The polling interval to use when scanning for active cameras
scan_for_active_cameras_polling_interval_in_seconds=3600

# How often to retrieve a still image from each camera for the console
still_image_scan_refresh_interval_in_seconds=60

# How often the HTML front-end should refresh the display
console_static_image_refresh_interval_in_seconds=61

# Credentials to access the FOSCAM/REST/Sumpple API (yes, all cameras must share the same credentials)
camera_api_username="admin"
camera_api_password_file=os.environ['HOME'] + "/.sumpple_password"

# How long should still images be retained for each camera
# TO DO: Convert this to a storage limit (e.g. keep 500MB worth of total data, something appropriate to a Pi zero SD card, or even better, allow a different storae limit for each camera))
number_of_still_images_to_retain=1000

def run_image_cleanup():
  # TO DO:  This.  Note that we want to keep a certain number of images regardless of the polling interval.  If we have 1000 images, we should sporadically delete
  #         images so that we always have as long a history as possible, just "less" history (for example we go from one image an hour, to one per day, to one per month, etc)
  log("run_image_cleanup(): >");

def scan_network_for_cameras():
  # TO DO: Instead of using a static list of IPs, accept a subnet mask and scan the subnet looking for cameras
  log("scan_network_for_cameras(): >");
  for camera in camera_list:
    log("scanning camera at address: " + camera)
    try:
      with open(camera_api_password_file, 'r') as password_file:
        camera_api_password = password_file.read().strip()
    except IOError:
      log ("scan_network_for_cameras(): !!!!! FATAL ERROR !!!!!!: Could not locate the password file (" + camera_api_password_file  + ")")
      sys.exit()
    log("scan_network_for_cameras(): Using credentials (" + camera_api_username + "," + camera_api_password + ")")
  last_scan_for_active_cameras = int(round(time.time() * 1000))
  
def poll_active_cameras_and_generate_still_images():
  log("poll_active_cameras_and_generate_still_images(): >")

def scan_loop():
  log("scan_loop(): >")
  while True: 
    current_time = int(round(time.time() * 1000))
    if (
         (last_scan_for_active_cameras == 0) or 
         ((current_time - last_scan_for_active_cameras) > scan_for_active_cameras_polling_interval_in_seconds)
     ):
      scan_network_for_cameras()
    if active_cameras:
      poll_active_cameras_and_generate_still_images()
    else: 
      log("scan_loop: no active cameras")
    run_image_cleanup()
    time.sleep(still_image_scan_refresh_interval_in_seconds)

  
def log(message):
  print "SimpleSumpple: " + '{:%Y.%m.%d %H:%M:%S}'.format(datetime.datetime.now()) + ": " + message

if __name__ == "__main__":
  scan_loop()
