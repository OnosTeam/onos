// rf69_reliable_datagram_server.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple addressed, reliable messaging server
// with the RHReliableDatagram class, using the RH_RF69 driver to control a RF69 radio.
// It is designed to work with the other example rf69_reliable_datagram_client
// Tested on Moteino with RFM69 http://lowpowerlab.com/moteino/
// Tested on miniWireless with RFM69 www.anarduino.com/miniwireless
// Tested on Teensy 3.1 with RF69 on PJRC breakout board



/*
*                  Arduino      RFM69W
*                  GND----------GND   (ground in)
*                  3V3----------3.3V  (3.3V in)
*  interrupt 0 pin D2-----------DIO0  (interrupt request out)
*           SS pin D10----------NSS   (chip select in)
*          SCK pin D13----------SCK   (SPI clock in)
*         MOSI pin D11----------MOSI  (SPI Data in)
*         MISO pin D12----------MISO  (SPI Data out)

*/



//   WARNING   DON'T USE THE VARIABLE I BECAUSE IS ALREDY USED BY THE RADIO LIBRARY AND WILL BE RESETTED OFTEN...





#include <RHReliableDatagram.h>
#include <RH_RF69.h>
#include <SPI.h>

#define CLIENT_ADDRESS 1
#define SERVER_ADDRESS 2

//#define DEVMODE 0

String data_from_serial;
uint8_t i;

// Singleton instance of the radio driver
RH_RF69 driver;
//RH_RF69 driver(15, 16); // For RF69 on PJRC breakout board with Teensy 3.1
//RH_RF69 rf69(4, 2); // For MoteinoMEGA https://lowpowerlab.com/shop/moteinomega

// Class to manage message delivery and receipt, using the driver declared above
RHReliableDatagram manager(driver, SERVER_ADDRESS);








String  serial_number="0000";



   //onos_d07v001s0000_#]

char serial_message_type_of_onos_cmd;
uint8_t serial_message_first_pin_used;
uint8_t serial_message_second_pin_used;
int serial_message_value;
String serial_message_answer="er00_#]";
String serial_message_sn="";

uint8_t serial_msg_lenght=19;
uint8_t counter;
boolean enable_print=0;




