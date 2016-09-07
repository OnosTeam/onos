#include <Arduino.h>
#ifdef HEADER_HELPERFUNC
  #define HEADER_HELPERFUNC

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
char received_serial_number[13];






///////////////////////////////////////

void decodeOnosCmd(const char *received_message,int this_node_address ,char serial_number[13]);
