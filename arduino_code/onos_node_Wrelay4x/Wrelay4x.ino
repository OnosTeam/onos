/*
 * O.N.O.S.  arduino WlightVx node  firmware by Marco Rigoni 9-11-16  onos.info@gmail.com 
 * more info on www.myonos.com 
 *
 */


/*


/*
*                  Arduino      RFM69W
*                  GND----------GND   (ground in)
*                  3V3----------3.3V  (3.3V in)
*  interrupt 0 pin D2-----------DIO0  (interrupt request out)
*              pin D9-----------RST   (radio module reset)   
*           SS pin D10----------NSS   (chip select in)
*          SCK pin D13----------SCK   (SPI clock in)
*         MOSI pin D11----------MOSI  (SPI Data in)
*         MISO pin D12----------MISO  (SPI Data out)
                   D3 ----------switch	
                   D5 ----------led
                   D6 ----------1 simple relay
                   D7 ----------1 simple relay
                   D8 ----------1 simple relay
                   D9 ----------1 simple relay
                    

*/




/* RFM69 library and code by Felix Rusu - felix@lowpowerlab.com
// Get libraries at: https://github.com/LowPowerLab/
// Make sure you adjust the settings in the configuration section below !!!
// **********************************************************************************
// Copyright Felix Rusu, LowPowerLab.com
// Library and code by Felix Rusu - felix@lowpowerlab.com
// **********************************************************************************
// License
// **********************************************************************************
// This program is free software; you can redistribute it 
// and/or modify it under the terms of the GNU General    
// Public License as published by the Free Software       
// Foundation; either version 3 of the License, or        
// (at your option) any later version.                    
//                                                        
// This program is distributed in the hope that it will   
// be useful, but WITHOUT ANY WARRANTY; without even the  
// implied warranty of MERCHANTABILITY or FITNESS FOR A   
// PARTICULAR PURPOSE. See the GNU General Public        
// License for more details.                              
//                                                        
// You should have received a copy of the GNU General    
// Public License along with this program.
// If not, see <http://www.gnu.org/licenses></http:>.
//                                                        
// Licence can be viewed at                               
// http://www.gnu.org/licenses/gpl-3.0.txt
//
// Please maintain this license information along with authorship
// and copyright notices in any redistribution of this code
// **********************************************************************************/
 
#include <RFM69.h>    //get it here: https://www.github.com/lowpowerlab/rfm69
#include <SPI.h>
#include <RFM69_ATC.h> 
#include <EEPROM.h>
#include <OnosMsg.h>
//*********************************************************************************************
// *********** IMPORTANT SETTINGS - YOU MUST CHANGE/CONFIGURE TO FIT YOUR HARDWARE *************
//*********************************************************************************************
#define NETWORKID     100  //the same on all nodes that talk to each other

 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
#define FREQUENCY     RF69_868MHZ
//define FREQUENCY      RF69_433MHZ
#define INITENCRYPTKEY     "onosEncryptKey00" //exactly the same 16 characters/bytes on all nodes!
#define IS_RFM69HCW    true // set to 'true' if you are using an RFM69HCW module
 
//*********************************************************************************************
#define SERIAL_BAUD   115200
 
#define RFM69_CS      10
#define RFM69_IRQ     2
#define RFM69_IRQN    0  // Pin 2 is IRQ 0!
#define RFM69_RST     9


#define ATC_RSSI      -75   //power signal from -30(stronger) to -95(weaker) 
#define targetRSSI    -40

#define remote_node   //tell the compiler that this is a remote node
//#define local_node  //tell the compiler that this is a local node
 
int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;



boolean radio_enabled=1;

unsigned long sync_time=0;

char serial_number[13]="Wrelay4x0007";
char node_fw[]="5.27";
char encript_key[17]="onosEncryptKey01";  //todo read it from eeprom
char init_encript_key[17]=INITENCRYPTKEY;
int this_node_address=254; //i start with 254

volatile int old_address=254; 

unsigned long get_address_timeout=0;

volatile unsigned long button_time_same_status=0;

volatile boolean button_still_same_status=1; 

