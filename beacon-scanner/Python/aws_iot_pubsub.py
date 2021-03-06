''' /*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import blescan
import sys
import bluetooth._bluetooth as bluez
import scanutil
import oled
import subprocess
import os
import dotenv
import socket
import beacon_utility
import file_access
import i2c_util
from dotenv import load_dotenv, find_dotenv
load_dotenv("/opt/msx/iot-detroit-august2018/beacon-scanner/Python/.env", override=True, verbose=True)

# The main loop now uses an environment variable to determine how to filter beacon scan
beacon_scan_expr = os.getenv("BEACON_SCAN_EXPR")
BEACON_UUID = os.getenv("BEACON_UUID")

# Set some constants...
health_signal_code = 1111
reset_signal_code = 1112
beacon_response_signal_code = 2222
EXITCODE_EVERYTHING_OK = 0
EXITCODE_RESET_SIGNAL_SECTION = 1
EXITCODE_BLUETOOTH_SCAN_SECTION = 2
EXITCODE_HEALTH_SIGNAL_SECTION = 3

# get the hostname
hostname = os.uname()[1]

# Set the clientId to hostname
clientId = hostname

# Set the code version
aws_iot_code_version = "1.21"

# Check to see if anything connected to i2c on bus 1
i2c_found = i2c_util.i2c_find(1)
print(i2c_found)
# Initialize OLED Display Object
oled_data = oled.init_oled(64, i2c_found)

# Initialize File Access Object
file_access_data = file_access.FileAccess()


dev_id = 0
try:
        sock = bluez.hci_open_dev(dev_id)
        print "ble thread started"
	oled.display_general_msg(oled_data, "BLE Thread Started", "", "", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
except:
        print "error accessing bluetooth device..."
	oled.display_general_msg(oled_data, "Bluetooth Error", "", "", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
        sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

# Custom MQTT message callback
def status_sub_callback(client, userdata, message):
	# convert message.payload to json object
	p_obj = json.loads(message.payload)
	if p_obj["device"] == hostname:
		print(p_obj["device"])
		print(message.payload)
		ackmsg = {}
		ackmsg['device'] = hostname
		ackmsg['ssid'] = subprocess.check_output("iwgetid -r", shell=True)
		ackmsg['ipaddr'] = scanutil.get_ip_addr()
		ackmsg['wifi_rssi'] = scanutil.get_wifi_rssi('wlan0')
		ackjson = json.dumps(ackmsg, ensure_ascii=False)
		oled.display_general_msg(oled_data, "Received Message", hostname, ackmsg['ssid'], "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 5, i2c_found)
		myAWSIoTMQTTClient.publishAsync(status_ack_topic, ackjson, 1, ackCallback=customPubackCallback)

# Custom MQTT Puback callback
def customPubackCallback(mid):
    print("Received PUBACK packet id: ")
    print(mid)
    print("++++++++++++++\n\n")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="beacon", help="Targeted topic")
parser.add_argument("-srt", "--statrxtopic", action="store", dest="status_rx_topic", default="beacon_status_rx", help="Subscribe Topic")
parser.add_argument("-sat", "--statacktopic", action="store", dest="status_ack_topic", default="beacon_status_ack", help="Ack Topic")
parser.add_argument("-mt", "--messageType", action="store", dest="messageType", default="string", help="Message Type")
parser.add_argument("-as", "--syncType", action="store", dest="syncType", default="async", help="sync or async")
parser.add_argument("-st", "--sleepTimer", action="store", dest="sleepTime", default=5, help="Time to sleep in main loop in seconds")
parser.add_argument("-lc", "--loopCount", action="store", dest="loopCount", default=100, help="Loop Count for BLE Prase")
parser.add_argument("-hct", "--healthTimeThresh", action="store", dest="healthTimeThresh", default=600, help="Health Time Threshold in seconds")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket

# set the topic as feature/company/hostname
topic = args.topic
topic = topic + "/" + hostname[:3] + "/" + hostname

status_rx_topic = args.status_rx_topic
status_ack_topic = args.status_ack_topic
messageType = args.messageType
parse_loop_count = args.loopCount
health_time_thresh = args.healthTimeThresh

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.ERROR)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
oled.display_general_msg(oled_data, "Init AWS IoT...", clientId, "", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
try:
	oled.display_general_msg(oled_data, "Connecting to AWS IoT...", clientId, "", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	myAWSIoTMQTTClient.connect()
	print("Connected to AWS IoT...\n")
except:
	oled.display_general_msg(oled_data, "Could not connect to AWS...", "Checking Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	if scanutil.have_internet():
		oled.display_general_msg(oled_data, "Could not connect to AWS...", "Internet OK...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	else:
		oled.display_general_msg(oled_data, "Could not connect to AWS...", "No Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	exit(1)

try:
	oled.display_general_msg(oled_data, "Subscribing to Topic...", clientId, status_rx_topic, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	myAWSIoTMQTTClient.subscribe(status_rx_topic, 1, status_sub_callback)
except:
	oled.display_general_msg(oled_data, "Could not subscribe to topic...", clientId, status_rx_topic, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	exit(1)

time.sleep(1)

# Check to see if exit file exists
# If it does, read the code and set as exitcode
file_access_data.readExitFileAndSetCode()
print("read file...")
print(file_access_data.exitcode)

# Send a reset signal to AWS for debugging
resetMessage = str(str(scanutil.display_mac_addr()) + ", " + str(reset_signal_code) + ", " + str(aws_iot_code_version) + ", " + str(file_access_data.exitcode) + ", 0, " + str(int(time.time())))

print("Sending Reset Signal...\n")
print(resetMessage)

# Initialize the exit code as everything OK
file_access_data.writeExitCode(EXITCODE_EVERYTHING_OK)

try:
	oled.display_general_msg(oled_data, "Sending Reset Signal...", "", clientId, socket.gethostname(), aws_iot_code_version, 1, i2c_found)
	myAWSIoTMQTTClient.publishAsync(topic, resetMessage, 1, ackCallback=customPubackCallback)
	print("Sent Reset Signal...")
except:
	print("Could not send Reset Signal...")
	oled.display_general_msg(oled_data, "Could Not Publish...", "Checking Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
	# exit out of the program if no internet
	if (not(scanutil.have_internet())):
		oled.display_general_msg(oled_data, "Could Not Publish...", "No Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
		file_access_data.writeExitCode(EXITCODE_RESET_SIGNAL_SECTION)
		exit(1)

time.sleep(1)

# Mark the initial unix time that the loop starts to use for health signal timer/counter
old_time = int(time.time())

# Initialize beacon sum dictionary that counts the number of beacon responses
beacon_sum = {}
beacon_sum_all_old = 0

# Loop forever publishing to MQTT topics
while True:
	message = {}
	healthmsg = {}
	# Run the BLE Scan
	# Display that the beacon scan is starting
	oled.display_beacon_scan_msg(oled_data, "Scanning for beacons...", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 0.1, i2c_found)
	# Zero loop_count
	loop_count = 0
	returnedList = blescan.parse_events(sock, parse_loop_count)
	for beacon in returnedList:
		# Filter the beacon scan based on beacon_scan_expr
		# eval() evaluates the string conditional
                if (eval(beacon_scan_expr)):
			message['beacon_uuid'] = beacon.buuid
			message['beacon_major'] = beacon.major
			message['beacon_minor'] = beacon.minor
			message['beacon_rssi'] = beacon.rssi[0]
			message['btime'] = beacon.btime
			message['mac_addr'] = beacon.mac_addr
			messageJson = json.dumps(message)
			strMessage = str(beacon.mac_addr) + ", " + str(beacon_response_signal_code) + ", " + str(beacon.major) + ", " + str(beacon.minor) + ", " + str(beacon.rssi[0]) + ", " + str(beacon.btime)

			# Check the messagType argument to determine message format
			if args.messageType == 'json':
				pubmessage = messageJson
			else:
				pubmessage = strMessage

			# Check the syncType argument to determine which type of publish message to send
			if args.syncType == 'async':
				# Perform some simple error catching on publish command
				# MQTT Broker handles offline queueing so not sure when we would see error
				try:
					oled.display_general_msg(oled_data, "Publishing AWS MQTT...", clientId, "", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
					myAWSIoTMQTTClient.publishAsync(topic, pubmessage, 1, ackCallback=customPubackCallback)
				except:
					oled.display_general_msg(oled_data, "Could Not Publish...", "Checking Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
					# exit out of the program if no internet
					if (not(scanutil.have_internet())):
						oled.display_general_msg(oled_data, "Could Not Publish...", "No Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
						file_access_data.writeExitCode(EXITCODE_BLUETOOTH_SCAN_SECTION)
						exit(1)
			else:
				myAWSIoTMQTTClient.publish(topic, pubmessage, 1)

			print('Published topic %s: %s\n' % (topic, pubmessage))
			print('Loop count: %d / %d\n' % (loop_count, len(returnedList)))
			loop_count = loop_count + 1
			# Sum the amount of times we see a specific beacon minor
			beacon_sum = beacon_utility.accumulate_beacons(beacon_sum, {beacon.minor:1})
			print(beacon_sum)
			print("total beacon pings: %s \n" % beacon_utility.accumulate_all_beacons(beacon_sum))
			oled.display_beacon_info(oled_data, beacon, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), beacon_sum[beacon.minor], aws_iot_code_version, 0.1, i2c_found)
			time.sleep(args.sleepTime)

	oled.display_beacon_scan_msg(oled_data, "Receiver sleeping...", "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1.1, i2c_found)

	# Sum all the received beacon pings
	# This is currently cumulative of all pings received since reset
	beacon_sum_all = beacon_utility.accumulate_all_beacons(beacon_sum)

	# Calculate the time difference since the last health signal
	health_time_diff = int(time.time()) - old_time
	print("health time difference: %s \n" % str(health_time_diff))

	# check to see if health_count greater than health count threshold
	if (health_time_diff >= health_time_thresh):
		# Store the time that health signal is sent
		old_time = int(time.time())

		# Calculate the difference between successive total beacon sums to get the
		# total beacon sum since the last health signal
		beacon_sum_diff = beacon_sum_all - beacon_sum_all_old
		beacon_sum_all_old = beacon_sum_all

		print("Sending health signal code...\n\n")
		print("Time difference: %s\n" % str(health_time_diff))
		healthmsg['mac_address'] = str(scanutil.display_mac_addr())
		healthmsg['time'] = int(time.time())
		healthMessage = str(healthmsg['mac_address']) + ", " + str(health_signal_code) + ", " + str(aws_iot_code_version) + ", " + str(health_time_diff) + ", " + str(beacon_sum_diff) + ", " + str(healthmsg['time'])

		try:
			oled.display_general_msg(oled_data, "Sending Health Signal...", "", clientId, str(socket.gethostname()), aws_iot_code_version, 1, i2c_found)
			myAWSIoTMQTTClient.publishAsync(topic, healthMessage, 1, ackCallback=customPubackCallback)
			print('Published health topic %s: %s\n' % (topic, healthMessage))
		except:
			oled.display_general_msg(oled_data, "Could Not Publish...", "Checking Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
			# exit out of the program if no internet
			if (not(scanutil.have_internet())):
				oled.display_general_msg(oled_data, "Could Not Publish...", "No Internet...", clientId, "WiFi RSSI: " + scanutil.get_wifi_rssi('wlan0'), aws_iot_code_version, 1, i2c_found)
				file_access_data.writeExitCode(EXITCODE_HEALTH_SIGNAL_SECTION)
				exit(1)
	else:
		print('Time since last signal %d less than threshold of %d.\n' % (health_time_diff, health_time_thresh))
