/*
 * O.N.O.S.  arduino WlightSS node  firmware by Marco Rigoni 27-8-16  onos.info@gmail.com 
 * more info on www.myonos.com 
 *
 */


/*


/*
*                  Arduino      RFM69W
*                  GND----------GND   (ground in)
*                  3V3----------3.3V  (3.3V in)
*  interrupt 0 pin D2-----------DIO0  (interrupt request out)
*              pin D9-----------RST   (radio module reset)   
*           SS pin D10----------NSS   (chip select in)
*          SCK pin D13----------SCK   (SPI clock in)
*         MOSI pin D11----------MOSI  (SPI Data in)
*         MISO pin D12----------MISO  (SPI Data out)


*/




/* RFM69 library and code by Felix Rusu - felix@lowpowerlab.com
// Get libraries at: https://github.com/LowPowerLab/
// Make sure you adjust the settings in the configuration section below !!!
// **********************************************************************************
// Copyright Felix Rusu, LowPowerLab.com
// Library and code by Felix Rusu - felix@lowpowerlab.com
// **********************************************************************************
// License
// **********************************************************************************
// This program is free software; you can redistribute it 
// and/or modify it under the terms of the GNU General    
// Public License as published by the Free Software       
// Foundation; either version 3 of the License, or        
// (at your option) any later version.                    
//                                                        
// This program is distributed in the hope that it will   
// be useful, but WITHOUT ANY WARRANTY; without even the  
// implied warranty of MERCHANTABILITY or FITNESS FOR A   
// PARTICULAR PURPOSE. See the GNU General Public        
// License for more details.                              
//                                                        
// You should have received a copy of the GNU General    
// Public License along with this program.
// If not, see <http://www.gnu.org/licenses></http:>.
//                                                        
// Licence can be viewed at                               
// http://www.gnu.org/licenses/gpl-3.0.txt
//
// Please maintain this license information along with authorship
// and copyright notices in any redistribution of this code
// **********************************************************************************/
 
#include <RFM69.h>    //get it here: https://www.github.com/lowpowerlab/rfm69
#include <SPI.h>
#include <RFM69_ATC.h> 
#include <EEPROM.h>

//*********************************************************************************************
// *********** IMPORTANT SETTINGS - YOU MUST CHANGE/CONFIGURE TO FIT YOUR HARDWARE *************
//*********************************************************************************************
#define NETWORKID     100  //the same on all nodes that talk to each other

 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
//#define FREQUENCY     RF69_868MHZ
#define FREQUENCY      RF69_433MHZ
#define ENCRYPTKEY     "sampleEncryptKey" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HCW    false // set to 'true' if you are using an RFM69HCW module
 
//*********************************************************************************************
#define SERIAL_BAUD   115200
 
#define RFM69_CS      10
#define RFM69_IRQ     2
#define RFM69_IRQN    0  // Pin 2 is IRQ 0!
#define RFM69_RST     3

#define LED           5  // onboard blinky

#define ATC_RSSI      -75   //power signal from -30(stronger) to -95(weaker) 
#define targetRSSI    -40
 
int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;



boolean radio_enabled=1;

unsigned long sync_time=0;

char serial_number[13]="WLightSA0005";

char node_fw[]="5.13";

int this_node_address=254; //i start with 254

int old_address=254; 

unsigned long get_address_timeout=0;


/*
WLightSS node parameter:
  relay_pin     --> the pin where the relay coil is connected
  relay_check_pin-->the pin connected to the relay that tell the node if the relay is on or off
  photoresistor_pin  
  lux_threshold --> a threshold the user can set to turn on the light if this node receive a selective command like: setLightif..
  lux_value     --> the value readed from the photoresistence , this value will be sent with each sync
  lamp_state    --> the state of the lamp (turned on "1" ,turned off "0")  will be sent to onos with sync and each time it changes
  lamp_mode     --> the lamp mode..0 is standard,2 is blinking_slow,3 is blinking_fast,4 is auto_turn_on_when_dark.
                    will be readed from eeprom at startup. 
  time_on       --> total time of the lamp was on from when the arduino was turned on,will be sent with each sync
  persons_count --> total number of persons in the room, for future use..if persons >0 and lux>lux_threshold turn on lamp. 
  old_persons_count-->previous value of persons_count
  time_from_turn_on --> variable used to store the millis() when the lamp was turned on.
  time_continuos_on --> seconds since the lamps is on (if is on now otherwise is 0) 
  timeout_to_turn_off-->   if time_continuos_on> timeout_to_turn_off  the lamp will be turned off (default is 10 hours)
  temperature        --> temperature from the sensor 

*/