/*
WPlugAvx node parameter:
  relay1_set_pin     --> the pin where the first relay set coil is connected
  relay1_reset_pin     --> the pin where the first relay set coil is connected

  relay2_set_pin     --> the pin where the second relay set coil is connected
  relay2_reset_pin     --> the pin where the second relay set coil is connected
  main_obj_state    --> the state of the main_obj (turned on "1" ,turned off "0")  will be sent to onos with sync and each time it changes
  time_on       --> total time of the main_obj was on from when the arduino was turned on,will be sent with each sync
  time_from_turn_on --> variable used to store the millis() when the main_obj was turned on.
  time_continuos_on --> seconds since the main_obj is on (if is on now otherwise is 0) 

*/


//////////////////////////////////Start of Standard part to run decodeOnosCmd()//////////////////////////////////
#define rx_msg_lenght 61
int onos_cmd_start_position=-99;  
int onos_cmd_end_position=-99;  
char received_message_type_of_onos_cmd[3];
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;
//volatile char decoded_uart_answer[24]="er00_#]";
volatile char decoded_radio_answer[24]="er00_#]";
int received_message_address=0; //must be int..
volatile char filtered_uart_message[rx_msg_lenght+3];
volatile char filtered_radio_message[rx_msg_lenght+3];
volatile char syncMessage[28];
volatile char str_this_node_address[4];
uint8_t main_obj_selected=0;
uint8_t rx_obj_selected=0;
volatile char progressive_msg_id=48;  //48 is 0 in ascii   //a progressive id to make each message unique
volatile char received_serial_number[13];
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////
// node object pinuot//

// define object numbers to use in the pin configuration warning this is not the pinout numbers
#define relay1  0
#define relay2  1
#define relay3  2
#define relay4  3
#define button  4
#define led     5
const uint8_t number_of_total_objects=7;      // 7 because there are 6 elements + a null 

uint8_t node_obj_pinout[number_of_total_objects];  // 6  objects 4 relay 1 button and a led  made 7 to store the last element as void for array in c..
uint8_t node_obj_status[number_of_total_objects];  // 6  objects 4 relay 1 button and a led  made 7 to store the last element as

uint8_t obj_button_pin;
//end node object pinuot, continue in setup() // 

OnosMsg OnosMsgHandler=OnosMsg();  //create the OnosMsg object

uint8_t radioRetry=3;      //todo: make this changable from serialport
uint8_t radioTxTimeout=20;  //todo: make this changable from serialport

# define gateway_address 1
boolean first_sync=1;
int random_time=0;


unsigned long time_continuos_on=0;
unsigned long time_since_last_sync=0;
unsigned long time_from_turn_on=0;
float minutes_time_from_turn_on;
char tmp_minutes_time_from_turn_on_array[5];
char minutes_time_from_turn_on_array[5];

int timeout_to_turn_off=0;//0=disabled    600; //10 hours    todo   add the possibility to set it from remote

uint8_t skipRadioRxMsg=0;
uint8_t skipRadioRxMsgThreshold=5;
boolean radio_msg_to_decode_is_avaible=0;

volatile char main_obj_state=0;
//int old_main_obj_state=5;



unsigned long time_to_reset_encryption=3000; //this must be greater than time_to_change_status 
unsigned long time_to_change_status=30;


int tmp_number;
volatile uint8_t tryed_times;
uint8_t counter;
uint8_t pointer;
/*

const float VccExpected   = 3.0;
const float VccCorrection = 2.860/2.92;  // Measured Vcc by multimeter divided by reported Vcc
Vcc vcc(VccCorrection);
static int oldBatteryPcnt = 0;
*/



int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}




boolean changeObjStatus(char obj_number,int status_to_set){

   Serial.print("changeObjStatus executed with  status:");
   Serial.println(status_to_set);

  if (obj_number!=button){ //will not change the status to the button...

    digitalWrite(node_obj_pinout[obj_number],!status_to_set); // !  is only for this hardware since the ralay are actived low..

    if (obj_number==0){
      main_obj_state=status_to_set;
      changeObjStatus(led,!status_to_set);
    }


    node_obj_status[obj_number]=status_to_set;

    return(1);
  }






return(0);

}


