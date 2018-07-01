/*
 * O.N.O.S.  arduino WlightVx node  firmware by Marco Rigoni 9-11-16  onos.info@gmail.com 
 * more info on www.myonos.com 
 *
 */
// python-build-start
// arduino:avr:uno
// /dev/ttyUSB0
// python-build-end

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
#include <avr/wdt.h>

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


#define ATC_RSSI      -50   //power signal from -30(stronger) to -95(weaker) 
#define targetRSSI    -50

#define remote_node   //tell the compiler that this is a remote node
//#define local_node  //tell the compiler that this is a local node
 


#ifdef __AVR_ATmega1284P__
  #define FLASH_SS      23 // and FLASH SS on D23
#else
  #define FLASH_SS      8 // and FLASH SS on D8
#endif



//**************************************Onos Define node **************************************

//#define ota_enabled    //enable ota update

#if defined(ota_enabled)
  #include <RFM69_OTA.h>     //get it here: https://github.com/lowpowerlab/RFM69
  #include <SPIFlash.h>      //get it here: https://github.com/lowpowerlab/spiflash
  unsigned long ota_loop_start_time=0;
  unsigned long  ota_timeout=25000;  //25 seconds 
  SPIFlash flash(FLASH_SS, 0x1F65); //EF30 for windbond 4mbit flash  , 0x1F65 for AT25DN512C , i used the 'i' comand from serial port after i get the flash error and it said '1F65' , i put it here and the error disappeared
#endif 
char serial_number[13]="xxxxxxxxxxxx";
char numeric_serial[5]="0001";   // this is the progressive numeric serial number

//you should comment all the type but the one you want to use
//commentare tutti i tipi di nodo tranne quello utilizzato
#define node_type_WPlug1vx
/*
#define node_type_Wrelay4x
#define node_type_WreedSaa
#define node_type_WLightSS  not implemented
#define node_type_WPlug1vx  
#define node_type_WIRbarr0  not implemented
#define node_type_WSoilHaa  not implemented
*/                  


//************************************End ofOnos Define node **************************************




//**********************************Onos objects configuration **************************************

#define ENABLE_RADIO_RESET_PIN 0


#if defined(node_type_WreedSaa)
  // define object numbers to use in the pin configuration warning this is not the pinout numbers
  const uint8_t reed1 = 0;
  const uint8_t button = 1;
  const uint8_t led = 2;
  const uint8_t tempSensor = 3;
  const uint8_t digOut = 4;
  const uint8_t reed2 = 5;
  const uint8_t syncTimeout = 6;
  const uint8_t reed1Logic = 7;
  const uint8_t reed2Logic = 8;
  const uint8_t battery_state = 9;
  const uint8_t luminosity_sensor = 10;
  
  const uint8_t number_of_total_objects = 11; //11 because there are 10 elements + a null for the array closing
  const int node_default_timeout = 60; // seconds
  #define battery_node            // tell the software to go to sleep to keep battery power. 
  uint8_t reed_sensors_state = 0;  //store the state of the 2 reeds sensors
  uint8_t logic_reed1_status = 0;
  uint8_t logic_reed2_status = 0;
  
  volatile uint8_t reed1_status_sent = 0;
  volatile uint8_t reed2_status_sent = 0;
  
  int temperature_sensor_value = 0;
  const uint8_t analog_readings = 20;  //repeated readings  , don't make them more than 20 or there will be overflow
  uint8_t temperature_sensor_value_byte = 0;
  //uint8_t temperature_sensor_lower_byte=0;
  //uint8_t temperature_sensor_upper_byte=0;
  int luminosity_sensor_value = 0;
  uint8_t luminosity_sensor_value_byte = 0;
  int battery_value = 0;
  byte battery_value_byte = 0;
  
#elif defined(node_type_Wrelay4x)
  // define object numbers to use in the pin configuration warning this is not the pinout numbers
  const uint8_t relay1 = 0;
  const uint8_t relay2 = 1;
  const uint8_t relay3 = 2; 
  const uint8_t relay4 = 3;
  const uint8_t button = 4;
  const uint8_t led    = 5;
  const uint8_t syncTimeout = 6;
  // #define IS_RFM69HCW    false
  
  const uint8_t number_of_total_objects = 7;
  const int node_default_timeout = 180;  //seconds
  #undef ENABLE_RADIO_RESET_PIN
    #define ENABLE_RADIO_RESET_PIN 1  //  enable the use of the radio reset pin to reset the radio module
  
#elif defined(node_type_WLightSS)
  const int node_default_timeout = 360;
  #undef ENABLE_RADIO_RESET_PIN
    #define ENABLE_RADIO_RESET_PIN 1  //  enable the use of the radio reset pin to reset the radio module

