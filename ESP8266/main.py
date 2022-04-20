
"""
OTA updater for ESP32 running Micropython by David Flory.
Tutorial: https://randomnerdtutorials.com/esp32-esp8266-micropython-ota-updates/

This is a simple way to run a python program on the ESP32 and download updates or a different program
to run from an HTTP server, either from the web or your local network.

Put all the imports needed for internet in boot, plus a global variable called OTA
The main file creates the internet connection then runs whatever program is required. I call the program 'program.py'

program.py is the main program, and can be whatever you want. The only requisite for this to work with OTA is that
it must be imported into the module 'main' and it must check periodically for updates.
The Program should have a function that can be called by 'main' to start it.

We can overwrite program.py while it is running, because it has been imported on boot into the namespace of 'main'.
All that is required is a reboot after a new Program.py is downloaded. In this case the deep sleep function will reboot the ESP32.

"""
#When prog.py finishes, if OTA = True, main downloads it and overwrites program.py, then effectively reboots.
#If OTA is false main just exits.

#this is the program to be executed. Note we do not use the '.py' extension.
import program

import machine #needed for the deep sleep function

from umqttsimple import MQTTClient 


#Broker MQTT for the updates
#replace with your PHP server URL or local IP address (Raspberry Pi IP Address)
#upd_url="http://192.168.0.14/get_ESP_data.php?file=program.py"
mqtt_server = 'public.mqtthq.com'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'DOMHOTEL/H001/R001/UPDATE/#'
topic_pub = b'hello'

#change your wifi credentials here. 
ssid = 'LowiA456'
password = '6HD5X2W2UHHWJA'

print('OTA is ' + str(OTA))#debug

#here we set up the network connection
station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
print(station.config('mac'))


print(implementation.name)
print(uname()[3])
print(uname()[4])
print()

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print("MAC: " + mac)
print()


# connect to MQTT Broker
def sub_cb(topic, msg):
    
    print(topic.decode().strip("'\n"))
    print( msg.decode().strip("'\n"))
 
  

def connect_and_subscribe():
  time.sleep(2)
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server,port=1883,keepalive=0)
  client.set_callback(sub_cb)
  time.sleep(1)

  client.connect()
  time.sleep(1)

  client.subscribe('DOMHOTEL/H001/R001/UPDATE/#')
  
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  #time.sleep(5)
  machine.deepsleep(5000)



try:
  client = connect_and_subscribe()
except :
  print("errore conn MQTT")
  restart_and_reconnect()


if OTA == 0:
    print('starting program')
    OTA = program.mainprog(OTA)
    
#mainprog() is the starting function for my program. OTA is set to 0 on boot so the first time this code
#is run, it sets up the network connection and then runs the program.
#The following code only runs when program.py exits with OTA = 1

try:
    client.check_msg()
    #time.sleep(1)

except :
    print("MQTT - 2")


if OTA == 1:
    print('Downloading update')
    #download the update and overwrite program.py
    response = requests.get(upd_url)
    x = response.text.find("FAIL")
    if x > 15:
        #download twice and compare for security
        x = response.text
        response = requests.get(upd_url)
        if response.text == x:
            f = open("program.py","w")
            f.write(response.text)
            f.flush()
            f.close
            
            #soft reboot 
            print('reboot now')
            machine.deepsleep(5000)
