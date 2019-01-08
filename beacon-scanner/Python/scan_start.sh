#!/bin/bash

printf "Starting Script...\n"

# stop script on error
set -e

# Check to see if user downloaded the AWS start.sh file to the python directory
if [ ! -f ./start.sh ]; then
	printf "\nstart.sh not found. Please download from AWS....\n"
	exit 0
else
	printf "\nNeed to remove any extra newlines at EOF if they exist...\n"
	while [ -z "$(tail -c 1 start.sh)" ]
	do
		printf "Newline found at end of file...\n"
		head -c -1 start.sh > start.tmp
		mv start.tmp start.sh
	done
	printf "\nExtracting Credentials from AWS start.sh file...\n"
	# The credentials that we are looking for are located after the call to the python function in the AWS start.sh file
	# grep appears to be more stable than the previous while loop
	AWSINFO="$(grep -o ".py -e.*" start.sh)"
fi

# Check to see if root CA file exists, download if not
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# Provide write access to python dist-packages directory. This is needed to install python libraries here.
sudo chmod -R 777 /usr/local/lib/python2.7/dist-packages/

# install AWS Device SDK for Python if not already installed
if [ ! -d /usr/local/lib/python2.7/dist-packages/AWSIoTPythonSDK ]; then
  printf "\nInstalling AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python.git
  pushd aws-iot-device-sdk-python
  python setup.py install
  popd
fi

# It appears that Raspbian Stretch comes pre-installed with bluez 5.43 but we still need to install python-bluez
sudo apt-get install python-bluez

# run Beacon Scanner App using provided certificates
# will populate the python command from downloaded AWS connection package start.sh
printf "\nRunning Beacon Scanner Application...\n"
PYTHONFILE="aws_iot_pubsub${AWSINFO}"

# Initiate the python command with the desired file and arguments
sudo python ${PYTHONFILE}
