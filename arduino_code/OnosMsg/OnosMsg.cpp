/*
#   Copyright 2014-2018 Marco Rigoni                                          #
#   ElettronicaOpenSource.com   elettronicaopensource@gmail.com               #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU General Public License as published by      #
#   the Free Software Foundation, either version 3 of the License, or         #
#   (at your option) any later version.                                       # 
#																			  #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU General Public License for more details.                              #
#                                                                             #
#   You should have received a copy of the GNU General Public License         #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
*/

#include "Arduino.h"
#include "OnosMsg.h"



OnosMsg::OnosMsg(){
        rx_obj_selected=0;
}


char OnosMsg::hexCharToDec(char value)  // given a value in ascii hexadecimal it will return the same value in decimal
{
        value = value + 48 ; // to compensate for the -48 in the rest of the code
        switch (value) {
                case 'a' :
                        return(10);  // return 10 given 'a'
                case 'b' :
                        return(11);
                case 'c' :
                        return(12);
                case 'd' :
                        return(13);
                case 'e' :
                        return(14);
                case 'f' :
                        return(15);
                default:
                        return(value - 48 ); // if the value is not > 9 return it as it is
                    
        }

}

char OnosMsg::charDecToHex(int value)  // given a value in ascii hexadecimal it will return the same value in decimal
{
     
        switch (value) {
                case 10 :
                        return('a');  // return 10 given 'a'
                case 11 :
                        return('b');
                case 12 :
                        return('c');
                case 13 :
                        return('d');
                case 14 :
                        return('e');
                case 15 :
                        return('f');
                default:
                        return(value + '0'); // if the value is not > 9 return it as it is
                    
        }

}

