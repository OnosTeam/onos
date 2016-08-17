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

#define DEVMODE 1
 

//pin setup print
#define DEVMODE2 1    

#define DEVMODE3 1          

#define onos_center_port 81
String setup_msg="";
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
String node_fw="5.13";
String node_code_name="Plug6way0001";
String serial_number=node_code_name.substring(8);  //BANANA TO READ FROM EEPROM
uint8_t mac[6] = {0x00,0x01,0x02,0x03,0x04,0x05};  //BANANA to change for each node
uint8_t analog_count=0;
//uint8_t pins_to_reset1=99;  //pin used with a set reset relay pin
//uint8_t pins_to_reset2=99;  //pin used with a set reset relay pin

EthernetServer server = EthernetServer(9000); //port number 9000





   //onos_d07v001s0001_#]

char serial_message_type_of_onos_cmd;
uint8_t serial_message_first_pin_used;
uint8_t serial_message_second_pin_used;
uint8_t serial_message_value;
String serial_message_answer="er01";
String serial_message_sn="";

uint8_t serial_msg_lenght=19;
uint8_t counter;





void decodeOnosCmd(char received_message[]){

 // Serial.println(F("decodeOnosCmd executed"));
  serial_message_answer="err0";
  if ((received_message[0]=='o')&&(received_message[1]=='n')&&(received_message[2]=='o')&&(received_message[3]=='s')&&(received_message[4]=='_'))
  { // the onos cmd was found           onos_d07v001s0001_#]
    serial_message_answer="cmdRx_#]";                  

    serial_message_sn="";

    serial_message_sn=serial_message_sn+received_message[13]+received_message[14]+received_message[15]+received_message[16];


    serial_message_type_of_onos_cmd=received_message[5];
         
    serial_message_first_pin_used=((received_message[6])-48)*10+(  (received_message[7])-48);

    serial_message_second_pin_used=-1;
                                    

    serial_message_value=(received_message[9]-'0')*100+(received_message[10]-'0')*10+(received_message[11]-'0')*1;

              
    if ((serial_message_value<0)||(serial_message_value>255)){ //status check
      serial_message_value=0;
      serial_message_answer="er0_status_#]";
      return;
    }
 

    if (serial_message_sn!=serial_number) {//onos command for a remote arduino node
      serial_message_answer="remote_#]"; 
      return; //return because i don't need to decode the message..i need to retrasmit it to the final node.
    }


    switch (serial_message_type_of_onos_cmd) {

      case 'd':{     //digital write       onos_d07v001s0001_#]
        serial_message_answer="ok_#]";
        break;
      }

      case 'a':{     //pwm write           onos_a07v100s0001_#]
        serial_message_answer="ok_#]";
        break;
      }
              
      case 's':{     //servo controll      onos_s07v180s0001_#]
        serial_message_answer="ok_#]";
        break;
      }  

      case 'r':{     //relay               onos_r1716v1s0004_#]
        serial_message_answer="ok_#]";
        serial_message_second_pin_used=((received_message[8])-48)*10+(  (received_message[9])-48)*1;
        serial_message_value=(received_message[11]-'0');
        break;
      } 

      default:{
        serial_message_answer="type_err";
        Serial.println(F("onos_cmd_type_error"));  
      }
  

   }//end of the switch case



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












 } // end of if message start with onos_   






}// end of decodeOnosCmd()









//server part





