
from network import WLAN 
from umqttsimple import MQTTClient 
from machine import Timer
import machine
import time
import ubinascii
import random

global client
global room_number
global v_messages
global CURRENT_TIME

room_number = '333'
v_messages= {}

plug_pin  = machine.Pin(25, machine.Pin.OUT)
ligth_pin = machine.Pin(26, machine.Pin.OUT)
ac_pin    = machine.Pin(14, machine.Pin.OUT)

client_id = ubinascii.hexlify(machine.unique_id())
client_id = b'346f28af96f4'


keepLiveTime = 120
print("--------------------")
print(client_id)
print(random.getrandbits(16))
        
def extractTime(value) :
    
    v_day    = int(value[0:2] )
    v_month  = int(value[3:5])
    v_year   = int(value[6:10])
    v_hour   = int(value[11:13])
    v_minute = int(value[14:16])
    
    v_time = (v_year,v_month,v_day,v_hour,v_minute,0,0,0,0)
    time_unix = time.mktime( v_time )
    
    return time_unix
    

def sub_cb(topic, msg):
    
    print(topic)
    print(msg)
    
    v_messages[topic.decode().strip("'\n")] = msg.decode().strip("'\n")
 
  

def connect_and_subscribe():
  time.sleep(2)
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server,port=1883,keepalive=keepLiveTime)
  print(client)
  client.set_callback(sub_cb)
  time.sleep(1)

  result = client.connect()
  
  print(result)
  
  time.sleep(1)

  client.subscribe('DOMHOTEL/H001/R'+room_number+'/SET/#')
  
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(5)
  #client = connect_and_subscribe()
  machine.reset()






try:
  client = connect_and_subscribe()
except :
  print("errore conn MQTT")
  
  restart_and_reconnect()

tim = Timer(-1)
tim.init(period=keepLiveTime*1000, mode=Timer.PERIODIC, callback=lambda t: keepLiveTimeCb(client))

def keepLiveTimeCb(c):
  print("PINGGGGGGG")
  
  try:
    c.ping()
    c.publish("DOMHOTEL/H001/R"+room_number+"/PING","PING",retain=False)
    #time.sleep(1)
  except :
    print("MQTT - 9")
    restart_and_reconnect()
  
  time.sleep(1)




while True:
    
    # ricevo messaggi in coda  
    try:
        client.check_msg()
    #time.sleep(1)

    except :
        print("MQTT - 2")

 
 #----------------------------------------------
    print(v_messages)
    
    messages = v_messages.copy()
    
    CURRENT_TIME = time.time()


    #-------------------------------------------------------------
    for message in messages :
        
        setting = (message[ message.find("SET/")+4  : ] ).split("/")
        
        command = setting[0]
        if len(setting) == 1 :
            subcommand = None
        else:
            subcommand = setting[1]
        
        #------- start or stop immediate
        if (subcommand == None ):
            
            print(command, messages[message] )
            
            #A T T E N Z I O NE --------------------------------------------
            # accrocchio per visulizzare bene i led dei relais--------------
            if (messages[message] == '0') :
                val = 1
            else :
                val = 0
            # fine accrocchio ----------------------------------------
            if (command == "PLUG") :
                print("setto PLUG : ", str(val))
                plug_pin.value(val)
                client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/PLUG",messages[message],retain=True)

            elif (command == "LIGTH") :
                print("setto LIGTH : ", str(val))
                ligth_pin.value(val)
                client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/LIGTH",messages[message],retain=True)

            elif (command == "AC") :
                print("setto AC : ", str(val))
                ac_pin.value(val)
                client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/AC",messages[message],retain=True)

                        
            del v_messages[message] 
            
        elif (subcommand == "START" ):
            
            time_start = extractTime(messages[message] )
            
            if (CURRENT_TIME >= time_start ):
                
                print(subcommand + '  - START')
                
                if (command == "PLUG") :
                    print("setto PLUG : ", "1")
                    plug_pin.value(0)
                    client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/PLUG","1",retain=True)

                elif (command == "LIGTH") :
                    print("setto LIGTH : ", "1")
                    ligth_pin.value(0)
                    client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/LIGTH","1",retain=True)

                elif (command == "AC") :
                    print("setto AC : ", "1")
                    ac_pin.value(0)
                    client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/AC","1",retain=True)
                    
                del v_messages[message] 
                
            else :
                print(subcommand + '  - QUEUED')
        
        elif (subcommand == "STOP" ):
             
            time_stop = extractTime(messages[message] )
            
            if (CURRENT_TIME >= time_stop ):
                
                print(subcommand + '  - STOP')
                
                if (command == "PLUG") :
                    print("setto PLUG : ", "0")
                    plug_pin.value(1)
                    client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/PLUG","0",retain=True)

                elif (command == "LIGTH") :
                    print("setto LIGTH : ", "0")
                    ligth_pin.value(1)
                    client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/LIGTH","0",retain=True)

                elif (command == "AC") :
                    print("setto AC : ", "0")
                    ac_pin.value(1)
                    client.publish("DOMHOTEL/H001/R"+room_number+"/STATUS/AC","0",retain=True)
                
                del v_messages[message] 
                
            else :
                print(subcommand + '  - QUEUED')
 
 
 
    time.sleep(2)


