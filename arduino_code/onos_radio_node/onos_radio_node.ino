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
                   D8 ----------1 (chip select flash)
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
#include <LowPower.h>
//*********************************************************************************************
// *********** IMPORTANT SETTINGS - YOU MUST CHANGE/CONFIGURE TO FIT YOUR HARDWARE *************
//*********************************************************************************************
#define NETWORKID     100  //the same on all nodes that talk to each other

 
//Match frequency to the hardware version of the radio on your Feather
//#define FREQUENCY     RF69_433MHZ
//define FREQUENCY     RF69_868MHZ
#define FREQUENCY      RF69_433MHZ
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
 


#ifdef __AVR_ATmega1284P__
  #define FLASH_SS      23 // and FLASH SS on D23
#else
  #define FLASH_SS      8 // and FLASH SS on D8
#endif



//**************************************Onos Define node **************************************

//#define ota_enabled 1   //enable ota update

#if defined(ota_enabled)
  #include <RFM69_OTA.h>     //get it here: https://github.com/lowpowerlab/RFM69
  #include <SPIFlash.h>      //get it here: https://github.com/lowpowerlab/spiflash
  unsigned long ota_loop_start_time=0;
  #define ota_timeout 25000  //25 seconds 
  SPIFlash flash(FLASH_SS, 0x1F65); //EF30 for windbond 4mbit flash  , 0x1F65 for AT25DN512C , i used the 'i' comand from serial port after i get the flash error and it said '1F65' , i put it here and the error disappeared

#endif 
char serial_number[13]="xxxxxxxxxxxx";
char numeric_serial[5]="0004";   // this is the progressive numeric serial number

//you should comment all the type but the one you want to use
//commentare tutti i tipi di nodo tranne quello utilizzato
#define node_type_WPlug1vx
/*
#define node_type_Wrelay4x
#define node_type_WreedSaa
#define node_type_WLightSS
#define node_type_WPlug1vx
#define node_type_WIRbarr0
#define node_type_WSoilHaa
*/                  


//************************************End ofOnos Define node **************************************




//**********************************Onos objects configuration **************************************




#if defined(node_type_WreedSaa)
  // define object numbers to use in the pin configuration warning this is not the pinout numbers
  #define reed1   0
  #define button  1
  #define led     2
  #define tempSensor   3
  #define digOut  4
  #define reed2   5
  #define syncTime  6
  #define reed1Logic  7
  #define reed2Logic  8
  #define battery_state 9
  #define luminosity_sensor 10

  #define TOTAL_OBJECTS 11 //11 because there are 10 elements + a null for the array closing
  #define node_default_timeout 1500 //36000000  //10 minutes of timeout
  #define battery_node 1            // tell the software to go to sleep to keep battery power. 
  uint8_t reed_sensors_state=0;  //store the state of the 2 reeds sensors
  uint8_t logic_reed1_status=0;
  uint8_t logic_reed2_status=0;

  uint8_t reed1_status_sent=0;
  uint8_t reed2_status_sent=0;

  int temperature_sensor_value=0;
  #define analog_readings 20  //repeated readings  , don't make them more than 20 or there will be overflow
  uint8_t temperature_sensor_value_byte=0;
  //uint8_t temperature_sensor_lower_byte=0;
  //uint8_t temperature_sensor_upper_byte=0;
  int luminosity_sensor_value=0;
  uint8_t luminosity_sensor_value_byte=0;
  int battery_value=0;
  byte battery_value_byte=0;

#elif defined(node_type_Wrelay4x)
  // define object numbers to use in the pin configuration warning this is not the pinout numbers
  #define relay1  0
  #define relay2  1
  #define relay3  2 
  #define relay4  3
  #define button  4
  #define led     5
  #define syncTime  6
  #define IS_RFM69HCW    false

  #define TOTAL_OBJECTS 7
  #define node_default_timeout 1500
 
#elif defined(node_type_WLightSS)
  #define node_default_timeout 1500

#elif defined(node_type_WPlug1vx)
  // define object numbers to use in the pin configuration warning this is not the pinout numbers
  #define relay1  0
  #define button  1
  #define led     2
  #define syncTime  3
  #define TOTAL_OBJECTS 4
  #define node_default_timeout 1500

