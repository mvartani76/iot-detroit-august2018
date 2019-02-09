import socket
import os

try:
    import httplib
except:
    import http.client as httplib

# function to get the ip address
def get_ip_addr():
	try:
		ip_addr = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
	except:
		ip_addr = "0.0.0.0"
	return ip_addr

# Function that checks to see if there is an internet connection
def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

# Simple function to check WiFi RSSI
def get_wifi_rssi(wifi_interface):
	cmd = "iwconfig " + wifi_interface + " | grep Signal | /usr/bin/awk '{print $4}' | /usr/bin/cut -d'=' -f2"
	return os.popen(cmd).read()