void server_handler(EthernetClient client_query ){

  char received_query [25];// query from the browser or from onos with urlib
  uint8_t i=0;
  uint8_t pin_number_used;
  char msg_lenght=18;
  String answer="nocmd1_#]";
  uint8_t quit=0;


  counter=0;
  char data_from_serial [25];
  char second_array[21];
  unsigned long timeout=millis()+200;


  while (client_query.connected() ) {

    //banana  make watchdog
    

    if(client_query.available() > 0){  

/*
      if (i>23){  // make the buffer long only 24 char
        //Serial.println(received_query);
        i=0;
      }
      
*/    

      if ( millis()>timeout){
        Serial.println(F("serial_timeout---------------------------------"));
        break;
      }



        
      received_query[i]=client_query.read(); 


      if (i<2){
        i=i+1;
        continue;     
      }


      //Serial.println(received_query[i]);
      //i=i+1;
        // if you've gotten to the end of the line (received the series of "_#]"
        // characters)  the  request has ended,
        // so you can send a reply
       
        if (i >2){


          if (  (received_query[i] == ']') && (received_query[i-1] == '#')&(received_query[i-2] == '_')) {
            Serial.println("received end of packet-------------------------------");
            // send a standard http response header
            quit=1;

            //continue; 
          }
        } 




      if  ((i>msg_lenght-1)||((received_query[i-1]=='#')&&(received_query[i]==']')  ) ){//   ){//   onos_a05v2550001_#]

/*
        Serial.println("im here-------------------------------");
        Serial.print(received_query[i-msg_lenght]);
        Serial.print(received_query[i-msg_lenght+1]);

*/
        if ((received_query[i-serial_msg_lenght]=='o')&&(received_query[i-serial_msg_lenght+1]=='n')&&(received_query[i-serial_msg_lenght+2]=='o')&&(received_query[i-serial_msg_lenght+3]=='s')&&(received_query[i-serial_msg_lenght+4]=='_'))
        { // the onos cmd was found
          answer="cmdRx_#]";

          


#if defined(DEVMODE)
          Serial.println(F("onos cmd received:"));
#endif
/*


          Serial.print(received_query[i-msg_lenght+5]);  //a
          Serial.print(received_query[i-msg_lenght+6]);  //0
          Serial.print(received_query[i-msg_lenght+7]);  //5
          Serial.print(received_query[i-msg_lenght+8]);  //v
          Serial.print(received_query[i-msg_lenght+9]);  //2
          Serial.print(received_query[i-msg_lenght+10]);  //5
          Serial.print(received_query[i-msg_lenght+11]);  //5

*/


          for (uint8_t pointer = 0; pointer < serial_msg_lenght; pointer++) {
            second_array[pointer]=received_query[i-serial_msg_lenght+pointer];
         //Serial.println("mmm");
         //Serial.println(second_array[pointer]);
          }    

          decodeOnosCmd(second_array);
         

#if defined(DEVMODE)
          Serial.println(F("sn:"));
          Serial.println(sn);
#endif

          if (serial_message_sn==serial_number){   
            char reg =serial_message_first_pin_used/8;
            char pos =serial_message_first_pin_used%8;


            if ( (  (bitRead(used_pins[reg],pos))==1 )&&(  (bitRead(digital_setup[reg],pos))==1 )){// the pin is used and not as digital input

#if defined(DEVMODE)
              Serial.print(F("pin used:"));
              Serial.print(pin_number_used);
#endif

              answer="err_#]";                                             

              uint8_t status_value=(received_query[i-msg_lenght+9]-'0')*100+(received_query[i-msg_lenght+10]-'0')*10+(received_query[i-msg_lenght+11]-'0')*1;

#if defined(DEVMODE)
              Serial.print(F("s_toSet:"));
              Serial.println(status_value);
#endif
               
              if ((status_value<0)||(status_value>255)){ //status check
                status_value=0;
                answer="er0_status_#]";
                quit=1;
                continue;
              }



              if (received_query[i-msg_lenght+5]=='d'){     //digital write      onos_d07v001s0001

                pinMode(pin_number_used, OUTPUT); 
                digitalWrite(pin_number_used, status_value); 
                answer="ok_#]";
                quit=1;
                continue;
              }





               if (received_query[i-msg_lenght+5]=='a'){     //pwm write     onos_a07v100s0001
                 analogWrite(pin_number_used, status_value); 
                 answer="ok_#]";
                 quit=1;
                 continue;
               }

              
               if (received_query[i-msg_lenght+5]=='s'){     //servo controll      onos_s07v180s0001
                 analogWrite(pin_number_used, status_value); //banana  to add servo
                 answer="ok_#]";
                 quit=1;
                 continue;
               }  


               if (received_query[i-msg_lenght+5]=='r'){     //relay      onos_r0607v1s0001  onos_r1716v1s0004_#]
                 uint8_t second_pin_number_used=((received_query[i-msg_lenght+8])-48)*10+(  (received_query[i-msg_lenght+9])-48)*1;
                 //ram?
#if defined(DEVMODE)
                 Serial.println(F("relay"));
#endif
                 reg =second_pin_number_used/8;
                 pos =second_pin_number_used%8;

                 if (true){//( (  (bitRead(used_pins[reg],pos))==1 )&&(  (bitRead(digital_setup[reg],pos))==1 )){//also the second pin is used and not as digital input

                   uint8_t status=(received_query[i-msg_lenght+11])-48;
#if defined(DEVMODE)
                   Serial.println(status);
#endif
                   answer="er1_status_#]";                    
                   if ((status==0)||(status==1)){ //status check
                     digitalWrite(pin_number_used, status); 
                     digitalWrite(second_pin_number_used,!status); 
                     //attention with this only one relay per message can be setted!!!
                     //pins_to_reset1=pin_number_used;
                     //pins_to_reset2=second_pin_number_used;
                     delay(150);
                     digitalWrite(pin_number_used,0); 
                     digitalWrite(second_pin_number_used,0);  
                     answer="ok_#]";
                     quit=1;
                     continue;
                   }
                 }       
               }


              }
              else{
#if defined(DEVMODE)    
                Serial.print(F("pin NOT  used:"));
#endif
                answer="err_pin_#]";   
                quit=1;
                continue;
                }


              }// end if sn
              else{
#if defined(DEVMODE)    
                Serial.print(F("err_sn:"));
#endif
                answer="err_sn"+serial_number+"_#]";  
                quit=1;
                continue; 
              }
         

            }//end if onos_

            /*Serial.print(F("pin selected:"));
            Serial.println(pin_number_used); 
            delay(2000); */ //banana to remove


          }


      



    i=i+1;

    }
    else{
     


      client_query.println(answer);
      client_query.flush();    
      client_query.stop();
      break;
    }





  }
}





