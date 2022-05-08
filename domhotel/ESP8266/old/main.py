# Complete project details at https://RandomNerdTutorials.com
import ubinascii
import machine
from time import sleep
from read_config import read_config

import time


from machine import Pin, I2C, ADC
import ssd1306


import onewire

import ds18x20




# ESP8266 Pin assignment
i2c = I2C(-1, scl=Pin(5), sda=Pin(4))

oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


  
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
  


#wri = Writer(oled, freesans24_num)



old_temp = 0


# definisco gli indirizzi delle sonde
SondeTemp = {}
SondeVal  = {}
SondeVal["ST/VAL/ST01"] = 0
#SondeVal["ST/VAL/ST02"] = 0
#SondeVal["ST/VAL/ST03"] = 0
#SondeVal["ST/VAL/ST04"] = 0
#SondeVal["ST/VAL/ST05"] = 0
#SondeVal["ST/VAL/ST06"] = 0

SondeTemp["ST/VAL/ST01"] = bytearray(b'(\xffu\\\xb4\x16\x05f')
#SondeTemp["ST/VAL/ST02"] = bytearray(b'(\xff\xe5\xca\xb4\x16\x03\xe4')
#SondeTemp["ST/VAL/ST03"] = bytearray(b'(\xff\xee^\xb4\x16\x05\xa6')
#SondeTemp["ST/VAL/ST04"] = bytearray(b'(\xff\x8fn\xb4\x16\x052')
#SondeTemp["ST/VAL/ST05"] = bytearray(b'(\xff$\xc6\xc0\x16\x04\xeb')
#SondeTemp["ST/VAL/ST06"] = bytearray(b'(\xff$\xc6\xc0\x16\x04\xeb')


ds_pin = machine.Pin(15)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))



while True:
 
  ds_sensor.convert_temp()
  time.sleep_ms(750)
  for sonda in SondeTemp:
    val = ds_sensor.read_temp(SondeTemp[str(sonda)])
   
    if val != SondeVal[str(sonda)] :
      print(str(sonda))
      print(val)
      oled.fill(0)
      oled.text("temp", 0, 0)
      oled.show()
      SondeVal[str(sonda)] = val
      
  sleep(3)

