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




PZEM004Tv30 pzem(9, 10);

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

/*
void sendData(char sensor_number, float power, float current, float energy, float voltage, float power_factor, float frequency) {




  Serial.print(F("Sending mqtt data "));
  Serial.print(F("sensor_number:"));
  Serial.println(sensor_number);


  char msgBuffer[60];
  uint8_t  tmp_len = strlen(msgBuffer);
  memset(msgBuffer,0,sizeof(msgBuffer)); //to clear the array

  strcpy(msgBuffer, "{");

  strcat(msgBuffer, (sensor_number=='1') ? "\"W1\":" : "\"W2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(power,4,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  
  strcat(msgBuffer, (sensor_number=='1') ? "\"A1\":" : "\"A2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(current,4,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");

  
  strcat(msgBuffer, (sensor_number=='1') ? "\"Wh1\":" : "\"Wh2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(energy,8,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");


  strcat(msgBuffer, (sensor_number=='1') ? "\"V1\":" : "\"V2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(voltage,5,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");

  strcat(msgBuffer, (sensor_number=='1') ? "\"Pf1\":" : "\"Pf2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(voltage,3,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  
  strcat(msgBuffer, (sensor_number=='1') ? "\"Hz1\":" : "\"Hz2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(voltage,3,1, &msgBuffer[tmp_len]);
 
  

  strcat(msgBuffer, "}");
  tmp_len = strlen(msgBuffer);
  msgBuffer[tmp_len + 1] = '\0'; //close the string

  
//  if(mqttClient.connect(CLIENT_ID)) {
  if (mqttClient.connect("arduinoClient", "mqtt-onos", "onosmqtt1234")) {

    Serial.println(F(" mqtt connected"));
    //mqttClient.publish("outTopic2", "work");

    mqttClient.publish("MqttPzWhMeter0000,", msgBuffer);
    //mqttClient.publish("MqttPzemWM000","hello world");

    
  }
}
*/

void sendAllData(float power1,float power2, float current1, float current2, float energy1, float energy2, float voltage1,
                 float voltage2, float power_factor1, float power_factor2, float frequency1, float frequency2) {

/*
MqttPzemWM000 b'{"W2":11.10,"A2":12.20,"Wh2":   13.30,"V2":14.40,"Pf2":14.40,"Hz2":14.4,}'
zigbee2mqtt/0x00158d00040aaf3e b'{"battery":100,"voltage":3045,"contact":true,"linkquality":134}'

*/


  Serial.print(F("Sending mqtt data "));


  char msgBuffer[180];
  uint8_t  tmp_len = strlen(msgBuffer);
  memset(msgBuffer,0,sizeof(msgBuffer)); //to clear the array

  strcpy(msgBuffer, "{");

  strcat(msgBuffer,"\"W1\":");
  tmp_len = strlen(msgBuffer);
  dtostrf(power1,4,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer,"\"W2\":");
  tmp_len = strlen(msgBuffer);
  dtostrf(power2,4,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer, "\"A1\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(current1,4,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");

  strcat(msgBuffer, "\"A2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(current2,4,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer, "\"Wh1\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(energy1,8,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");

  strcat(msgBuffer, "\"Wh2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(energy2,8,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");

  strcat(msgBuffer, "\"V1\":" ); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(voltage1,5,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer, "\"V2\":" ); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(voltage2,5,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer, "\"Pf1\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(power_factor1,3,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer, "\"Pf2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(power_factor2,3,2, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");
  
  strcat(msgBuffer, "\"Hz1\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(frequency1,3,1, &msgBuffer[tmp_len]);
  strcat(msgBuffer, ",");

  strcat(msgBuffer, "\"Hz2\":"); //(condition) ? optionA : optionB; if condition is true return optionA...
  tmp_len = strlen(msgBuffer);
  dtostrf(frequency2,3,1, &msgBuffer[tmp_len]);


  strcat(msgBuffer, "}");
  tmp_len = strlen(msgBuffer);
  msgBuffer[tmp_len + 1] = '\0'; //close the string

  
//  if(mqttClient.connect(CLIENT_ID)) {
  if (mqttClient.connect("arduinoClient", "mqtt-onos", "onosmqtt1234")) {

    Serial.println(F(" mqtt connected"));
    //mqttClient.publish("outTopic2", "work");

    mqttClient.publish("MqttPzWhMeter0000,", msgBuffer);
    //mqttClient.publish("MqttPzemWM000","hello world");

    
  }
}


void loop() {

  

    

    float power1 = pzem.power();
    if( !isnan(power1) ){
        Serial.print(F("Pwr: ")); Serial.print(power1); Serial.println(F("W"));
    } else {
        power1 = 999;
        Serial.println("Er_PWR");
    }

    float energy1 = pzem.energy();
    if( !isnan(energy1) ){
        Serial.print(F("Energy: ")); Serial.print(energy1,3); Serial.println(F("kWh"));
    } else {
        energy1 = 999;
        Serial.println(F("Er_en"));
    }
    
    float voltage1 = pzem.voltage();
    
    if( !isnan(voltage1) ){
        Serial.print(F("Voltage: ")); Serial.print(voltage1); Serial.println(F("V"));
    } else {
        voltage1 = 999;
        Serial.println("Error_voltage");
    }
    
    float current1 = pzem.current();
    
    if( !isnan(current1) ){
        Serial.print(F("Current: ")); Serial.print(current1); Serial.println(F("A"));
    } else {
        current1 = 999;
        Serial.println(F("Er_I"));
    }
    float frequency1 = pzem.frequency();
    
    if( !isnan(frequency1) ){
        Serial.print(F("Freq: ")); Serial.print(frequency1, 1); Serial.println(F("Hz"));
    } else {
        frequency1 = 999;
        Serial.println(F("Error_F"));
    }

    float pf1 = pzem.pf();
    
    if( !isnan(pf1) ){
        Serial.print(F("PF: ")); Serial.println(pf1);
    } else {
        pf1 = 999;
        Serial.println(F("Error_pwr_f"));
    }

    Serial.println();
  // it's time to send new data?
    //sendData(power,current,energy,voltage,pf,frequency);

    
  //sendData('1',11.1,12.2,13.3,14.4,15.5,16.6);

  //sendData('2',11.1,12.2,13.3,14.4,15.5,16.6);


  
  sendAllData(power1,12.2,current1,14.4,energy1,16.6,voltage1,18.8,pf1,20.0,frequency1,22.2);



  mqttClient.loop();
    
  delay(500);
}