#elif defined(node_type_WIRbarr0)
  #define node_default_timeout 1500

#elif defined(node_type_WSoilHaa)
  #define node_default_timeout 1500


#endif 


#if defined(battery_node)   //if the node is a battery node:
byte keep_ADCSRA=ADCSRA; //save the state of the register;

int stay_awake_period=700 ;   //how long in ms the node will stay awake to receive radio messages.
unsigned long awake_time=0;

#endif 

const uint8_t number_of_total_objects=TOTAL_OBJECTS ;

uint8_t node_obj_pinout[number_of_total_objects]; 
int node_obj_status[number_of_total_objects];  






//********************************End of Onos objects configuration **************************************




int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;



boolean radio_enabled=1;

unsigned long sync_time=0;
unsigned long sync_timeout=node_default_timeout;


char node_fw[]="5.27";
char encript_key[17]="onosEncryptKey01";  //todo read it from eeprom
//char init_encript_key[17]=INITENCRYPTKEY;
int this_node_address=254; //i start with 254


unsigned long get_address_timeout=0;

unsigned long *get_address_timeout_pointer=&get_address_timeout;


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
#define decoded_radio_answer_lenght 32
#define syncMessage_lenght 28

#define DEVMODE 1
int onos_cmd_start_position=-99;  
int onos_cmd_end_position=-99;  
char received_message_type_of_onos_cmd[3];
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;
//volatile char decoded_uart_answer[24]="er00_#]";
volatile char decoded_radio_answer[decoded_radio_answer_lenght]="er00_#]";
int received_message_address=0; //must be int..
//volatile char filtered_uart_message[rx_msg_lenght+3];
volatile char filtered_radio_message[rx_msg_lenght+3];
volatile char syncMessage[syncMessage_lenght];
volatile char str_this_node_address[4];
uint8_t main_obj_selected=0;
uint8_t rx_obj_selected=0;
volatile char progressive_msg_id=48;  //48 is 0 in ascii   //a progressive id to make each message unique
volatile char received_serial_number[13]; //used in OnosMsg
volatile boolean reInitializeRadio=0;
volatile boolean ota_loop=0; //enable the ota receiver loop
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////


uint8_t obj_button_pin;
//end node object pinuot, continue in setup() // 

OnosMsg OnosMsgHandler=OnosMsg();  //create the OnosMsg object

uint8_t radioRetry=3;      //todo: make this changable from serialport
uint8_t radioTxTimeout=20;  //todo: make this changable from serialport
uint8_t radioRetryAllarm=100; 
uint8_t radioTxTimeoutAllarm=50;  

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

   Serial.print(F("changeObjStatus executed with  status:"));
   Serial.println(status_to_set);

  if (obj_number!=button){ //will not change the status to the button...

#if defined(node_type_WreedSaa)
    if ( (obj_number==led)|(obj_number==digOut) ){
      digitalWrite(node_obj_pinout[obj_number],status_to_set); // 
      Serial.println(F("digitalWrite with obj")); 
    }

#elif defined(node_type_Wrelay4x)

    if (obj_number==0){
      main_obj_state=status_to_set;
      digitalWrite(node_obj_pinout[obj_number],!status_to_set); //  ! the relay are on when the pin is at gnd
      Serial.println(F("digitalWrite with obj")); 
      changeObjStatus(led,status_to_set);
    }
    else if(obj_number<4) { //objects from 0 to 3 are relay  
      digitalWrite(node_obj_pinout[obj_number],!status_to_set); //  ! the relay are on when the pin is at gnd
      Serial.println(F("digitalWrite with obj")); 
    }
    else if (obj_number==led){
      digitalWrite(node_obj_pinout[obj_number],status_to_set); // 
      Serial.println(F("digitalWrite with obj")); 
    }
#elif defined(node_type_WPlug1vx)


    if (obj_number==0){
      main_obj_state=status_to_set;
      digitalWrite(5,!status_to_set); // set relay1
      digitalWrite(6,!status_to_set); // set relay2
      digitalWrite(7,status_to_set);// reset both relays
      Serial.println(F("digitalWrite with obj")); 
      changeObjStatus(led,status_to_set);
    }

    else if (obj_number==led){
      digitalWrite(node_obj_pinout[obj_number],status_to_set); // 
      Serial.println(F("digitalWrite with obj")); 
    }


#endif

    else if(obj_number==syncTime){  // if the object sent is syncTime change the sync_timeout with the value received
      sync_timeout=status_to_set*1000;// get the value in seconds
    }

    node_obj_status[obj_number]=status_to_set;

    return(1);
  }


