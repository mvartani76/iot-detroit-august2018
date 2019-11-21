#!/bin/bash

# disabling wifi power management
printf "\nDisabling WiFi Power Management...\n"
/sbin/iwconfig wlan0 power off

# load environment variables from .env file
set -o allexport
source .env
set +o allexport

# run Beacon Scanner App using provided certificates
printf "\nRunning Beacon Scanner Application...\n"
python $AWS_IOT_PYTHON_CMD_OPTIONS

