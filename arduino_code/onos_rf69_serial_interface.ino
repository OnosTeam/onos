



/*
 * O.N.O.S.  arduino serial gateway  firmware by Marco Rigoni 27-8-16  onos.info@gmail.com 
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
#include <OnosMsg.h>
//*********************************************************************************************
// *********** IMPORTANT SETTINGS - YOU MUST CHANGE/ONFIGURE TO FIT YOUR HARDWARE *************
//*********************************************************************************************
#define NETWORKID     100  // The same on all nodes that talk to each other
 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
#define FREQUENCY     RF69_868MHZ
//#define FREQUENCY     RF69_433MHZ
#define INITENCRYPTKEY     "onosEncryptKey00" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HCW   true // set to 'true' if you are using an RFM69HCW module
 
//*********************************************************************************************
#define SERIAL_BAUD   115200
 
#define RFM69_CS      10
#define RFM69_IRQ     2
#define RFM69_IRQN    0  // Pin 2 is IRQ 0!
#define RFM69_RST     9
 
 
#define ATC_RSSI      -75   //power signal from -30(stronger) to -95(weaker) 
#define targetRSSI    -40
 
//#define remote_node   //tell the compiler that this is a remote node
#define local_node      //tell the compiler that this is a local node



int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;
 






unsigned long sync_time=0;

char serial_number[13]="ProminiS0001";

char node_fw[]="5.26";
char encript_key[17]=INITENCRYPTKEY;  //todo read it from eeprom

int this_node_address=1; //must be int..

volatile int old_address=254; 

unsigned long get_address_timeout=0;

unsigned long timeout;

boolean first_sync=0; //tell the node if the first sync was made ,not used here


//////////////////////////////////Start of Standard part to run decodeOnosCmd()//////////////////////////////////
#define rx_msg_lenght 61
int onos_cmd_start_position=-99;  
int onos_cmd_end_position=-99;  
char received_message_type_of_onos_cmd[3];
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;
char decoded_uart_answer[24]="er00_#]";
volatile char decoded_radio_answer[24]="er00_#]";
int received_message_address=0; //must be int..
volatile char filtered_uart_message[rx_msg_lenght+3];
volatile char filtered_radio_message[rx_msg_lenght+3];
volatile char syncMessage[28];
volatile char str_this_node_address[4];
uint8_t main_obj_selected=0;
uint8_t rx_obj_selected=0;
volatile char progressive_msg_id=48;  //48 is 0 in ascii   //a progressive id to make each message unique
volatile char received_serial_number[13];
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////
// node object pinuot//

// define object numbers to use in the pin configuration
#define relay1  0
#define relay2  1
#define relay3  2
#define relay4  3
#define button  4
#define led     5
const uint8_t number_of_total_objects=7;      // 7 because there are 6 elements + a null 

uint8_t node_obj_pinout[number_of_total_objects];  // 6  objects 4 relay 1 button and a led  made 7 to store the last element as void for array in c..
uint8_t node_obj_status[number_of_total_objects];  // 6  objects 4 relay 1 button and a led  made 7 to store the last element as

//end node object pinuot, continue in setup() // 

OnosMsg OnosMsgHandler=OnosMsg();  //create the OnosMsg object


uint8_t radioRetry=3;      //todo: make this changable from serialport
uint8_t radioTxTimeout=70;  //todo: make this changable from serialport
uint8_t uartPriority=0;
uint8_t radioPriority=0;


volatile int tmp_number;
volatile uint8_t counter;
volatile uint8_t pointer;



char data_from_serial[rx_msg_lenght+5];
boolean enable_answer_back=0;
boolean message_to_decode_avaible=0;
boolean serial_msg_to_decode_is_avaible=0;
boolean radio_msg_to_decode_is_avaible=0;


uint8_t skipUartRxMsg=0;

int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}




void composeSyncMessage(){

  //[S_001sy3.05ProminiS0001_#] 

  tmp_number=0;
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
    strcat(syncMessage, "sy");

  }

  strcat(syncMessage, serial_number);
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

void makeSyncMessage(){

  //[S_001sy3.05ProminiS0001_#] 
  

  for (pointer = 0; pointer <= rx_msg_lenght; pointer++) {
    Serial.print(syncMessage[pointer]);
    if (pointer<2){
      continue;
    }

    if ((syncMessage[pointer-2]=='_')&&(syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ) {//  
        break;
      }
    }   
    Serial.print('\n'); 
    Serial.flush(); //make sure all serial data is clocked out ,waiting until is done


}




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



void serialEvent() { 

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */

  serial_msg_to_decode_is_avaible=checkAndReceiveSerialMsg();
  


}