return(0);

}


void composeSyncMessage(){


  Serial.println(F("composeSyncMessage executed"));
  //[S_123ul5.24WPlugAvx000810000x_#]




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


#if defined(node_type_WreedSaa)
//[S_001rsWreedSaa000132Lgx_#]      reeds:3, temperature sensor:2, luminosity sensor:L, battery sensor:g 


  node_obj_status[reed1]=digitalRead(node_obj_pinout[reed1]);
  node_obj_status[reed2]=digitalRead(node_obj_pinout[reed2]);
  
  reed1_status_sent=node_obj_status[reed1];
  reed2_status_sent=node_obj_status[reed2];


  Serial.print(F("reed1_status="));
  Serial.println(node_obj_status[reed1]);
  Serial.print(F("reed2_status="));
  Serial.println(node_obj_status[reed2]);

  logic_reed1_status=(node_obj_status[reed1])^(node_obj_status[reed1Logic]); //the 2 value must be different for the result to be 1
  logic_reed2_status=(node_obj_status[reed2])^(node_obj_status[reed2Logic]);



  if ((logic_reed1_status==0)&&(logic_reed2_status==0)){
    reed_sensors_state='0';   
  }
  else if ((logic_reed1_status==0)&&(logic_reed2_status==1)){
    reed_sensors_state='1';   
  }
  else if ((logic_reed1_status==1)&&(logic_reed2_status==0)){
    reed_sensors_state='2';   
  }
  else if ((logic_reed1_status==1)&&(logic_reed2_status==1)){
    reed_sensors_state='3';   
  }

  Serial.print(F("reed_total_status="));
  Serial.println(reed_sensors_state);

 // temperature_sensor_value=(  analogRead(A0)*3.0 * 100.0) / 1024;//3v, lm35 temp sensor 10mv each celsius

  for (uint8_t i=0;i<=analog_readings;i=i+1){
    temperature_sensor_value=temperature_sensor_value+(analogRead(node_obj_pinout[tempSensor])*3.0 * 100.0) / 1024;//3v, lm35 temp sensor 10mv each celsius  
    delay(1);
    luminosity_sensor_value= luminosity_sensor_value+analogRead(node_obj_pinout[luminosity_sensor])/4;
    delay(1);
    battery_value=battery_value+analogRead(node_obj_pinout[battery_state])/4;
    delay(1);
  }
  
  temperature_sensor_value=(temperature_sensor_value/analog_readings)+1;  // +1 is to never transmitt a binary 0 ..


  if (temperature_sensor_value>254){// limit the data to only a byte
    temperature_sensor_value=254;  
  }
  temperature_sensor_value_byte=byte(temperature_sensor_value); //cast from int to byte

/*
  //convert from integer to 2 binary bytes 
  //for example 1024 will be        00000100 00000000
  if (temperature_sensor_value<256){
    temperature_sensor_upper_byte=0;
    temperature_sensor_lower_byte=byte(temperature_sensor_value);
  }
  else{
    temperature_sensor_upper_byte=byte(temperature_sensor_value/256);   
    temperature_sensor_lower_byte=byte(temperature_sensor_value % 256);

  }

*/

  luminosity_sensor_value=(luminosity_sensor_value/analog_readings)+1;  // +1 is to never transmitt a binary 0 ..
  if (luminosity_sensor_value>254){// limit the data to only a byte
    luminosity_sensor_value=254;  
  }

  luminosity_sensor_value_byte=byte(luminosity_sensor_value);//get the value of the lux sensor , 0:255

  battery_value=(battery_value/analog_readings)+1;  // +1 is to never transmitt a binary 0 ..

  if (battery_value>254){// limit the data to only a byte
    battery_value=254;  
  }

  battery_value_byte=byte(battery_value);


  Serial.print(F("temperature_sensor_value="));
  Serial.print(temperature_sensor_value);


  Serial.print(F(",luminosity="));
  Serial.print(luminosity_sensor_value);

  Serial.print(F(",battery_value="));
  Serial.print(battery_value);

  Serial.print(F(",battery_value_byte="));
  Serial.println(battery_value_byte);
/*
  //todo remove these fixed values
  temperature_sensor_upper_byte=60;
  temperature_sensor_lower_byte=61;
  luminosity_sensor_value=51;
  battery_value=49;
*/

  if (this_node_address==254){
    strcat(syncMessage, "ga");
    strcat(syncMessage, node_fw);
    strcat(syncMessage, serial_number);
  }
  else{
    strcat(syncMessage, "rs");
    strcat(syncMessage, serial_number);

    syncMessage[strlen(syncMessage)]=reed_sensors_state;   

    syncMessage[strlen(syncMessage)]=temperature_sensor_value_byte;  

    syncMessage[strlen(syncMessage)]=luminosity_sensor_value;  

    syncMessage[strlen(syncMessage)]=battery_value; 
  }


 
#elif defined(node_type_Wrelay4x)

  if (this_node_address==254){
    strcat(syncMessage, "ga");
    strcat(syncMessage, node_fw);
    strcat(syncMessage, serial_number);
  }
  else{
  //[S_123r4Wrelay4x00080110x_#]     0110 is the 4 relay status
    strcat(syncMessage, "r4");
 // strcat(syncMessage, "sy");
 
    strcat(syncMessage, serial_number);

    syncMessage[strlen(syncMessage)]=node_obj_status[0]+48;  
    syncMessage[strlen(syncMessage)]=node_obj_status[1]+48;  
    syncMessage[strlen(syncMessage)]=node_obj_status[2]+48;  
    syncMessage[strlen(syncMessage)]=node_obj_status[3]+48;  
  }


#elif defined(node_type_WPlug1vx)

  if (this_node_address==254){
    strcat(syncMessage, "ga");
    strcat(syncMessage, node_fw);
    strcat(syncMessage, serial_number);
  }
  else{
  //[S_123r4Wrelay4x00080110x_#]     0110 is the 4 relay status
    strcat(syncMessage, "ul");
 // strcat(syncMessage, "sy");
 
    strcat(syncMessage, serial_number);

    syncMessage[strlen(syncMessage)]=node_obj_status[0]+48;  

  }





#elif defined(node_type_WLightSS)

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

  syncMessage[strlen(syncMessage)]=main_obj_state+48;   //+48 for ascii translation

  Serial.print(F("composeSyncMessage executed with  status:"));
  Serial.println(main_obj_state);
  strcat(syncMessage, minutes_time_from_turn_on_array);

#endif  //end node_type_WLightSS




  if (progressive_msg_id<122){  //122 is z in ascii
    progressive_msg_id=progressive_msg_id+1;
  }
  else{
    progressive_msg_id=48;  //48 is 0 in ascii
  }

  syncMessage[strlen(syncMessage)]=progressive_msg_id; //put the variable msgid in the array 
  //Serial.println(syncMessage[28]);
  //Serial.println(strlen(syncMessage));
  strcat(syncMessage, "_#]");
  

}