void composeSyncMessage(){

  Serial.println("composeSyncMessage executed");
  //[S_123ul5.24WPlugAvx000810000x_#]

  if (progressive_msg_id<122){  //122 is z in ascii
    progressive_msg_id=progressive_msg_id+1;
  }
  else{
    progressive_msg_id=48;  //48 is 0 in ascii
  }

  if (main_obj_state==1){
      
    if (time_continuos_on!=0){
      time_from_turn_on=time_from_turn_on+(millis()-time_continuos_on);
      time_since_last_sync=millis();  // to implement...
    }

  }

 // char char_main_obj_state[2];
 // char_main_obj_state[0]=main_obj_state+48;





  minutes_time_from_turn_on=0;  //time_from_turn_on/60000; //get minutes from milliseconds  todo set it correctly..


  if( minutes_time_from_turn_on>9999) {//banana todo change it in some way...
    minutes_time_from_turn_on=0;

  }





  memset(tmp_minutes_time_from_turn_on_array,0,sizeof(tmp_minutes_time_from_turn_on_array)); //to clear the array
  memset(minutes_time_from_turn_on_array,0,sizeof(minutes_time_from_turn_on_array)); //to clear the array
 
  //itoa (minutes_time_from_turn_on,minutes_time_from_turn_on_array,10);  //convert from int to char array
  //dtostrf  //convert from float to char array
  if (minutes_time_from_turn_on<10){
    dtostrf(minutes_time_from_turn_on,1, 0, tmp_minutes_time_from_turn_on_array);
    strcpy(minutes_time_from_turn_on_array,"000");
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }

  else if (minutes_time_from_turn_on<100){
    dtostrf(minutes_time_from_turn_on,2, 0, tmp_minutes_time_from_turn_on_array);
    strcpy(minutes_time_from_turn_on_array,"00");
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }

  else if (minutes_time_from_turn_on<1000){
    dtostrf(minutes_time_from_turn_on,3, 0, tmp_minutes_time_from_turn_on_array);
    strcpy(minutes_time_from_turn_on_array,"0");
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }

  else if (minutes_time_from_turn_on<10000){
    dtostrf(minutes_time_from_turn_on,4, 0, tmp_minutes_time_from_turn_on_array);
    strcat(minutes_time_from_turn_on_array,tmp_minutes_time_from_turn_on_array);
  }



  //snprintf(minutes_time_from_turn_on_array, 5, "%d", minutes_time_from_turn_on); //convert from float to char array

  

  tmp_number=0;
  //strcpy(str_this_node_address,"");
  memset(str_this_node_address,0,sizeof(str_this_node_address)); //to clear the array
  str_this_node_address[0]='0';
  str_this_node_address[1]='0';
  str_this_node_address[2]='0';

  if (this_node_address>99){
    str_this_node_address[0]=(this_node_address/100)+48;
    tmp_number=this_node_address%100;
    str_this_node_address[1]=(tmp_number/10)+48;
    tmp_number=this_node_address%10; 
    str_this_node_address[2]=tmp_number+48;

  }

  else if (this_node_address>9){
    str_this_node_address[1]=(tmp_number/10)+48;
    tmp_number=this_node_address%10; 
    str_this_node_address[2]=tmp_number+48;

  }
  else{ 
    str_this_node_address[2]=this_node_address+48;
  }
  

  //strcpy(syncMessage, "");
  memset(syncMessage,0,sizeof(syncMessage)); //to clear the array
  strcpy(syncMessage, "[S_");
  strcat(syncMessage, str_this_node_address);


  if (first_sync==1 ){
    strcat(syncMessage, "ga");
    strcat(syncMessage, node_fw);
  }
  else{
    strcat(syncMessage, "ul");

  }

 // strcat(syncMessage, "sy");
  strcat(syncMessage, serial_number);
  

    //[S_123ul5.24WPlugAvx000810000x_#]

/*
  if (main_obj_state==0){
    strcat(syncMessage,"0");
  }
  else{
    strcat(syncMessage,"1");
  }
*/
  syncMessage[strlen(syncMessage)]=main_obj_state+48;   //+48 for ascii translation


  Serial.print("composeSyncMessage executed with  status:");
  Serial.println(main_obj_state);


  strcat(syncMessage, minutes_time_from_turn_on_array);
  syncMessage[strlen(syncMessage)]=progressive_msg_id; //put the variable msgid in the array 
  //Serial.println(syncMessage[28]);
  //Serial.println(strlen(syncMessage));
  strcat(syncMessage, "_#]");
  




}



