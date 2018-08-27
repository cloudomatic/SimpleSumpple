#!/usr/bin/python

import datetime, time, os, sys, requests, shutil

# e.g. ALL, ERROR, INFO, NONE
log_level='ALL'

# This is the lsit of "known" cameras.  If IP addresses are not known, put in all "suspected" addresses.
#   TO DO:  Change this to a subnet to scan
camera_list=["10.0.0.2", "10.0.0.3", "10.0.0.4"]

# Directory to store the image data.  In general, this will be served via Apache HTTP
image_data_base_folder="/var/www/html/sumpple_images"

# Credentials to access the FOSCAM/REST/Sumpple API (yes, all cameras must share the same credentials)
camera_api_username="admin"
camera_api_password_file=os.environ['HOME'] + "/.sumpple_password"

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
# How long should still images be retained for each camera
# TO DO: Convert this to a storage limit (e.g. keep 500MB worth of total data, something appropriate to a Pi zero SD card, or even better, allow a different storae limit for each camera))
number_of_still_images_to_retain=1000

def run_image_cleanup():
  # TO DO:  This.  Note that we want to keep a certain number of images regardless of the polling interval.  If we have 1000 images, we should sporadically delete
  #         images so that we always have as long a history as possible, just "less" history (for example we go from one image an hour, to one per day, to one per month, etc)
  log("run_image_cleanup(): >");

def check_for_sumpple_camera_at_address(ip_address):
  log("check_for_sumpple_camera_at_address(): > ip_address=" + ip_address);
  try: 
    camera_status_request = requests.get('http://' + ip_address + '/js/customer.js')
    log("check_for_sumpple_camera_at_address(): http status code: " + str(camera_status_request.status_code), "DEBUG");
    if (camera_status_request.status_code == 200):
      log("check_for_sumpple_camera_at_address(): found camera at " + ip_address);
      return True
  except:
      pass
  return False

def scan_network_for_cameras():
  # TO DO: Instead of using a static list of IPs, accept a subnet mask and scan the subnet looking for cameras
  log("scan_network_for_cameras(): >");
  for camera_address in camera_list:
    log("scan_network_for_cameras(): scanning camera at address: " + camera_address)
    if (check_for_sumpple_camera_at_address(camera_address)):
      log("scan_network_for_cameras(): Found a compatible camera at " + camera_address)
      active_cameras.append(camera_address)
  last_scan_for_active_cameras = int(round(time.time() * 1000))
  
def pull_still_images_from_active_cameras():
  log("pull_still_images_from_active_cameras(): >")
  try:
    with open(camera_api_password_file, 'r') as password_file:
      camera_api_password = password_file.read().strip()
  except IOError:
    log ("pull_still_images_from_active_cameras(): !!!!! FATAL ERROR !!!!!!: Could not locate the password file (" + camera_api_password_file  + ")")
    sys.exit()
  log("pull_still_images_from_active_cameras(): Using credentials (" + camera_api_username + "," + camera_api_password + ")")
  for camera_address in active_cameras:
    # We need two timestamps here, an "image overlay" timestamp, and a timestamp to put on the image file itself (for the function where the user wants to grab an archived image.  
    #   Some cameras will print the current timestamp on the jpeg itself,
    #   while others will not.  Since we want to be able to quickly see in the console 
    #   whether an image is "current", we should overlay this timestamp on the image when displayed, which is best done in Javascript on the browser side.  We can
    #   store this timestamp in a file called <imagefilename>.metadata, since there will probably be other things we'll want to store about the image down the road, IR on/off, camera direction if it's panning, etc
    current_time=datetime.datetime.now()
    image_file_timestamp='{:%Y.%m.%d_%H:%M:%S}'.format(current_time)
    image_display_timestamp='{:%Y.%m.%d %H:%M:%S}'.format(current_time)
    log("pull_still_images_from_active_cameras(): Retrieving still image from " + camera_address + " via the FOSCAM 'snapshot' function", "DEBUG")
    snapshot_request=requests.get("http://" + camera_address + "/cgi-bin/video_snapshot.cgi?user=" + camera_api_username + "&pwd=" + camera_api_password, stream=True)
    log("pull_still_images_from_active_cameras(): snapshot HTTP response code: " + str(snapshot_request.status_code), "DEBUG")
    if snapshot_request.status_code == 200:
      snapshot_filename=image_data_base_folder + "/" + camera_address + ".latest.jpg"
      snapshot_archived_filename=image_data_base_folder + "/" + camera_address + "_" + image_file_timestamp + ".jpg"
      with open(snapshot_archived_filename, 'wb') as snapshot_file:
        snapshot_request.raw.decode_content=True
        shutil.copyfileobj(snapshot_request.raw, snapshot_file)
      # We copy the archived file to the "latest" file after the download is complete so that we don't get a partial image
      shutil.copyfile(snapshot_archived_filename, snapshot_filename)

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
      log("scan_loop(): active camera list: ")
      for camera in active_cameras:
        log("scan_loop():                  " + camera)
      pull_still_images_from_active_cameras()
    else: 
      log("scan_loop: no active cameras")
    run_image_cleanup()
    time.sleep(still_image_scan_refresh_interval_in_seconds)

def log(message, level="INFO"):
  if (level >= log_level):
    print "SimpleSumpple: " + '{:%Y.%m.%d %H:%M:%S}'.format(datetime.datetime.now()) + ": " + message

if __name__ == "__main__":
  scan_loop()