void sendSyncMessage(uint8_t retry,uint8_t tx_timeout=150){

 // composeSyncMessage();
  

/*
  if (first_sync!=1 ){
    syncMessage[6]='r'; //modify the message
    syncMessage[7]='a'; //modify the message
  }
*/

  Serial.println(F(" sendWithRetry sendSyncMessage executed"));
  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage),retry,tx_timeout)) {
    // note that the max delay time is 255..because is uint8_t
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)
    Serial.println(F("sent_sync_message1"));
//    Blink(LED, 50, 3); //blink LED 3 times, 50ms between blinks
    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
  }

  radio.receiveDone(); //put radio in RX mode
  sync_time=millis();
}




void getAddressFromGateway(){
   Serial.println(F("getAddressFromGateway executed"));

  //[S_123ga5.24WPlugAvx000810000x_#]

  composeSyncMessage();
  syncMessage[6]='g'; //modify the message to get a address instead of just sync.
  syncMessage[7]='a'; //modify the message to get a address instead of just sync.

  Serial.println(F(" sendWithRetry getAddressFromGateway executed"));


  Serial.print(F("msg send:")); 

  for (pointer = 0; pointer <= 35; pointer++) {
    Serial.print(syncMessage[pointer]); 
    if ((syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ) {//  
      break;
    }

  }
  Serial.println(F("msg end:")); 

  tryed_times=0;
  while (tryed_times < radioRetry ){
    Serial.println(F("radio tx start"));

    if (radio.sendWithRetry(gateway_address, syncMessage,strlen(syncMessage),1,radioTxTimeout)) {
      // note that the max delay time is 255..because is uint8_t
      //target node Id, message as string or byte array, message length,retries, milliseconds before retry
      //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)

      Serial.println(F("sent_get_address"));
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
      delay(15);
      //LowPower.powerDown(SLEEP_15MS, ADC_OFF, BOD_OFF);
      //ADCSRA=keep_ADCSRA; //resume the status of the register

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
    Serial.print(F(" id:"));
    Serial.println(radio.SENDERID);
    Serial.print((char*)radio.DATA);
    Serial.print(F("   [RX_RSSI:"));Serial.print(radio.RSSI);Serial.print(F("]"));
    //CheckForWirelessHEX(radio, flash, false);  //to check for ota messages..
 
    //check if received message contains Hello World

    //uint8_t message_copy[rx_msg_lenght+1];

    //strcpy(filtered_radio_message,"");
    //memset(filtered_radio_message,0,sizeof(filtered_radio_message)); //to clear the array

    //Serial.println(radio.SENDERID);
    if (radio.TARGETID!=this_node_address){
      Serial.println(F("[S_er9_radioAddress_#]"));
      return(0); // todo: implement a forward of the message? 
    }

    Serial.print(F("msg_start:"));

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


    Serial.println(F(":msg_stop"));


    if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){

      Serial.println(F("onos cmd  found-------------------------------"));
      //noInterrupts(); // Disable interrupts    //important for lamp node 
      //decodeOnosCmd(filtered_radio_message);
      OnosMsgHandler.decodeOnosCmd(filtered_radio_message,decoded_radio_answer);




      if( (decoded_radio_answer[0]=='o')&&(decoded_radio_answer[1]=='k')){//if the message was ok...
      //check if sender wanted an ACK
        if (radio.ACKRequested()){
          radio.sendACK();
          Serial.println(F(" - ACK sent"));
          sync_time=millis();
        }
        //interrupts(); // Enable interrupts
      return(1); 

      }
      else{
        Serial.print(F("error in message decode i will not send the ACK,i found:"));
        uint8_t k=0;
        while (k<decoded_radio_answer_lenght){
          if (decoded_radio_answer[k]==0){
            break;
          } 
          Serial.print(decoded_radio_answer[k]);
          k=k+1;
        } 

        Serial.println();
        return(0); 

       // checkCurrentRadioAddress(); //if the mesage received is wrong i will check and send a address request if needed becausethe onos gateway will wait a moment after the tranmission failure.

        //interrupts(); // Enable interrupts 
      }

    //interrupts(); // Enable interrupts
    
    }
    else{
      strcpy(decoded_radio_answer,"nocmd0_#]");
      Serial.print(F("error in message nocmd0_#]"));
      Serial.print(onos_cmd_start_position);
      Serial.println(onos_cmd_end_position);
      return(0); 
    }

  
    

  }// end if (radio.receiveDone())




}








void checkCurrentRadioAddress(){
  if(reInitializeRadio==1){
    beginRadio();
    reInitializeRadio=0;
  }


#if defined(remote_node)   // only if this is a remote node..

  if (this_node_address==254){// i have not the proper address yet..

    random_time=4000;//random(4000,5000);
 
    if ((millis()-*get_address_timeout_pointer)>random_time){ //every 4000/5000 ms

#if defined(DEVMODE)
      Serial.print(F("get_address_timeout>time:"));
      Serial.println((millis()-*get_address_timeout_pointer));
#endif

      *get_address_timeout_pointer=millis();



      getAddressFromGateway();  //ask the gateway for a proper address

    }

  }
  else{
    //random_time=1500;//random(1500,2500);
    if ((millis()-sync_time)>sync_timeout){ //every 1500/2500 ms
   
      composeSyncMessage();

#if defined(battery_node) // defined(node_type_WreedSaa)
      sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm);
      //sync_time=millis();
      //  I put the node to sleep
      Serial.println(F("I go to sleep"));
      radio.sleep();
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      delayMicroseconds(50);
      ADCSRA=keep_ADCSRA; //resume the status of the register
      composeSyncMessage();
      sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm);
      //sync_time=millis();

      awake_time=millis();
      Serial.println(F("w for possible messages"));
      while ((millis()-awake_time)>stay_awake_period ){
        radio_msg_to_decode_is_avaible=checkAndHandleIncomingRadioMsg();
      }
      Serial.println(F("end wait"));


#else    //not a battery node
      Serial.println(F("not a battery node part executed"));
      composeSyncMessage();
      sendSyncMessage(radioRetry,radioTxTimeout);
      //sync_time=millis();

#endif  //end  if defined(battery_node)




    }


  }