#elif defined(node_type_WPlug1vx)
  // define object numbers to use in the pin configuration warning this is not the pinout numbers
  const uint8_t relay1 = 0;
  const uint8_t button = 1;
  const uint8_t led = 2;
  const uint8_t syncTimeout = 3;
  const uint8_t number_of_total_objects = 4;
  const int node_default_timeout = 180;
  #undef ENABLE_RADIO_RESET_PIN
    #define ENABLE_RADIO_RESET_PIN 1  //  enable the use of the radio reset pin to reset the radio module

#elif defined(node_type_WIRbarr0)
  const int node_default_timeout = 360;
  #undef ENABLE_RADIO_RESET_PIN
    #define ENABLE_RADIO_RESET_PIN 1  //  enable the use of the radio reset pin to reset the radio module

#elif defined(node_type_WSoilHaa)
  const int node_default_timeout = 360;
  #undef ENABLE_RADIO_RESET_PIN
    #define ENABLE_RADIO_RESET_PIN 1  //  enable the use of the radio reset pin to reset the radio module
#endif 


#if defined(battery_node)   //if the node is a battery node:
  volatile byte keep_ADCSRA = ADCSRA; //save the state of the register;
  //unsigned long sleep_percentage = 0.9;// the ratio between sleep and awake time expressed as 0.x where 1.0 is 100% and 0.01 is 1%
  unsigned long stay_awake_period = 5 ;//how long in sec the node will stay awake to receive radio messages.
  uint8_t sleep_cycles = uint8_t( ( (node_default_timeout - stay_awake_period )/8 ) - 1 );  // number of sleep cycle to do ...8 seconds for each sleep cycle..
  unsigned long awake_time = 0;

#endif 


uint8_t node_obj_pinout[number_of_total_objects]; 
volatile int node_obj_status[number_of_total_objects];  






//********************************End of Onos objects configuration **************************************




int16_t packetnum = 0;  // packet counter, we increment per xmission
 
RFM69_ATC radio;



boolean radio_enabled=1;

unsigned long sync_time=0;
unsigned long *get_sync_time=&sync_time;
unsigned long sync_timeout=node_default_timeout;

volatile boolean interrupt_called=0;

char node_fw[]="01";
char encript_key[17]="onosEncryptKey01";  //todo read it from eeprom
//char init_encript_key[17]=INITENCRYPTKEY;
int this_node_address=254; //i start with 254


unsigned long get_address_timeout=0;

unsigned long *get_address_timeout_pointer=&get_address_timeout;


volatile unsigned long button_time_same_status=0;

volatile boolean button_still_same_status=1; 



volatile char enable_change_object_from_decoded_msg = 0;
volatile char obj_number_from_decoded_msg = 0;
volatile int obj_status_to_set_from_decoded_msg = 0;



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
const uint8_t rx_msg_lenght = 61;
const uint8_t decoded_radio_answer_lenght = 32;
const uint8_t syncMessage_lenght = 28;

#define DEVMODE 1
int onos_cmd_start_position=-99;  
int onos_cmd_end_position=-99;  
char received_message_type_of_onos_cmd[3];
uint8_t received_message_first_pin_used;
uint8_t received_message_second_pin_used;
int received_message_value;  //used in OnosMsg.cpp
//volatile char decoded_uart_answer[24]="er00_#]";
char decoded_radio_answer[decoded_radio_answer_lenght]="er00_#]";
int received_message_address=0; //must be int..
//volatile char filtered_uart_message[rx_msg_lenght+3];
char filtered_radio_message[rx_msg_lenght+3];
char syncMessage[syncMessage_lenght];
char str_this_node_address[3];
uint8_t main_obj_selected=0;
uint8_t rx_obj_selected=0;
char progressive_msg_id=48;  //48 is 0 in ascii   //a progressive id to make each message unique
char received_serial_number[13]; //used in OnosMsg
boolean reInitializeRadio=0;
boolean ota_loop=0; //enable the ota receiver loop
//////////////////////////////////End of Standard part to run decodeOnosCmd()//////////////////////////////////


uint8_t obj_button_pin;
//end node object pinuot, continue in setup() // 

OnosMsg OnosMsgHandler=OnosMsg();  //create the OnosMsg object

uint8_t radioRetry=3;      //todo: make this changable from serialport
uint8_t radioTxTimeout=20;  //todo: make this changable from serialport
uint8_t radioRetryAllarm=100; 
uint8_t radioTxTimeoutAllarm=50;  

# define gateway_address 1
//boolean first_sync=1;
unsigned long random_time=0;


/*unsigned long time_continuos_on=0;
unsigned long time_since_last_sync=0;
unsigned long time_from_turn_on=0;
float minutes_time_from_turn_on;
char tmp_minutes_time_from_turn_on_array[5];
char minutes_time_from_turn_on_array[5];

int timeout_to_turn_off=0;//0=disabled    600; //10 hours    todo   add the possibility to set it from remote

*/
//uint8_t skipRadioRxMsg=0;
//uint8_t skipRadioRxMsgThreshold=5;


volatile char main_obj_state=0;
//int old_main_obj_state=5;



unsigned long time_to_reset_encryption=3000; //this must be greater than time_to_change_status 
unsigned long time_to_change_status=30;


