# Complete project details at https://RandomNerdTutorials.com

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp

import ntptime



#import onewire

#import ds18x20


esp.osdebug(None)
import gc
gc.collect()

ssid = 'LowiA456'
password = '6HD5X2W2UHHWJA'
mqtt_server = 'public.mqtthq.com'
#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'DOMHOTEL/H001/R001/SET/#'
topic_pub = b'hello'

last_message = 0
message_interval = 5
counter = 0

#ds_pin = machine.Pin(25)
#ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))



station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


print("Local time before synchronization：%s" %str(time.localtime()))
ntptime.settime()
print("Local time after synchronization：%s" %str(time.localtime()))