//////////////////////////////////Start of Standard part to run decodeOnosCmd()//////////////////////////////////
#define rx_msg_lenght 61
int onos_cmd_start_position=-99;  
int onos_cmd_end_position=-99;  
char received_message_type_of_onos_cmd[3];
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;
char received_message_answer[rx_msg_lenght+6]="er00_#]";
int received_message_address=0; //must be int..
char filtered_onos_message[rx_msg_lenght+3];
char syncMessage[28];
char str_this_node_address[4];
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////


char received_serial_number[13];
# define gateway_address 1



unsigned long time_continuos_on=0;
unsigned long time_from_turn_on=0;

int lux_threshold=0;
int lux_value=0;
boolean lamp_state=0;

int relay_pin=7;
int relay_check_pin=8;
int photoresistor_pin=A0;





int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}







void composeSyncMessage(){


  //[S_001um3.05ProminiS0001000_#] 
//   example:   [S_001um3.05ProminiS00010167123_#]     #lux=167  lamp is at 0 , 123 minutes on since boot  
  if (lamp_state==1){
      
    if (time_continuos_on!=0){
      time_from_turn_on=time_from_turn_on+(millis()-time_continuos_on);
    }

  }

  char char_lamp_state[2];
  char_lamp_state[0]=lamp_state+48;


  lux_value=analogRead(photoresistor_pin);

  char lux_value_array[4];

  ltoa(lux_value,lux_value_array,4);  //convert from int to char array


  int minutes_time_from_turn_on;
  minutes_time_from_turn_on=time_from_turn_on/60000; //get minutes from milliseconds

  char minutes_time_from_turn_on_array[4];
 
  itoa (minutes_time_from_turn_on,minutes_time_from_turn_on_array,4);  //convert from int to char array

  
  int tmp_number=0;
  strcpy(str_this_node_address,"");

  str_this_node_address[0]='0';
  str_this_node_address[1]='0';
  str_this_node_address[2]='0';

  if (this_node_address>99){
    str_this_node_address[0]=(this_node_address/100)+48;
    tmp_number=this_node_address%100;
    str_this_node_address[1]=(tmp_number/10)+48;
    tmp_number=this_node_address%10; 
    str_this_node_address[2]=tmp_number+48;

  }

  else if (this_node_address>9){
    str_this_node_address[1]=(tmp_number/10)+48;
    tmp_number=this_node_address%10; 
    str_this_node_address[2]=tmp_number+48;

  }
  else{ 
    str_this_node_address[2]=this_node_address+48;
  }
  

  strcpy(syncMessage, "");
  strcpy(syncMessage, "[S_");
  strcat(syncMessage, str_this_node_address);
  strcat(syncMessage, "um");
  strcat(syncMessage, node_fw);
  strcat(syncMessage, serial_number);
  strcat(syncMessage, char_lamp_state);
  strcat(syncMessage, lux_value_array);
  strcat(syncMessage, minutes_time_from_turn_on_array);
  strcat(syncMessage, "_#]");

/*
  for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
    Serial.print(syncMessage[pointer]);
    if (pointer<2){
      continue;
    }

    if ((syncMessage[pointer-2]=='_')&&(syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ) {//  
        break;
      }
    }   
    Serial.print('\n'); 

*/

}




void sendSyncMessage(){




  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage),3,700)) {
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)
    Serial.println("sent_sync_message");
    Blink(LED, 50, 3); //blink LED 3 times, 50ms between blinks
  }


}




void getAddressFromGateway(){
   Serial.println("getAddressFromGateway executed");

  //[S_001ga3.05ProminiS0001_#]


  syncMessage[6]='g'; //modify the message to get a address instead of just sync.
  syncMessage[7]='a'; //modify the message to get a address instead of just sync.

  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage),3,700)) {
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)
    Serial.println("sent_get_address");
    Blink(LED, 50, 3); //blink LED 3 times, 50ms between blinks
  }

  syncMessage[6]='s'; //modify the message to get a address instead of just sync.
  syncMessage[7]='y'; //modify the message to get a address instead of just sync.

  //decode message

/*
  if (radio.receiveDone())
  {
    //print message received to serial
    Serial.print('[');Serial.print(radio.SENDERID);Serial.print("] ");
    Serial.print((char*)radio.DATA);
    Serial.print("   [RX_RSSI:");Serial.print(radio.RSSI);Serial.print("]");
 



    //check if received message contains address
    //[S_123sa3.05ProminiS0001_#]
   
    if( (strstr((char *)radio.DATA[6],'s'))&&(strstr((char *)radio.DATA[7],'a') ) )
    {
      //check if sender wanted an ACK
      if (radio.ACKRequested())
      {
        radio.sendACK();
        Serial.println(" - ACK sent");
      }
      Blink(LED, 40, 3); //blink LED 3 times, 40ms between blinks
    }  
  }
 
*/

  radio.receiveDone(); //put radio in RX mode
   

}