uint8_t tried_times;
uint8_t counter;
uint8_t pointer;
/*

const float VccExpected   = 3.0;
const float VccCorrection = 2.860/2.92;  // Measured Vcc by multimeter divided by reported Vcc
Vcc vcc(VccCorrection);
static int oldBatteryPcnt = 0;
*/


/*
int freeRam () 
{
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}

*/

void status_change_from_msg(char obj_number, int status_to_set)
{
        enable_change_object_from_decoded_msg = 1;
        obj_number_from_decoded_msg = obj_number;
        obj_status_to_set_from_decoded_msg = status_to_set;
}

boolean changeObjStatus(char obj_number,int status_to_set)
{

  Serial.print(F("changeObjStatusExecutedStatus:"));
  Serial.println(status_to_set);
  
  if (obj_number==button){ //will not change the status to the button...
    return(0);
  }
  

  #if defined(node_type_WreedSaa)
    if ( (obj_number==led)|(obj_number==digOut) ){
    digitalWrite(node_obj_pinout[obj_number],!status_to_set); // 
    Serial.println(F("dw_With_obj")); 
    }

  #elif defined(node_type_Wrelay4x)
    if (obj_number==0){
      main_obj_state=status_to_set;
      digitalWrite(node_obj_pinout[obj_number],!status_to_set); //  ! the relay are on when the pin is at gnd
      Serial.println(F("dw_With_obj")); 
      changeObjStatus(led,!status_to_set);
    }
    else if(obj_number<4) { //objects from 0 to 3 are relay  
      digitalWrite(node_obj_pinout[obj_number],!status_to_set); //  ! the relay are on when the pin is at gnd
      Serial.println(F("dw_With_obj")); 
    }
    else if (obj_number==led){
      digitalWrite(node_obj_pinout[obj_number],status_to_set); // 
      Serial.println(F("dw_With_obj")); 
    }
    
  #elif defined(node_type_WPlug1vx)
    if (obj_number==0){
      main_obj_state=status_to_set;
      delayMicroseconds(580);  // to prevent overcurrent absorption 

      digitalWrite(5,!status_to_set); // set relay1
      delayMicroseconds(580);  // to prevent overcurrent absorption I will drive a relay at a time..
      digitalWrite(6,!status_to_set); // set relay2
      delayMicroseconds(580);  // to prevent overcurrent absorption I will drive a relay at a time..
      digitalWrite(7,status_to_set);// reset both relays
      Serial.println(F("dw_With_obj")); 
      changeObjStatus(led,!status_to_set);
    }
    
    else if (obj_number==led){
      digitalWrite(node_obj_pinout[obj_number],status_to_set); // 
      Serial.println(F("dw_With_obj")); 
    }
    
    
  #endif

  if(obj_number==syncTimeout){  // if the object sent is syncTimeout change the sync_timeout with the value received
    sync_timeout=(unsigned long)(status_to_set*1000);// I need the cast otherwise there will be a overflow..
  }
  
  node_obj_status[obj_number]=status_to_set;
  
  return(1);



return(0);

}


