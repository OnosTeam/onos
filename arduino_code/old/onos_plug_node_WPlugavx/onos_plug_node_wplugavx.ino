/*
 * O.N.O.S.  arduino WlightVx node  firmware by Marco Rigoni 9-11-16  onos.info@gmail.com 
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

//#include <Vcc.h>


//*********************************************************************************************
// *********** IMPORTANT SETTINGS - YOU MUST CHANGE/CONFIGURE TO FIT YOUR HARDWARE *************
//*********************************************************************************************
#define NETWORKID     100  //the same on all nodes that talk to each other

 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
//#define FREQUENCY     RF69_868MHZ
#define FREQUENCY      RF69_433MHZ
#define ENCRYPTKEY     "sampleEncryptKey" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HCW    true // set to 'true' if you are using an RFM69HCW module
 
//*********************************************************************************************
#define SERIAL_BAUD   115200
 
#define RFM69_CS      10
#define RFM69_IRQ     2
#define RFM69_IRQN    0  // Pin 2 is IRQ 0!
#define RFM69_RST     9


#define ATC_RSSI      -75   //power signal from -30(stronger) to -95(weaker) 
#define targetRSSI    -40
 
int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;



boolean radio_enabled=1;

unsigned long sync_time=0;

char serial_number[13]="WPlugAvx0008";
char node_fw[]="5.26";

int this_node_address=254; //i start with 254

int old_address=254; 

unsigned long get_address_timeout=0;

unsigned long get_decode_time=0;
/*
WPlugAvx node parameter:
  relay1_set_pin     --> the pin where the first relay set coil is connected
  relay1_reset_pin     --> the pin where the first relay set coil is connected

  relay2_set_pin     --> the pin where the second relay set coil is connected
  relay2_reset_pin     --> the pin where the second relay set coil is connected
  main_obj_state    --> the state of the main_obj (turned on "1" ,turned off "0")  will be sent to onos with sync and each time it changes
  time_on       --> total time of the main_obj was on from when the arduino was turned on,will be sent with each sync
  time_from_turn_on --> variable used to store the millis() when the main_obj was turned on.
  time_continuos_on --> seconds since the main_obj is on (if is on now otherwise is 0) 

*/


//////////////////////////////////Start of Standard part to run decodeOnosCmd()//////////////////////////////////
#define rx_msg_lenght 61
int onos_cmd_start_position=-99;  
int onos_cmd_end_position=-99;  
char received_message_type_of_onos_cmd[3];
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;
char received_message_answer[24]="er00_#]";
int received_message_address=0; //must be int..
char filtered_onos_message[rx_msg_lenght+3];
char syncMessage[48];
char str_this_node_address[4];
uint8_t main_obj_selected=0;
uint8_t rx_obj_selected=0;
char progressive_msg_id=48;  //48 is 0 in ascii   //a progressive id to make each message unique
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////

uint8_t radioRetry=3;      //todo: make this changable from serialport
uint8_t radioTxTimeout=20;  //todo: make this changable from serialport
char received_serial_number[13];
# define gateway_address 1
boolean first_sync=1;



unsigned long time_continuos_on=0;
unsigned long time_since_last_sync=0;
unsigned long time_from_turn_on=0;
int timeout_to_turn_off=0;//0=disabled    600; //10 hours    todo   add the possibility to set it from remote

uint8_t skipRadioRxMsg=0;
uint8_t skipRadioRxMsgThreshold=5;

char main_obj_state=0;
//int old_main_obj_state=5;

// node object pinuot// 
int relay1_set_pin=6;    
int relay1_reset_pin=5;
int relay2_set_pin=8;    
int relay2_reset_pin=7;
int obj_button_pin=3;
int obj_led_pin=4; 
//end node object pinuot// 


/*

const float VccExpected   = 3.0;
const float VccCorrection = 2.860/2.92;  // Measured Vcc by multimeter divided by reported Vcc
Vcc vcc(VccCorrection);
static int oldBatteryPcnt = 0;
*/



