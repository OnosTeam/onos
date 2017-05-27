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
extern boolean first_sync;

class OnosMsg {
  public:
    OnosMsg();
    volatile char *received_message_answer;
    volatile char *received_message;

    void decodeOnosCmd(char *received_message,char *received_message_answer);


  private:

    volatile char received_message_type_of_onos_cmd[3];
    int received_message_address; //must be int..
    volatile int received_message_value;
    volatile int received_message_first_pin_used;
    volatile int received_message_second_pin_used;
    volatile uint8_t main_obj_selected;
    volatile uint8_t rx_obj_selected;
    volatile char progressive_msg_id;  //48 is 0 in ascii   //a progressive id to make each message unique

};

#endif




