#include "Arduino.h"
#include "OnosMsg.h"



OnosMsg::OnosMsg(){
  received_message_address=0;
  progressive_msg_id=0;
  rx_obj_selected=0;
  main_obj_selected=0;

}


void OnosMsg::decodeOnosCmd(char *received_message,char *decoded_result){




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


    //[S_123ga5.24WPlugAvx000810000x_#]

       
    if ( received_message_type_of_onos_cmd[0]=='g' && received_message_type_of_onos_cmd[1]=='a' ){

      strcpy(decoded_result,"ok");
      return; 
    }

    else if ( received_message_type_of_onos_cmd[0]=='u' && received_message_type_of_onos_cmd[1]=='l' ){

      strcpy(decoded_result,"ok");
      return;
    }

    else if ( received_message_type_of_onos_cmd[0]=='d' && received_message_type_of_onos_cmd[1]=='w' ){

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