void OnosMsg::decodeOnosCmd(char *received_message,char *decoded_result)
{
        
        /*
        Serial.print("decodeOnosCmd() executed with this_node_address:"); 
        Serial.print(this_node_address);
        Serial.println(F("end")); 
        
        printf("decodeOnosCmd");
        */
        
        
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
        memset(decoded_result,0,sizeof(decoded_result)); //to clear the array
        strcpy(decoded_result,"[S_err01_#]");
        
        
        if ((received_message[0]=='[')&&(received_message[1]=='S')
                                      &&(received_message[2]=='_') ) {
        // the onos cmd was found           [S_001dw06001_#]
                
                received_message_address=hexCharToDec(received_message[3]-48)*16
                                        +hexCharToDec(received_message[4]-48);
                //Serial.print(F("received_message_address:")); 
                //Serial.println(received_message_address); 


                
                if (received_message_address!=this_node_address) {//onos command for a remote arduino node
                        strcpy(decoded_result,"[S_remote_#]");
                /*
                Serial.print(F("serial_number222:")); 
                Serial.print(serial_number);
                Serial.println(F("end")); 
                */
                        return; //return because I don't need to decode the message..I need to retrasmit it to another node or OnosCenter.
                }
                
                strcpy(decoded_result,"[S_er_cmdRNotfound_#]"); 
                
                received_msg_cmd_type[0]=received_message[5];
                
                //[S_123ga5.24WPlugAvx000810000x_#]
                
                
                if ( received_msg_cmd_type[0]=='g' ){
                        strcpy(decoded_result,"ok");
                        return; 
                }
                
                else if ( received_msg_cmd_type[0]=='u' ){
                        strcpy(decoded_result,"ok");
                        return;
                }
                
                
                //[S_123otx_#
                else if ( received_msg_cmd_type[0]=='o' ){
                        ota_loop=1;
                        strcpy(decoded_result,"ok");
                        return;
                }
                
                
                // [S_13D040x_#]
                // [S_01D041x_#]
                // [S_01D040x_#]
                // [S_04D041x_#]
                else if ( received_msg_cmd_type[0]=='D' ){    // totest   # digital pin controll
                                received_message_value=received_message[8]-48;
                        if (received_message_value>1){ 
                                strcpy(decoded_result,"[S_erD_status_#]");
                                return;
                        }
                        
                        received_message_first_pin_used= ((received_message[6])-48)*10
                                                       +(  (received_message[7])-48)*1;
                        
                        pinMode(received_message_first_pin_used, OUTPUT); 
                        digitalWrite(received_message_first_pin_used, received_message_value); 
                        strcpy(decoded_result,"ok");
                        /*
                        Serial.print("decodeOnosCmd() dw executed with received_message_first_pin_used :"); 
                        Serial.print(received_message_first_pin_used);
                        Serial.print("status=:"); 
                        Serial.print(received_message_value);
                        */
                        return;
                }
                
                //[S_08a06ffx_#]   # analog object controll
                else if( received_msg_cmd_type[0]=='a' ){   // totest
                        
                        received_message_value = hexCharToDec(received_message[8] - 48) * 16
                                               + hexCharToDec(received_message[9] - 48);
                        
                        if ((received_message_value<0)||(received_message_value>255)){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"[S_era_status_#]"); 
                                return;
                        }
                        
                        received_message_first_pin_used= ((received_message[8])-48)*10
                                                       +(  (received_message[9])-48)*1;
                        analogWrite(received_message_first_pin_used, received_message_value); 
                        strcpy(decoded_result,"ok");
                        return;
                } 
                
                
                //[S_01r04051x_#] 
                else if( received_msg_cmd_type[0]=='r' ){  // totest
                
                        received_message_value=received_message[10]-48;      
                        
                        if (received_message_value>1){ 
                                strcpy(decoded_result,"[S_err_status_#]"); 
                                return;
                        }
                        
                        received_message_first_pin_used= ((received_message[6])-48)*10
                                                       +(  (received_message[7])-48)*1;
                                                       
                        received_message_second_pin_used=((received_message[8])-48)*10
                                                        +(  (received_message[9])-48)*1;
                        
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
                
                //[S_05C0612x_#]    #configuration analog object  totest
                else if( received_msg_cmd_type[0]=='C' ){
                
                        received_message_value=hexCharToDec(received_message[8]-48)*16
                                              +hexCharToDec(received_message[9]-48);
                        if ((received_message_value<0)||(received_message_value>255)){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                memset(decoded_result,0,sizeof(decoded_result)); //to clear the array
                                strcpy(decoded_result,"er_ac_status_#]"); 
                                return;
                        }
                        
                        rx_obj_selected= ((received_message[6])-48)*10
                                       + (received_message[7])-48;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                Serial.println(F("er_ac_obj_number_#]"));
                                memset(decoded_result,0,sizeof(decoded_result)); //to clear the array  
                                strcpy(decoded_result,"er_ac_obj_number_#]"); 
                                return; 
                        }
                        
                        return;
                } 
                
                
                //[S_05c001x_#]    #configuration digital object   
                else if( received_msg_cmd_type[0]=='c'){
                
                        received_message_value=int(received_message[8]-48);
                        
                        if (received_message_value>1){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"er_dc_status_#]"); 
                                return;
                        }
                        
                        rx_obj_selected= ((received_message[6])-48)*10+(  (received_message[7])-48)*1;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                //Serial.println(F("er_dc_obj_number_#]"));  
                                strcpy(decoded_result,"er_dc_obj_number_#]"); 
                                return; 
                        }
                        else{
                                status_change_from_msg(rx_obj_selected,received_message_value);
                        }
                        
                        
                        return;
                } 

                //[S_08a06ffx_#]     # analog object controll      
                else if( received_msg_cmd_type[0]=='a'){
                
                        received_message_value = hexCharToDec(received_message[8] - 48) * 16
                                               + hexCharToDec(received_message[9] - 48); 
                                                                      
                        if ((received_message_value<0)||(received_message_value>255)){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"[S_era_status_#]"); 
                                return;
                        }

                        rx_obj_selected = ((received_message[6])-48)*10+(  (received_message[7])-48)*1;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                //Serial.println(F("er_do_obj_number_#]"));  
                                strcpy(decoded_result,"er_ao_obj_number_#]"); 
                                return; 
                        }
                        else{
                                status_change_from_msg(rx_obj_selected,received_message_value); 
                                // todo: make this return 0 or 1 to tell if the operation was completed.
                        }

                        return;
                } 
                //[S_12d001x_#]   [S_0ad001x_#]    # digital object controll      0a is the address 10
                else if( received_msg_cmd_type[0]=='d'){
                
                        received_message_value=(received_message[8]-48);
                        
                        if (received_message_value>1){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"er_do_status_#]"); 
                                return;
                        }
                        
                        rx_obj_selected= ((received_message[6])-48)*10+(  (received_message[7])-48)*1;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                //Serial.println(F("er_do_obj_number_#]"));  
                                strcpy(decoded_result,"er_do_obj_number_#]"); 
                                return; 
                        }
                        else{
                                status_change_from_msg(rx_obj_selected,received_message_value); 
                                // todo: make this return 0 or 1 to tell if the operation was completed.
                        }
                        
                        
                        return;
                } 

                // [S_fes02Wrelay4x0007x_#]     [S_fes02WPlug1vx0001x_#]
                
                else if( received_msg_cmd_type[0]=='s'){   // set address to this node
                
                        received_message_value = hexCharToDec(received_message[6]-48)*16
                                               + hexCharToDec(received_message[7]-48);


                        //todo: use  strstr to compare this and avoid making the copy array char * pch;  pch = strstr (str,"simple"); 
                        memset(received_serial_number,0,sizeof(received_serial_number)); //to clear the array 
                        
                        received_serial_number[0] = received_message[8];
                        received_serial_number[1] = received_message[9];
                        received_serial_number[2] = received_message[10];
                        received_serial_number[3] = received_message[11];
                        received_serial_number[4] = received_message[12];
                        received_serial_number[5] = received_message[13]; 
                        received_serial_number[6] = received_message[14];
                        received_serial_number[7] = received_message[15];
                        received_serial_number[8] = received_message[16];
                        received_serial_number[9] = received_message[17];
                        received_serial_number[10] = received_message[18]; 
                        received_serial_number[11] = received_message[19];



                        //    todo implement it!
                        if (strcmp(received_serial_number,serial_number)!=0) {//onos command not for this  node
                                strcpy(decoded_result,"er1_sn:"); 
                                // strcat(decoded_result,"rx_sn:");
                                // strcat(decoded_result,received_serial_number);
                                //strcat(decoded_result,"_#]");
                                return;
                        } 
                        
                        
                        if ((received_message_value<0)||(received_message_value>254)){ //status check
                                /*
                                Serial.print(F("received_message_value:"));
                                Serial.println(received_message_value);
                                Serial.print(F("received_message[6]:"));
                                Serial.println(received_message[6]-48);
                                Serial.print(F("received_message[7]:"));
                                Serial.println(received_message[7]-48);
                                
                                Serial.print(F("hex received_message[6]:"));
                                Serial.println(hexCharToDec(received_message[6]-48));
                                Serial.print(F("hex received_message[7]:"));
                                Serial.println(hexCharToDec(received_message[7]-48));
                                */
                                received_message_value=0;
                                strcpy(decoded_result,"[S_ers_status_#]"); 
                                return;
                        }
                        
                        noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
                        this_node_address=received_message_value;
                        strcpy(decoded_result,"ok");
                        //Serial.print(F("i will change radio address to:"));
                        //Serial.println(this_node_address);
                        reInitializeRadio=1;  //to execute beginRadio()
                        interrupts();
                        //first_sync=0;
                        
                        return;
                }


                // [S_01eProminiS0001onosEncryptKey00x_#]           "onosEncryptKey00" is the encrypt key 
                
                // [S_23eWrelay4x0007onosEncryptKey00x_#]           "onosEncryptKey00" is the encrypt key 
                // [S_feeWrelay4x0007onosEncryptKey00x_#]           "onosEncryptKey00" is the encrypt key 
                
                
                
                else if( received_msg_cmd_type[0]=='e' ){  //todo   set encrypt key to this node
                
                        
                        //todo: use  strstr to compare this and avoid making the copy array char * pch;  pch = strstr (str,"simple"); 
                        
                        memset(received_serial_number,0,sizeof(received_serial_number)); //to clear the array 
                        
                        received_serial_number[0] = received_message[6];
                        received_serial_number[1] = received_message[7];
                        received_serial_number[2] = received_message[8];
                        received_serial_number[3] = received_message[9];
                        received_serial_number[4] = received_message[10];
                        received_serial_number[5] = received_message[11]; 
                        received_serial_number[6] = received_message[12];
                        received_serial_number[7] = received_message[13];
                        received_serial_number[8] = received_message[14];
                        received_serial_number[9] = received_message[15];
                        received_serial_number[10] = received_message[16]; 
                        received_serial_number[11] = received_message[17];



                        //    todo implement it!
                        if (strcmp(received_serial_number,serial_number)!=0) {//onos command not for this  node
                                strcpy(decoded_result,"er2_sn_#]"); 
                                return;
                        } 

                        memset(encript_key,0,sizeof(encript_key)); //to clear the array 

                        encript_key[0] = received_message[18];
                        encript_key[1] = received_message[19];
                        encript_key[2] = received_message[20];
                        encript_key[3] = received_message[21]; 
                        encript_key[4] = received_message[22];
                        encript_key[5] = received_message[23];
                        encript_key[6] = received_message[24];
                        encript_key[7] = received_message[25];
                        encript_key[8] = received_message[26]; 
                        encript_key[9] = received_message[27];
                        encript_key[10] = received_message[28];
                        encript_key[11] = received_message[29];
                        encript_key[12] = received_message[30];
                        encript_key[13] = received_message[31]; 
                        encript_key[14] = received_message[32];
                        encript_key[15] = received_message[33];
                        encript_key[16] = '\0';
                        //encript_key[16] = received_message[34];


                        noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
                        strcpy(decoded_result,"ok");
                        #if defined(DEVMODE)
                          Serial.print(F("[S_i will change radio address to:_#]"));
                          Serial.println(this_node_address);
                        #endif
                        
                        reInitializeRadio=1;  //to execute beginRadio()
                        
                        #if defined(remote_node)   // only if this is a remote node.. 
                          this_node_address=254;
                        #endif
                        
                        //first_sync=0;
                        
                        return;
                }
                
                //[S_01begin_#]
                else if( received_msg_cmd_type[0]=='b' ) {  //todo
                        if( received_message[5]=='b' && received_message[6]=='e' 
                                               && received_message[7]=='g' 
                                               && received_message[8]=='i' 
                                               && received_message[9]=='n'){
                                strcpy(decoded_result,"ok");
                        }
                        else{
                                strcpy(decoded_result,"err_beg");
                        }
                        return;
                }

                else if( received_msg_cmd_type[0]=='m' ){  //mars rover
/*
// the mars rover will have 8 objects for the wheels movement 
// 4 digital objects to tell if each wheels motors should move forward or backward
// 4 analog objects to tell the pwm value each motor should use,(for speed controll, from 0 to 255)
// 4 analog object to tell the pivoting servos what angle they should move to (from 0 to 180 degrees)

// there will be a coded message to compress all this data in a single message: 

//  [S_famDAoAoAoAoSoSoSoSox_#]    
//  Where:
//  The fa is the 250 address...
//  The m stand for mars rover
//  The D is a binary where the last 4 bits are the digital object to tell if each wheels motors should move forward(1) or backward(0) 
//  Each Ao is  a hex of the 4 analog objects to tell the pwm value each motor should use,(for speed controll, from 0 to 255)
//  Each So is a hex of the 4 analog object to tell the pivoting servos what angle they should move to (from 0 to 180 degrees)
*/
                
                        byte motors_directions_byte = received_message[6];
                        
                        int motor0_direction = motors_directions_byte & B00000001;
                        
                        int motor1_direction = motors_directions_byte & B00000010;

                        int motor2_direction = motors_directions_byte & B00000100;
                        
                        int motor3_direction = motors_directions_byte & B00001000;
                        
                                        
                        int motor0_speed = hexCharToDec(received_message[7]-48)*16
                                              +hexCharToDec(received_message[8]-48);

                        int motor1_speed = hexCharToDec(received_message[9]-48)*16
                                              +hexCharToDec(received_message[10]-48);

                        int motor2_speed = hexCharToDec(received_message[11]-48)*16
                                              +hexCharToDec(received_message[12]-48);
                                              
                        int motor3_speed = hexCharToDec(received_message[13]-48)*16
                                              +hexCharToDec(received_message[14]-48);
                                              
                                              
                        int motor0_orientation_angle = hexCharToDec(received_message[15]-48)*16
                                              +hexCharToDec(received_message[16]-48);   
                                              
                        int motor1_orientation_angle = hexCharToDec(received_message[17]-48)*16
                                              +hexCharToDec(received_message[18]-48);   
                                              
                        int motor2_orientation_angle = hexCharToDec(received_message[19]-48)*16
                                              +hexCharToDec(received_message[20]-48);   
                                              
                        int motor3_orientation_angle = hexCharToDec(received_message[21]-48)*16
                                              +hexCharToDec(received_message[22]-48);                                                                                                                                             
                        
                        int buttons0 = received_message[22];
                        
                        int buttons1 = received_message[23];
                        
                        int cross_button_status = bitRead(buttons0, 0) ;
                        
                        int square_button_status =  bitRead(buttons0, 1) ;

                        int circle_button_status =  bitRead(buttons0, 2) ;
         
                        int triangle_button_status =  bitRead(buttons0, 3) ;
                        
                        
                        int l1_button_status = bitRead(buttons1, 0) ;
                        
                        int r1_button_status = bitRead(buttons1, 1) ;

                        int l2_button_status = bitRead(buttons1, 2) ;
         
                        int r2_button_status = bitRead(buttons1, 3) ;                       
                                                
                        int l3_button_status = bitRead(buttons1, 4) ;

                        int r3_button_status = bitRead(buttons1, 5) ;
         
                        int start_button_status = bitRead(buttons1, 6) ;                         
                       
                        int select_button_status = bitRead(buttons1, 7) ;                          
                      
                       
                       
                       
                        if ((buttons0 | B11101111) == B11101111){ //up arrow
                                __asm__("nop\n\t"); //nop just to fill this if ... 
                        }
                        else if ((buttons0 | B01111111) == B01111111){ //down arrow
                                __asm__("nop\n\t"); //nop just to fill this if ... 
                        }
                        else if ((buttons0 | B11011111) == B11011111){ //right arrow
                                __asm__("nop\n\t"); //nop just to fill this if ... 
                        }
                        
                        else if ((buttons0 | B10111111) == B10111111){ //left arrow
                                __asm__("nop\n\t"); //nop just to fill this if ... 
                        }
                        
                        else if ((buttons0 | B00001111) == B11111111){ //no arrow pressed
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }
                        
                        else if ((buttons0 | B00001111) == B11111111){ //no arrow pressed
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

/*
                        if ((buttons0 | B11111110) == B11111111){ // x pressed
                                changeObjStatus(12,motor0_direction);
                        }

                        if ((buttons0 | B11111101) == B11111111){ //square pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons0 | B11111011) == B11111111){ //circle pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons0 | B11110111) == B11111111){ //triangle pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        
                        if ((buttons1 | B11111110) == B11111111){ // l1 pressed
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons1 | B11111101) == B11111111){ //r1 pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons1 | B11111011) == B11111111){ //l2 pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons0 | B11110111) == B11111111){ //r2 pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }       

                        if ((buttons1 | B11101111) == B11111111){ // l3 pressed
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons1 | B11011111) == B11111111){ //r3 pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons1 | B10111111) == B11111111){ //start pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }

                        if ((buttons0 | B01111111) == B11111111){ //select pressed 
                                __asm__("nop\n\t"); //nop just to fill this if ... 

                        }        
*/

                        changeObjStatus(12,cross_button_status);
                                                              
                        changeObjStatus(0,motor0_direction);
                        changeObjStatus(1,motor1_direction);
                        changeObjStatus(2,motor2_direction);
                        changeObjStatus(3,motor3_direction);
                                                                                                        
                        changeObjStatus(4,motor0_speed);
                        changeObjStatus(5,motor1_speed);
                        changeObjStatus(6,motor2_speed);
                        changeObjStatus(7,motor3_speed);
                        
                        changeObjStatus(8 ,motor0_orientation_angle);
                        changeObjStatus(9 ,motor1_orientation_angle);
                        changeObjStatus(10,motor2_orientation_angle);
                        changeObjStatus(11,motor3_orientation_angle);                                        
                        
                        strcpy(decoded_result,"ok");
                        
                        
                        return;
                } 


        } // end of if message start with [S_ 




}// end of decodeOnosCmd()
