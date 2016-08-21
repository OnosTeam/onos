/*
 * O.N.O.S.  node firmware by Marco Rigoni 28-4-15  elettronicaopensource@gmail.com 
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
uint8_t digital_setup[10];
char digital_status[10];
boolean pin_status_to_update=0;
uint8_t used_pins[10];
uint8_t analog_in_setup[10];
uint8_t analog_tolerance=20;
uint16_t analog_values[17];// store the  values from analog input   2 bytes for each data

//banana read eeprom and retrieve the node_type and serial umber then compose the mac address 
char node_type='a';     //banana temp 'a' for arduino pro mini
char serial_char=1 ;   //banana to read from eprom
char node_fw[]="5.13";
char node_code_name[]="Plug6way0001";
char serial_number[]="0001"; //BANANA TO READ FROM EEPROM





uint8_t mac[6] = {0x00,0x01,0x02,0x03,0x04,0x05};  //BANANA to change for each node
uint8_t analog_count=0;
//uint8_t pins_to_reset1=99;  //pin used with a set reset relay pin
//uint8_t pins_to_reset2=99;  //pin used with a set reset relay pin

EthernetServer server = EthernetServer(9000); //port number 9000



    
   //onos_r1716v1s0004_#]
   //onos_d07v001s0001_#]

char serial_message_type_of_onos_cmd;
uint8_t serial_message_first_pin_used;
uint8_t serial_message_second_pin_used;
int serial_message_value;
char serial_message_answer[21]="er00_#]";
char serial_message_sn[5]="";

uint8_t serial_msg_lenght=19;
uint8_t counter;
boolean enable_print=0;






boolean is_pin_setup_as_do(uint8_t pin_number_to_check){
  char reg =pin_number_to_check/8;
  char pos =pin_number_to_check%8;
  boolean is_digital_out=0; 
  if ( (  (bitRead(used_pins[reg],pos))==1 )&&(  (bitRead(digital_setup[reg],pos))==1 )){// the pin is used and not as digital input


#if defined(DEVMODE)
      Serial.print(F("pin used:"));
      Serial.print(pin_number_to_check);
#endif


      is_digital_out=1;  
  }
  return(is_digital_out);
}


void decodeOnosCmd(char received_message[]){
#if defined(DEVMODE)
  Serial.println(F("decodeOnosCmd executed"));
#endif

  strcpy(serial_message_answer,"err01_#]");
  if ((received_message[0]=='o')&&(received_message[1]=='n')&&(received_message[2]=='o')&&(received_message[3]=='s')&&(received_message[4]=='_'))
  { // the onos cmd was found           onos_d07v001s0001_#]


    strcpy(serial_message_answer,"cmdRx_#]");               


    strcpy(serial_message_sn,""); 

    serial_message_sn[0]=received_message[13];
    serial_message_sn[1]=received_message[14];
    serial_message_sn[2]=received_message[15];
    serial_message_sn[3]=received_message[16];



    serial_message_type_of_onos_cmd=received_message[5];
         
    serial_message_first_pin_used=((received_message[6])-48)*10+(  (received_message[7])-48);

    serial_message_second_pin_used=-1;
                                    

    if (received_message[8]=='v'){
      serial_message_value=(received_message[9]-48)*100+(received_message[10]-48)*10+(received_message[11]-48)*1;

      if ((serial_message_value<0)||(serial_message_value>255)){ //status check
        serial_message_value=0;
      //Serial.println(F("onos_cmd_value_error"));  
        strcpy(serial_message_answer,"er0_status_#]"); 
        return;
      }



    }
    else{
 
      if (received_message[10]=='v'){

        serial_message_value=(received_message[11]-'0');

        if ((serial_message_value==0)||(serial_message_value==1)){ //status check  
          strcpy(serial_message_answer,"cmdRx_#]");
        }
        else{
          strcpy(serial_message_answer,"er1_status_#]");  
          return;                 
        }

      }

    }



               








 

    if (strcmp(serial_message_sn,serial_number)!=0) {//onos command for a remote arduino node
      strcpy(serial_message_answer,"ersn0_#]");
      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


    switch (serial_message_type_of_onos_cmd) {

      case 'd':{     //digital write       onos_d07v001s0001_#]
        strcpy(serial_message_answer,"ok_#]");
        if (is_pin_setup_as_do(serial_message_first_pin_used)==0) { //if the pin is not setted up as digital out
          strcpy(serial_message_answer,"er_ds_#]");
          return;
        }

        pinMode(serial_message_first_pin_used, OUTPUT); 
        digitalWrite(serial_message_first_pin_used, serial_message_value); 
        break;
      }

      case 'a':{     //pwm write           onos_a07v100s0001_#]
        analogWrite(serial_message_first_pin_used, serial_message_value); 
        strcpy(serial_message_answer,"ok_#]");
        break;
      }
              
      case 's':{     //servo controll      onos_s07v180s0001_#]
        strcpy(serial_message_answer,"ok_#]");
        if (is_pin_setup_as_do==0) { //if the pin is not setted up as digital out
          strcpy(serial_message_answer,"er_ds_#]");

        }
        analogWrite(serial_message_first_pin_used, serial_message_value); //todo:  to add servo
        break;
      }  

      case 'g':{     //get digital status  onos_g0708v0s0001_#]  
        pinMode(serial_message_first_pin_used, INPUT); 
        pinMode(serial_message_second_pin_used, INPUT); 
        char val_first_pin=digitalRead(serial_message_first_pin_used)+48;
        char val_second_pin=digitalRead(serial_message_second_pin_used)+48;
        strcpy(serial_message_answer,""); 
        strcpy(serial_message_answer,"ok_s="); 
        serial_message_answer[5]=val_first_pin;
        serial_message_answer[6]=val_second_pin;
        serial_message_answer[7]='_';
        serial_message_answer[8]='#';
        serial_message_answer[9]=']';

        //strcat(serial_message_answer,"_#]");
        // answer will be like:   ok_s=00_#] 
        
        
        break;
      }  

      case 'r':{     //relay               onos_r1716v1s0004_#]
        strcpy(serial_message_answer,"ok_#]");
        serial_message_second_pin_used=((received_message[8])-48)*10+(  (received_message[9])-48)*1;


        if (is_pin_setup_as_do(serial_message_first_pin_used)==0) { //if the pin is not setted up as digital out
          strcpy(serial_message_answer,"er_ds1_#]");

        }
        if (is_pin_setup_as_do(serial_message_second_pin_used)==0) { //if the pin is not setted up as digital out
          strcpy(serial_message_answer,"er_ds2_#]");

        }


        pinMode(serial_message_first_pin_used, OUTPUT); 
        pinMode(serial_message_second_pin_used, OUTPUT); 
        //note to se a relay you have to transmit before the set pin and after the reset pin , the lessere first
        //  so for example serial_message_first_pin_used =14   serial_message_second_pin_used=15
        digitalWrite(serial_message_first_pin_used,!serial_message_value); 
        digitalWrite(serial_message_second_pin_used,serial_message_value); 
                     //attention with this only one relay per message can be setted!!!
                     //pins_to_reset1=pin_number_used;
                     //pins_to_reset2=second_pin_number_used;
        delay(150);
        digitalWrite(serial_message_first_pin_used,0); 
        digitalWrite(serial_message_second_pin_used,0);  



         



        break;
      } 

      default:{
        strcpy(serial_message_answer,"type_err");
        Serial.println(F("onos_cmd_type_error"));  
      }
  

   }//end of the switch case


    /*

    Serial.print(F("onos_cmd:"));
    Serial.println(serial_message_type_of_onos_cmd);

    Serial.print(F("serial_number:"));
    Serial.print(serial_message_sn);


    Serial.println(F("pin_used:"));
    Serial.println(serial_message_first_pin_used);
    Serial.println(F("pin_used2:"));
    Serial.println(serial_message_second_pin_used);

    Serial.print(F("message_value:"));
    Serial.println(serial_message_value);


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
  char data_from_serial [25];
  char filtered_onos_message[21];
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


    if (counter<2){
      counter=counter+1;
      continue;     
    }


    if  ((counter>serial_msg_lenght-1)||((data_from_serial[counter-1]=='#')&&(data_from_serial[counter]==']')  ) ){//   

     // onos_s07v180s0001_#]

/*
     Serial.println("im here-------------------------------");
     Serial.println(data_from_serial[counter-serial_msg_lenght-3]);
     Serial.println(data_from_serial[counter-serial_msg_lenght-2]);
     Serial.println(data_from_serial[counter-serial_msg_lenght-1]);
     Serial.println(data_from_serial[counter-serial_msg_lenght]);
     Serial.println(data_from_serial[counter-serial_msg_lenght+1]);
     Serial.println(data_from_serial[counter-serial_msg_lenght+2]);
     Serial.println("ddd here-------------------------------");   

*/

      if ((data_from_serial[counter-serial_msg_lenght]=='o')&&(data_from_serial[counter-serial_msg_lenght+1]=='n')&&(data_from_serial[counter-serial_msg_lenght+2]=='o')&&(data_from_serial[counter-serial_msg_lenght+3]=='s')&&(data_from_serial[counter-serial_msg_lenght+4]=='_')){

#if defined(DEVMODE)
       Serial.println(F("onos cmd received0:"));
#endif


        for (uint8_t pointer = 0; pointer <= serial_msg_lenght; pointer++) {
          filtered_onos_message[pointer]=data_from_serial[counter-serial_msg_lenght+pointer];

#if defined(DEVMODE)
          Serial.println(filtered_onos_message[pointer]);

#endif
    
        }
       
        decodeOnosCmd(filtered_onos_message);

        if(((serial_message_answer[0]=='o')&&(serial_message_answer[1]=='k'))||(strcmp(serial_message_answer,"remote_#]")==0)){
          char onos_cmd_type= serial_message_type_of_onos_cmd;   
          uint8_t onos_first_pin_used=serial_message_first_pin_used;
          uint8_t onos_second_pin_used=serial_message_second_pin_used;
          uint8_t onos_status_to_set=serial_message_value;


/*
         Serial.println("sn");
         Serial.println(serial_message_sn);
         Serial.println("__sn");
*/

          if (strcmp(serial_message_sn,serial_number)==0) {//onos command for this arduino node
          //  Serial.print("ok_local");
            counter=0;
          } 
          else{ //onos command to send to a remote node

#if defined(DEVMODE)
            Serial.print("wrong_sn");
#endif
            strcpy(serial_message_answer,"ersn1_#]");
            counter=0;
          }



  
        }
        else{// error decoding the serial message
  
          break;
        }



      }
      else{//no onos_ cmd found

        strcpy(serial_message_answer,"nocmd1_#]");

      }




     counter=0;
     continue;
  }
 
   
  counter=counter+1;




     
    }//end while  client_query.available()


    if (enable_print==1){ //write if there is a not recognise message  shorter...

      client_query.println(serial_message_answer);
      client_query.flush();    
      client_query.stop();
      enable_print=0;

#if defined(DEVMODE)
      Serial.print(F("answer:"));
      Serial.println(serial_message_answer);
#endif


      break;


    }




  }


}