#endif  // end if defined(remote_node) 

}


void beginRadio(){

  interrupts(); // Enable interrupts

  *get_address_timeout_pointer=millis();

  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)

  radio.encrypt(encript_key);
  


  radio.enableAutoPower(targetRSSI);
 
  Serial.print(F("\nListening at "));
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(F(" MHz"));
  Serial.print(F("radio address changed to:"));
  Serial.println(this_node_address);

#if defined(battery_node)   //if the node is a battery node:
  keep_ADCSRA=ADCSRA; //save the state of the register

#endif 


}

void buttonStateChanged(){

  button_time_same_status=millis();
  button_still_same_status=0;

}

#if defined(node_type_WreedSaa)

void handleReed(){//handle the reed sensor
  //node_obj_status[reed1Logic]=0;
  Serial.println(F("handleReed called"));
  composeSyncMessage();
  sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm); 

/*
  if (digitalRead(node_obj_pinout[reed1])==node_obj_status[reed1Logic]){ //the sensor should send allarm
    composeSyncMessage();
    sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm); 
  }

  else if (digitalRead(node_obj_pinout[reed2])==node_obj_status[reed2Logic]){ //the sensor should send allarm
    composeSyncMessage();
    sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm); 
  }
*/

}
#endif  //end  if defined(node_type_WreedSaa)



