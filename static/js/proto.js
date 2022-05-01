

// ----   configurazione MQtt ---------- INIZIO ----------
//var hostname = "wss://broker.hivemq.com";
var hostname = "broker.emqx.io";
//var port = 8083;
var port = 8084;
//var port = 1883;
//var clientId = "ArduWeb";
var clientId = "clientID-" + parseInt(Math.random() * 100);
//clientId += new Date().getUTCMilliseconds();
var username = "";
var password = "";

var MQTT_CONNECTED = false ;

let SUBSCRIBE;
SUBSCRIBE = true;

let send_Ok ;
send_Ok = false;

let mqttClient;


// ----   configurazione MQtt ---------- FINE ----------




// Initiates a connection to the MQTT broker
function pippo(){
    
    window.console.log("----sono in connect -------");
    
   mqttClient = new Paho.MQTT.Client(hostname, port, clientId);
    
    
// set callback handlers
mqttClient.onConnectionLost = onConnectionLost;
mqttClient.onMessageArrived = MessageArrived;

// connect the client
mqttClient.connect({useSSL:true,onSuccess:Connected, onFailure:ConnectionFailed});




//mqttClient.onMessageArrived =  MessageArrived;
//mqttClient.onConnectionLost = ConnectionLost;
    
}

/*Callback for successful MQTT connection */
function Connected() {
  window.console.log("Connected");
   stringa = 'DOMHOTEL/H001/R333/STATUS/#'
    console.log(stringa)
  
  mqttClient.subscribe(stringa);
  
  MQTT_CONNECTED = true;
  
  
  //if (SUBSCRIBE ) {
  
  //  mqttClient.subscribe('DOMHOTEL/H001/+/STATUS/#');
    
  //  }
}

/*Callback for failed connection*/
function ConnectionFailed(res) {
    window.console.log("Connect failed:" + res.errorMessage);
    MQTT_CONNECTED = false;
    pippo();

}

/*Callback for lost connection*/
function onConnectionLost(res) {
  if (res.errorCode !== 0) {
    window.console.log("Connection lost:" + res.errorMessage);

   pippo();
  }
}



/*Callback for incoming message processing */
function MessageArrived(message) {
    let componente ;
    let valore ;
    let compo;
    let target ;

    console.log("Message arrived ! ----")
    componente = message.destinationName ;
    
    valore     = message.payloadString ;
    compo = componente.substring(componente.lastIndexOf("/")+1,)

    console.log(componente)
    console.log(compo)
    
    console.log(valore)
        
    
    switch(compo) {
        case "TEMP":  
            try {
                target = document.getElementById("temp")
                console.log(target)
                target.innerHTML = valore + "  C°";
            }
            finally {
                break;
            }
        //case "HUM":  
        //    target = document.getElementById("hum")
        //    console.log(target)
        //    target.innerHTML = valore + "  %°";
        //
        //    break;
        case "PLUG":  
            try{
                if (valore == 0 || valore == "0" ){
                    document.getElementById("plug-off").disabled = false;
                    document.getElementById("plug-off").checked = true;
                    document.getElementById("plug-on").disabled = true;
                    document.getElementById("plug-on").checked = false;
                }
                else {
                    document.getElementById("plug-off").disabled = true;
                    document.getElementById("plug-off").checked = false;
                    document.getElementById("plug-on").disabled = false;
                    document.getElementById("plug-on").checked = true;
                    
                }
            }
            finally {
            
                break;
            }
            
        case "LIGTH":  
        
            try {
            
                if (valore == 0 || valore == "0" ){
                    document.getElementById("ligth-off").disabled = false;
                    document.getElementById("ligth-off").checked = true;
                    document.getElementById("ligth-on").disabled = true;
                    document.getElementById("ligth-on").checked = false;
                }
                else {
                    document.getElementById("ligth-off").disabled = true;
                    document.getElementById("ligth-off").checked = false;
                    document.getElementById("ligth-on").disabled = false;
                    document.getElementById("ligth-on").checked = true;
                }
            }
            finally {
            
                break;
            }
        
        case "AC":  
        
            try {
            
                if (valore == 0 || valore == "0" ){
                    document.getElementById("ac-off").disabled = false;
                    document.getElementById("ac-off").checked = true;
                    document.getElementById("ac-on").disabled = true;
                    document.getElementById("ac-on").checked = false;
                }
                else {
                    document.getElementById("ac-off").disabled = true;
                    document.getElementById("ac-off").checked = false;
                    document.getElementById("ac-on").disabled = false;
                    document.getElementById("ac-on").checked = true;
                    
                }
            }
            finally {
            
                break;
            }
    }


}

