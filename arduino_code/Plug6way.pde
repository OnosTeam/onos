/*
 * O.N.O.S.  node firmware by Marco Rigoni 28-4-15  elettronicaopensource@gmail.com 
 * more info on www.myonos.com 
 * UIPEthernet is a TCP/IP stack that can be used with a enc28j60 based
 * Ethernet-shield.
 *
 * UIPEthernet uses the fine uIP stack by Adam Dunkels <adam@sics.se>
 *
 */


/*


Wire up as following (ENC = module side):
- ENC SO -> Arduino pin 12
- ENC SI -> Arduino pin 11
- ENC SCK -> Arduino pin 13
- ENC CS -> Arduino pin 10
- ENC VCC -> Vcc 3V3 
- ENC GND -> Arduino Gnd pin
*/


// to reset arduino :  asm volatile ("  jmp 0");
#include <UIPEthernet.h>
#include <avr/wdt.h> //watchdog


//uncomment this for dev mode

//#define DEVMODE 1
 

//pin setup print
//#define DEVMODE2 1    

//#define DEVMODE3 1          

#define onos_center_port 81

EthernetClient client;
uint8_t first_time=1;
uint8_t only_digital_out=1;  //set to 0 if the node is not only a digital out type
signed long next;
unsigned long sync_time=0;
unsigned long keep_powerline_alive_time=0;
uint8_t digital_setup[10];
char digital_status[10];
boolean pin_status_to_update=0;
uint8_t used_pins[10];
uint8_t analog_in_setup[10];
uint8_t analog_tolerance=20;
uint16_t analog_values[17];// store the  values from analog input   2 bytes for each data

//banana read eeprom and retrieve the node_type and serial number then compose the mac address 



char serial_number[]="Plug6way0001"; //BANANA TO READ FROM EEPROM

char node_fw[]="5.13";

int this_node_address=999; //note that onos must send this number to talk with ethernet and powerline nodes 


uint8_t mac[6]; // {0x00,0x01,0x02,0x03,0x04,0x05};  //BANANA to change for each node




EthernetServer server = EthernetServer(9000); //port number 9000



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







uint8_t counter=0;
char data_from_serial[rx_msg_lenght+5];
boolean enable_print=0;







void composeSyncMessage(){

  //[S_001sy3.05ProminiS0001_#] 
  int tmp_number=0;
  strcpy(str_this_node_address,"");

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
  


  strcpy(syncMessage, "[S_");
  strcat(syncMessage, str_this_node_address);
  strcat(syncMessage, "sy");
  strcat(syncMessage, node_fw);
  strcat(syncMessage, serial_number);
  strcat(syncMessage, "_#]");

/*
  for (uint8_t pointer = 0; pointer <= rx_msg_lenght; pointer++) {
    Serial.print(syncMessage[pointer]);
    if (pointer<2){
      continue;
    }

    if ((syncMessage[pointer-2]=='_')&&(syncMessage[pointer-1]=='#')&&(syncMessage[pointer]==']')  ) {//  
        break;
      }
    }   
    Serial.print('\n'); 

*/

}


