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
#include "onos_message_decode.h"

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
 
int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;



boolean radio_enabled=1;

unsigned long sync_time=0;

char serial_number[13]="WLightSS0004";

char node_fw[]="5.13";

int this_node_address=254; //i start with 254

int old_address=254; 

unsigned long get_address_timeout=0;




# define gateway_address 1



int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}







void composeSyncMessage(){

  //[S_001sy3.05ProminiS0001_#] 

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
  strcat(syncMessage, "sy");
  strcat(syncMessage, node_fw);
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




void sendSyncMessage(){




  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage))) {
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

  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage))) {
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








 
void setup() {


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
      decodeOnosCmd(filtered_onos_message,this_node_address,serial_number);

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

  else if ((millis()-sync_time)>5000){ //every 5000 ms
   
   
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