boolean checkAndReceiveSerialMsg(){







/*
  timeout=millis()+50;
  bitClear(EIMSK,RFM69_IRQ); //disable only rfm69 interrupt

  while (millis()<timeout){ //wait to get serial data from serial interrupt without rfm69 interrupt interference

    delayMicroseconds(10);
  }
  bitSet(EIMSK,RFM69_IRQ);  //resable  rfm69 interrupt

*/

  counter=0;
  message_to_decode_avaible=0;
  timeout=millis()+200;
  onos_cmd_start_position=-99;  
  onos_cmd_end_position=-99;  
  memset(data_from_serial,0,sizeof(data_from_serial)); //to clear the array

  while (Serial.available() > 0) {
    
    enable_answer_back=1;
  // Serial.println(F("im"));
   //Serial.println(counter);
   // read the incoming byte:
    //if (counter==0){
    delayMicroseconds(210);//210 the serial doesnt work without this delay... to change if you change baud rate (increase with lower baud rate)
    //}  
    data_from_serial[counter] =(char) Serial.read();

    if ( millis()>timeout){
      Serial.println(F("[S_serial_timeout---------------------------------_#]"));
      break;
    }


   

    if (counter>rx_msg_lenght){  //prevent overflow
      Serial.println(F("[S_array_overflow prevented---_#]"));
      Serial.println(counter);
      Serial.println(F("end"));
      counter=0;
      Serial.println("start:");
      for (pointer = 0; pointer <= rx_msg_lenght; pointer++) {
        Serial.print(data_from_serial[pointer]); 
      }
      Serial.println(":end");
      continue;     
    }



    if (counter<2){
      counter=counter+1;
      continue;
    }
    message_to_decode_avaible=1;



    if ( (data_from_serial[counter-2]=='[')&&(data_from_serial[counter-1]=='S')&&(data_from_serial[counter]=='_')  ){//   
      // Serial.println("cmd start found-------------------------------");
       onos_cmd_start_position=counter-2;
    }


    if( (data_from_serial[counter-2]=='_')&&(data_from_serial[counter-1]=='#')&&(data_from_serial[counter]==']')&&(onos_cmd_start_position!=-99) ){//   onos cmd found
    //   Serial.println("cmd end found-------------------------------");
      onos_cmd_end_position=counter-2;

      memset(filtered_uart_message,0,sizeof(filtered_uart_message)); //to clear the array

      for (pointer = 0; pointer <= rx_msg_lenght; pointer++) {
        filtered_uart_message[pointer]=data_from_serial[onos_cmd_start_position+pointer];
          //Serial.println(filtered_uart_message[pointer]);
        if ((filtered_uart_message[pointer-1]=='#')&&(filtered_uart_message[pointer]==']')  ) {//  
          break;
        }

      }


      //decodeOnosCmd(filtered_uart_message,decoded_uart_answer);
      OnosMsgHandler.decodeOnosCmd(filtered_uart_message,decoded_uart_answer);
      if ( strcmp(decoded_uart_answer,"[S_remote_#]")==0){
        ForwardSerialMessageToRadio(filtered_uart_message,received_message_address);
      }
      else {
        sendSerialAnswerFromSerialMsg();
      }


      if (Serial.available() > 0){
        counter=0; 
        timeout=millis()+200; //reset the timeout on each onos cmd
        continue; //i have found a cmd ..but, i will look for other ones..
      }
      else{
        return(1);
      }

 
    }//closed if onocmd found


    counter=counter+1;

  }// end of while rx receive



  strcpy(decoded_uart_answer,"[S_nocmd0_#]");
  sendSerialAnswerFromSerialMsg();
  return(0);//no cmd found




}








boolean ForwardSerialMessageToRadio(char *msg_to_send_to_radio,int radio_address){
  memset(decoded_uart_answer,0,sizeof(decoded_uart_answer)); //to clear the array
  if (radio.sendWithRetry(radio_address, msg_to_send_to_radio, strlen(msg_to_send_to_radio),radioRetry,radioTxTimeout)) {
              // note that the max delay time is 255..because is uint8_t
              //target node Id, message as string or byte array, message length,retries, milliseconds before retry
              //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)

            strcpy(decoded_uart_answer,"ok_#]");
            radio.receiveDone(); //put radio in RX mode
            sendSerialAnswerFromSerialMsg();
            return(1);
          }

          else{// failed to contact radio node or radio node didn't answer
               // Serial.println("sendtoWait failed");
            strcpy(decoded_uart_answer,"[S_ertx1_#]");  
            radio.receiveDone(); //put radio in RX mode
            sendSerialAnswerFromSerialMsg();
            delay(10);//delay to allow the remote node to talk after a transmission failure
            return(0);
          }


}

