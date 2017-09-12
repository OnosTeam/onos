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

extern volatile char str_this_node_address[4];
extern uint8_t main_obj_selected;
extern uint8_t rx_obj_selected;
extern volatile char progressive_msg_id;  //48 is 0 in ascii   //a progressive id to make each message unique
extern const uint8_t number_of_total_objects;
extern volatile char received_serial_number[13];
extern char serial_number[13];
extern volatile char decoded_radio_answer[];
extern int received_message_address;
extern uint8_t main_obj_selected;
extern char encript_key[17];
extern volatile boolean reInitializeRadio;
void beginRadio(void);  //prototype of the function used in the node..
boolean changeObjStatus(char,int);
extern volatile boolean ota_loop;  //enable the ota receiver loop

class OnosMsg {
  public:
    OnosMsg();
    volatile char *received_message_answer;
    volatile char *received_message;

    void decodeOnosCmd(char *received_message,char *received_message_answer);

  private:

    volatile char received_message_type_of_onos_cmd[3];
    volatile int received_message_value;
    volatile int received_message_first_pin_used;
    volatile int received_message_second_pin_used;

    volatile uint8_t rx_obj_selected;


};

#endif