int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}




boolean changeObjStatus(char obj_number,int status_to_set){
   Serial.print(F("changeObjStatus executed with  status:"));
   Serial.println(status_to_set);

  if (obj_number==0){

    digitalWrite(relay1_set_pin,status_to_set); 
    digitalWrite(relay1_reset_pin,!status_to_set); 
    digitalWrite(relay2_set_pin,status_to_set); 
    digitalWrite(relay2_reset_pin,!status_to_set); 
    digitalWrite(obj_led_pin,status_to_set);
    main_obj_state=status_to_set;
/*
    delay(20);
    digitalWrite(relay1_set_pin,0); 
    digitalWrite(relay1_reset_pin,0); 
    digitalWrite(relay2_set_pin,0); 
    digitalWrite(relay2_reset_pin,0); 
*/
    return(1);
  }




return(0);

}


void composeSyncMessage(){

  Serial.println(F("composeSyncMessage executed"));
  //[S_123ul5.24WPlugAvx000810000x_#]

  if (progressive_msg_id<122){  //122 is z in ascii
    progressive_msg_id=progressive_msg_id+1;
  }
  else{
    progressive_msg_id=48;  //48 is 0 in ascii
  }

  if (main_obj_state==1){
      
    if (time_continuos_on!=0){
      time_from_turn_on=time_from_turn_on+(millis()-time_continuos_on);
      time_since_last_sync=millis();  // to implement...
    }

  }

 // char char_main_obj_state[2];
 // char_main_obj_state[0]=main_obj_state+48;




  float minutes_time_from_turn_on;
 // minutes_time_from_turn_on=2;  //time_from_turn_on/60000; //get minutes from milliseconds


  if( minutes_time_from_turn_on>9999) {//banana todo change it in some way...
    minutes_time_from_turn_on=0;

  }


  char tmp_minutes_time_from_turn_on_array[5];
  char minutes_time_from_turn_on_array[5];
  //strcpy(tmp_minutes_time_from_turn_on_array,"");
  //strcpy(minutes_time_from_turn_on_array,"");

  memset(tmp_minutes_time_from_turn_on_array,0,sizeof(tmp_minutes_time_from_turn_on_array)); //to clear the array
  memset(minutes_time_from_turn_on_array,0,sizeof(minutes_time_from_turn_on_array)); //to clear the array
 
  //itoa (minutes_time_from_turn_on,minutes_time_from_turn_on_array,10);  //convert from int to char array
  //dtostrf  //convert from float to char array
  if (minutes_time_from_turn_on<10){
    dtostrf(minutes_time_from_turn_on,1, 0, tmp_minutes_time_from_turn_on_array);
    strcpy(minutes_time_from_turn_on_array,"000");
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }

  else if (minutes_time_from_turn_on<100){
    dtostrf(minutes_time_from_turn_on,2, 0, tmp_minutes_time_from_turn_on_array);
    strcpy(minutes_time_from_turn_on_array,"00");
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }

  else if (minutes_time_from_turn_on<1000){
    dtostrf(minutes_time_from_turn_on,3, 0, tmp_minutes_time_from_turn_on_array);
    strcpy(minutes_time_from_turn_on_array,"0");
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }

  else if (minutes_time_from_turn_on<10000){
    dtostrf(minutes_time_from_turn_on,4, 0, tmp_minutes_time_from_turn_on_array);
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }



  //snprintf(minutes_time_from_turn_on_array, 5, "%d", minutes_time_from_turn_on); //convert from float to char array

  

  int tmp_number=0;
  //strcpy(str_this_node_address,"");
  memset(str_this_node_address,0,sizeof(str_this_node_address)); //to clear the array
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
  

  //strcpy(syncMessage, "");
  memset(syncMessage,0,sizeof(syncMessage)); //to clear the array
  strcpy(syncMessage, "[S_");
  strcat(syncMessage, str_this_node_address);


  if (first_sync==1 ){
    strcat(syncMessage, "ga");
    strcat(syncMessage, node_fw);
  }
  else{
    strcat(syncMessage, "ul");

  }

 // strcat(syncMessage, "sy");
  strcat(syncMessage, serial_number);
  

    //[S_123ul5.24WPlugAvx000810000x_#]

/*
  if (main_obj_state==0){
    strcat(syncMessage,"0");
  }
  else{
    strcat(syncMessage,"1");
  }
*/
  syncMessage[strlen(syncMessage)]=main_obj_state+48;   //+48 for ascii translation


   Serial.print(F("composeSyncMessage executed with  status:"));
   Serial.println(main_obj_state);


  strcat(syncMessage, minutes_time_from_turn_on_array);
  syncMessage[strlen(syncMessage)]=progressive_msg_id; //put the variable msgid in the array 
  //Serial.println(syncMessage[28]);
  //Serial.println(strlen(syncMessage));
  strcat(syncMessage, "_#]");
  




}