//end of server part







//client part




void usePinSetup(uint8_t number,uint8_t d_conf,uint8_t an_conf,uint8_t used,char mode,boolean isSetup){
    //number contain the register pins number
    //data contain the config setup for the pin in that register
    //used contain the information to tell arduino if each pin of that register is used or not
    //mode tell arduino that if isSetup is 1 then it has to set the pins in the register as specify by the mode value
    uint8_t i=0;

    while (i <8){ // from 0 to 7   , all the byte bits
      uint8_t pin_number=(number*8)+i;  //get the current pin number

      #if defined(DEVMODE2)
      Serial.print(F("pinN:"));
      Serial.print(pin_number);
      #endif
      if (bitRead(used,i)==1 ){// the pin is used
        
        if (bitRead(d_conf, i)==1 ){// the pin is not used as digital input but in other mode
          #if defined(DEVMODE2)
          Serial.print(F("as: "));
          #endif 
/*

          if ((mode=='s')&&(isSetup==1)){ // if the mode is servo and it is setup time
            Serial.println(F("s"));   //servo output
          }

          if (mode=='b'){
            Serial.println(F("ao"));
          }

*/
          if (mode=='d'){
            #if defined(DEVMODE2)
            Serial.println(F("do"));
            #endif
            pinMode(pin_number, OUTPUT); 
           
          }

        }
        else{// the bit is = 0 so the pin is used as digital input or analog input

          uint16_t tmp_analog_diff=0; 
/*

          Serial.print(F("i:          "));
          Serial.println(i);
          Serial.print(F("an conf:          "));
          Serial.println(an_conf);
          Serial.print(F("an conunt!!!:          "));
          Serial.println(analog_count);
*/
            delay(2);                    // wait for adc converter
            if ( ( (analog_count<16)&&(isSetup==0))&&bitRead(an_conf,i)==1)    { // &&(bitRead(an_conf,i)==1))  if is not the setup time and the pin is analog
              #if defined(DEVMODE2)
              Serial.print(F("as: "));
              Serial.println(F("ai"));  //analog input
              #endif
              uint16_t tmp_analog_value=analogRead(pin_number);  
              

              if (tmp_analog_value>analog_values[analog_count]){
                tmp_analog_diff=tmp_analog_value-analog_values[analog_count];
              }
              else{
                tmp_analog_diff=analog_values[analog_count]-tmp_analog_value;
              }

              #if defined(DEVMODE2)
              Serial.println(analog_values[analog_count]);
              Serial.println(tmp_analog_value);   
              #endif
              if ((tmp_analog_diff>analog_tolerance)||(pin_status_to_update>0)){//tmp_analog_diff>analog_tolerancethe analog value differs from the prev
                #if defined(DEVMODE2)
                Serial.println(F("analog_values[analog_count]="));
                Serial.println(analog_values[analog_count]);
                Serial.println(F("tmp_analog_value"));
                Serial.println(tmp_analog_value);
                Serial.println(F("difference="));
                Serial.println(analog_values[analog_count]-tmp_analog_value);
                #endif

                analog_values[analog_count]=tmp_analog_value;
                #if defined(DEVMODE2)              
                Serial.println(F("ai=differentttttttttttttttttttttttt                     "));
                #endif
                if (pin_status_to_update<1){
                  pin_status_to_update=3;   
                }
                //delay(800);  
              }

/* 
              else{         
                //analog_values[analog_count]=tmp_analog_value;      
                delay(2);                    // wait for adc converter
              }
           

              uint8_t tmp_byte0=lowByte(tmp_analog_value);//now contain the half lower 8 bytes from the 16 byte data
              uint8_t tmp_byte1=highByte(tmp_analog_value);// now contain the half upper 8 bytes from the 16    
              Serial.print(F("ai=                     "));
              Serial.println(analog_values[analog_count]);  
              Serial.print(F("acount=                     "));
              Serial.println(analog_count);  
              Serial.print(F("fbyte=                     "));
              Serial.println(tmp_byte0);  
              Serial.print(F("sbyte=                     "));
              Serial.println(tmp_byte1);  


              delay(500);    
            */    

              analog_count=analog_count+1;  // analog_count will travel from 0 to 15

            }
           #if defined(DEVMODE2)
            else{//setup time
              Serial.print(F("as: ")); 
              Serial.println(F("not ai"));
              
           }
           #endif

          


          if ((true)&&(bitRead(an_conf,i)==0 )){// &&(bitRead(an_conf,i)==0 )the pin is used as digital input and not as analog input
            #if defined(DEVMODE2)
            Serial.print(F("as: "));
            Serial.println(F("di"));
            #endif

            if(isSetup==1){//is pin setup time
              pinMode(pin_number, INPUT); 

            }            
            else{ //is not pin setup time  //read the pin and store the value in the array
              uint8_t tmp_digital_status=digitalRead(pin_number);
              uint8_t previous_status=bitRead(digital_status[number],i);

              if (tmp_digital_status!=previous_status){   
                #if defined(DEVMODE2)
                Serial.print(pin_number);  
                Serial.print(F(" change to: "));       
                Serial.println(tmp_digital_status);           
                #endif
                pin_status_to_update=3;     // flag to send the digital data
                bitWrite(digital_status[number], i, tmp_digital_status);//update the bit value with the current one
              }

            }  


         
          }
        }      


         // i=i+1;
         // continue;
        #if defined(DEVMODE)
        Serial.println();   
        #endif 
        i=i+1;

      }
      else{
        #if defined(DEVMODE2)
        Serial.print(F("as: "));
        Serial.println(F("NOTused"));
        #endif
        i=i+1;
      }


    }     
    




}