void composeSyncMessage()
{
  Serial.println(F("composeSyncMessageExec"));
  //[S_01g05ProminiS0001x_#] 
  //strcpy(str_this_node_address,"");
  memset(str_this_node_address,0,sizeof(str_this_node_address)); //to clear the array
  str_this_node_address[0]='0';
  str_this_node_address[1]='0';
  
  //tmp_char_this_node_address = this_node_address ;  //make the cast of int to char

  str_this_node_address[0] = char(OnosMsgHandler.charDecToHex( this_node_address / 16) );
  str_this_node_address[1] = char(OnosMsgHandler.charDecToHex( this_node_address % 16) );
  str_this_node_address[2] = '\0';
  
  Serial.println(F("local_address_dec:"));
  Serial.println(this_node_address);

  Serial.println(F("local_address_hex:"));
  Serial.println(str_this_node_address[0]);
  Serial.println(str_this_node_address[1]);
  
  
  
  
  //strcpy(syncMessage, "");
  memset(syncMessage,0,sizeof(syncMessage)); //to clear the array
  strcpy(syncMessage, "[S_");
  strcat(syncMessage, str_this_node_address);
  
  #if defined(node_type_WreedSaa)
    //[S_01uWreedSaa000132Lgx_#]      reeds:3, temperature sensor:2, luminosity sensor:L, battery sensor:g 
    
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
      while (ADCSRA & (1 << ADSC)) ; //wait for the reading of previous analog read 
      luminosity_sensor_value= luminosity_sensor_value+analogRead(node_obj_pinout[luminosity_sensor])/4;
      while (ADCSRA & (1 << ADSC)) ; //wait for the reading of previous analog read 
      battery_value=battery_value+analogRead(node_obj_pinout[battery_state])/4;
      while (ADCSRA & (1 << ADSC)) ; //wait for the reading of previous analog read 
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
      strcat(syncMessage, "g");
      strcat(syncMessage, node_fw);
      strcat(syncMessage, serial_number);
    }
    else{
      strcat(syncMessage, "u");
      strcat(syncMessage, serial_number);
      
      uint8_t  tmp_len = strlen(syncMessage);
      
      syncMessage[tmp_len] = reed_sensors_state;   
      syncMessage[tmp_len + 1] = temperature_sensor_value_byte;  
      syncMessage[tmp_len + 2] = luminosity_sensor_value;   
      syncMessage[tmp_len + 3] = battery_value; 
      syncMessage[tmp_len + 4] = '\0'; 
    }
  
  #elif defined(node_type_Wrelay4x)
    
    if (this_node_address==254){
      strcat(syncMessage, "g");
      strcat(syncMessage, node_fw);
      strcat(syncMessage, serial_number);
    }
    else{
      //[S_123r4Wrelay4x00080110x_#]     0110 is the 4 relay status
      strcat(syncMessage, "u");
      // strcat(syncMessage, "sy");
      strcat(syncMessage, serial_number);
      uint8_t  tmp_len = strlen(syncMessage);
      syncMessage[tmp_len]=node_obj_status[0]+48;  
      syncMessage[tmp_len + 1]=node_obj_status[1]+48;  
      syncMessage[tmp_len + 2]=node_obj_status[2]+48;  
      syncMessage[tmp_len + 3]=node_obj_status[3]+48;  
      syncMessage[tmp_len + 4] = '\0'; 
      
    }
    
  #elif defined(node_type_WPlug1vx)
    
    if (this_node_address==254){
      strcat(syncMessage, "g");
      strcat(syncMessage, node_fw);
      strcat(syncMessage, serial_number);
    }
    else{
      //[S_123r4Wrelay4x00080110x_#]     0110 is the 4 relay status
      strcat(syncMessage, "u");
      // strcat(syncMessage, "sy");
      
      strcat(syncMessage, serial_number);
      uint8_t  tmp_len = strlen(syncMessage);
      syncMessage[tmp_len] = node_obj_status[0]+48; 
      syncMessage[tmp_len + 1] = '\0';
      
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
    
    
    
    // TODO: use sprintf(tmp_minutes_time_from_turn_on_array,"%04u",minutes_time_from_turn_on);  
    
    if (minutes_time_from_turn_on<10){
      dtostrf(minutes_time_from_turn_on,1, 0, tmp_minutes_time_from_turn_on_array);  //make a mull terminating array..
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
        
    uint8_t  tmp_len = strlen(syncMessage);
    syncMessage[tmp_len]=main_obj_state+48;   //+48 for ascii translation
    syncMessage[tmp_len + 1] = '\0';
          
    
    Serial.print(F("composeSyncMessageExecStatus:"));
    Serial.println(main_obj_state);
    strcat(syncMessage, minutes_time_from_turn_on_array);
  
  #endif  //end node_type_WLightSS
  
  
  if (progressive_msg_id<122){  //122 is z in ascii
    progressive_msg_id=progressive_msg_id+1;
  }
  else{
    progressive_msg_id=48;  //48 is 0 in ascii
  }
  
  
  uint8_t  tmp_len = strlen(syncMessage);
  syncMessage[tmp_len]=progressive_msg_id; //put the variable msgid in the array 
  syncMessage[tmp_len + 1] = '\0';
  //Serial.println(syncMessage[28]);
  //Serial.println(strlen(syncMessage));
  strcat(syncMessage, "_#]");
  

}



void sendSyncMessage(uint8_t retry,uint8_t tx_timeout=150)
{
  
  // composeSyncMessage();
  
  
  /*
  if (first_sync!=1 ){
  syncMessage[6]='r'; //modify the message
  syncMessage[7]='a'; //modify the message
  }
  */

  #if ENABLE_RADIO_RESET_PIN == 1  // if the radio reset pin is used in this node ..
    // unsigned long timetest=0;
    // timetest=millis(); 
    beginRadio();  //beginradio() takes about 12 ms to execute ...
    // Serial.print(F("prova time:"));
    // Serial.print(millis()-timetest);
  #endif
  
  Serial.println(F("sendWithRetrySendSyncMessageExecuted_#]"));
  if (radio.sendWithRetry(gateway_address, syncMessage, strlen(syncMessage),retry,tx_timeout)) {
    // note that the max delay time is 255..because is uint8_t
    //target node Id, message as string or byte array, message length,retries, milliseconds before retry
    //(uint8_t toAddress, const void* buffer, uint8_t bufferSize, uint8_t retries, uint8_t retryWaitTime)
    Serial.println(F("sent_sync_message1"));
    //    Blink(LED, 50, 3); //blink LED 3 times, 50ms between blinks
    //skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
    *get_sync_time=millis();

  }
  else{
    Serial.println(F("Error_sent_sync_msg_failed"));
    delay(1);

  }

  radio.receiveDone(); //put radio in RX mode
  //*get_sync_time=millis();
}




void getAddressFromGateway()
{
  Serial.println(F("getAddressFromGw ex"));
  
  //[S_123ga5.24WPlugAvx000810000x_#]
  
  composeSyncMessage();
  //syncMessage[5]='g'; //modify the message to get a address instead of just sync.  
  Serial.println(F("sendWRetry getAddressFromGw ex"));
  
  
  Serial.print(F("msgToSend:")); 
  
  for (pointer = 0; pointer < sizeof(syncMessage); pointer++){
    Serial.print(syncMessage[pointer]); 
    if (pointer > 0){
      if ((syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ){//  
        break;
      }
    }
  
  }
  Serial.println(F(":end")); 
  
  tried_times=0;


  
  while (tried_times < radioRetry ){
    Serial.println(F("r loopStart"));
    
    #if ENABLE_RADIO_RESET_PIN == 1  // if the radio reset pin is used in this node ..
      // unsigned long timetest=0;
      // timetest=millis(); 
      beginRadio();  //beginradio() takes about 12 ms to execute ...
      // Serial.print(F("prova time:"));
      // Serial.print(millis()-timetest);
    #endif
    
    /*
     * Serial.println(F("temp:"));
     * Serial.println(radio.readTemperature());
    */
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
      // skipRadioRxMsg=0; //reset the counter to allow this node to receive query 
      break;// exit the while (tried_times < radioRetry )
    }
    else{
      Serial.println(F("RadioTxFail,IRetry"));
      //random_time=10;//random(10,radioTxTimeout*3);
      tried_times=tried_times+1;
      delay(100);
      
      //LowPower.powerDown(SLEEP_15MS, ADC_OFF, BOD_OFF);
      //ADCSRA=keep_ADCSRA; //resume the status of the register
      
    }
  
  
  }
  
  syncMessage[6]='u'; //modify the message
  syncMessage[7]='l'; //modify the message
  *get_sync_time=millis();  // to prevent the skip rx message in the loop() when there is no address received yet..
  radio.receiveDone(); //put radio in RX mode
}




boolean checkAndHandleIncomingRadioMsg(){

  //print message received to serial
  Serial.print(F(" id:"));
  Serial.println(radio.SENDERID);
  Serial.print((char*)radio.DATA);
  Serial.print(F(" [RX_RSSI:"));Serial.print(radio.RSSI);Serial.print(F("]"));
  /*
  #if defined(ota_enabled)   //if the node is a battery node:
  CheckForWirelessHEX(radio, flash, false);  //to check for ota messages..
  #endif 
  */
  
  //uint8_t message_copy[rx_msg_lenght+1];
  
  //strcpy(filtered_radio_message,"");
  //memset(filtered_radio_message,0,sizeof(filtered_radio_message)); //to clear the array
  
  //Serial.println(radio.SENDERID);
  if (radio.TARGETID!=this_node_address){
    Serial.println(F("[S_er9_radioAddress_#]"));
    return(0); // todo: implement a forward of the message? 
  }
  
  Serial.print(F("msgStart:"));
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
      
    if (counter > (sizeof(filtered_radio_message)-1) ){  // to prevent overflow
      Serial.println(F("[S_erA_overflow_filtered_radio_message_#]"));
      break; 
    }
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
  
  
  Serial.println(F(":msgStop"));
  
  
  if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){
  
  Serial.println(F("onosCmdFound"));
  //noInterrupts(); // Disable interrupts    //important for lamp node 
  //decodeOnosCmd(filtered_radio_message);
  OnosMsgHandler.decodeOnosCmd(filtered_radio_message,decoded_radio_answer);
  
  
  if( (decoded_radio_answer[0]=='o')&&(decoded_radio_answer[1]=='k')){//if the message was ok...
    //check if sender wanted an ACK
    if (radio.ACKRequested()){
    radio.sendACK();
    Serial.println(F("-ACKsent"));
    *get_sync_time=millis();
    }
    if (enable_change_object_from_decoded_msg == 1){
      changeObjStatus(obj_number_from_decoded_msg,obj_status_to_set_from_decoded_msg);
      enable_change_object_from_decoded_msg = 0;

    }
  
    //interrupts(); // Enable interrupts
  return(1); 
  
  }
  else{
    Serial.print(F("errorInMsgDecode_I_dont_sendACK,i found:"));
    //  uint8_t k=0;
    //  while (k<decoded_radio_answer_lenght)
    for (uint8_t k=0; k<decoded_radio_answer_lenght; k++)
    {
      if (decoded_radio_answer[k]==0)
      {
        break;
      } 
      Serial.print(decoded_radio_answer[k]);
     // k=k+1;
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
    Serial.print(F("error_IN_msg_nocmd0_#]"));
    //Serial.print(onos_cmd_start_position);
    //Serial.println(onos_cmd_end_position);
    for (counter = 0; counter <= radio.DATALEN; counter++) {
      Serial.print(radio.DATA[counter]);
    }
    Serial.println(F("end_msg"));
    return(0); 
  }
  

}








void checkCurrentRadioAddress()
  {
  //Serial.println(F("checkCurrentRadioAddress()"));

  if(reInitializeRadio==1){
    Serial.print(F("reInitializeRadio==1"));
    beginRadio();
    reInitializeRadio=0;
    composeSyncMessage();
    sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm);
    // TODO: add return();  ?
  }
  
  
  #if defined(remote_node)   // only if this is a remote node..
    
    if (this_node_address==254){// i have not the proper address yet..
  
      random_time=10000;//random(4000,5000);
      
      if ((millis()-(*get_address_timeout_pointer))>random_time){ //every 10000/5000 ms
        #if defined(DEVMODE)
          Serial.print(F("get_address_timeout>time:"));
          Serial.println((millis()-*get_address_timeout_pointer));
        #endif
        
        getAddressFromGateway();  //ask the gateway for a proper address
        *get_address_timeout_pointer=millis();

      }
    }
    else{
/*
      Serial.print(F("*get_sync_time:")); 
      Serial.print(*get_sync_time);
      Serial.print(F("millis()-*get_sync_time:")); 
      Serial.print(millis()-*get_sync_time);
      Serial.print(F(",sync_timeout:")); 
      Serial.println(sync_timeout);
      */

      //random_time=1500;//random(1500,2500);
      
      #if defined(battery_node) // defined(node_type_WreedSaa)
        Serial.print(F("stay_awake_period:"));
        Serial.println(stay_awake_period,DEC);
        if ((millis()-*get_sync_time)>(stay_awake_period *1000)){ //every n ms
          composeSyncMessage();
          sendSyncMessage(radioRetryAllarm,radioTxTimeoutAllarm);
          //sync_time=millis(); changed, now is in sendSyncMessage
          /*
          awake_time=millis();
          Serial.println(F("wait_for_possible_rx_messages"));
          while ((millis()-awake_time)<stay_awake_period ){
            //note: if stay_awake_period < node_default_timeout 
            //      you will not see any delay on the frequency of node sync 
            //      because the time is taken from the node_default_timeout...
            Serial.print(F("millis()-awake_time:"));
            Serial.println(millis()-awake_time);
            //TODO: put if(millis()-awake_time)<stay_awake_period )--->sleep   in the main loop...
            if (radio.receiveDone()){
              //skipRadioRxMsg=skipRadioRxMsg+1;
              checkAndHandleIncomingRadioMsg();
            }
          }
          Serial.println(F("endWait"));
          */
          //  I put the node to sleep
          Serial.print(F("IGoToSleep for:"));
          Serial.print(sleep_cycles*8);
          Serial.println(F("sec"));
          Serial.flush();  //make sure all serial data is clocked

          radio.sleep();
          for (uint8_t i=0;i<=sleep_cycles;i=i+1){
            LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
          }
          Serial.println(F("EndSleep"));


          
          delayMicroseconds(50);
          ADCSRA=keep_ADCSRA; //resume the status of the register
        } // end  if ((millis()-*get_sync_time)> ..
        
      #endif  //end  if defined(battery_node)

      #ifndef battery_node // if not defined(node_type_WreedSaa)    //not a battery node
        if ((millis()-*get_sync_time)>sync_timeout){ //every 1500/2500 ms
          Serial.println(F("notABatteryNodePartExec"));
          composeSyncMessage();
          sendSyncMessage(radioRetry,radioTxTimeout);
            //sync_time=millis(); changed in in sendSyncMessage
        }
      #endif  //end  if defined(battery_node)


    }
    
  #endif  // end if defined(remote_node) 
  
}


void beginRadio()
{
  
  interrupts(); // Enable interrupts
  
  #if ENABLE_RADIO_RESET_PIN == 1  // if the radio reset pin is used in this node ..
    digitalWrite(RFM69_RST,1);
    delay(1); // delay for the module to receive the command
    digitalWrite(RFM69_RST,0); 
    delay(10); // delay to wait for the module to restart
  #endif

  
  *get_address_timeout_pointer=millis();
  
  // Initialize radio
  radio.initialize(FREQUENCY,this_node_address,NETWORKID);
  if (IS_RFM69HCW) {
    radio.setHighPower();    // Only for RFM69HCW & HW!
  }
  radio.setPowerLevel(31); // power output ranges from 0 (5dBm) to 31 (20dBm)
  
  radio.encrypt(encript_key);
  
  
  
  radio.enableAutoPower(targetRSSI);
  
  Serial.print(F("\nListeningAt:"));
  Serial.print(FREQUENCY==RF69_433MHZ ? 433 : FREQUENCY==RF69_868MHZ ? 868 : 915);
  Serial.println(F(" MHz"));
  Serial.print(F("radioAddrChTo:"));
  Serial.println(this_node_address);
  
  #if defined(battery_node)   //if the node is a battery node:
    keep_ADCSRA=ADCSRA; //save the state of the register
  #endif 
  

}

void buttonStateChanged()
{
  button_time_same_status=millis();   // i know it doesn't work correctly inside interrupt but it will give me the last timer anyway.
  button_still_same_status=0;
}

#if defined(node_type_WreedSaa)

  void handleReed()
  {//handle the reed sensor
    //node_obj_status[reed1Logic]=0;
    Serial.println(F("handleReedCalled"));
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



void handleButton()
{//handle the main node button , you can't call this from interrupt because millis() won't work

  Serial.print(F("handleButton()ex"));
  Serial.print(F("btn_still_same_status:"));
  Serial.print(button_still_same_status);
  Serial.print(F("btn_t_same_status:"));
  Serial.println(millis()-button_time_same_status);

   // Serial.print(F("obj_button pressed"));
  if (((millis()-button_time_same_status)>time_to_reset_encryption)
    &&( (millis()-button_time_same_status)<time_to_reset_encryption*2)){  //button pressed for more than x seconds
  
    Serial.println(F("time_to_reset_encryption_#]"));
    noInterrupts(); // Disable interrupts ,this will be reenabled from beginRadio()
    memset(encript_key,0,sizeof(encript_key)); //to clear the array
    strcpy(encript_key,INITENCRYPTKEY);//reset the encript_key to default to made the first sync with onoscenter 
    this_node_address=254;//reset the node address
    //first_sync=1;
    setup();
    //beginRadio();  //restart radio with the default encript_key  
    //checkCurrentRadioAddress();  
    interrupts(); // Enable interrupts 
    button_time_same_status=millis();
  }

  if (((millis()-button_time_same_status)>time_to_change_status)
                &&(button_still_same_status==0)){
    Serial.println(F("time_to_change_status_#]"));
    changeObjStatus(main_obj_selected,!main_obj_state);  // this will make a not of current state
    button_still_same_status=1;
    composeSyncMessage();
    sendSyncMessage(radioRetry+2,radioTxTimeout); 
    button_time_same_status=millis();
    delay(100);//todo change it smaller

  }

}
#if defined(node_type_WreedSaa)
  void interrupt1_handler()
  {

    detachInterrupt(1);
    interrupt_called=1;
    //Serial.println(F("interrupt called"));
    #if defined(battery_node)   //if the node is a battery node:
      ADCSRA=keep_ADCSRA; //resume the status of the register
    #endif
    handleReed();
    reed1_status_sent=node_obj_status[reed1];
    reed2_status_sent=node_obj_status[reed2];
    //delay(2);  //delays won't work in thw interrupt..
    node_obj_status[reed1]=digitalRead(node_obj_pinout[reed1]);
    node_obj_status[reed2]=digitalRead(node_obj_pinout[reed2]);
    /* 
    if ((reed1_status_sent!=node_obj_status[reed1] ) |(reed2_status_sent!=node_obj_status[reed2] )){ //if the reed has changed status during last transmission
    Serial.println(F("-reed has changed again"));
    handleReed();
    }
    */
    attachInterrupt(1, interrupt1_handler, CHANGE); //set interrupt on the hardware interrupt 1
    handleReed();
  
  }
#endif



#if defined(ota_enabled)
void ota_receive_loop()
{

  Serial.println(F("ota_receive_loop()exec"));

  ota_loop_start_time=millis()+5000;

  while( (millis()-ota_loop_start_time)>ota_timeout) {
    CheckForWirelessHEX(radio, flash, false);
  }
  ota_loop=0;

}
#endif


void setup()
{
  noInterrupts(); // Disable interrupts    //important for lamp node
  
/*
 * 
 *
 * All AVR based boards have an SS pin that is useful when they act as a slave controlled by an external master.
 * this pin should be set always as OUTPUT otherwise the SPI interface could be put automatically into slave mode by hardware,
 * rendering the library inoperative. 
 * 
*/
  pinMode(RFM69_CS, OUTPUT);  //  NSS setted as output        

  node_obj_status[syncTimeout]=node_default_timeout;
  sync_timeout=(unsigned long)node_default_timeout*1000;  // I need the cast otherwise there will be a overflow..
  
  #if ENABLE_RADIO_RESET_PIN == 1  // if the radio reset pin is used in this node ..
    pinMode(RFM69_RST, OUTPUT); 
  #endif

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
    node_obj_pinout[tempSensor]=A0;   // the forth object is the temperature sensor connected on analog pin 1  
    node_obj_pinout[battery_state]=A1;   // the 9th object is the battery state connected on analog pin 0  
    node_obj_pinout[luminosity_sensor]=A2; 
    node_obj_pinout[digOut]=9;  // the    5  object is the digital output connected on pin 9 
    node_obj_pinout[reed2]=6;   // the    6  object is the reed2 connected on pin 6 
    // END OBJECTS PIN DEFINITION_______________________________________________________________
    pinMode(node_obj_pinout[reed1], INPUT);
    pinMode(node_obj_pinout[button], INPUT);
    pinMode(node_obj_pinout[led], OUTPUT);
    pinMode(node_obj_pinout[digOut], OUTPUT);
    pinMode(node_obj_pinout[reed2], INPUT);
    digitalWrite(node_obj_pinout[reed1],1); //set pullup on reed
    //  digitalwrite(node_obj_pinout[reed2],1);



  #elif defined(node_type_Wrelay4x)
    memset(serial_number,0,sizeof(serial_number)); //to clear the array
    strcpy(serial_number,"Wrelay4x");
    strcat(serial_number,numeric_serial);
    // OBJECTS PIN DEFINITION___________________________________________________________________
    node_obj_pinout[relay1]=7;  // the first  object is the relay 1 connected on pin 7 
    node_obj_pinout[relay2]=5;  // the second object is the relay 2 connected on pin 5  
    node_obj_pinout[relay3]=6;  // the third  object is the relay 3 connected on pin 9 
    node_obj_pinout[relay4]=5;  // the forth  object is the relay 4 connected on pin 3 
    node_obj_pinout[led]=4;     // the fifth  object is the led     connected on pin 4
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
    memset(serial_number,0,sizeof(serial_number)); //to clear the array
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
  
  
  
  //while (!Serial); // wait until serial console is open, remove if not tethered to computer
  Serial.begin(SERIAL_BAUD);
  
  
  
  
  Serial.println(F("Setup -----------------"));
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
  digitalWrite(node_obj_pinout[led], 1); // 1 to to turn ledd off
  
  
  //enabling interrupt must be the LAST THING YOU DO IN THE SETUP!!!!
  #if defined(node_type_WreedSaa)
    attachInterrupt(1, interrupt1_handler, CHANGE); //set interrupt on the hardware interrupt 1
    Serial.println(F("WreedSaa interrupt en"));
  #elif defined(node_type_WPlug1vx)
    digitalWrite(node_obj_pinout[led], 0); // 1 to to turn ledd off
    attachInterrupt(digitalPinToInterrupt(node_obj_pinout[button]), buttonStateChanged, FALLING);
    Serial.println(F("WPlug1vx interrupt en"));
  #elif defined(node_type_Wrelay4x)
    attachInterrupt(digitalPinToInterrupt(node_obj_pinout[button]), buttonStateChanged, FALLING);
    Serial.println(F("Wrelay4x interrupt en"));

  #endif 
  
  
  
  
  
  
  
  interrupts(); 
  // if analog input pin 1 is unconnected, random analog
  // noise will cause the call to randomSeed() to generate
  // different seed numbers each time the sketch runs.
  // randomSeed() will then shuffle the random function.
  //randomSeed(analogRead(1));
  
  
  #if defined(ota_enabled)   //warning don't move this part (leave it as last part after enabling interrupts or the arduino will sometimes not boot.
    if (flash.initialize())
      Serial.println(F("SPI Flash Init OK!"));
    else
      Serial.println(F("SPI Flash Init FAIL!"));
  #endif 
  
  
}
 
void loop() 
{

  #if defined(node_type_Wrelay4x)
    if (button_still_same_status==0){  //filter 
      obj_button_pin=node_obj_pinout[button];
      if (digitalRead(obj_button_pin)==0) { 
        handleButton();
      }
    }
  #elif defined(node_type_WPlug1vx)
    if (button_still_same_status==0){  //filter 
      obj_button_pin=node_obj_pinout[button];
      if (digitalRead(obj_button_pin)==0){ 
        handleButton();
      }
    }
  #elif defined(node_type_WreedSaa)
    if (interrupt_called == 1){
      Serial.println(F("interruptCall"));
      interrupt_called = 0;
    }
  #endif 
  
  
  
  
  if ((millis()-*get_sync_time)>(sync_timeout*3)){
    // if the timeout is n time greater than the default it means there are too many rx messages(with possible errors)
    // I will skip one in order to sens a sync message
    Serial.println(F("IskipRxradioPartOnce"));
    goto radioTx;
  }
/*
  if (skipRadioRxMsg>skipRadioRxMsgThreshold){  //to allow the execution of radio tx , in case there are too many rx query..
    skipRadioRxMsg=0;  //reset the counter to allow this node to receive query 
    Serial.println(F("IskipRxradioPartOnce"));
    goto radioTx;
  }
*/

  #if defined(ota_enabled)  
  if (ota_loop==1){
    ota_receive_loop();
  }
  #endif 
  
  if (radio.receiveDone()){
    //skipRadioRxMsg=skipRadioRxMsg+1;
    checkAndHandleIncomingRadioMsg();
  }
  
  radioTx:
  
  radio.receiveDone();  //put radio in RX mode
  Serial.flush();  //make sure all serial data is clocked
  
  checkCurrentRadioAddress();
  

}  //END OF LOOP()

void Blink(byte PIN, byte DELAY_MS, byte loops)
{
  for (byte i=0; i<loops; i++){
    digitalWrite(PIN,HIGH);
    delay(DELAY_MS);
    digitalWrite(PIN,LOW);
    delay(DELAY_MS);
  }
}