// Publish a Message
function MessageSend(codice,valore) {

    var message = new Paho.MQTT.Message(valore);
    message.destinationName = codice;
    message.qos = 0;
    message.retained = true;
    
    try {
        mqttClient.send(message);
        send_Ok = true;
    }
    catch {
        send_Ok = false;
        //alert("Send Message Error ...  Retry !")
        console.log("Send Message Error ...  Retry !")
    }

}




function handleClick(myRadio, compo) {
        let selectedValue ;
        selectedValue = myRadio.value;
        
        if (myRadio.dataset.room) {
            roomNumber = myRadio.dataset.room 
        }
        else {
            roomNumber = "001"
        }
        
        console.log(compo + " - " +selectedValue+'  -  '+roomNumber) ;
       
        codice = "DOMHOTEL/H001/R"+roomNumber+"/SET/" + compo
        
        MessageSend(codice, selectedValue )
}

function sendControl(json_data){
  
    console.log(json_data);
    
    // PLUG
    if (json_data.plug == "1") {
        console.log("plug 1")
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/PLUG/START" 
        MessageSend(codice, json_data.plug_start )
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/PLUG/STOP" 
        MessageSend(codice, json_data.plug_stop )
    }
    else if (json_data.plug == "0") {
        console.log("plug 0")

        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/PLUG" 
        console.log(codice)
        console.log(json_data.plug)
        MessageSend(codice, json_data.plug)
    }
    
    // LIGTH
    if (json_data.ligth == "1") {
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/LIGTH/START" 
        MessageSend(codice, json_data.ligth_start )
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/LIGTH/STOP" 
        MessageSend(codice, json_data.ligth_stop )
    }
    else if (json_data.ligth == "0"){
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/LIGTH" 
        MessageSend(codice, json_data.ligth)
        console.log("spengo ligth")
        console.log(codice)
        console.log(json_data.ligth)
    }
    // AC
    if (json_data.ac == "1") {
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/AC/START" 
        MessageSend(codice, json_data.ac_start )
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/AC/STOP" 
        MessageSend(codice, json_data.ac_stop )
    }
    else if (json_data.ac == "0"){
        codice = "DOMHOTEL/H001/R"+json_data.room+"/SET/AC" 
        MessageSend(codice, json_data.ac)
    }
    if (send_Ok) {
        return true;
    }
    else{
        return false;
    }
}   
                   
function delReserve(room_number){
  
    var currentdate = new Date(); 
    var datetime = currentdate.getDate() + "/"
                + (currentdate.getMonth()+1)  + "/" 
                + currentdate.getFullYear() + " "  
                + currentdate.getHours() + ":"  
                + currentdate.getMinutes() 
    var datetime = new Date().today() + " " + new Date().timeNow();
    //alert(datetime)
    
    let response
    response = confirm('Confirm to delete ?')
    
    if(response) {
    
        codice = "DOMHOTEL/H001/R"+room_number+"/SET/PLUG/STOP" 
        MessageSend(codice, datetime)
        codice = "DOMHOTEL/H001/R"+room_number+"/SET/LIGTH/STOP" 
        MessageSend(codice, datetime)
        codice = "DOMHOTEL/H001/R"+room_number+"/SET/AC/STOP" 
        MessageSend(codice, datetime)
        
        if (send_Ok) {
            return true;
        }
        else{
            return false;
        }
    }
    else {
        window.history.back();  
        
    }
}

// For todays date;
Date.prototype.today = function () { 
    return ((this.getDate() < 10)?"0":"") + this.getDate() +"/"+(((this.getMonth()+1) < 10)?"0":"") + (this.getMonth()+1) +"/"+ this.getFullYear();
}

// For the time now
Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes()  ;
}
