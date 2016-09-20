
#include "onos_message_decode.h"
#include "Arduino.h"

char received_serial_number[13];


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




void decodeOnosCmd(const char *received_message,int this_node_address,char serial_number[13]){
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
