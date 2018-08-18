#!/bin/bash

#
# Program to scan Sumpple IP cameras and create a webpage of snapshots.  
# Clicking on a snapshot will take you to the live feed for that camera in a new tab.
# Program should work with any Foscam-type IP camera
#

# TO DOS: Scan a subnet mask instead of a static list

## Globals
DEBUG=1
# Warning!!! The image_data_directory to store image data should be dedicated, as images older than [image_storage_period_in_days] are deleted
image_data_directory=/var/www/html/sumpple_images
image_storage_period_in_days=10
camera_username=admin
camera_password_file=$HOME/.sumpple_password
camera_password=
passive_scan_refresh_interval=10
camera_ip_scan_refresh_interval=300
#camera_ip_list="10.0.0.0 10.0.0.1 10.0.0.2 10.0.0.3 10.0.0.4 10.0.0.5 10.0.0.6 10.0.0.7 10.0.0.8 10.0.0.9 10.0.0.10 10.0.0.11 10.0.0.12 10.0.0.13 10.0.0.14"
camera_ip_list="10.0.0.2 10.0.0.3 10.0.0.9 10.0.0.10"
camera_ip_subnet="10.0.0.0/24"
# I deliberately made this non-responsive, as I wanted to ensure that all the images fit onto a single
# window, regardless of device
html_table_width=4

## Locals
last_camera_ip_scan_time=0
camera_ip_address_list=""

scan_for_cameras() {
    if [ $DEBUG ]; then echo "DEBUG: scan_for_cameras(): >"; fi
    for ip_address in $camera_ip_list; do
      if [ $DEBUG ]; then echo "DEBUG: scan_for_cameras(): Looking for a camera at address $ip_address"; fi
      if (checkForSumppleCameraAtAddress $ip_address); then
        if [ $DEBUG ]; then echo "DEBUG: scan_for_cameras(): Found camera at address $ip_address"; fi
        camera_ip_address_list="$camera_ip_address_list $ip_address"
        if [ $DEBUG ]; then echo "DEBUG: scan_for_cameras(): Adding $ip_address to camera list, current list [$camera_ip_address_list]"; fi
      fi
    done
    last_camera_ip_scan_time=`date +%s`
    if [ $DEBUG ]; then echo "DEBUG: scan_for_cameras(): <"; fi
}

setup() {
  if [ ! -w $image_data_directory ]; then
    mkdir $image_data_directory
    if [ ! -w $image_data_directory ]; then
      echo -e  "\n\nERROR! Could not create image data directory at $image_data_directory\n\n"
      exit 1
    fi
  fi
  if [ ! -r $camera_password_file ]; then 
    echo -e "\n\n ERROR!  Set the camera(s) admin password in $camera_password_file, e.g.\n \n      echo \"53cr3t5\" > $camera_password_file \n\n and restart \n\n"
    exit 2
  else
    camera_password=`cat $camera_password_file`
  fi
}


checkForSumppleCameraAtAddress() {
  camera_ip_address=$1 
  if [ `curl -s --connect-timeout 2 http://$camera_ip_address/js/customer.js | grep sumpple | wc -l` -gt 0 ]; then
    return 0;
  else 
    return 1;
  fi
}

setup_httpd() {
  # TODO: This is heavily customized to Rasbian (apt-get)
  sudo apt-get update
  sudo apt-get install -y httpd mod_ssl
}


retrieve_snapshots_from_all_cameras() {
    # Check the camera_ip_scan_refresh_interval to see if it's time to rescan the local network for cameras
    #    Sumpple cameras don't always come up with the same IP address (e.g. after a momentary power outage)
    seconds_since_epoch=`date +%s`
    if [ $DEBUG ]; then echo "DEBUG: retrieve_snapshots_from_all_cameras(): `expr $seconds_since_epoch - $last_camera_ip_scan_time` seconds have elapsed since network camera sca
n"; fi
    if [ `expr $seconds_since_epoch - $last_camera_ip_scan_time` -gt $camera_ip_scan_refresh_interval ]; then
      scan_for_cameras
    fi
    for ip_address in $camera_ip_address_list; do
      current_timestamp=`date "+%Y%m%d%H%M%S"`
      if [ $DEBUG ]; then echo "DEBUG: retrieve_snapshots_from_all_cameras(): Taking snapshot from camera at $ip_address at timestamp $current_timestamp"; fi
      curl -so $image_data_directory/tmp.jpeg http://$ip_address/cgi-bin/video_snapshot.cgi?user=$camera_username\&pwd=$camera_password
      if [ $DEBUG ]; then echo "DEBUG: retrieve_snapshots_from_all_cameras(): Archiving image to $image_data_directory/$ip_address.`date +%Y%m%d%H%M%S`.jpeg"; fi
      cp $image_data_directory/tmp.jpeg $image_data_directory/$ip_address.current_snapshot.jpeg
      cp $image_data_directory/$ip_address.current_snapshot.jpeg  $image_data_directory/$ip_address.`date +%Y%m%d%H%M%S`.jpeg
    done
}

cleanup_image_data_directory() { 
  if [ `ls $image_data_directory/*snapshot*.jpeg | wc -l` -gt 0 ]; then
    find $image_data_directory -name '*snapshot*.jpeg' -ctime +10 -exec rm -rf {} \;
    echo ""
  fi
}

# Start of main program
setup
while [ 1 ]; do
  retrieve_snapshots_from_all_cameras
  #cleanup_image_data_directory
  sleep $passive_scan_refresh_interval
done