void sendSyncMessage(uint8_t retry,uint8_t timeout=150){

  composeSyncMessage();


  if (first_sync!=1 ){
    syncMessage[6]='u'; //modify the message
    syncMessage[7]='l'; //modify the message
  }


  Serial.println(F(" sendWithRetry sendSyncMessage executed"));
  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage),retry,timeout)) {
    // note that the max delay time is 255..because is uint8_t
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)
    Serial.println(F("sent_sync_message1"));
//    Blink(LED, 50, 3); //blink LED 3 times, 50ms between blinks
    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
  }


}




void getAddressFromGateway(){
   Serial.println(F("getAddressFromGateway executed"));

  //[S_123ga5.24WPlugAvx000810000x_#]

  composeSyncMessage();
  syncMessage[6]='g'; //modify the message to get a address instead of just sync.
  syncMessage[7]='a'; //modify the message to get a address instead of just sync.

  Serial.println(F(" sendWithRetry getAddressFromGateway executed"));

  if (radio.sendWithRetry(gateway_address, syncMessage,strlen(syncMessage),radioRetry,radioTxTimeout)) {
    // note that the max delay time is 255..because is uint8_t
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)



    Serial.println(F("sent_get_address ok"));
    /*
    for (char a=0;a<(35);a=a+1){
      Serial.print(syncMessage[a]);
    }
    Serial.println("end_get_address"); 
    */



    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
  }
  else{
    Serial.println(F(" failed to receive ack from sendWithRetry"));

  }

  syncMessage[6]='u'; //modify the message
  syncMessage[7]='l'; //modify the message

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



