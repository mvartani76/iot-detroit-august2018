import time
# Import libraries needed for OLED display
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class OledData(object):
    def __init__(self, width=None, height=None, image=None, draw=None, padding=None, top=None, bottom=None, x=None, font=None, disp=None):
        self.width = width
        self.height = height
        self.image = image
        self.draw = draw
        self.padding = padding
        self.top = top
	self.bottom = bottom
	self.x = x
	self.font = font
	self.disp = disp


def init_oled():
	# Initialize OLED Display
	RST = None
	# 128x32 display with hardware I2C:
	disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

	# Initialize library.
	disp.begin()

	# Clear display.
	disp.clear()
	disp.display()

	# Create blank image for drawing.
	# Make sure to create image with mode '1' for 1-bit color.
	width = disp.width
	height = disp.height
	image = Image.new('1', (width, height))

	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)

	# Draw a black filled box to clear the image.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	# Draw some shapes.
	# First define some constants to allow easy resizing of shapes.
	padding = -2
	top = padding
 	bottom = height-padding
	# Move left to right keeping track of the current x position for drawing shapes.
	x = 0

	# Load default font.
	font = ImageFont.load_default()

	# Store into Oled Class
	oled = OledData(width, height, image, draw, padding, top, bottom, x, font, disp)
	return oled

# display_beacon_info() displays the time, major, minor, and rssi
def display_beacon_info(oled, beacon):
	current_time = time.strftime('%m/%d/%Y %H:%M:%S')
	# Display time and beacon information on OLED display
        oled.draw.rectangle((0,0,oled.width,oled.height), outline=0, fill=0)
        oled.draw.text((oled.x, oled.top), current_time, font=oled.font, fill=255)
        oled.draw.text((oled.x, oled.top+8), "Major: " + str(beacon.major), font=oled.font, fill=255)
        oled.draw.text((oled.x, oled.top+16), "Minor: " + str(beacon.minor), font=oled.font, fill=255)
        oled.draw.text((oled.x, oled.top+25), "RSSI: " + str(beacon.rssi[0]), font=oled.font, fill=255)
        oled.disp.image(oled.image)
        oled.disp.display()
        time.sleep(0.1)

# display_beacon_scan_msg()  displays the time and a message
def display_beacon_scan_msg(oled, msg, code_ver):
	oled.disp.clear()
	current_time = time.strftime('%m/%d/%Y %H:%M:%S')
	# Display time and beacon information on OLED display
	oled.draw.rectangle((0,0,oled.width,oled.height), outline=0, fill=0)
	oled.draw.text((oled.x, oled.top), current_time, font=oled.font, fill=255)
	oled.draw.text((oled.x, oled.top+8), msg, font=oled.font, fill=255)
	oled.draw.text((oled.x, oled.top+25), code_ver, font=oled.font, fill=255)
	oled.disp.image(oled.image)
	oled.disp.display()
	time.sleep(0.1)

def display_general_msg(oled, msg1, msg2, msg3, delay):
	oled.disp.clear()
	current_time = time.strftime('%m/%d/%Y %H:%M:%S')
	# Display time and msgs on OLED display
        oled.draw.rectangle((0,0,oled.width,oled.height), outline=0, fill=0)
        oled.draw.text((oled.x, oled.top), current_time, font=oled.font, fill=255)
        oled.draw.text((oled.x, oled.top+8), msg1, font=oled.font, fill=255)
	oled.draw.text((oled.x, oled.top+16), msg2, font=oled.font, fill=255)
        oled.draw.text((oled.x, oled.top+25), msg3, font=oled.font, fill=255)
        oled.disp.image(oled.image)
        oled.disp.display()
        time.sleep(delay)
