#include "Arduino.h"
#include "OnosMsg.h"




OnosMsg::OnosMsg(){
        rx_obj_selected=0;
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
                
                        received_message_address=(received_message[3]-48)*100
                                                +(received_message[4]-48)*10
                                                +(received_message[5]-48)*1;
                
                if (received_message_address!=this_node_address) {//onos command for a remote arduino node
                        strcpy(decoded_result,"[S_remote_#]");
                /*
                Serial.print(F("serial_number222:")); 
                Serial.print(serial_number);
                Serial.println(F("end")); 
                */
                        return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
                }
                
                strcpy(decoded_result,"[S_er_cmdRNotfound_#]"); 
                
                received_msg_cmd_type[0]=received_message[6];
                received_msg_cmd_type[1]=received_message[7];
                
                //[S_123ga5.24WPlugAvx000810000x_#]
                
                
                if ( received_msg_cmd_type[0]=='g' && received_msg_cmd_type[1]=='a' ){
                        strcpy(decoded_result,"ok");
                        return; 
                }
                
                else if ( received_msg_cmd_type[0]=='u' && received_msg_cmd_type[1]=='l' ){
                        strcpy(decoded_result,"ok");
                        return;
                }
                
                
                //[S_123otx_#
                else if ( received_msg_cmd_type[0]=='o' && received_msg_cmd_type[1]=='t' ){
                        ota_loop=1;
                        strcpy(decoded_result,"ok");
                        return;
                }
                
                
                // [S_123dw04001_#]
                // [S_001dw04001_#]
                // [S_001dw04000_#]
                // [S_254dw04000_#]
                else if ( received_msg_cmd_type[0]=='d' && received_msg_cmd_type[1]=='w' ){
                                received_message_value=received_message[12]-48;
                        if (received_message_value>1){ 
                                strcpy(decoded_result,"[S_er0_status_#]");
                                return;
                        }
                        
                        received_message_first_pin_used= ((received_message[8])-48)*10
                                                       +(  (received_message[9])-48)*1;
                        
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
                
                //[S_001aw06125_#]
                else if( received_msg_cmd_type[0]=='a' && received_msg_cmd_type[1]=='w' ){
                        
                        received_message_value=(received_message[10]-48)*100
                                              +(received_message[11]-48)*10
                                              +(received_message[12]-48)*1;
                        
                        if ((received_message_value<0)||(received_message_value>255)){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"[S_er0_status_#]"); 
                                return;
                        }
                        
                        received_message_first_pin_used= ((received_message[8])-48)*10
                                                       +(  (received_message[9])-48)*1;
                        analogWrite(received_message_first_pin_used, received_message_value); 
                        strcpy(decoded_result,"ok");
                        return;
                } 
                
                
                //[S_001sr04051_#] 
                else if( received_msg_cmd_type[0]=='s' && received_msg_cmd_type[1]=='r' ){
                
                        received_message_value=received_message[12]-48;      
                        
                        if (received_message_value>1){ 
                                strcpy(decoded_result,"[S_er0_status_#]"); 
                                return;
                        }
                        
                        received_message_first_pin_used= ((received_message[8])-48)*10
                                                       +(  (received_message[9])-48)*1;
                                                       
                        received_message_second_pin_used=((received_message[10])-48)*10
                                                        +(  (received_message[11])-48)*1;
                        
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
                
                //[S_001ac06125_#]    #configuration analog object
                else if( received_msg_cmd_type[0]=='a' && received_msg_cmd_type[1]=='c' ){
                
                        received_message_value=(received_message[10]-48)*100
                                              +(received_message[11]-48)*10
                                              +(received_message[12]-48)*1;
                        
                        if ((received_message_value<0)||(received_message_value>255)){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                memset(decoded_result,0,sizeof(decoded_result)); //to clear the array
                                strcpy(decoded_result,"er_ac_status_#]"); 
                                return;
                        }
                        
                        rx_obj_selected= ((received_message[8])-48)*10
                                       +(  (received_message[9])-48)*1;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                Serial.println(F("er_ac_obj_number_#]"));
                                memset(decoded_result,0,sizeof(decoded_result)); //to clear the array  
                                strcpy(decoded_result,"er_ac_obj_number_#]"); 
                                return; 
                        }
                        
                        return;
                } 
                
                
                //[S_001dc001x_#]    #configuration digital object
                else if( received_msg_cmd_type[0]=='d' && received_msg_cmd_type[1]=='c' ){
                
                        received_message_value=int(received_message[10]-48);
                        
                        if (received_message_value>1){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"er_dc_status_#]"); 
                                return;
                        }
                        
                        rx_obj_selected= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                Serial.println(F("er_dc_obj_number_#]"));  
                                strcpy(decoded_result,"er_dc_obj_number_#]"); 
                                return; 
                        }
                        else{
                                changeObjStatus(rx_obj_selected,received_message_value);
                        }
                        
                        
                        return;
                } 
                
                
                
                //[S_123do001x_#]   [S_001do001x_#]    # digital object controll
                else if( received_msg_cmd_type[0]=='d' && received_msg_cmd_type[1]=='o' ){
                
                        received_message_value=(received_message[10]-48);
                        
                        if (received_message_value>1){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"er_do_status_#]"); 
                                return;
                        }
                        
                        rx_obj_selected= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
                        
                        strcpy(decoded_result,"ok");
                        
                        if (rx_obj_selected>number_of_total_objects){ //object out of the range
                                //Serial.println(F("er_do_obj_number_#]"));  
                                strcpy(decoded_result,"er_do_obj_number_#]"); 
                                return; 
                        }
                        else{
                                changeObjStatus(rx_obj_selected,received_message_value);
                        }
                        
                        
                        return;
                } 
                
                
                // [S_254sa123Wrelay4x0007_#]     [S_254sa123WreedSaa0004_#]   [S_254sa123WPlug1vx0004_#]  
                
                else if( received_msg_cmd_type[0]=='s' && received_msg_cmd_type[1]=='a' ){
                
                        received_message_value=(received_message[8]-48)*100
                                              +(received_message[9]-48)*10
                                              +(received_message[10]-48);
                        
                        
                        //todo: use  strstr to compare this and avoid making the copy array char * pch;  pch = strstr (str,"simple"); 
                        memset(received_serial_number,0,sizeof(received_serial_number)); //to clear the array 
                        
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
                                strcpy(decoded_result,"er1_sn:"); 
                                // strcat(decoded_result,"rx_sn:");
                                // strcat(decoded_result,received_serial_number);
                                //strcat(decoded_result,"_#]");
                                return;
                        } 
                        
                        
                        if ((received_message_value<0)||(received_message_value>254)){ //status check
                                received_message_value=0;
                                //Serial.println(F("onos_cmd_value_error"));  
                                strcpy(decoded_result,"er0_status_#]"); 
                                return;
                        }
                        
                        noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
                        this_node_address=received_message_value;
                        strcpy(decoded_result,"ok");
                        Serial.print(F("i will change radio address to:"));
                        Serial.println(this_node_address);
                        reInitializeRadio=1;  //to execute beginRadio()
                        interrupts();
                        //first_sync=0;
                        
                        return;
                }
                
                
                // [S_001ceProminiS0001onosEncryptKey00x_#]           "onosEncryptKey00" is the encrypt key 
                
                // [S_123ceWrelay4x0007onosEncryptKey00x_#]           "onosEncryptKey00" is the encrypt key 
                // [S_254ceWrelay4x0007onosEncryptKey00x_#]           "onosEncryptKey00" is the encrypt key 
                
                
                
                else if( received_msg_cmd_type[0]=='c' && received_msg_cmd_type[1]=='e' ){
                
                        
                        //todo: use  strstr to compare this and avoid making the copy array char * pch;  pch = strstr (str,"simple"); 
                        
                        memset(received_serial_number,0,sizeof(received_serial_number)); //to clear the array 
                        
                        received_serial_number[0]= received_message[8];
                        received_serial_number[1]= received_message[9];
                        received_serial_number[2]= received_message[10];
                        received_serial_number[3]= received_message[11];
                        received_serial_number[4]= received_message[12];
                        received_serial_number[5]= received_message[13]; 
                        received_serial_number[6]= received_message[14];
                        received_serial_number[7]= received_message[15];
                        received_serial_number[8]= received_message[16];
                        received_serial_number[9]= received_message[17];
                        received_serial_number[10]= received_message[18]; 
                        received_serial_number[11]= received_message[19];
                        
                        
                        
                        //    todo implement it!
                        if (strcmp(received_serial_number,serial_number)!=0) {//onos command not for this  node
                                strcpy(decoded_result,"er2_sn_#]"); 
                                return;
                        } 
                        
                        memset(encript_key,0,sizeof(encript_key)); //to clear the array 
                        
                        encript_key[0]= received_message[20];
                        encript_key[1]= received_message[21];
                        encript_key[2]= received_message[22];
                        encript_key[3]= received_message[23]; 
                        encript_key[4]= received_message[24];
                        encript_key[5]= received_message[25];
                        encript_key[6]= received_message[26];
                        encript_key[7]= received_message[27];
                        encript_key[8]= received_message[28]; 
                        encript_key[9]= received_message[29];
                        encript_key[10]= received_message[30];
                        encript_key[11]= received_message[31];
                        encript_key[12]= received_message[32];
                        encript_key[13]= received_message[33]; 
                        encript_key[14]= received_message[34];
                        encript_key[15]= received_message[35];
                        encript_key[16]= received_message[36];
                        
                        
                        noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
                        strcpy(decoded_result,"ok");
                        #if defined(DEVMODE)
                        Serial.print(F("[S_i will change radio address to:_#]"));
                        #endif
                        Serial.println(this_node_address);
                        reInitializeRadio=1;  //to execute beginRadio()
                        
                        #if defined(remote_node)   // only if this is a remote node.. 
                        this_node_address=254;
                        #endif
                        
                        //first_sync=0;
                        
                        return;
                }
                
                //[S_001begin_#]
                else if( received_msg_cmd_type[0]=='b' && received_msg_cmd_type[1]=='e'){
                        if( received_message[6]=='b' && received_message[7]=='e' 
                                               && received_message[8]=='g' 
                                               && received_message[9]=='i' 
                                               && received_message[10]=='n'){
                                strcpy(decoded_result,"ok");
                        }
                        else{
                                strcpy(decoded_result,"err_beg");
                        }
                        return;
                }
                
                
                
                
        
        } // end of if message start with [S_ 
        
        
        
        


}// end of decodeOnosCmd()