void sendSerialAnswerFromSerialMsg(){

  if (enable_answer_back!=1){ //write if there is a not recognised message
    return;
  }

  if((decoded_uart_answer[0]=='o')&&(decoded_uart_answer[1]=='k')){
      //strcpy(received_message_answer,""); 
    memset(decoded_uart_answer,0,sizeof(decoded_uart_answer)); //to clear the array
    strcat(decoded_uart_answer,filtered_uart_message);
    Serial.print(F("[S_ok"));
    for (pointer = 0; pointer <= rx_msg_lenght; pointer++) {
 
      if (pointer<3){//to skip the "[S_"  because I have just sent it..
        continue;
      }
      Serial.print(filtered_uart_message[pointer]);

      if ((filtered_uart_message[pointer-1]=='#')&&(filtered_uart_message[pointer]==']')  ) {//  
        break;
      }
    }   
    Serial.print('\n'); 
    Serial.flush(); //make sure all serial data is clocked out ,waiting until is done
    sync_time=millis();
    enable_answer_back=0;
    // the answer will be : [S_ok+ message received

  }

  else{

    Serial.print(decoded_uart_answer); 
    Serial.print('\n'); 
    Serial.flush(); //make sure all serial data is clocked out ,waiting until is done

  }
    
  memset(decoded_uart_answer,0,sizeof(decoded_uart_answer)); //to clear the array  
  strcpy(decoded_uart_answer,"[S_nocmd2_#]");  
  //strcpy(filtered_uart_message,""); 
  memset(filtered_uart_message,0,sizeof(filtered_uart_message)); //to clear the array
  //Serial.flush(); //make sure all serial data is clocked out 
  enable_answer_back=0;


}



boolean checkAndHandleIncomingRadioMsg(){

  if (radio.receiveDone()){
    //print message received to serial

/*
      Serial.print('[');Serial.print(radio.SENDERID);Serial.print("] ");
      Serial.print((char*)radio.DATA);
      Serial.print("   [RX_RSSI:");Serial.print(radio.RSSI);Serial.print("]");
*/
 
    //check if received message contains Hello World

    onos_cmd_start_position=-99;  
    onos_cmd_end_position=-99;  

      //strcpy(filtered_radio_message,"");
    memset(filtered_radio_message,0,sizeof(filtered_radio_message)); //to clear the array

    //Serial.println(radio.SENDERID);
    /*
    if (radio.TARGETID!=this_node_address){
      Serial.println(F("[S_er9_radioAddress_#]"));
      return(0); // todo: implement a forward of the message? 
    }
    */

    //unsigned long get_decode_time=micros();  //64 o 68
    //for (uint8_t counter = 0; counter <= rx_msg_lenght; counter++) {

    for (uint8_t counter = 0; counter < radio.DATALEN; counter++) {

      filtered_radio_message[counter]=radio.DATA[counter];
      //  Serial.println(filtered_radio_message[counter]);

    //[S_001dw06001_#]
      if (counter<2){
        continue;
      }
      if ( (filtered_radio_message[counter-2]=='[')&&(filtered_radio_message[counter-1]=='S')&&(filtered_radio_message[counter]=='_')  ){//   
       // Serial.println("cmd start found-------------------------------");
        onos_cmd_start_position=counter-2;
      }


      if( (filtered_radio_message[counter-2]=='_')&&(filtered_radio_message[counter-1]=='#')&&(filtered_radio_message[counter]==']')  ){//   
        //  Serial.println("cmd end found-------------------------------");
        onos_cmd_end_position=counter-2;
        break;// now the message has ended
      }


    }


    //Serial.println(micros()-get_decode_time);


    if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){
    //    Serial.println("onos cmd  found-------------------------------");
      //decodeOnosCmd(filtered_radio_message,decoded_radio_answer);
      OnosMsgHandler.decodeOnosCmd(filtered_radio_message,decoded_radio_answer);

      if( (decoded_radio_answer[0]=='o')&&(decoded_radio_answer[1]=='k')||(strcmp(decoded_radio_answer,"[S_remote_#]")==0)){//if the message was ok...
      //check if sender wanted an ACK
        if (radio.ACKRequested()){
          radio.sendACK();
          //Serial.println(" - ACK sent");

        }
        return(1); 
      }
      else{
        Serial.println(F("[S_error in message decode from radio node i will not send the ACK_#]"));
        return(0);
      }


    }
    else{
      strcpy(decoded_uart_answer,"[S_nocmd1_#]");
      Serial.print(F("[S_error in message nocmd1_#]"));
      Serial.print('\n'); 
      Serial.flush(); //make sure all serial data is clocked out 
      return(0); 
    }

  }

}



