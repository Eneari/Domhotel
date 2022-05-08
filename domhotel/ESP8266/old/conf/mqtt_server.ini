# Complete project details at https://RandomNerdTutorials.com
from umqttsimple import MQTTClient
import ubinascii
import machine
from time import sleep
from read_config import read_config


from machine import Pin, I2C, ADC
import ssd1306

from writer import Writer

# Font
import freesans24_num


import math

mqtt_server = read_config("/conf/mqtt_server.ini")
client_id = ubinascii.hexlify(machine.unique_id())

# ESP8266 Pin assignment
i2c = I2C(-1, scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server)
  #client.set_callback(sub_cb)
  client.connect()
  print('Connected to %s MQTT broker' % (mqtt_server))
  oled.fill(0)
  oled.text('Conn. MQTT broker', 0, 0)
  oled.text(mqtt_server, 0, 12)
  oled.show()
  sleep(5)
  return client

def restart_and_reconnect():
  global  mqtt_server
  print('Failed to connect to MQTT broker. Reconnecting...')
  oled.fill(0)
  oled.text('Failed conn. MQTT broker', 0, 0)
  oled.text(mqtt_server, 0, 12)
  oled.show()
  sleep(10)
  machine.reset()

    
  
def get_ntc() :
    pot = ADC(0)
    pot_value = pot.read()
      
    try:
        Temp = math.log(((10240000/pot_value) - 10000));
        Temp = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * Temp * Temp ))* Temp )
        Temp = Temp - 273.15
        Temp = Temp -2  # calibrazione
    except:
        Temp = 0
            
    return round(Temp,2)
  

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()
  
  
  


wri = Writer(oled, freesans24_num)

while True:
 
  Temp = get_ntc() 
  print(Temp)
  oled.fill(0)
  wri.set_textpos(oled, 8, 8)  # verbose = False to suppress console output
  wri.printstring("T:"+str(Temp))
  oled.show()
  
  try:
    client.publish("ST/VAL/ST10", str(Temp) ,retain=True)
  except OSError as e:
    restart_and_reconnect()
    
  sleep(2)

