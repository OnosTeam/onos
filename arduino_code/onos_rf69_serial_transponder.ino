



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
//*********************************************************************************************
// *********** IMPORTANT SETTINGS - YOU MUST CHANGE/ONFIGURE TO FIT YOUR HARDWARE *************
//*********************************************************************************************
#define NETWORKID     100  // The same on all nodes that talk to each other
 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
//#define FREQUENCY     RF69_868MHZ
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "sampleEncryptKey" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HCW   true // set to 'true' if you are using an RFM69HCW module
 
//*********************************************************************************************
#define SERIAL_BAUD   115200
 
#define RFM69_CS      10
#define RFM69_IRQ     2
#define RFM69_IRQN    0  // Pin 2 is IRQ 0!
#define RFM69_RST     9
 
 
#define ATC_RSSI      -75   //power signal from -30(stronger) to -95(weaker) 
 
int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;
 





unsigned long sync_time=0;

char serial_number[13]="ProminiS0001";

char node_fw[]="5.26";

int this_node_address=1; //must be int..


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
char decoded_radio_answer[24]="er00_#]";
int received_message_address=0; //must be int..
char filtered_uart_message[rx_msg_lenght+3];
char filtered_radio_message[rx_msg_lenght+3];
char syncMessage[28];
char str_this_node_address[4];
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////

uint8_t radioRetry=3;      //todo: make this changable from serialport
uint8_t radioTxTimeout=70;  //todo: make this changable from serialport
uint8_t uartPriority=0;
uint8_t radioPriority=0;


uint8_t counter=0;
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



