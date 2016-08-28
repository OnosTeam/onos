/*
 * O.N.O.S.  arduino serial gateway  firmware by Marco Rigoni 27-8-16  onos.info@gmail.com 
 * more info on www.myonos.com 
 * UIPEthernet is a TCP/IP stack that can be used with a enc28j60 based
 * Ethernet-shield.
 *
 * UIPEthernet uses the fine uIP stack by Adam Dunkels <adam@sics.se>
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
#define NODEID        1    // The unique identifier of this node
#define RECEIVER      2    // The recipient of packets
 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
//#define FREQUENCY     RF69_868MHZ
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "sampleEncryptKey" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HCW   false // set to 'true' if you are using an RFM69HCW module
 
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
 

//#define DEVMODE 0


uint8_t i;




boolean radio_enabled=1;


unsigned long sync_time=0;


char serial_number[13]="ProminiS0001";

char node_fw[]="5.13";

int this_node_address=1; //must be int..



#define rx_msg_lenght 31

char received_message_type_of_onos_cmd;
char received_message_flag;
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;
char received_message_answer[rx_msg_lenght+6]="er00_#]";
char received_message_sn[13]="";
int received_message_address=0; //must be int..

uint8_t counter;
boolean enable_answer_back=0;


int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}




void sendSyncMessage(){

  // onos_s3.05v1sProminiS0001f001_#]
  char syncMessage[rx_msg_lenght+3];

  char str_this_node_address[4];

  str_this_node_address[0]=(this_node_address/100)+'0';
  str_this_node_address[1]=(this_node_address/10)+'0';
  str_this_node_address[2]=(this_node_address/1)+'0';

  strcpy(syncMessage, "onos_s ");
  strcat(syncMessage, node_fw);
  strcat(syncMessage, "v1s");
  strcat(syncMessage, serial_number);
  strcat(syncMessage, "f");
  strcat(syncMessage, str_this_node_address);

  strcat(syncMessage, "_#]");

  for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
    Serial.print(syncMessage[pointer]);

    if ((syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ) {//  
        break;
      }
    }   
    Serial.print('\n'); 



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



void decodeOnosCmd(const char *received_message){

 // Serial.println(F("decodeOnosCmd executed"));

  strcpy(received_message_answer,"err01_#]");
  if ((received_message[0]=='o')&&(received_message[1]=='n')&&(received_message[2]=='o')&&(received_message[3]=='s')&&(received_message[4]=='_'))
  { // the onos cmd was found           onos_d07v001sProminiS0001f001_#] 

    strcpy(received_message_answer,"cmdRx_#]");               


    received_message_type_of_onos_cmd=received_message[5];


    strcpy(received_message_sn,""); 

    received_message_sn[0]=received_message[13];
    received_message_sn[1]=received_message[14];
    received_message_sn[2]=received_message[15];
    received_message_sn[3]=received_message[16];
    received_message_sn[4]=received_message[17];
    received_message_sn[5]=received_message[18];
    received_message_sn[6]=received_message[19];
    received_message_sn[7]=received_message[20];
    received_message_sn[8]=received_message[21];
    received_message_sn[9]=received_message[22];
    received_message_sn[10]=received_message[23];
    received_message_sn[11]=received_message[24];

 
    received_message_flag=received_message[25];  

    received_message_address=(received_message[26]-48)*100+(received_message[27]-48)*10+(received_message[28]-48)*1;


         
    received_message_first_pin_used=((received_message[6])-48)*10+(  (received_message[7])-48);

    received_message_second_pin_used=-1;
                                    

    received_message_value=(received_message[9]-48)*100+(received_message[10]-48)*10+(received_message[11]-48)*1;

               
 
 

    if ((received_message_address!=this_node_address)||((strcmp(received_message_sn,serial_number)!=0))) {//onos command for a remote arduino node
      strcpy(received_message_answer,"remote_#]");


      if  ( strcmp(received_message_sn,serial_number)==0 ){// wrong sn but address for this node
        strcpy(received_message_answer,"er2_sn#]"); 
      }



/*
      Serial.print(F("serial_number:")); 
      Serial.print(received_message_sn);

      Serial.print(F("serial_number222:")); 
      Serial.print(serial_number);
      Serial.println(F("end")); 
*/
      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


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


    
/*
    Serial.print(F("onos_cmd:"));
    Serial.println(received_message_type_of_onos_cmd);

    Serial.print(F("serial_number:"));
    Serial.print(received_message_sn);


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
  while (!Serial); // wait until serial console is open
  Serial.begin(SERIAL_BAUD);

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
  radio.setPowerLevel(6); // power output ranges from 0 (5dBm) to 31 (20dBm)
  
  radio.encrypt(ENCRYPTKEY);
  

  radio.enableAutoPower(ATC_RSSI);


  pinMode(LED, OUTPUT);

/*
  Serial.print("\nTransmitting at ");
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(" MHz");

*/  
  Serial.print(F("arduino_ready_#]/n"));
  radio_enabled=1;


/*
  Serial.print("memory:");
  Serial.println(freeRam ());

*/
  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM

  // If you are using a high power RF69, you *must* set a Tx power in the
  // range 14 to 20 like this:
  // driver.setTxPower(14);
}