void decodeOnosCmd(char received_message[]){

 // Serial.println(F("decodeOnosCmd executed"));
  serial_message_answer="err01_#]";
  if ((received_message[0]=='o')&&(received_message[1]=='n')&&(received_message[2]=='o')&&(received_message[3]=='s')&&(received_message[4]=='_'))
  { // the onos cmd was found           onos_d07v001s0001_#]
    serial_message_answer="cmdRx_#]";                  

    serial_message_sn="";

    serial_message_sn=serial_message_sn+received_message[13]+received_message[14]+received_message[15]+received_message[16];


    serial_message_type_of_onos_cmd=received_message[5];
         
    serial_message_first_pin_used=((received_message[6])-48)*10+(  (received_message[7])-48);

    serial_message_second_pin_used=-1;
                                    

    serial_message_value=(received_message[9]-48)*100+(received_message[10]-48)*10+(received_message[11]-48)*1;

               
    if ((serial_message_value<0)||(serial_message_value>255)){ //status check
      serial_message_value=0;
      //Serial.println(F("onos_cmd_value_error"));  
      serial_message_answer="er0_status_#]";
      return;
    }
 

    if (serial_message_sn!=serial_number) {//onos command for a remote arduino node
      //serial_message_answer="remote_#]"; 
      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


    switch (serial_message_type_of_onos_cmd) {

      case 'd':{     //digital write       onos_d07v001s0001_#]
        serial_message_answer="ok_#]";
        break;
      }

      case 'a':{     //pwm write           onos_a07v100s0001_#]
        serial_message_answer="ok_#]";
        break;
      }
              
      case 's':{     //servo controll      onos_s07v180s0001_#]
        serial_message_answer="ok_#]";
        break;
      }  

      case 'r':{     //relay               onos_r1716v1s0004_#]
        serial_message_answer="ok_#]";
        serial_message_second_pin_used=((received_message[8])-48)*10+(  (received_message[9])-48)*1;
        serial_message_value=(received_message[11]-'0');
        break;
      } 

      default:{
        serial_message_answer="type_err";
        Serial.println(F("onos_cmd_type_error"));  
      }
  

   }//end of the switch case


    /*

    Serial.print(F("onos_cmd:"));
    Serial.println(serial_message_type_of_onos_cmd);

    Serial.print(F("serial_number:"));
    Serial.print(serial_message_sn);


    Serial.println(F("pin_used:"));
    Serial.println(serial_message_first_pin_used);
    Serial.println(F("pin_used2:"));
    Serial.println(serial_message_second_pin_used);

    Serial.print(F("message_value:"));
    Serial.println(serial_message_value);


    */









 } // end of if message start with onos_   






}// end of decodeOnosCmd()











void setup() 
{
  Serial.begin(115200);
  if (!manager.init())
    Serial.println("init failed");

  Serial.println(F("ready"));

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM

  // If you are using a high power RF69, you *must* set a Tx power in the
  // range 14 to 20 like this:
  // driver.setTxPower(14);
}

uint8_t data[] = "And hello back to you";
// Dont put this on the stack:
uint8_t buf[RH_RF69_MAX_MESSAGE_LEN];

void loop()
{
  if (manager.available())
  {
    // Wait for a message addressed to us from the client
    uint8_t len = sizeof(buf);
    uint8_t from;
    if (manager.recvfromAck(buf, &len, &from))
    {
      Serial.print("got request from : 0x");
      Serial.print(from, HEX);
      Serial.print(": ");
      Serial.println((char*)buf);

      // Send a reply back to the originator client
      if (!manager.sendtoWait(data, sizeof(data), from))
        Serial.println("sendtoWait failed");
    }
  }







  counter=0;
  char data_from_serial [25];
  char second_array[21];
  unsigned long timeout=millis()+200;

  while (Serial.available() > 0) {
    enable_print=1;
  // Serial.println(F("im"));
   //Serial.println(counter);
   // read the incoming byte:
    delayMicroseconds(150);  //the serial doesnt work without this delay...

    data_from_serial[counter] = Serial.read();

    if ( millis()>timeout){
      Serial.println(F("serial_timeout---------------------------------"));
      break;
    }


    if (counter<2){
      counter=counter+1;
      continue;     
    }


    if  ((counter>serial_msg_lenght-1)||((data_from_serial[counter-1]=='#')&&(data_from_serial[counter]==']')  ) ){//   

     // onos_s07v180s0001_#]

/*
     Serial.println("im here-------------------------------");
     Serial.println(data_from_serial[counter-serial_msg_lenght-3]);
     Serial.println(data_from_serial[counter-serial_msg_lenght-2]);
     Serial.println(data_from_serial[counter-serial_msg_lenght-1]);
     Serial.println(data_from_serial[counter-serial_msg_lenght]);
     Serial.println(data_from_serial[counter-serial_msg_lenght+1]);
     Serial.println(data_from_serial[counter-serial_msg_lenght+2]);
     Serial.println("ddd here-------------------------------");   

*/

      if ((data_from_serial[counter-serial_msg_lenght]=='o')&&(data_from_serial[counter-serial_msg_lenght+1]=='n')&&(data_from_serial[counter-serial_msg_lenght+2]=='o')&&(data_from_serial[counter-serial_msg_lenght+3]=='s')&&(data_from_serial[counter-serial_msg_lenght+4]=='_')){

#if defined(DEVMODE)
       Serial.println(F("onos cmd received0:"));
#endif


        for (uint8_t pointer = 0; pointer < serial_msg_lenght; pointer++) {
          second_array[pointer]=data_from_serial[counter-serial_msg_lenght+pointer];
         //Serial.println("mmm");
         //Serial.println(second_array[pointer]);
        }
       
        decodeOnosCmd(second_array);

        if((serial_message_answer=="ok_#]")||(serial_message_answer=="remote_#]")){
          char onos_cmd_type= serial_message_type_of_onos_cmd;   
          uint8_t onos_first_pin_used=serial_message_first_pin_used;
          uint8_t onos_second_pin_used=serial_message_second_pin_used;
          uint8_t onos_status_to_set=serial_message_value;


/*
         Serial.println("sn");
         Serial.println(serial_message_sn);
         Serial.println("__sn");
*/
          if (serial_message_sn==serial_number) {//onos command for this arduino node
            Serial.print("ok_local");
            counter=0;
          } 
          else{ //onos command to send to a remote node
            Serial.print("ok_remote");
            counter=0;
          }



  
        }
        else{// error decoding the serial message
     //     serial_answer="er02";
     //     Serial.print(serial_message_answer);
          break;
        }



      }
      else{//no onos_ cmd found

        serial_message_answer="nocmd1_#]";

      }




     counter=0;
     continue;
  }
 





   
  counter=counter+1;

  }

  if (enable_print==1){ //write if there is a not recognise message  shorter...

    Serial.print(serial_message_answer);
    enable_print=0;

  }
 


}

