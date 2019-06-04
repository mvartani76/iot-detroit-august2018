#!/bin/bash

# disabling wifi power management
printf "\nDisabling WiFi Power Management...\n"
/sbin/iwconfig wlan0 power off

# run Beacon Scanner App using provided certificates
printf "\nRunning Beacon Scanner Application...\n"
python $AWS_IOT_PYTHON_CMD_OPTIONS