void loop()
{


  if (radio_enabled==1){

      // Wait for a message addressed to us from the client
      uint8_t a = 0;//noop
   

  }







  counter=0;
  char data_from_serial [rx_msg_lenght+5];
  char filtered_onos_message[rx_msg_lenght+3];
  unsigned long timeout=millis()+200;

  while (Serial.available() > 0) {
    enable_answer_back=1;
  // Serial.println(F("im"));
   //Serial.println(counter);
   // read the incoming byte:
    delayMicroseconds(150);  //the serial doesnt work without this delay...

    data_from_serial[counter] = Serial.read();

    if ( millis()>timeout){
      Serial.println(F("serial_timeout---------------------------------"));
      break;
    }


   

    if (counter>rx_msg_lenght){  //prevent overflow
      Serial.println(F("array_overflow---------------------------------"));
      Serial.println(counter);
      Serial.println(F("end"));
      counter=0;
      continue;     
    }


    if (counter<2){
      counter=counter+1;
      continue;     
    }


    if  ((counter>rx_msg_lenght-1)||((data_from_serial[counter-1]=='#')&&(data_from_serial[counter]==']')  ) ){//   

     // onos_s07v180s0001f000_#]

/*
     Serial.println("im here-------------------------------");
     Serial.println(data_from_serial[counter-rx_msg_lenght-3]);
     Serial.println(data_from_serial[counter-rx_msg_lenght-2]);
     Serial.println(data_from_serial[counter-rx_msg_lenght-1]);
     Serial.println(data_from_serial[counter-rx_msg_lenght]);
     Serial.println(data_from_serial[counter-rx_msg_lenght+1]);
     Serial.println(data_from_serial[counter-rx_msg_lenght+2]);
     Serial.println("ddd here-------------------------------");   

*/

      if ((data_from_serial[counter-rx_msg_lenght]=='o')&&(data_from_serial[counter-rx_msg_lenght+1]=='n')&&(data_from_serial[counter-rx_msg_lenght+2]=='o')&&(data_from_serial[counter-rx_msg_lenght+3]=='s')&&(data_from_serial[counter-rx_msg_lenght+4]=='_')){

#if defined(DEVMODE)
       Serial.println(F("onos cmd received0:"));
#endif

        uint8_t message_copy[rx_msg_lenght+1];
        strcpy(filtered_onos_message,"");

        for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
          filtered_onos_message[pointer]=data_from_serial[counter-rx_msg_lenght+pointer];
          message_copy[pointer]=data_from_serial[counter-rx_msg_lenght+pointer]; 
          //Serial.println(filtered_onos_message[pointer]);
          if ((filtered_onos_message[pointer-1]=='#')&&(filtered_onos_message[pointer]==']')  ) {//  
            break;
          }

         //Serial.println("mmm");
         //Serial.println(filtered_onos_message[pointer]);
        }
       // Serial.println("filtered_onos_message:");
        //Serial.println(filtered_onos_message);
       
        decodeOnosCmd(filtered_onos_message);

        if(((received_message_answer[0]=='o')&&(received_message_answer[1]=='k'))||(strcmp(received_message_answer,"remote_#]")==0)){



/*
         Serial.println("sn");
         Serial.println(received_message_sn);
         Serial.println("__sn");
*/



          

          if (strcmp(received_message_answer,"remote_#]")!=0) {//onos command for this arduino node
            //Serial.print("ok_local");
            strcpy(received_message_answer,"ok_local_#]");
            counter=0;
          } 
          else{ //onos command to send to a remote node
            if ((radio_enabled==1)&&(received_message_flag=='f')){ // if radio is active and the flag is setted as forward..


              //put here the radio  transmit part



              if (radio.sendWithRetry(received_message_address, filtered_onos_message, strlen(filtered_onos_message))) {
              //target node Id, message as string or byte array, message length,retries, milliseconds before retry
              //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)


               // Serial.println("OK");
                strcpy(received_message_answer,"ok_#]");
                radio.receiveDone(); //put radio in RX mode
                break;  
              }
 

              else{
               // Serial.println("sendtoWait failed");
                strcpy(received_message_answer,"ertx1_#]");  
                radio.receiveDone(); //put radio in RX mode
                break;
                 //delay(500);
              }




            }
            else {//radio is disabled 
              strcpy(received_message_answer,"ertx3_#]");
              break;
            }

              

            counter=0;
          }



  
        }
        else{// error decoding the serial message

          break;
        }



      }
      else{//no onos_ cmd found

        strcpy(received_message_answer,"nocmd1_#]");
        break;

      }




     counter=0;
     continue;
  }
  else{

    strcpy(received_message_answer,"nocmd2_#]");

  }





   
  counter=counter+1;

  }




  if (enable_answer_back==1){ //write if there is a not recognise message  shorter...
    if((received_message_answer[0]=='o')&&(received_message_answer[1]=='k')){
      //strcpy(received_message_answer,""); 
      //strcat(received_message_answer,filtered_onos_message);
      Serial.print("ok");
      for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
        Serial.print(filtered_onos_message[pointer]);

        if ((filtered_onos_message[pointer-1]=='#')&&(filtered_onos_message[pointer]==']')  ) {//  
          break;
        }
      }   
      Serial.print('\n'); 
      sync_time=millis();
      enable_answer_back=0;
      // the answer will be : "ok"+receivedmesssage for example: okonos_d05v001sProminiS0001f001_#]

    }

    else{

      Serial.print(received_message_answer); 
      Serial.print('\n'); 

    }
    

    strcpy(received_message_answer,"VOID");  
    strcpy(filtered_onos_message,""); 

    Serial.flush(); //make sure all serial data is clocked out before sleeping the
    enable_answer_back=0;
  }


 

  unsigned long t=millis();
  if ( (t-sync_time)>12000){   //each 120 sec time contact the onosCenter and update the current ip address
    sync_time=t;
  // onos_s3.05v1sProminiS0001f001_#]

  sendSyncMessage();

  }




}

