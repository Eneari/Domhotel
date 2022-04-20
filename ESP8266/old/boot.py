# Complete project details at https://RandomNerdTutorials.com

#import machine
#import micropython
import network
import esp

from read_config import read_config


#esp.osdebug(None)
import gc
gc.collect()

ssid = read_config("/conf/ssid.ini")
password = read_config("/conf/password.ini")


station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

import webrepl
webrepl.start()

from machine import Pin, I2C
import ssd1306
from time import sleep

i2c = I2C(-1, scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

oled.fill(0)
oled.text("Conn. Success", 0, 0)
oled.text(str(station.ifconfig()), 0, 12)
oled.show()
sleep(5)


#import main
