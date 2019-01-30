'''
/*
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
import oled
import os
import dotenv
from dotenv import load_dotenv, find_dotenv
load_dotenv("/opt/msx/iot-detroit-august2018/beacon-scanner/Python/.env", override=True, verbose=True)

# The main loop now uses an environment variable to determine how to filter beacon scan
# Display the expression used for debug purposes
beacon_scan_expr = os.getenv("BEACON_SCAN_EXPR")
BEACON_UUID = os.getenv("BEACON_UUID")

print beacon_scan_expr
print BEACON_UUID

# Set the code version
aws_iot_code_version = "1.2"

# Initialize OLED Display Object
oled_data = oled.init_oled(64)

dev_id = 0
try:
        sock = bluez.hci_open_dev(dev_id)
        print "ble thread started"
	oled.display_general_msg(oled_data, "BLE Thread Started", "", "", 1)
except:
        print "error accessing bluetooth device..."
	oled.display_general_msg(oled_data, "Bluetooth Error", "", "", 1)
        sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

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
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="beacon", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="publish",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")
parser.add_argument("-mt", "--messageType", action="store", dest="messageType", default="string", help="Message Type")
parser.add_argument("-as", "--syncType", action="store", dest="syncType", default="async", help="sync or async")
parser.add_argument("-st", "--sleepTimer", action="store", dest="sleepTime", default=5, help="Time to sleep in main loop in seconds")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic
messageType = args.messageType

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

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
oled.display_general_msg(oled_data, "Init AWS IoT...", "", "", 1)
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
oled.display_general_msg(oled_data, "Connecting to AWS IoT...", "", "", 1)
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
while True:
	if args.mode == 'both' or args.mode == 'publish':
		message = {}
		# Run the BLE Scan
		# Display that the beacon scan is starting
		oled.display_beacon_scan_msg(oled_data, "Scanning for beacons...", aws_iot_code_version)
		# Zero loop_count
		loop_count = 0
		returnedList = blescan.parse_events(sock, 10)
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
				strMessage = str(beacon.mac_addr) + ", " + beacon.buuid + ", " + str(beacon.major) + ", " + str(beacon.minor) + ", " + str(beacon.rssi[0]) + ", " + str(beacon.btime)
				
				# Check the messagType argument to determine message format
				if args.messageType == 'json':
					pubmessage = messageJson
				else:
					pubmessage = strMessage

				# Check the syncType argument to determine which type of publish message to send
				if args.syncType == 'async':
					myAWSIoTMQTTClient.publishAsync(topic, pubmessage, 1, ackCallback=customPubackCallback)
				else:
					myAWSIoTMQTTClient.publish(topic, pubmessage, 1)
				if args.mode == 'publish':
					print('Published topic %s: %s\n' % (topic, pubmessage))
					print('Loop count: %d / %d\n' % (loop_count, len(returnedList)))
					loop_count = loop_count + 1
					oled.display_beacon_info(oled_data, beacon, aws_iot_code_version)
				time.sleep(args.sleepTime)
	oled.display_beacon_scan_msg(oled_data, "Receiver sleeping...", aws_iot_code_version)
	time.sleep(1)