void sendSyncMessage(uint8_t retry,uint8_t tx_timeout=150){

  composeSyncMessage();
  

  if (first_sync!=1 ){
    syncMessage[6]='u'; //modify the message
    syncMessage[7]='l'; //modify the message
  }




  Serial.println(" sendWithRetry sendSyncMessage executed");
  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage),retry,tx_timeout)) {
    // note that the max delay time is 255..because is uint8_t
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)
    Serial.println("sent_sync_message1");
//    Blink(LED, 50, 3); //blink LED 3 times, 50ms between blinks
    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
  }

  radio.receiveDone(); //put radio in RX mode
}




void getAddressFromGateway(){
   Serial.println("getAddressFromGateway executed");

  //[S_123ga5.24WPlugAvx000810000x_#]

  composeSyncMessage();
  syncMessage[6]='g'; //modify the message to get a address instead of just sync.
  syncMessage[7]='a'; //modify the message to get a address instead of just sync.

  Serial.println(" sendWithRetry getAddressFromGateway executed");


  Serial.print("msg send:"); 

  for (pointer = 0; pointer <= 35; pointer++) {
    Serial.print(syncMessage[pointer]); 
    if ((syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ) {//  
      break;
    }

  }
  Serial.println("msg end:"); 

  tryed_times=0;
  while (tryed_times < radioRetry ){
    Serial.println(F("radio tx start"));

    if (radio.sendWithRetry(gateway_address, syncMessage,strlen(syncMessage),1,radioTxTimeout)) {
      // note that the max delay time is 255..because is uint8_t
      //target node Id, message as string or byte array, message length,retries, milliseconds before retry
      //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)

      Serial.println("sent_get_address");
    /*
    for (char a=0;a<(35);a=a+1){
      Serial.print(syncMessage[a]);
    }
    Serial.println("end_get_address"); 
    */


      skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
      break;// exit the while (tryed_times < radioRetry )
    }
    else{
      Serial.print(F("radio tx failed, I retry"));
      random_time=10;//random(10,radioTxTimeout*3);
      tryed_times=tryed_times+1;
      delay(random_time);
    }


  }

  syncMessage[6]='u'; //modify the message
  syncMessage[7]='l'; //modify the message


  radio.receiveDone(); //put radio in RX mode
   

}




boolean checkAndHandleIncomingRadioMsg(){

  if (radio.receiveDone()){

    skipRadioRxMsg=skipRadioRxMsg+1;


    //print message received to serial
    Serial.print(" id:");
    Serial.println(radio.SENDERID);
    Serial.print((char*)radio.DATA);
    Serial.print("   [RX_RSSI:");Serial.print(radio.RSSI);Serial.print("]");

 
    //check if received message contains Hello World

    //uint8_t message_copy[rx_msg_lenght+1];

    //strcpy(filtered_radio_message,"");
    //memset(filtered_radio_message,0,sizeof(filtered_radio_message)); //to clear the array

    //Serial.println(radio.SENDERID);
    if (radio.TARGETID!=this_node_address){
      Serial.println(F("[S_er9_radioAddress_#]"));
      return(0); // todo: implement a forward of the message? 
    }

    Serial.print("msg_start:");

    onos_cmd_start_position=-99;  
    onos_cmd_end_position=-99;  

      //strcpy(filtered_radio_message,"");
    memset(filtered_radio_message,0,sizeof(filtered_radio_message)); //to clear the array

    Serial.println(radio.TARGETID);
    
    if (radio.TARGETID!=this_node_address){
      Serial.println(F("[S_er9_radioAddress_#]"));
      return(0); // todo: implement a forward of the message? 
    }
    

    //for (uint8_t counter = 0; counter <= rx_msg_lenght; counter++) {

    for (counter = 0; counter <= radio.DATALEN; counter++) {
      filtered_radio_message[counter]=radio.DATA[counter];
      //  Serial.println(filtered_radio_message[counter]);

    //[S_001dw06001_#]
      if (counter<2){
        continue;
      }
      if ( (filtered_radio_message[counter-2]=='[')&&(filtered_radio_message[counter-1]=='S')&&(filtered_radio_message[counter]=='_')  ){//   
       // Serial.println("cmd start found-------------------------------");
        onos_cmd_start_position=counter-2;
      }


      if( (filtered_radio_message[counter-2]=='_')&&(filtered_radio_message[counter-1]=='#')&&(filtered_radio_message[counter]==']')  ){//   
        //  Serial.println("cmd end found-------------------------------");
        onos_cmd_end_position=counter-2;
        break;// now the message has ended
      }


    }


    Serial.println(":msg_stop");


    if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){

      Serial.println("onos cmd  found-------------------------------");
      //noInterrupts(); // Disable interrupts    //important for lamp node 
      //decodeOnosCmd(filtered_radio_message);
      OnosMsgHandler.decodeOnosCmd(filtered_radio_message,decoded_radio_answer);




      if( (decoded_radio_answer[0]=='o')&&(decoded_radio_answer[1]=='k')){//if the message was ok...
      //check if sender wanted an ACK
        if (radio.ACKRequested()){
          radio.sendACK();
          Serial.println(" - ACK sent");
          sync_time=millis();
        }
        //interrupts(); // Enable interrupts
      return(1); 

      }
      else{
        Serial.print("error in message decode i will not send the ACK,i found:");
        Serial.print(decoded_radio_answer[0]);
        Serial.print(decoded_radio_answer[1]);
        Serial.print(decoded_radio_answer[2]);
        Serial.print(decoded_radio_answer[3]);
        Serial.println(decoded_radio_answer[4]);
        return(0); 

       // checkCurrentRadioAddress(); //if the mesage received is wrong i will check and send a address request if needed becausethe onos gateway will wait a moment after the tranmission failure.

        //interrupts(); // Enable interrupts 
      }

    //interrupts(); // Enable interrupts
    
    }
    else{
      strcpy(decoded_radio_answer,"nocmd0_#]");
      Serial.print("error in message nocmd0_#]");
      Serial.print(onos_cmd_start_position);
      Serial.println(onos_cmd_end_position);
      return(0); 
    }

  
    

  }// end if (radio.receiveDone())


}