void handleButton(){//handle the main node button , you can't call this from interrupt because millis() won't work

  Serial.print(F("handleButton() executed "));
  Serial.print("button_still_same_status:");
  Serial.print(button_still_same_status);
  Serial.print("button_time_same_status:");
  Serial.println(millis()-button_time_same_status);





   // Serial.print(F("obj_button pressed"));
  if (((millis()-button_time_same_status)>time_to_reset_encryption)&&( (millis()-button_time_same_status)<time_to_reset_encryption*2)){  //button pressed for more than x seconds
      Serial.println(F("time_to_reset_encryption ---------------------------------_#]"));
      noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
      memset(encript_key,0,sizeof(encript_key)); //to clear the array
      strcpy(encript_key,INITENCRYPTKEY);//reset the encript_key to default to made the first sync with onoscenter 
      this_node_address=254;//reset the node address
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
    composeSyncMessage();
    sendSyncMessage(radioRetry+2,radioTxTimeout); 
    button_still_same_status=1;
    button_time_same_status=millis();
    delay(100);//todo change it smaller

  }

}
#if defined(node_type_WreedSaa)
void interrupt1_handler(){



  detachInterrupt(1);
  Serial.println(F("interrupt called"));
#if defined(battery_node)   //if the node is a battery node:
  ADCSRA=keep_ADCSRA; //resume the status of the register
#endif
  handleReed();
  reed1_status_sent=node_obj_status[reed1];
  reed2_status_sent=node_obj_status[reed2];
  delay(2);
  node_obj_status[reed1]=digitalRead(node_obj_pinout[reed1]);
  node_obj_status[reed2]=digitalRead(node_obj_pinout[reed2]);
  
  if ((reed1_status_sent!=node_obj_status[reed1] ) |(reed2_status_sent!=node_obj_status[reed2] )){ //if the reed has changed status during last transmission
    Serial.println(F("-reed has changed again"));
    handleReed();
  }


}
#endif