void decodeOnosCmd(const char *received_message){
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

  strcpy(received_message_answer,"err01_#]");



  if ((received_message[0]=='[')&&(received_message[1]=='S')&&(received_message[2]=='_') ) {
 // the onos cmd was found           [S_001dw06001_#]


    strcpy(received_message_answer,"cmdRx_#]");               


    received_message_type_of_onos_cmd[0]=received_message[6];
    received_message_type_of_onos_cmd[1]=received_message[7];

    received_message_address=(received_message[3]-48)*100+(received_message[4]-48)*10+(received_message[5]-48)*1;


         

    if (received_message_address!=this_node_address) {//onos command for a remote arduino node
      strcpy(received_message_answer,"remote_#]");

/*


      Serial.print(F("serial_number222:")); 
      Serial.print(serial_number);
      Serial.println(F("end")); 
*/
      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


    //[S_001dw06001_#]
    if ( received_message_type_of_onos_cmd[0]=='d' && received_message_type_of_onos_cmd[1]=='w' ){

      received_message_value=received_message[12]-48;
      if (received_message_value>1){ 
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;

      pinMode(received_message_first_pin_used, OUTPUT); 
      digitalWrite(received_message_first_pin_used, received_message_value); 
      strcpy(received_message_answer,"ok");
      return;
    }
    
    //[S_001aw06125_#]
    else if( received_message_type_of_onos_cmd[0]=='a' && received_message_type_of_onos_cmd[1]=='w' ){
 
      received_message_value=(received_message[10]-48)*100+(received_message[11]-48)*10+(received_message[12]-48)*1;

      if ((received_message_value<0)||(received_message_value>255)){ //status check
        received_message_value=0;
      //Serial.println(F("onos_cmd_value_error"));  
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
      analogWrite(received_message_first_pin_used, received_message_value); 
      strcpy(received_message_answer,"ok");
      return;
    } 

 
    //[S_001sr04051_#] 
    else if( received_message_type_of_onos_cmd[0]=='s' && received_message_type_of_onos_cmd[1]=='r' ){

      received_message_value=received_message[12]-48;      

      if (received_message_value>1){ 
        strcpy(received_message_answer,"er0_status_#]"); 
        return;
      }

      received_message_first_pin_used= ((received_message[8])-48)*10+(  (received_message[9])-48)*1;
      received_message_second_pin_used=((received_message[10])-48)*10+(  (received_message[11])-48)*1;

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

      strcpy(received_message_answer,"ok");
      return;
    }


/*


    switch (received_message_type_of_onos_cmd) {
                                         //onos_d05v001sProminiS0002f002_#] to remote..
      case 'd':{     //digital write       onos_d05v001sProminiS0001f001_#]  where the last'a' will be a char from 0 to 255 indicating the address of the node
        if (received_message_value>1){ 
          strcpy(received_message_answer,"er0_status_#]"); 
          break;
        }
      
        pinMode(received_message_first_pin_used, OUTPUT); 
        digitalWrite(received_message_first_pin_used, received_message_value); 
        strcpy(received_message_answer,"ok");
        break;
      }

      case 'a':{     //pwm write           onos_a07v100sProminiS0001f001_#]
        analogWrite(received_message_first_pin_used, received_message_value); 
        strcpy(received_message_answer,"ok");
        break;
      }

      case 's':{     //servo controll      onos_s07v180sProminiS0001f001_#]
        //servo are not supported yet
        //myservo.attach(received_message_first_pin_used);  // attaches the servo on pin 2 to the servo object 
        //myservo.write(received_message_value);              // tell servo to go to position in variable 'pos'
        strcpy(received_message_answer,"ok");
        break;
      }  

      case 'g':{     //get digital status  onos_g0403v0sProminiS0001f001_#]
        pinMode(received_message_first_pin_used, INPUT); 
        pinMode(received_message_second_pin_used, INPUT);
        digitalWrite(received_message_first_pin_used,1); //enable internal pullup resistors
        digitalWrite(received_message_second_pin_used,1);//enable internal pullup resistors
        delayMicroseconds(20);  //wait a bit
        char val_first_pin=digitalRead(received_message_first_pin_used)+48;
        char val_second_pin=digitalRead(received_message_second_pin_used)+48;
        strcpy(received_message_answer,""); 
        strcpy(received_message_answer,"ok_s="); 
        received_message_answer[5]=val_first_pin;
        received_message_answer[6]=val_second_pin;
        received_message_answer[7]='_';
        received_message_answer[8]='#';
        received_message_answer[9]=']';

        //strcat(received_message_answer,"_#]");
        // answer will be like:   ok_s=00_#] 
        
        
        break;
      }  
                                           
      case 'r':{     //relay               onos_r1415v1sProminiS0001f001_#]
        received_message_value=(received_message[11]-'0');


        strcpy(received_message_answer,"ok");
        received_message_second_pin_used=((received_message[8])-48)*10+(  (received_message[9])-48)*1;

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

        break;
      } 

      default:{
        strcpy(received_message_answer,"type_err");
        Serial.println(F("onos_cmd_type_error"));  
      }
  

   }//end of the switch case

*/
    
/*
    Serial.print(F("onos_cmd:"));
    Serial.println(received_message_type_of_onos_cmd);




    Serial.println(F("pin_used:"));
    Serial.println(received_message_first_pin_used);
    Serial.println(F("pin_used2:"));
    Serial.println(received_message_second_pin_used);

    Serial.print(F("message_value:"));
    Serial.println(received_message_value);


    
*/








 } // end of if message start with onos_   






}// end of decodeOnosCmd()












//server part
void server_handler(EthernetClient client_query ){

  char received_query [25];// query from the browser or from onos with urlib
  uint8_t i=0;
  uint8_t pin_number_used;
  char msg_lenght=18;
  uint8_t quit=0;


  counter=0;


  unsigned long timeout=millis()+200;


  while (client_query.connected() ) {

    //banana  make watchdog
    

    while(client_query.available() > 0){  



      enable_print=1;
  // Serial.println(F("im"));
   //Serial.println(counter);
   // read the incoming byte:
      delayMicroseconds(100);  //the serial doesnt work without this delay...

      data_from_serial[counter] = client_query.read(); 

      if ( millis()>timeout){
        Serial.println(F("serial_timeout---------------------------------"));
        break;
      }
  
      if (counter>rx_msg_lenght){  //prevent overflow
        Serial.println(F("array_overflow prevented---"));
        Serial.println(counter);
        Serial.println(F("end"));
        counter=0;
        continue;     
      }


      if (counter<2){
        counter=counter+1;
        continue;     
      }


      if ( (filtered_onos_message[counter-2]=='[')&&(filtered_onos_message[counter-1]=='S')&&(filtered_onos_message[counter]=='_')  ){//   
        Serial.println("cmd start found-------------------------------");
        onos_cmd_start_position=counter-2;
      }


      if( (filtered_onos_message[counter-2]=='_')&&(filtered_onos_message[counter-1]=='#')&&(filtered_onos_message[counter]==']')  ){//   
        Serial.println("cmd end found-------------------------------");
        onos_cmd_end_position=counter-2;
        break;// now the message has ended
      }


      counter=counter+1;
     
      }//end while  client_query.available()


    if ( (onos_cmd_start_position!=-99) && (onos_cmd_end_position!=-99 )){
      Serial.println("onos cmd  found-------------------------------");
      decodeOnosCmd(filtered_onos_message);

      if( (received_message_answer[0]=='o')&&(received_message_answer[1]=='k')){//if the message was ok...
      //check if sender wanted an ACK

          Serial.println(" - ACK sent");


      }
      else{
        Serial.println("error in message decode i will not send the ACK");
      }



    }
    else{
      strcpy(received_message_answer,"nocmd0_#]");
      Serial.println("error in message nocmd0_#]");
    }



    if (enable_print==1){ //write if there is a not recognise message  shorter...

      client_query.println(received_message_answer);
      client_query.flush();    
      client_query.stop();
      enable_print=0;

#if defined(DEVMODE)
      Serial.print(F("answer:"));
      Serial.println(received_message_answer);
#endif


      break;


    }




  }


}





//end of server part







//client part





void pinsSetup(){


  //serial_number="ProminiA0001";
  boolean setup_done=0;


  while (setup_done==0){


    #if defined(DEVMODE)
    Serial.println(F("get setup"));
    #endif
    if (client.connect(IPAddress(192,168,101,1),onos_center_port)){
//old      192.168.0.101/onos_cmd?cmd=pinsetup&node_sn=ProminiA0001&node_fw=4.85&node_ip=192.168.0.7__


//    "pinsetup?sn=ProminiA0001&fw=4.85_#]"

      char ask_setup[37]; 
      strcpy(ask_setup,"pinsetup?sn=");
      strcat(ask_setup,serial_number);
      strcat(ask_setup,"&fw=");
      strcat(ask_setup,node_fw);
      strcat(ask_setup,"_#]");


    #if defined(DEVMODE)
      Serial.print(F(" setup:"));

      Serial.println(ask_setup);
    #endif

      client.println(ask_setup);
      client.flush();
      boolean en=1;
      next = millis() + 1000;

      
      while(client.available()==0){




        #if defined(DEVMODE)
        Serial.println(F("waitAnswerFromServer"));
        #endif
        if (next - millis() < 0){
        #if defined(DEVMODE)
          Serial.println(F("Cl disconnect"));
        #endif
          client.flush();
          client.stop();
          en=0;
          break;
        }
        
      }
      if (en==0){
        continue;
      }
      #if defined(DEVMODE)
      Serial.println(F("Cl connect"));
      #endif
     // byte size;
      //size = client.available()+1;

      //uint8_t* msg = (uint8_t*)malloc(size);// create a byte pointer with a free address from malloc
      // uint8_t   is the same as byte on arduino 2009 , unsigned 8 bit variable
      

      uint8_t i=0;
      
      uint8_t prev_msg=0;
      boolean read_msg=0;
       
      //byte digital_setup[10]; 
      uint8_t msg=0;
      while(client.available() > 0){  
        
        msg=client.read();
      #if defined(DEVMODE)
        Serial.println(msg);
      #endif


      }

      client.stop();
      


  } //if client.connect 

  else{
      #if defined(DEVMODE)
    Serial.println(F("Cl connect fail3"));
      #endif
    client.flush();
    client.stop();
    delay(100); 
    continue;
  }


  if (setup_done==0){  //(msg_array not containing the setup ..
      #if defined(DEVMODE)
    Serial.println(F("ServerAnswerNotOk"));
      #endif
    client.flush();
    client.stop();
    delay(200); 
    continue;

  }




 }//while setup_done 
  
//now i have the setup



}// pinsetup closed


void setup() {
 // wdt_disable();
 //wdt_reset();
#if defined(DEVMODE)
  Serial.begin(115200);
  Serial.print(F("start "));

#endif


  mac[0] =serial_number[11];  
  mac[1] =serial_number[10];
  mac[2] =serial_number[9];
  mac[3] =serial_number[8];
  mac[4] =serial_number[7];
  mac[5] =serial_number[6];

  delay(200); //wait for the ethernet module to power on 

   //IPAddress myIP(192,168,0,26);
   //Ethernet.begin(mac,myIP);
 // wdt_enable(WDTO_8S);
 // wdt_reset();
  Ethernet.begin(mac);
  Serial.print(F("Ethernet.begin "));





  delay(100);   // give the Ethernet shield a second to initialize:
  //wdt_reset();
#if defined(DEVMODE)
  Serial.print(F("localIP: "));
  Serial.println(Ethernet.localIP());
  Serial.print(F("subnetMask: "));
  Serial.println(Ethernet.subnetMask());
  Serial.print(F("gatewayIP: "));
  Serial.println(Ethernet.gatewayIP());

#endif

/*
  Serial.print(F("dnsServerIP: "));
  Serial.println(Ethernet.dnsServerIP());
*/
  next = 0;

  //banana to check if the arduino get a valid ip
  //client.stop();	// DISCONNECT FROM THE SERVER
  //wdt_reset();
  pinsSetup();

  server.begin();
  //Serial.println(F("Serverstart"));
  //wdt_reset();


}

void loop() {
  //wdt_reset();
  //if (((signed long)(millis() - next)) > 0)


//#if defined(DEVMODE)
 // Serial.println(F("loop"));
//#endif    
  EthernetClient client_request = server.available(); 
  unsigned long diff_time = millis ();

    if (client_request){
   // Serial.println(F("q r"));
      if (client_request.connected()){
        server_handler(client_request);

       }
    //Serial.println(F("q ans"));

  }









//digital part ,not used in socket nodes type unocomment
// if ((pin_status_to_update>0)&&(!client_request)){//send the data n times

  if (  (millis()-keep_powerline_alive_time )>2500){  //each 2,5 seconds to keep the powerline alive

    sync_time=millis();
    if (client.connect(IPAddress(192,168,101,1),onos_center_port+5)){ //just to keep the powerline active

      delayMicroseconds(1); //just to do something
    }
    #if defined(DEVMODE3)
    Serial.print(F("pin_status_to_update= "));
    Serial.println("deleted.....not_used");

    #endif    
 
      
  }

  else{ //just to keep alive...

    
    if ( (millis()-sync_time)>60000){   //each 60 sec time contact the onosCenter and update the current ip address
      sync_time=millis();
      if (client.connect(IPAddress(192,168,101,1),onos_center_port)){


        char ask_sync[33]="n_sync?sn=";

        composeSyncMessage();

        client.print(syncMessage);
        client.flush();


        next = millis() + 1000;
        while(client.available()==0){

          if (next - millis() < 0){
        #if defined(DEVMODE)
            Serial.println(F("Cl disconnect"));
        #endif
            client.flush();
            client.stop();
            break;

          }

    
        }

        uint8_t msg=0;
        while(client.available() > 0){  
        
          msg=client.read();

        }
        client.stop();


    	#if defined(DEVMODE)
   		Serial.println(F(" node ip updated"));
   		#endif 
   		client.stop();	// DISCONNECT FROM THE SERVER
    	} 

    	if (client.connected()) { 
		  client.stop();	// DISCONNECT FROM THE SERVER
	}


  }

}// END     if ( (sync_time-t)>10000){






/*

 k=0;
  while (k<9){
    Serial.print(F("an setup= "));
    Serial.println(analog_in_setup[k]);
  k=k+1;
  } 
*/




}