void pinsSetup(){


  //node_code_name="ProminiA0001";
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
      strcat(ask_setup,node_code_name);
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

        if (prev_msg=='s'){
          if (msg=='='){  //start of the setup  msg
            i=0; //the cont start now
            read_msg=1;
            continue;
          }

        }


        if (msg=='s'){
          prev_msg=msg;
        }

        if (read_msg==1){
      #if defined(DEVMODE)
          Serial.print(F("i="));
          Serial.println(i);
      #endif

          if (i<9){   //read used pins
            used_pins[i]=msg;
          }
          
          if ((i>8)&(i<18)){  //the current msg contain a digital setup 
      #if defined(DEVMODE)
            Serial.println(F("d conf"));
            Serial.println(msg);
      #endif
            digital_setup[i-9]=msg;
            usePinSetup(i-9,msg,0,used_pins[i-9],'d',1);

            
          }
          
          if ((i>17)&(i<27)){  //the current msg contain a analog input setup 
      #if defined(DEVMODE)
            Serial.println(F("a in setup"));
            Serial.println(msg);
      #endif
            analog_in_setup[i-18]=msg;
            delay(900); 
            //usePinSetup(i-18,0,msg,used_pins[i-18],'a',1); 


          }
          if ((i>26)&(i<36)){  //the current msg contain a analog out setup 
      #if defined(DEVMODE)
            Serial.println(F("a out"));
            Serial.println(msg);
      #endif
            usePinSetup(i-27,msg,0,used_pins[i-27],'b',1);


          }
          if ((i>35)&(i<45)){  //the current msg contain a servo setup 
      #if defined(DEVMODE)
            Serial.println(F("servo"));
            Serial.println(msg);
      #endif
            usePinSetup(i-36,msg,0,used_pins[i-36],'s',1);


          }

          if (i>44){  
            setup_done=1;
          }


          i=i+1;

        }

        
        
        
      }

      client.stop();
      



      