void decodeOnosCmd(char *received_message,char *decoded_result){
 
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

  strcpy(decoded_result,"[S_err01_#]");



  if ((received_message[0]=='[')&&(received_message[1]=='S')&&(received_message[2]=='_') ) {
 // the onos cmd was found           [S_001dw06001_#]


    strcpy(decoded_result,"[S_cmdRx_#]");               


    received_message_type_of_onos_cmd[0]=received_message[6];
    received_message_type_of_onos_cmd[1]=received_message[7];

    received_message_address=(received_message[3]-48)*100+(received_message[4]-48)*10+(received_message[5]-48)*1;


         

    if (received_message_address!=this_node_address) {//onos command for a remote arduino node
      strcpy(decoded_result,"[S_remote_#]");

/*


      Serial.print(F("serial_number222:")); 
      Serial.print(serial_number);
      Serial.println(F("end")); 
*/
      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


    //[S_001dw06001_#]
    if ( received_message_type_of_onos_cmd[0]=='d' && received_message_type_of_onos_cmd[1]=='w' ){

      received_message_value=received_message[12]-48;
      if (received_message_value>1){ 
        strcpy(decoded_result,"[S_er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;

      pinMode(received_message_first_pin_used, OUTPUT); 
      digitalWrite(received_message_first_pin_used, received_message_value); 
      strcpy(decoded_result,"ok");
      return;
    }
    
    //[S_001aw06125_#]
    else if( received_message_type_of_onos_cmd[0]=='a' && received_message_type_of_onos_cmd[1]=='w' ){
 
      received_message_value=(received_message[10]-48)*100+(received_message[11]-48)*10+(received_message[12]-48)*1;

      if ((received_message_value<0)||(received_message_value>255)){ //status check
        received_message_value=0;
      //Serial.println(F("onos_cmd_value_error"));  
        strcpy(decoded_result,"[S_er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
      analogWrite(received_message_first_pin_used, received_message_value); 
      strcpy(decoded_result,"ok");
      return;
    } 

 
    //[S_001sr04051_#] 
    else if( received_message_type_of_onos_cmd[0]=='s' && received_message_type_of_onos_cmd[1]=='r' ){

      received_message_value=received_message[12]-48;      

      if (received_message_value>1){ 
        strcpy(decoded_result,"[S_er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
      received_message_second_pin_used=((received_message[10])-48)*10+(  (received_message[11])-48)*1;

      pinMode(received_message_first_pin_used, OUTPUT); 
      pinMode(received_message_second_pin_used, OUTPUT); 
      //note to se a relay you have to transmit before the set pin and after the reset pin , the lessere first
      //  so for example received_message_first_pin_used =14   received_message_second_pin_used=15
      digitalWrite(received_message_first_pin_used, !received_message_value); 
      digitalWrite(received_message_second_pin_used,received_message_value); 
      //attention with this only one relay per message can be setted!!!
      //pins_to_reset1=pin_number_used;
      //pins_to_reset2=second_pin_number_used;
      delay(150);
      digitalWrite(received_message_first_pin_used,0); 
      digitalWrite(received_message_second_pin_used,0);  

      strcpy(decoded_result,"ok");
      return;
    }

    else if( received_message_type_of_onos_cmd[0]=='s' && received_message_type_of_onos_cmd[1]=='a' ){
      first_sync=0; //this node has made the first sync with the onoscenter
      strcpy(decoded_result,"ok");
      return;
    }

/*


    switch (received_message_type_of_onos_cmd) {
                                         //onos_d05v001sProminiS0002f002_#] to remote..
      case 'd':{     //digital write       onos_d05v001sProminiS0001f001_#]  where the last'a' will be a char from 0 to 255 indicating the address of the node
        if (received_message_value>1){ 
          strcpy(received_message_answer,"er0_status_#]"); 
          break;
        }
      
        pinMode(received_message_first_pin_used, OUTPUT); 
        digitalWrite(received_message_first_pin_used, received_message_value); 
        strcpy(received_message_answer,"ok");
        break;
      }

      case 'a':{     //pwm write           onos_a07v100sProminiS0001f001_#]
        analogWrite(received_message_first_pin_used, received_message_value); 
        strcpy(received_message_answer,"ok");
        break;
      }

      case 's':{     //servo controll      onos_s07v180sProminiS0001f001_#]
        //servo are not supported yet
        //myservo.attach(received_message_first_pin_used);  // attaches the servo on pin 2 to the servo object 
        //myservo.write(received_message_value);              // tell servo to go to position in variable 'pos'
        strcpy(received_message_answer,"ok");
        break;
      }  

      case 'g':{     //get digital status  onos_g0403v0sProminiS0001f001_#]
        pinMode(received_message_first_pin_used, INPUT); 
        pinMode(received_message_second_pin_used, INPUT);
        digitalWrite(received_message_first_pin_used,1); //enable internal pullup resistors
        digitalWrite(received_message_second_pin_used,1);//enable internal pullup resistors
        delayMicroseconds(20);  //wait a bit
        char val_first_pin=digitalRead(received_message_first_pin_used)+48;
        char val_second_pin=digitalRead(received_message_second_pin_used)+48;
        strcpy(received_message_answer,""); 
        strcpy(received_message_answer,"ok_s="); 
        received_message_answer[5]=val_first_pin;
        received_message_answer[6]=val_second_pin;
        received_message_answer[7]='_';
        received_message_answer[8]='#';
        received_message_answer[9]=']';

        //strcat(received_message_answer,"_#]");
        // answer will be like:   ok_s=00_#] 
        
        
        break;
      }  
                                           
      case 'r':{     //relay               onos_r1415v1sProminiS0001f001_#]
        received_message_value=(received_message[11]-'0');


        strcpy(received_message_answer,"ok");
        received_message_second_pin_used=((received_message[8])-48)*10+(  (received_message[9])-48)*1;

        pinMode(received_message_first_pin_used, OUTPUT); 
        pinMode(received_message_second_pin_used, OUTPUT); 
        //note to se a relay you have to transmit before the set pin and after the reset pin , the lessere first
        //  so for example received_message_first_pin_used =14   received_message_second_pin_used=15
        digitalWrite(received_message_first_pin_used, !received_message_value); 
        digitalWrite(received_message_second_pin_used,received_message_value); 
                     //attention with this only one relay per message can be setted!!!
                     //pins_to_reset1=pin_number_used;
                     //pins_to_reset2=second_pin_number_used;
        delay(150);
        digitalWrite(received_message_first_pin_used,0); 
        digitalWrite(received_message_second_pin_used,0);  

        break;
      } 

      default:{
        strcpy(received_message_answer,"type_err");
        Serial.println(F("onos_cmd_type_error"));  
      }
  

   }//end of the switch case

*/
    
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
      for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
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

      for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
        filtered_uart_message[pointer]=data_from_serial[onos_cmd_start_position+pointer];
          //Serial.println(filtered_uart_message[pointer]);
        if ((filtered_uart_message[pointer-1]=='#')&&(filtered_uart_message[pointer]==']')  ) {//  
          break;
        }

      }


      decodeOnosCmd(filtered_uart_message,decoded_uart_answer);
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
    for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
 
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
      decodeOnosCmd(filtered_radio_message,decoded_radio_answer);

      if( (decoded_radio_answer[0]=='o')&&(decoded_radio_answer[1]=='k')||(strcmp(decoded_radio_answer,"[S_remote_#]")==0)){//if the message was ok...
      //check if sender wanted an ACK
        if (radio.ACKRequested()){
          radio.sendACK();
  //        Serial.println(" - ACK sent");

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
      for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
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

  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)
  
  radio.encrypt(ENCRYPTKEY);
  





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

