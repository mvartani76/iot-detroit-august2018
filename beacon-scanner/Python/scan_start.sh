#!/bin/bash

# run Beacon Scanner App using provided certificates
printf "\nRunning Beacon Scanner Application...\n"
python $AWS_IOT_PYTHON_CMD_OPTIONS -m "both"

