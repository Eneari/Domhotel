
import time

v_messages = {"DOMHOTEL/H001/R001/SET/AC": "1",
            "DOMHOTEL/H001/R101/SET/AC/START" : "19/03/2022 18:51" ,
            "DOMHOTEL/H001/R101/SET/AC/STOP" :  "19/03/2022 18:52"
            }
            

print("Local time ：%s" %str(time.localtime()))

utime = time.time()
print("Unix time ：%s" %str(utime))

CURRENT_TIME = time.time()

PLUG_PIN = ''
AC_PIN= ''
LIGTH_PIN=''
        
def extractTime(value) :
    
    v_day    = int(value[0:2] )
    v_month  = int(value[3:5])
    v_year   = int(value[6:10])
    v_hour   = int(value[11:13])
    v_minute = int(value[14:16])
    
    v_time = (v_year,v_month,v_day,v_hour,v_minute,0,0,0,0)
    time_unix = time.mktime( v_time )
    
    return time_unix
    


while True :
    
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
        
        print("command : ",command)
        print("sub command : ",subcommand)
        
        if (subcommand == None ):
            print(command, messages[message] )
            
            globals()[command+'_PIN'] = messages[message]
            
            del v_messages[message] 
            
        elif (subcommand == "START" ):
            
            time_start = extractTime(messages[message] )
            
            if (CURRENT_TIME >= time_start ):
                globals()[command+'_PIN'] = '1'
                print(command + '  - START')
                del v_messages[message] 
                
            else :
                print(subcommand + '  - QUEUED')
        
        elif (subcommand == "STOP" ):
             
            time_stop = extractTime(messages[message] )
            
            if (CURRENT_TIME >= time_stop ):
                globals()[command+'_PIN'] = '0'
                print(command + '  - STOP')
                del v_messages[message] 
                
            else :
                print(subcommand + '  - QUEUED')
                
        print('AC_PIN  ',AC_PIN)
        print('PLUG_PIN  ',PLUG_PIN)
        print('LIGTH_PIN  ',LIGTH_PIN)

                
    time.sleep(10)
