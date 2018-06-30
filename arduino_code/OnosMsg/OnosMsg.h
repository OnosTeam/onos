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








#ifndef OnosMsg_h
#define OnosMsg_h

#if ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
  #include "pins_arduino.h"
  #include "WConstants.h"
#endif




// Your class header here...
extern int this_node_address;
//extern boolean first_sync;

//extern char str_this_node_address[3];
extern uint8_t main_obj_selected;
extern uint8_t rx_obj_selected;
extern char progressive_msg_id;  //48 is 0 in ascii   //a progressive id to make each message unique
extern const uint8_t number_of_total_objects;
extern char received_serial_number[13];
extern char serial_number[13];
extern char decoded_radio_answer[];
extern int received_message_address;
extern uint8_t main_obj_selected;
extern char encript_key[17];
extern boolean reInitializeRadio;
void beginRadio(void);  //prototype of the function used in the node..
void status_change_from_msg(char,int);
extern boolean ota_loop;  //enable the ota receiver loop

class OnosMsg {
  public:
    OnosMsg();
    //volatile char *received_message_answer;
    //volatile char *received_message;

    void decodeOnosCmd(char *received_message,char *received_message_answer);
    char  hexCharToDec(char value);
    char  charDecToHex(int value);

  private:

    char received_msg_cmd_type[3];
    int received_message_value;
    int received_message_first_pin_used;
    int received_message_second_pin_used;
    uint8_t rx_obj_selected;


};

#endif