//end of server part







//client part

void sendInputPinData(){
  //banana to add analog to msgToSend
  String a_status_string;
  String d_status_string;
 // a_status_string.reserve(33); //reserve the memory
 // d_status_string.reserve(10); //reserve the memory
  a_status_string="a";
  d_status_string="d";
  String msg_input_data="onos";
  //uint16_t analog_values[17];// store the  values from analog input   2 bytes for each data
  uint8_t i=0;


  while (i<9){
    d_status_string=d_status_string+digital_status[i];
    i=i+1;
  }
  #if defined(DEVMODE3)
  Serial.println(F("d lenght:"));  //banana to remove
  Serial.println(d_status_string.length());
  #endif
  i=0;
  while (i<16){
#if defined(DEVMODE)    
    Serial.print(F("arr ="));

    Serial.println(analog_values[i]);  
#endif
    uint8_t tmp_byte0=lowByte(analog_values[i]); //tmp_byte0 now contain the half lower 8 bytes from the 16 byte data
    uint8_t tmp_byte1=highByte(analog_values[i]);  //tmp_byte1 now contain the half upper 8 bytes from the 16
    a_status_string=a_status_string+char(tmp_byte1);
    a_status_string=a_status_string+char(tmp_byte0);
/*
    Serial.print(F("a pin ="));  
    Serial.print(i);  
    Serial.print(F(" af value ="));  
    Serial.print(tmp_byte0);  
    Serial.print(F("as value ="));  
    Serial.println(tmp_byte1);  
    delay(100);
*/
    i=i+1;

  }

 // Serial.println(F("analog lenght:")); 
 // Serial.println(a_status_string.length());
  msg_input_data=msg_input_data+node_code_name+node_fw+d_status_string+a_status_string+"_#]"; //msg_input_data contain 9/10 byte for digital status and 16 for analog

//example :onosProminiA00014.92d000000000a00000000000000000000000000000000_#]


  #if defined(DEVMODE3)
  Serial.println(F("d lenght2:")); 
  Serial.println(d_status_string.length());
  Serial.println(F("msg size:")); 
  Serial.println(msg_input_data.length());
  #endif


  if (client.connect(IPAddress(192,168,101,1),onos_center_port)){
    //client.println("POST /index.html HTTP/1.1"); 
//	client.println("Host: 192.168.101.1"); // SERVER ADDRESS HERE TOO
//	client.println("Content-Type: onos/form-data"); 
//	client.print("Content-Length: "); 
//	client.println(msg_input_data.length()); 
//	client.println(); 
	client.print(msg_input_data); 
    client.stop();	// DISCONNECT FROM THE SERVER
    //pin_status_to_update=0;  //message sent 
    pin_status_to_update=pin_status_to_update-1;
#if defined(DEVMODE)
    Serial.println(F(" connected to onos "));
#endif
	} 

	if (client.connected()) { 
		client.stop();	// DISCONNECT FROM THE SERVER
	}

#if defined(DEVMODE)
  Serial.println(F("i send data! "));
#endif

}


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
      client.print("pinsetup?sn="+node_code_name+"&fw="+node_fw+"_#]");
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
    Serial.println(pin_status_to_update);
    #endif
    sendInputPinData();
    #if defined(DEVMODE3)
    Serial.print(F("pin_status_to_update= "));
    Serial.println(pin_status_to_update);
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
        client.print("n_sync?sn="+node_code_name+"&fw="+node_fw+"_#]");
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