#if defined(ota_enabled)
void ota_receive_loop(){

  Serial.println(F("ota_receive_loop() executed"));

  ota_loop_start_time=millis()+5000;

  while( (millis()-ota_loop_start_time)>ota_timeout) {
    CheckForWirelessHEX(radio, flash, false);
  }
  ota_loop=0;

}
#endif


void setup() {


  node_obj_status[syncTime]=node_default_timeout;
  sync_timeout=node_obj_status[syncTime];

#if defined(node_type_WreedSaa)
  node_obj_status[reed1Logic]=0; //logic 0 means reed1Logic will be 1 if the magnet is close to the reed sensor
  node_obj_status[reed2Logic]=0; //logic 0 means reed1Logic will be 1 if the magnet is close to the reed sensor

  memset(serial_number,0,sizeof(serial_number)); //to clear the array
  strcpy(serial_number,"WreedSaa");
  strcat(serial_number,numeric_serial);

// OBJECTS PIN DEFINITION__________________________________________________________________
  node_obj_pinout[reed1]=3;   // the first  object is the reed1 connected on pin 3 
  node_obj_pinout[button]=5;  // the second  object is the button  connected on pin 5 
  node_obj_pinout[led]=4;     // the third  object is the led     connected on pin 4
  node_obj_pinout[tempSensor]=A1;   // the forth object is the temperature sensor connected on analog pin 1  
  node_obj_pinout[battery_state]=A2;   // the 9th object is the battery state connected on analog pin 0  
  node_obj_pinout[luminosity_sensor]=A0; 
  node_obj_pinout[digOut]=9;  // the    5  object is the digital output connected on pin 9 
  node_obj_pinout[reed2]=6;   // the    6  object is the reed2 connected on pin 6 
// END OBJECTS PIN DEFINITION_______________________________________________________________
  pinMode(node_obj_pinout[reed1], INPUT);
  pinMode(node_obj_pinout[button], INPUT);
  pinMode(node_obj_pinout[led], OUTPUT);
  pinMode(node_obj_pinout[digOut], OUTPUT);
  pinMode(node_obj_pinout[reed2], INPUT);
  delay(2);
  digitalWrite(node_obj_pinout[reed1],1); //set pullup on reed
//  digitalwrite(node_obj_pinout[reed2],1);



#elif defined(node_type_Wrelay4x)
  memset(serial_number,0,sizeof(serial_number)); //to clear the array
  strcpy(serial_number,"Wrelay4x");
  strcat(serial_number,numeric_serial);
// OBJECTS PIN DEFINITION___________________________________________________________________
  node_obj_pinout[relay1]=7;  // the first  object is the relay 1 connected on pin 7 
  node_obj_pinout[relay2]=4;  // the second object is the relay 2 connected on pin 8  
  node_obj_pinout[relay3]=9;  // the third  object is the relay 3 connected on pin 9 
  node_obj_pinout[relay4]=6;  // the forth  object is the relay 4 connected on pin 3 
  node_obj_pinout[led]=5;     // the fifth  object is the led     connected on pin 5
  node_obj_pinout[button]=3;  // the sixth  object is the button  connected on pin 3 
// END OBJECTS PIN DEFINITION_______________________________________________________________
  pinMode(node_obj_pinout[relay1], OUTPUT);
  pinMode(node_obj_pinout[relay2], OUTPUT);
  pinMode(node_obj_pinout[relay3], OUTPUT);
  pinMode(node_obj_pinout[relay4], OUTPUT);
  pinMode(node_obj_pinout[led], OUTPUT);
  pinMode(node_obj_pinout[button], INPUT);

  digitalWrite(node_obj_pinout[button], HIGH); //enable pull up resistors

   
#elif defined(node_type_WLightSS)

#elif defined(node_type_WPlug1vx)
  memset(serial_number,0,sizeof(serial_number)); //to clear the array
  strcpy(serial_number,"WPlug1vx");
  strcat(serial_number,numeric_serial);
// OBJECTS PIN DEFINITION___________________________________________________________________
  node_obj_pinout[led]=4;     // the object is the led     connected on pin 4
  node_obj_pinout[button]=3;  // the object is the button  connected on pin 3 
// END OBJECTS PIN DEFINITION_______________________________________________________________

  pinMode(5, OUTPUT); // set relay1
  pinMode(6, OUTPUT); // set relay2
  pinMode(7, OUTPUT); // reset relay
  pinMode(node_obj_pinout[led], OUTPUT);
  pinMode(node_obj_pinout[button], INPUT);

  digitalWrite(node_obj_pinout[button], HIGH); //enable pull up resistors


#elif defined(node_type_WIRbarr0)
  node_obj_pinout[relay1]=4;  // the first  object is the relay 1 connected on pin 7 
#elif defined(node_type_WSoilHaa)
  node_obj_pinout[relay1]=4;  // the first  object is the relay 1 connected on pin 7 

#endif 








//  while (!Serial); // wait until serial console is open, remove if not tethered to computer
  noInterrupts(); // Disable interrupts    //important for lamp node

//  pinMode(RFM69_RST, OUTPUT);








  //while (!Serial); // wait until serial console is open, remove if not tethered to computer
  Serial.begin(SERIAL_BAUD);




  Serial.println(F("Setup -------------------------------------------------"));
  Serial.println(F("Feather RFM69W Receiver"));

#if defined(ota_enabled)
  if (flash.initialize())
    Serial.println("SPI Flash Init OK!");
  else
    Serial.println("SPI Flash Init FAIL!");
#endif 

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
  digitalWrite(node_obj_pinout[led], 1); // 1 to to turn ledd off


  interrupts(); 
  composeSyncMessage();


//enabling interrupt must be the LAST THING YOU DO IN THE SETUP!!!!
#if defined(node_type_WreedSaa)
  attachInterrupt(1, interrupt1_handler, CHANGE); //set interrupt on the hardware interrupt 1
#elif defined(node_type_WPlug1vx)
  digitalWrite(node_obj_pinout[led], 0); // 1 to to turn ledd off
  attachInterrupt(digitalPinToInterrupt(node_obj_pinout[button]), buttonStateChanged, FALLING);
#elif defined(node_type_Wrelay4x)
  attachInterrupt(digitalPinToInterrupt(node_obj_pinout[button]), buttonStateChanged, FALLING);
#endif 


  // if analog input pin 1 is unconnected, random analog
  // noise will cause the call to randomSeed() to generate
  // different seed numbers each time the sketch runs.
  // randomSeed() will then shuffle the random function.
  //randomSeed(analogRead(1));


}
 
void loop() {

#if defined(node_type_Wrelay4x)
  if (button_still_same_status==0){ //filter 

    obj_button_pin=node_obj_pinout[button];
    if (digitalRead(obj_button_pin)==0) { 
      handleButton();
    }
  }
#elif defined(node_type_WPlug1vx)
  if (button_still_same_status==0){ //filter 

    obj_button_pin=node_obj_pinout[button];
    if (digitalRead(obj_button_pin)==0) { 
      handleButton();
    }
  }
#endif 


  if (skipRadioRxMsg>skipRadioRxMsgThreshold){ //to allow the execution of radio tx , in case there are too many rx query..
    skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
    Serial.println(F("I skip the rxradio part once"));
    goto radioTx;


  }


#if defined(ota_enabled)   //if the node is a battery node:
    ota_loop=1;
  if (ota_loop==1){
    ota_receive_loop();
  }
#endif 


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