void forwardRadioMsgToSerialPort(){

    if(strcmp(decoded_radio_answer,"[S_remote_#]")==0){ //transmit the received data from the node to the serial port

      memset(decoded_radio_answer,0,sizeof(decoded_radio_answer)); //to clear the array
      for (pointer = 0; pointer <= rx_msg_lenght; pointer++) {
        Serial.print(filtered_radio_message[pointer]);
          

        if (pointer<2){
          continue;
        }

        if ((filtered_radio_message[pointer-2]=='_')&&(filtered_radio_message[pointer-1]=='#')&&(filtered_radio_message[pointer]==']')  ) {// 
          sync_time=millis();  
          break;
        }

      }   

      Serial.print('\n');  


    }


 
    radio.receiveDone(); //put radio in RX mode
    Serial.flush(); //make sure all serial data is clocked out ,waiting until is done

}


void checkCurrentRadioAddress(){

#if defined(remote_node)   // only if this is a remote node..

  if (old_address==254){// i have not the proper address yet..



    if (old_address!=this_node_address){//the address has changed and I restart radio to use it
 

      //radio.setAddress(this_node_address);
      beginRadio();
      old_address=this_node_address;
      get_address_timeout=millis();
      Serial.print("radio address changed to:");
      Serial.println(this_node_address);
      sendSyncMessage(radioRetry,radioTxTimeout);


    }

    random_time=4000;//random(4000,5000);
    


    if ((millis()-get_address_timeout)>random_time){ //every 4000/5000 ms
   
      get_address_timeout=millis();

      getAddressFromGateway();  //ask the gateway for a proper address


    }


  }
  else{
    random_time=1500;//random(1500,2500);
    if ((millis()-sync_time)>random_time){ //every 1500/2500 ms
   
      sync_time=millis();

      sendSyncMessage(radioRetry,radioTxTimeout);


    }

  }

#endif

}
void beginRadio(){

  interrupts(); // Enable interrupts

  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)

  radio.encrypt(encript_key);
  


  radio.enableAutoPower(targetRSSI);
 

}


void setup() {

  //pinMode(RFM69_RST, OUTPUT);
  //delay(95000); //wait for glinet to power on
  while (!Serial); // wait until serial console is open
  Serial.begin(SERIAL_BAUD);



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

  beginRadio();
  





/*
  Serial.print("\nTransmitting at ");
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(" MHz");

*/  







/*
  Serial.print("memory:");
  Serial.println(freeRam ());

*/
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM

  // If you are using a high power RF69, you *must* set a Tx power in the
  // range 14 to 20 like this:
  // driver.setTxPower(14);


  while (1){
    delayMicroseconds(20);
    if (Serial.available() > 2) {
       if (Serial.read()=='['){
         if (Serial.read()=='S'){
           if (Serial.read()=='_'){
             break;
           }
         }
       }
    }// end of if (Serial.available() > 3)


  } // end of   while (1){

  Serial.println(F("[S_arduino_ready_#]"));
  Serial.flush(); //make sure all serial data is clocked out ,waiting until is done
  composeSyncMessage();
  makeSyncMessage();

}



void loop(){

sync:

  if (first_sync==1){
    delay(1000);
    composeSyncMessage();
    makeSyncMessage();

  }




restart:


  if (Serial.available() > 0) {

    if (radioPriority>uartPriority){
      if (radioPriority>1){
        radioPriority=radioPriority-1; 
      }
      goto radioRxCheck; 
       
    }
    else{
      if (uartPriority>1){
        uartPriority=uartPriority-1; 
      }
      goto uartRxCheck;  

    }

  }


radioRxCheck:
    radio_msg_to_decode_is_avaible=checkAndHandleIncomingRadioMsg();
    if (radio_msg_to_decode_is_avaible==1){
      forwardRadioMsgToSerialPort();
    }
  





uartRxCheck:
  if (Serial.available() > 0) {
    serial_msg_to_decode_is_avaible=checkAndReceiveSerialMsg();
  }
  else{
    if ( (millis()-sync_time)>12000){   //each n sec time contact the onosCenter and update
      sync_time=millis();
      composeSyncMessage();
      makeSyncMessage();
    }
  }

 
  if (first_sync==1){  //if the node is not synced yet..sync it
    goto sync;
  }






}

