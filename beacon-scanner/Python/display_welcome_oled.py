import os
import time
import oled
import socket
import signal
import subprocess
from dotenv import load_dotenv, find_dotenv

# load .env file
load_dotenv("/opt/msx/iot-detroit-august2018/beacon-scanner/Python/.env", verbose=True)

# Initialize OLED Display Object
oled_data = oled.init_oled()

# Get the ip address
ip_addr = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]

# Get the SSID
ssid = subprocess.check_output("iwgetid -r", shell=True)

beacon_scan_expr = os.getenv("BEACON_SCAN_EXPR")

print len(beacon_scan_expr)

# Display welcome message
oled.display_general_msg(oled_data, ip_addr, ssid, beacon_scan_expr, 5)