/*
#  here the protocol:
#  start with 's='
#  then  add    9 bytes that rappresent the pin used (1 for pin used 0 for not used)   
#  after that   9 bytes that rappresent the digital pin setup from pin0 to pin 127 , where 1 is output ,0 is input
#  after that   9 bytes that tell arduino wich pin to set as analog input
#  after that   9 bytes that tell arduino wich pin to set as pwm output
#  after that   9 bytes that tell arduino wich pin to set as servo output
#  then  1   byte for future use , for now '#'
#  example:"s=000000000000000000000000000000000000000000000#"  the 0 are not 0 but the value corrisponding to ascii '0'
    # total 48 byte 
*/

     



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

  //banana ask the user to set the node_type and serial number and save them in the eeprom
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


  if ((first_time==1)&&(only_digital_out==1)){  // uses pins as received from onosCenter
    first_time=0;
    analog_count=0;
    uint8_t k=0;//k is used as register counter..in the arduino mega there are 72 pins , so the register will be 8
    while (k<9){  //for each pin reads the analog and the digital input pin
      usePinSetup(k,digital_setup[k],analog_in_setup[k],used_pins[k],'d',0);//its important to make the digital read before the analog read
      k=k+1;
    } 

  }//END if (first_time==1){




//reset the relay set reset pins (the relay will stay in the state they was ,closed or opened)