void checkCurrentRadioAddress(){

#if defined(remote_node)   // only if this is a remote node..

  if (old_address==254){// i have not the proper address yet..



    if (old_address!=this_node_address){//the address has changed and I restart radio to use it
 

      //radio.setAddress(this_node_address);
      beginRadio();
      old_address=this_node_address;
      get_address_timeout=millis();
      Serial.print("radio address changed to:");
      Serial.println(this_node_address);
      sendSyncMessage(radioRetry,radioTxTimeout);


    }

    random_time=4000;//random(4000,5000);
    


    if ((millis()-get_address_timeout)>random_time){ //every 4000/5000 ms
   
      get_address_timeout=millis();

      getAddressFromGateway();  //ask the gateway for a proper address


    }


  }
  else{
    random_time=1500;//random(1500,2500);
    if ((millis()-sync_time)>random_time){ //every 1500/2500 ms
   
      sync_time=millis();

      sendSyncMessage(radioRetry,radioTxTimeout);


    }

  }

#endif

}


void beginRadio(){

  interrupts(); // Enable interrupts

  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)

  radio.encrypt(encript_key);
  


  radio.enableAutoPower(targetRSSI);
 
  Serial.print("\nListening at ");
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(" MHz");




}

void buttonStateChanged(){

  button_time_same_status=millis();
  button_still_same_status=0;

}
 
