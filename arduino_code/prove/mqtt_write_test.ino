#include <PZEM004Tv30.h>
//#include <UIPEthernet.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>


/* Use software serial for the PZEM
 * Pin 11 Rx (Connects to the Tx pin on the PZEM)
 * Pin 12 Tx (Connects to the Rx pin on the PZEM)
*/

#define CLIENT_ID       "Watt_Meter0"
#define TOPIC           "Watt_Meter0_values"


#define PUBLISH_DELAY   5000

uint8_t mac[6] = {0x00,0x01,0x02,0x03,0x04,0x05};
IPAddress mqttServer(192,168,1,110);


void callback(char* topic, byte* payload, unsigned int length) {
  // handle message arrived
}

EthernetClient ethClient;
PubSubClient mqttClient(mqttServer, 1883, callback, ethClient);

void sendData(float power,float current, float energy, float voltage, float power_factor,float frequency) {

  Serial.print(F("Sending mqtt data "));
/*
  char msgBuffer[120];
  
  msgBuffer[0] = '{';
  strcat(msgBuffer, "\"Watt\":");
  strcat(msgBuffer,  dtostrf(power, 4, 2, msgBuffer));
  strcat(msgBuffer, ",");

  strcat(msgBuffer, "\"Ampere\":");
  strcat(msgBuffer,  dtostrf(current, 4, 2, msgBuffer));
  strcat(msgBuffer, ",");  

  strcat(msgBuffer, "\"Wh\":");
  strcat(msgBuffer,  dtostrf(energy, 10, 2, msgBuffer));
  strcat(msgBuffer, ",");  
  
  strcat(msgBuffer, "\"Volt\":");
  strcat(msgBuffer,  dtostrf(voltage, 5, 2, msgBuffer));
  strcat(msgBuffer, ",");  
  
  strcat(msgBuffer, "\"Pf\":");
  strcat(msgBuffer,  dtostrf(power_factor, 3, 2, msgBuffer));
  strcat(msgBuffer, ",");  

  strcat(msgBuffer, "\"Hz\":");
  strcat(msgBuffer,  dtostrf(frequency, 3, 1, msgBuffer));
  strcat(msgBuffer, ",");  
  uint8_t  tmp_len = strlen(msgBuffer);
  msgBuffer[tmp_len + 1] = '\0'; //close the string
*/    
//  if(mqttClient.connect(CLIENT_ID)) {
  if (mqttClient.connect("arduinoClient", "mqtt-onos", "onosmqtt1234")) {

    Serial.print(F(" mqtt connected"));
    //mqttClient.publish(TOPIC, msgBuffer);
    mqttClient.publish("outTopic","hello world");

    
  }
}



//PZEM004Tv30 pzem(11, 12);

void setup() {
  Serial.begin(115200);

  // setup ethernet communication using DHCP
  if(Ethernet.begin(mac) == 0) {
    Serial.println(F("Unable to configure Ethernet using DHCP"));
    for(;;);
  }
  Serial.println(F("Ethernet configured via DHCP"));
  Serial.print(F("IP: "));
  Serial.println(Ethernet.localIP());
  Serial.println();

  // setup mqtt client
  mqttClient.setClient(ethClient);
  mqttClient.setServer(mqttServer, 1883);
 // Serial.println(F("MQTT client configured"));
}

void loop() {

  /*
    float voltage = pzem.voltage();
    
    if( !isnan(voltage) ){
        Serial.print(F("Voltage: ")); Serial.print(voltage); Serial.println(F("V"));
    } else {
        Serial.println("Error_voltage");
    }
    
    float current = pzem.current();
    
    if( !isnan(current) ){
        Serial.print(F("Current: ")); Serial.print(current); Serial.println(F("A"));
    } else {
        Serial.println(F("Er_I"));
    }
    

    float power = pzem.power();
    if( !isnan(power) ){
        Serial.print(F("Pwr: ")); Serial.print(power); Serial.println(F("W"));
    } else {
        Serial.println("Er_PWR");
    }

    float energy = pzem.energy();
    if( !isnan(energy) ){
        Serial.print(F("Energy: ")); Serial.print(energy,3); Serial.println(F("kWh"));
    } else {
        Serial.println(F("Er_en"));
    }

    float frequency = pzem.frequency();
    
    if( !isnan(frequency) ){
        Serial.print(F("Freq: ")); Serial.print(frequency, 1); Serial.println(F("Hz"));
    } else {
        Serial.println(F("Error_F"));
    }

    float pf = pzem.pf();
    
    if( !isnan(pf) ){
        Serial.print(F("PF: ")); Serial.println(pf);
    } else {
        Serial.println(F("Error_pwr_f"));
    }

    Serial.println();
  // it's time to send new data?
    //sendData(power,current,energy,voltage,pf,frequency);

*/
    
    sendData(11,12,13,14,15,16);


  mqttClient.loop();
    
    delay(2000);
}