/*
if (pins_to_reset1!=99){
  digitalWrite(pins_to_reset1,0); 
  pins_to_reset1=99;
}
if (pins_to_reset2!=99){
  digitalWrite(pins_to_reset2,0); 
  pins_to_reset2=99;
}
*/



//digital part ,not used in socket nodes type unocomment
// if ((pin_status_to_update>0)&&(!client_request)){//send the data n times
  if (0){
    #if defined(DEVMODE3)
    Serial.print(F("pin_status_to_update= "));
    Serial.println("deleted.....not_used");

    #endif    
 
      
  }

  else{ //just to keep alive...

    unsigned long t=millis();
    if ( (t-sync_time)>60000){   //each 60 sec time contact the onosCenter and update the current ip address
      sync_time=t;
      if (client.connect(IPAddress(192,168,101,1),onos_center_port)){

//        client.println("GET /onos_cmd?cmd=sync&node_sn="+node_code_name+"&node_fw="+node_fw+"&node_ip="+Ethernet.localIP()+"__");
//        client.println(F( " HTTP/1.1"));
//	    client.print(F( "Host: " ));
//        client.println(F("192.168.101.1"));
//  	    client.println(F( "Connection: close" ));
        //n_sync?sn=ProminiA0001&fw=4.85_#]
        char ask_sync[33]="n_sync?sn=";

        strcat(ask_sync,node_code_name);
        strcat(ask_sync,"&fw=");
        strcat(ask_sync,node_fw);
        strcat(ask_sync,"_#]");

        client.print(ask_sync);
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
