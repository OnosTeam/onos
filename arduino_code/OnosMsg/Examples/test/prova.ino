
#include <OnosMsg.h>
char str_this_node_address[4];
OnosMsg OnosMsgHandler=OnosMsg();
char received_msg;
char msg_result[24];
int this_node_address=0;
boolean first_sync;
void setup()
{
  // No setup is required for this library


char received_msg="er00_#]";
char msg_result[24]="er00_#]";
int this_node_address=254;
boolean first_sync=0;

}

void loop() 
{
 
  OnosMsgHandler.decodeOnosCmd(received_msg,msg_result);


}