void decodeOnosCmd( char *received_message){

 // Serial.println(F("decodeOnosCmd executed"));





      
  get_decode_time=millis();

  memset(received_message_answer,0,sizeof(received_message_answer)); //to clear the array
  strcpy(received_message_answer,"err01_#]");



  if ((received_message[0]=='[')&&(received_message[1]=='S')&&(received_message[2]=='_') ) {
 // the onos cmd was found           [S_001dw06001_#]


    strcpy(received_message_answer,"cmdRx_#]");               


    received_message_type_of_onos_cmd[0]=received_message[6];
    received_message_type_of_onos_cmd[1]=received_message[7];

    received_message_address=(received_message[3]-48)*100+(received_message[4]-48)*10+(received_message[5]-48)*1;


     // int decodetime= millis()-get_decode_time;    
     // Serial.print("decode time01=") ;
     // Serial.println(decodetime) ;
    Serial.print(F("r_address:")) ;
    Serial.println(received_message_address) ;
    if ((received_message_address!=this_node_address)&(received_message_address!=254)) {//onos command for a remote arduino node
      strcpy(received_message_answer,"remote_#]");

      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }

/*
      Serial.print("decode time02=") ;
      Serial.println(millis()-get_decode_time) ;
      get_decode_time=millis();
*/

    //[S_123dw06001_#]
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

 
    //[S_123wb01x_#]
    else if( received_message_type_of_onos_cmd[0]=='w' && received_message_type_of_onos_cmd[1]=='b' ){

/*
      Serial.print("decode time03=") ;
      Serial.println(millis()-get_decode_time) ;
      get_decode_time=millis();
*/


      received_message_value=received_message[9]-48;   
      

      if (received_message_value>1){ 
        Serial.println(F("er0_status_#]"));  
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      rx_obj_selected= (received_message[8])-48;



      if (rx_obj_selected==main_obj_selected){ //first object selected
        strcpy(received_message_answer,"cmdRx_#]"); // just to make something..              

      }
      else{//there is only one main wp object in this wp node
        Serial.println(F("er_obj_number_#]"));  
        strcpy(received_message_answer,"er_obj_number_#]"); 
        return;
      }

/*
      Serial.print("decode time04=") ;
      Serial.println(millis()-get_decode_time) ;
      get_decode_time=millis();
*/
      boolean change_status_ok=0; 
      change_status_ok=changeObjStatus(main_obj_selected,received_message_value);


      if (change_status_ok!=1){
        memset(received_message_answer,0,sizeof(received_message_answer)); //to clear the array
        Serial.println(F("er_chobjstatus_#]"));  
        strcpy(received_message_answer,"er_chobjstatus_#]"); 
        return;

      }





/*
      Serial.print("decode time05=") ;
      Serial.println(millis()-get_decode_time) ;
      get_decode_time=millis();
*/


/*

      digitalWrite(relay1_set_pin,main_obj_state); 
      digitalWrite(relay1_reset_pin,!main_obj_state); 
      digitalWrite(relay2_set_pin,main_obj_state); 
      digitalWrite(relay2_reset_pin,!main_obj_state); 

      delay(100);



      digitalWrite(relay1_set_pin,0); 
      digitalWrite(relay1_reset_pin,0); 
      digitalWrite(relay2_set_pin,0); 
      digitalWrite(relay2_reset_pin,0); 
      

      time_continuos_on=millis();
      while (digitalRead(received_message_second_pin_used)!=received_message_value){
        delay(1);
        if (millis()-time_continuos_on>100){ // if the relay hasn't swiched after 100 ms from command..is broken..
          strcpy(received_message_answer,"err2_relay_#]");
          return;                                
        }

      }

*/
        

      if (time_continuos_on!=0){
        time_from_turn_on=time_from_turn_on+(millis()-time_continuos_on);
      }

      if (main_obj_state==1){
        time_continuos_on=millis();
      }
      else{
        time_continuos_on=0;
      }

      strcpy(received_message_answer,"ok"); 
      return;
    }

      
    //[S_254sa123WPlugAvx0008_#]

    else if( received_message_type_of_onos_cmd[0]=='s' && received_message_type_of_onos_cmd[1]=='a' ){

      received_message_value=(received_message[8]-48)*100+(received_message[9]-48)*10+(received_message[10]-48);


      //todo: use  strstr to compare this and avoid making the copy array char * pch;  pch = strstr (str,"simple"); 
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



   //    todo implement it!
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
      Serial.print(F("i will change radio address to:"));
      Serial.println(this_node_address);
      first_sync=0;
        

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








 } // end of if message start [S_






}// end of decodeOnosCmd()



void checkAndHandleIncomingRadioMsg(){

   
  onos_cmd_start_position=-99;
  onos_cmd_end_position=-99;

  if (radio.receiveDone()){

    skipRadioRxMsg=skipRadioRxMsg+1;

    get_decode_time=millis();
    //print message received to serial
    Serial.print(F(" id:"));
    Serial.println(radio.SENDERID);
    Serial.print((char*)radio.DATA);
    Serial.print("   [RX_RSSI:");Serial.print(radio.RSSI);Serial.print("]");

 
    //check if received message contains Hello World

    //uint8_t message_copy[rx_msg_lenght+1];

    //strcpy(filtered_onos_message,"");
    memset(filtered_onos_message,0,sizeof(filtered_onos_message)); //to clear the array
    Serial.print(F("msg_start:"));

    uint8_t onos_cmd_start_detector=0;
    uint8_t onos_cmd_end_detector=0;
    uint8_t filtered_count=0;  
 
    char tmp_byte=0;
    for (uint8_t counter = 0; counter <= sizeof(radio.DATA); counter++) {

      tmp_byte=radio.DATA[counter];
      
      //message_copy[counter]=radio.DATA[counter]; 
      Serial.print(tmp_byte);

    //[S_001dw06001_#]



      switch (tmp_byte) {
        case '[':{
          onos_cmd_start_detector=1; 
        }
        case 'S':{
          if (onos_cmd_start_detector==1){ 
            onos_cmd_start_detector=2; 
          }
          else{// reset automa
            onos_cmd_start_detector=0;
          }
        }

        case '_':{
          if (onos_cmd_start_detector==2){ 
            onos_cmd_start_detector=0; 
            onos_cmd_start_position=0;

          }
          else{// reset automa
            onos_cmd_start_detector=0;
          }
        }

      } // end switch

      if(onos_cmd_start_position!=-99){ //save the data only if the onos cmd is started
        filtered_onos_message[0]='[';
        filtered_onos_message[1]='S';

        filtered_onos_message[filtered_count]=tmp_byte;  //first time it should be '_'
        filtered_count=filtered_count+1; 






        if (filtered_onos_message[counter]=='_'){//   
          onos_cmd_end_detector=1;
        }
        else{

          if (filtered_onos_message[counter]=='#'){//   
            if (onos_cmd_end_detector==1){
              onos_cmd_end_detector=2;
            }
          }
          else{

            if (filtered_onos_message[counter]==']'){//   
              if (onos_cmd_end_detector==2){
                onos_cmd_end_detector=0;
                onos_cmd_end_position=filtered_count;
                break;
              }
            }
            else{ //reset the automa
              onos_cmd_end_detector=0;
  
            }

          } 


        }








      }    //end  if(onos_cmd_start_position!=-99){ //save the data only if the onos cmd is started


/*
      if (filtered_onos_message[counter]=='['){//   
        onos_cmd_start_detector=1;
      }
      else{

        if (filtered_onos_message[counter]=='S'){//   
          if (onos_cmd_start_detector==1){
            onos_cmd_start_detector=2;
          }
        }
        else{

          if (filtered_onos_message[counter]=='_'){//   
            if (onos_cmd_start_detector==2){
              onos_cmd_start_detector=0;
              onos_cmd_start_position=counter-2;
            }
          }
          else{ //reset the automa
            onos_cmd_start_detector=0;
          }

        } 


      }

*/



    }
    Serial.println(F(":msg_stop"));


    if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){

      Serial.println(F("onos cmd  found-------------------------------"));
      //noInterrupts(); // Disable interrupts    //important for lamp node 
      decodeOnosCmd(filtered_onos_message);

      Serial.print(F("decode time1=")) ;
      Serial.println(millis()-get_decode_time) ;
      get_decode_time=millis();

      if( (received_message_answer[0]=='o')&&(received_message_answer[1]=='k')){//if the message was ok...
      //check if sender wanted an ACK
        if (radio.ACKRequested()){
          radio.sendACK();
          Serial.println(F(" - ACK sent"));
          sync_time=millis();
        }
        //interrupts(); // Enable interrupts

      }
      else{
        Serial.print(F("error in message decode i will not send the ACK,i found:"));
        Serial.print(received_message_answer[0]);
        Serial.print(received_message_answer[1]);
        Serial.print(received_message_answer[2]);
        Serial.print(received_message_answer[3]);
        Serial.println(received_message_answer[4]);

       // checkCurrentRadioAddress(); //if the mesage received is wrong i will check and send a address request if needed becausethe onos gateway will wait a moment after the tranmission failure.

        //interrupts(); // Enable interrupts 
      }

    //interrupts(); // Enable interrupts

    }
    else{
      strcpy(received_message_answer,"nocmd0_#]");
      Serial.print(F("error in message nocmd0_#]"));
      Serial.print(onos_cmd_start_position);
      Serial.println(onos_cmd_end_position);
    }

  
    

  }// end if (radio.receiveDone())


}







void handleButton(){

  if (digitalRead(obj_button_pin)==0) {
    Serial.print(F("obj_button pressed"));

    while (digitalRead(obj_button_pin)==0){ //wait for button release
      delay(280);//todo change it smaller
    }

    changeObjStatus(main_obj_selected,!main_obj_state);  // this will make a not of current state
    sendSyncMessage(radioRetry+2,radioTxTimeout); 


  }


}



void checkCurrentRadioAddress(){


  if (old_address==254){// i have not the proper address yet..



    if (old_address!=this_node_address){//the address has changed and I restart radio to use it
 

      radio.setAddress(this_node_address);
      old_address=this_node_address;
      get_address_timeout=millis();
      Serial.print(F("radio address changed to:"));
      Serial.println(this_node_address);
      sendSyncMessage(radioRetry,radioTxTimeout);


    }


    if ((millis()-get_address_timeout)>5000){ //every 5000 ms
   
      get_address_timeout=millis();

      getAddressFromGateway();  //ask the gateway for a proper address


    }


  }
  else{

    if ((millis()-sync_time)>2000){ //every 5000 ms
   
      sync_time=millis();

      sendSyncMessage(radioRetry,radioTxTimeout);


    }

  }



}

 
void setup() {

  while (!Serial); // wait until serial console is open, remove if not tethered to computer
  noInterrupts(); // Disable interrupts    //important for lamp node

//  pinMode(RFM69_RST, OUTPUT);


  pinMode(relay1_set_pin, OUTPUT);
  pinMode(relay1_reset_pin, OUTPUT);
  pinMode(relay2_set_pin, OUTPUT);
  pinMode(relay2_reset_pin, OUTPUT);
  pinMode(obj_button_pin, INPUT);
  pinMode(obj_led_pin, OUTPUT);

  //while (!Serial); // wait until serial console is open, remove if not tethered to computer
  Serial.begin(SERIAL_BAUD);


  digitalWrite(obj_button_pin, HIGH); //enable pull up resistors


  Serial.println(F("Feather RFM69W Receiver"));


/*  

  WARNING do not uncomment this part or the radio will not work anymore!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  


/*  

  WARNING do not uncomment this part or the radio will not work anymore!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  


  // Hard Reset the RFM module

  digitalWrite(RFM69_RST, LOW);
  delay(50);
  digitalWrite(RFM69_RST, HIGH);
  delay(120);
  digitalWrite(RFM69_RST, LOW);
  delay(120);
  */

  interrupts(); // Enable interrupts

  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)

  radio.encrypt(ENCRYPTKEY);
  


  radio.enableAutoPower(targetRSSI);
 
  Serial.print(F("\nListening at "));
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(F(" MHz"));

  changeObjStatus(0,1);
  delay(300);
  changeObjStatus(0,0);

  Blink(obj_led_pin,100,3);  

  composeSyncMessage();


}
 
void loop() {




  digitalWrite(relay1_set_pin,0); 
  digitalWrite(relay1_reset_pin,0); 
  digitalWrite(relay2_set_pin,0); 
  digitalWrite(relay2_reset_pin,0); 
  handleButton();


  if (skipRadioRxMsg>skipRadioRxMsgThreshold){ //to allow the execution of radio tx , in case there are too many rx query..
    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
    Serial.println(F("I skip the rxradio part once"));
    goto radioTx;


  }



  checkAndHandleIncomingRadioMsg();


radioTx:
 
  radio.receiveDone(); //put radio in RX mode
  Serial.flush(); //make sure all serial data is clocked out before sleeping the MCU

  checkCurrentRadioAddress();


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