void handleButton(){
/*
  Serial.println(F("handleButton() executed "));
  Serial.print("button_still_same_status:");
  Serial.print(button_still_same_status);
  Serial.print("button_time_same_status:");
  Serial.println(millis()-button_time_same_status);
*/




/*  if (button_still_same_status==1){ //filter 
    //button_time_same_status=millis();
    return;
  }
*/

  if ((millis()-button_time_same_status)<time_to_change_status){ //filter 
    return;
  }





  obj_button_pin=node_obj_pinout[button];
  if (digitalRead(obj_button_pin)==0) {
    Serial.print(F("obj_button pressed"));
    if (((millis()-button_time_same_status)>time_to_reset_encryption)&&( (millis()-button_time_same_status)<time_to_reset_encryption*2)){  //button pressed for more than 20 seconds
        Serial.println(F("time_to_reset_encryption ---------------------------------_#]"));
        noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
        memset(encript_key,0,sizeof(encript_key)); //to clear the array
        strcpy(encript_key,init_encript_key);//reset the encript_key to default to made the first sync with onoscenter 
        old_address=254;//reset the node address
        first_sync=1;
        setup();
        //beginRadio();  //restart radio with the default encript_key  

        //checkCurrentRadioAddress();  
        interrupts(); // Enable interrupts 
        button_time_same_status=millis();
      }

    if (((millis()-button_time_same_status)>time_to_change_status)&&(button_still_same_status==0)){
      Serial.println(F("time_to_change_status_#]++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"));
      changeObjStatus(main_obj_selected,!main_obj_state);  // this will make a not of current state
      sendSyncMessage(radioRetry+2,radioTxTimeout); 
      button_still_same_status=1;
      button_time_same_status=millis();
      delay(100);//todo change it smaller

    }

  }


}




void setup() {

  node_obj_pinout[relay1]=7;  // the first  object is the relay 1 connected on pin 7 
  node_obj_pinout[relay2]=8;  // the second object is the relay 1 connected on pin 8  
  node_obj_pinout[relay3]=9;  // the third  object is the relay 3 connected on pin 9 
  node_obj_pinout[relay4]=6;  // the forth  object is the relay 4 connected on pin 3 
  node_obj_pinout[led]=5;     // the fifth  object is the led     connected on pin 5
  node_obj_pinout[button]=3;  // the sixth  object is the button  connected on pin 3 


//  while (!Serial); // wait until serial console is open, remove if not tethered to computer
  noInterrupts(); // Disable interrupts    //important for lamp node

//  pinMode(RFM69_RST, OUTPUT);


  pinMode(node_obj_pinout[relay1], OUTPUT);
  pinMode(node_obj_pinout[relay2], OUTPUT);
  pinMode(node_obj_pinout[relay3], OUTPUT);
  pinMode(node_obj_pinout[relay4], OUTPUT);
  pinMode(node_obj_pinout[led], OUTPUT);
  pinMode(node_obj_pinout[button], INPUT);

  attachInterrupt(digitalPinToInterrupt(node_obj_pinout[button]), buttonStateChanged, CHANGE);

  digitalWrite(node_obj_pinout[button], HIGH); //enable pull up resistors

  //while (!Serial); // wait until serial console is open, remove if not tethered to computer
  Serial.begin(SERIAL_BAUD);




  Serial.println(F("Setup -------------------------------------------------"));
  Serial.println(F("Feather RFM69W Receiver"));


/*  


  WARNING do not uncomment this part or the radio will not work anymore!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  


  // Hard Reset the RFM module

  digitalWrite(RFM69_RST, LOW);
  delay(50);
  digitalWrite(RFM69_RST, HIGH);
  delay(120);
  digitalWrite(RFM69_RST, LOW);
  delay(120);
  */
  beginRadio();

  changeObjStatus(0,1);
  delay(300);
  changeObjStatus(0,0);

  Blink(node_obj_pinout[led],100,3); 

  composeSyncMessage();

  // if analog input pin 1 is unconnected, random analog
  // noise will cause the call to randomSeed() to generate
  // different seed numbers each time the sketch runs.
  // randomSeed() will then shuffle the random function.
  //randomSeed(analogRead(1));


}
 
void loop() {





  handleButton();


  if (skipRadioRxMsg>skipRadioRxMsgThreshold){ //to allow the execution of radio tx , in case there are too many rx query..
    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
    Serial.println("I skip the rxradio part once");
    goto radioTx;


  }



  radio_msg_to_decode_is_avaible=checkAndHandleIncomingRadioMsg();


radioTx:
 
  radio.receiveDone(); //put radio in RX mode
  Serial.flush(); //make sure all serial data is clocked

  checkCurrentRadioAddress();


}//END OF LOOP()

void Blink(byte PIN, byte DELAY_MS, byte loops)
{
  for (byte i=0; i<loops; i++)
  {
    digitalWrite(PIN,HIGH);
    delay(DELAY_MS);
    digitalWrite(PIN,LOW);
    delay(DELAY_MS);
  }
}