void decodeOnosCmd(const char *received_message){
/*
  Serial.println(F("decodeOnosCmd executed"));

  Serial.println(received_message[0]);
  Serial.println(received_message[1]);
  Serial.println(received_message[2]);
  Serial.println(received_message[3]);
  Serial.println(received_message[4]);
  Serial.println(received_message[5]);
  Serial.println(received_message[6]);

*/

  strcpy(received_message_answer,"err01_#]");



  if ((received_message[0]=='[')&&(received_message[1]=='S')&&(received_message[2]=='_') ) {
 // the onos cmd was found           [S_001dw06001_#]


    strcpy(received_message_answer,"cmdRx_#]");               


    received_message_type_of_onos_cmd[0]=received_message[6];
    received_message_type_of_onos_cmd[1]=received_message[7];

    received_message_address=(received_message[3]-48)*100+(received_message[4]-48)*10+(received_message[5]-48)*1;


         

    if (received_message_address!=this_node_address) {//onos command for a remote arduino node
      strcpy(received_message_answer,"remote_#]");

      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


    //[S_001dw06001_#]
    if ( received_message_type_of_onos_cmd[0]=='d' && received_message_type_of_onos_cmd[1]=='w' ){

      received_message_value=received_message[12]-48;
      if (received_message_value>1){ 
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;

      pinMode(received_message_first_pin_used, OUTPUT); 
      digitalWrite(received_message_first_pin_used, received_message_value); 
      strcpy(received_message_answer,"ok");
      return;
    }
    
    //[S_001aw06125_#]
    else if( received_message_type_of_onos_cmd[0]=='a' && received_message_type_of_onos_cmd[1]=='w' ){
 
      received_message_value=(received_message[10]-48)*100+(received_message[11]-48)*10+(received_message[12]-48)*1;

      if ((received_message_value<0)||(received_message_value>255)){ //status check
        received_message_value=0;
      //Serial.println(F("onos_cmd_value_error"));  
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
      analogWrite(received_message_first_pin_used, received_message_value); 
      strcpy(received_message_answer,"ok");
      return;
    } 

 
    //[S_001sr04051_#] 
    else if( received_message_type_of_onos_cmd[0]=='s' && received_message_type_of_onos_cmd[1]=='r' ){

      received_message_value=received_message[12]-48;      

      if (received_message_value>1){ 
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
      received_message_second_pin_used=((received_message[10])-48)*10+(  (received_message[11])-48)*1;



      if (received_message_first_pin_used!=relay_pin){ 
        strcpy(received_message_answer,"er_relay_pin_#]"); 
        return;
      }

      if (received_message_first_pin_used!=relay_check_pin){ 
        strcpy(received_message_answer,"er_check_pin_#]"); 
        return;
      }



      digitalWrite(received_message_first_pin_used,received_message_value); 
      
      time_continuos_on=millis();
      while (digitalRead(received_message_second_pin_used)!=received_message_value){
        delay(1);
        if (millis()-time_from_turn_on>100){ // if the relay hasn't swiched after 100 ms from command..is broken..
          strcpy(received_message_answer,"err2_relay_#]");
          return;                                
        }

      }
        
      EEPROM.write(20, received_message_value);
      if (time_continuos_on!=0){
        time_from_turn_on=time_from_turn_on+(millis()-time_continuos_on);
      }

      if (received_message_value==1){

        time_continuos_on=millis();
      }
      else{
        time_continuos_on=0;


      }

      //note to set a relay you have to transmit before the control pin and after the check pin
      delay(100);
      strcpy(received_message_answer,"ok"); 
      return;
    }


    //[S_254sa123WLightSS0003_#]

    else if( received_message_type_of_onos_cmd[0]=='s' && received_message_type_of_onos_cmd[1]=='a' ){

      received_message_value=(received_message[8]-48)*100+(received_message[9]-48)*10+(received_message[10]-48);

      received_serial_number[0]= received_message[11];
      received_serial_number[1]= received_message[12];
      received_serial_number[2]= received_message[13];
      received_serial_number[3]= received_message[14];
      received_serial_number[4]= received_message[15];
      received_serial_number[5]= received_message[16]; 
      received_serial_number[6]= received_message[17];
      received_serial_number[7]= received_message[18];
      received_serial_number[8]= received_message[19];
      received_serial_number[9]= received_message[20];
      received_serial_number[10]= received_message[21]; 
      received_serial_number[11]= received_message[22];




      if (strcmp(received_serial_number,serial_number)!=0) {//onos command not for this  node
        strcpy(received_message_answer,"er1_sn_#]"); 
        return;
      } 


      if ((received_message_value<0)||(received_message_value>254)){ //status check
        received_message_value=0;
      //Serial.println(F("onos_cmd_value_error"));  
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }


      this_node_address=received_message_value;
      strcpy(received_message_answer,"ok");
      Serial.print("i will change radio address to:");
      Serial.println(this_node_address);

    }

    
/*
    Serial.print(F("onos_cmd:"));
    Serial.println(received_message_type_of_onos_cmd);



    Serial.println(F("pin_used:"));
    Serial.println(received_message_first_pin_used);
    Serial.println(F("pin_used2:"));
    Serial.println(received_message_second_pin_used);

    Serial.print(F("message_value:"));
    Serial.println(received_message_value);


    
*/








 } // end of if message start with onos_   






}// end of decodeOnosCmd()




 
void setup() {

  pinMode(relay_pin, OUTPUT); 
  pinMode(relay_check_pin, INPUT); 
  digitalWrite(relay_check_pin,1); //set pull up resistors




  while (!Serial); // wait until serial console is open, remove if not tethered to computer
  Serial.begin(SERIAL_BAUD);
 
  Serial.println("Feather RFM69W Receiver");
  
  // Hard Reset the RFM module
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, HIGH);
  delay(100);
  digitalWrite(RFM69_RST, LOW);
  delay(100);
  
  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)

  radio.encrypt(ENCRYPTKEY);
  
  pinMode(LED, OUTPUT);

  radio.enableAutoPower(targetRSSI);
 
  Serial.print("\nListening at ");
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(" MHz");
  
  composeSyncMessage();


}
 
void loop() {


  //check if something was received (could be an interrupt from the radio)
  
  if (radio.receiveDone()){
    //print message received to serial
    Serial.print('[');Serial.print(radio.SENDERID);Serial.print("] ");
    Serial.print((char*)radio.DATA);
    Serial.print("   [RX_RSSI:");Serial.print(radio.RSSI);Serial.print("]");

 
    //check if received message contains Hello World

    uint8_t message_copy[rx_msg_lenght+1];

    strcpy(filtered_onos_message,"");

    for (uint8_t counter = 0; counter <= rx_msg_lenght; counter++) {
      filtered_onos_message[counter]=radio.DATA[counter];
      message_copy[counter]=radio.DATA[counter]; 
      Serial.println(filtered_onos_message[counter]);

    //[S_001dw06001_#]
      if (counter<2){
        continue;
      }
      if ( (filtered_onos_message[counter-2]=='[')&&(filtered_onos_message[counter-1]=='S')&&(filtered_onos_message[counter]=='_')  ){//   
        Serial.println("cmd start found-------------------------------");
        onos_cmd_start_position=counter-2;
      }


      if( (filtered_onos_message[counter-2]=='_')&&(filtered_onos_message[counter-1]=='#')&&(filtered_onos_message[counter]==']')  ){//   
        Serial.println("cmd end found-------------------------------");
        onos_cmd_end_position=counter-2;
        break;// now the message has ended
      }


    }



    if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){
      Serial.println("onos cmd  found-------------------------------");
      decodeOnosCmd(filtered_onos_message);

      if( (received_message_answer[0]=='o')&&(received_message_answer[1]=='k')){//if the message was ok...
      //check if sender wanted an ACK
        if (radio.ACKRequested()){
          radio.sendACK();
          Serial.println(" - ACK sent");
        }

      }
      else{
        Serial.println("error in message decode i will not send the ACK");
      }



    }
    else{
      strcpy(received_message_answer,"nocmd0_#]");
      Serial.println("error in message nocmd0_#]");
    }

  


     // Blink(LED, 40, 3); //blink LED 3 times, 40ms between blinks
    

  }
 
  radio.receiveDone(); //put radio in RX mode
  Serial.flush(); //make sure all serial data is clocked out before sleeping the MCU





  if (old_address==254){// i have not the proper address yet..



    if (old_address!=this_node_address){//the address has changed and i restart radio to use it
 

      radio.setAddress(this_node_address);
      old_address=this_node_address;
      get_address_timeout=millis();
      old_address=this_node_address;
      Serial.print("radio address changed to:");
      Serial.println(this_node_address);
      composeSyncMessage();
      sendSyncMessage();


    }


    if ((millis()-get_address_timeout)>5000){ //every 5000 ms
   
      get_address_timeout=millis();

      getAddressFromGateway();  //ask the gateway for a proper address


    }


  }

  else if ((millis()-sync_time)>500){ //every 5000 ms
   
   
    sync_time=millis();

    composeSyncMessage();

    sendSyncMessage();


  }





}//END OF LOOP()

void Blink(byte PIN, byte DELAY_MS, byte loops)
{
  for (byte i=0; i<loops; i++)
  {
    digitalWrite(PIN,HIGH);
    delay(DELAY_MS);
    digitalWrite(PIN,LOW);
    delay(DELAY_MS);
  }
}

