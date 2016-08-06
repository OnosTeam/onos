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
#include <Servo.h>
  Servo myservo;  // create servo object to control a servo , you can use only one servo in a general promini onos code
                  //banana to use http://playground.arduino.cc/Code/MegaServo  in order to use more servos

//uncomment this for dev mode

#define DEVMODE 1
 

//pin setup print
//#define DEVMODE2 1    

//#define DEVMODE3 1          

String setup_msg="";
EthernetClient client;
signed long next;
uint8_t digital_setup[10];
char digital_status[10];
boolean pin_status_to_update=0;
uint8_t used_pins[10];
uint8_t analog_in_setup[10];
uint8_t analog_tolerance=20;
uint8_t analog_values[17];// store the  values from analog input   1 bytes for each data

//banana read eeprom and retrieve the node_type and serial umber then compose the mac address 
char node_type='a';     //banana temp 'a' for arduino pro mini
char serial_char=1 ;   //banana to read from eprom
String node_fw="5.19";
String node_code_name="ProminiA0007";
String serial_number=node_code_name.substring(8);  //BANANA TO READ FROM EEPROM
uint8_t mac[6] = {0x00,0x02,0x02,0x03,0x04,0x06};
uint8_t analog_count=0;

EthernetServer server = EthernetServer(9000); //port number 9000


/*


void sendQueryUntilAck(String query,uint8_t ackByte0,uint8_t ackByte1,uint8_t numberOfTry){
//send a query continuosly until an ack msg is received
  boolean query_done=0;
  uint8_t i=0;
  while (query_done==0){

    if (i>numberOfTry){
      query_done=1;  //number of try reached
      Serial.println(F("query try number reached without correct answer"));
      continue;
    }
    i=i+1;
    Serial.println(F("send query"));
  
    if (client.connect(IPAddress(192,168,0,101),80)){
//192.168.0.101/onos_cmd?cmd=pinsetup&node_sn=ProminiA0001&node_fw=4.85&node_ip=192.168.0.7__

      client.println(query);
      client.println(F( " HTTP/1.1"));
      client.print(F( "Host: " ));
      client.println(F("192.168.0.101"));
      client.println(F( "Connection: close" ));
      client.println();
      client.println();
      boolean en=1;
      next = millis() + 1000;

      
      while(client.available()==0){

        Serial.println(F("waitAnswerFromServer"));
        if (next - millis() < 0){
          Serial.println(F("Cl disconnect"));
          client.flush();
          client.stop();
          en=0;
          break;
        }
        
      }
      if (en==0){
        continue;
      }
      Serial.println(F("Cl connect"));
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
        Serial.println(msg);


        if (prev_msg==ackByte0){  //if the ackByte0 is right check ackByte1
          if (msg==ackByte1){  // ackByte1 is correct ,answer received correctly from server
            i=0; //the cont start now
            query_done=1;
            continue;
          }

        }


      }

        
        
        
    

  } //if client.connect 

  else{
    Serial.println(F("Cl connect fail3"));
    client.flush();
    client.stop();
    delay(100); 
    continue;
  }


  if (query_done==0){  //(msg_array not containing the ack msg ..
    Serial.println(F("ServerAnswerNotOk"));
    client.flush();
    client.stop();
    delay(200); 
    continue;

  }




 }//while query_done 

}


*/


//server part



void server_sendHeader(EthernetClient client_r)
{
  client_r.println(F("HTTP/1.1 200 OK"));
  client_r.println(F("Content-Type: text/html"));
  client_r.println(F("Connection: close"));  // the connection will be closed after completion of the response
  client_r.println();
  client_r.println(F("<!DOCTYPE HTML>"));
  client_r.println(F("<html>"));
}


void server_handler(EthernetClient client_query ){

  char browser_query [24];// query from the browser or from onos with urlib
  uint8_t i=0;
  uint8_t pin_number_used;
  char msg_lenght=17;
  String answer="nocmd";
  uint8_t quit=0;
  boolean currentLineIsBlank = true;
  while (client_query.connected() ) {

    //banana  make watchdog
    

    if((client_query.available() > 0)&&(quit==0)){          
      browser_query[i]=client_query.read(); 
      //Serial.println(browser_query[i]);
      //i=i+1;
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (browser_query[i] == '\n' && currentLineIsBlank) {
          // send a standard http response header
          quit=1;
          continue; 
        }
        if (browser_query[i] == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        } 
        else if (browser_query[i]!= '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }



      if ((i>msg_lenght)){//   onos_a05v2550001

        if ((browser_query[i-msg_lenght]=='o')&&(browser_query[i-msg_lenght+1]=='n')&&(browser_query[i-msg_lenght+2]=='o')&&(browser_query[i-msg_lenght+3]=='s')&&(browser_query[i-msg_lenght+4]=='_'))
        { // the onos cmd was found
          answer="cmdRx";
          String sn="";
          sn=sn+browser_query[i-msg_lenght+13]+browser_query[i-msg_lenght+14]+browser_query[i-msg_lenght+15]+browser_query[i-msg_lenght+16];
          Serial.println(F("onos cmd received:"));/*
          Serial.print(browser_query[i-msg_lenght+5]);  //a
          Serial.print(browser_query[i-msg_lenght+6]);  //0
          Serial.print(browser_query[i-msg_lenght+7]);  //5
          Serial.print(browser_query[i-msg_lenght+8]);  //v
          Serial.print(browser_query[i-msg_lenght+9]);  //2
          Serial.print(browser_query[i-msg_lenght+10]);  //5
          Serial.print(browser_query[i-msg_lenght+11]);  //5

*/
         
          pin_number_used=((browser_query[i-msg_lenght+6])-48)*10+(  (browser_query[i-msg_lenght+7])-48);
          //if (true){//{(pin_number_used>0)&&(pin_number_used<80)){ //pin check

 
         //   }



          Serial.println(F("sn:"));
          Serial.println(sn);
          if (serial_number==sn){   
            char reg =pin_number_used/8;
            char pos =pin_number_used%8;


            if ( (  (bitRead(used_pins[reg],pos))==1 )&&(  (bitRead(digital_setup[reg],pos))==1 )){// the pin is used and not as digital input
              Serial.print(F("pin used:"));
              Serial.print(pin_number_used);


              answer="err";                                             

              uint8_t status_value=(browser_query[i-msg_lenght+9]-'0')*100+(browser_query[i-msg_lenght+10]-'0')*10+(browser_query[i-msg_lenght+11]-'0')*1;

              Serial.print(F("s_toSet:"));
              Serial.println(status_value);

               
              if ((status_value<0)||(status_value>255)){ //status check
                status_value=0;
                answer="err_status";
                quit=1;
                continue;
              }



              if (browser_query[i-msg_lenght+5]=='d'){     //digital write      http://192.168.0.6:9000/onos_d07v001s0001

                pinMode(pin_number_used, OUTPUT); 
                digitalWrite(pin_number_used, status_value); 
                answer="onos_ok";
                quit=1;
                continue;
              }





               if (browser_query[i-msg_lenght+5]=='a'){     //pwm write      http://192.168.0.6:9000/onos_a07v100s0001
                 analogWrite(pin_number_used, status_value); 
                 answer="onos_ok";
                 quit=1;
                 continue;
               }

              
               if (browser_query[i-msg_lenght+5]=='s'){     //servo controll      http://192.168.0.6:9000/onos_s07v180s0001
                 myservo.write(status_value); //banana  to add servo
                 answer="onos_ok";
                 quit=1;
                 continue;
               }  


               if (browser_query[i-msg_lenght+5]=='r'){     //sr relay write      http://192.168.0.6:9000/onos_r0607v1s0001
                 uint8_t second_pin_number_used=((browser_query[i-msg_lenght+8])-48)*10+(  (browser_query[i-msg_lenght+9])-48)*1;
                 //ram?
                 Serial.println(F("relay"));
                 reg =second_pin_number_used/8;
                 pos =second_pin_number_used%8;

                 if (true){//( (  (bitRead(used_pins[reg],pos))==1 )&&(  (bitRead(digital_setup[reg],pos))==1 )){//also the second pin is used and not as digital input

                   uint8_t status=(browser_query[i-msg_lenght+11])-48;
                   Serial.println(status);
                   answer="err_status";                    
                   if ((status==0)||(status==1)){ //status check
                     digitalWrite(pin_number_used, status); 
                     digitalWrite(second_pin_number_used,!status); 
                     delay(50);
                     digitalWrite(pin_number_used,0); 
                     digitalWrite(second_pin_number_used,0);  
                     answer="onos_ok";
                     quit=1;
                     continue;
                   }
                 }       
               }


              }
              else{
                Serial.print(F("pin NOT  used:"));
                answer="err_pin";   
                quit=1;
                continue;
                }


              }// end if sn
              else{
                Serial.print(F("err_sn:"));
                answer="err_sn"+serial_number;  
                quit=1;
                continue; 
              }
         

            }//end if onos_

            /*Serial.print(F("pin selected:"));
            Serial.println(pin_number_used); 
            delay(2000); */ //banana to remove


          }


      

      if (i>23){  // make the buffer long only 24 char
        //Serial.println(browser_query);
        i=0;
      }
      


    i=i+1;
    }
    else{
      server_sendHeader(client_query);
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

 // a_status_string.reserve(33); //reserve the memory
 // d_status_string.reserve(10); //reserve the memory
  byte msg_input_data_len=43;//to modify if the lenght changed
  uint8_t msg_input_data[msg_input_data_len];  //40 bytes + 1 void
  msg_input_data[0]=111;//o
  msg_input_data[1]=110;//n
  msg_input_data[2]=111;//o
  msg_input_data[3]=115;//s
  
  //uint16_t analog_values[17];// store the  values from analog input   2 bytes for each data




  msg_input_data[4]=node_code_name.charAt(0);
  msg_input_data[5]=node_code_name.charAt(1);
  msg_input_data[6]=node_code_name.charAt(2);
  msg_input_data[7]=node_code_name.charAt(3);
  msg_input_data[8]=node_code_name.charAt(4);
  msg_input_data[9]=node_code_name.charAt(5);
  msg_input_data[10]=node_code_name.charAt(6);
  msg_input_data[11]=node_code_name.charAt(7);
  msg_input_data[12]=node_code_name.charAt(8);
  msg_input_data[13]=node_code_name.charAt(9);
  msg_input_data[14]=node_code_name.charAt(10);
  msg_input_data[15]=node_code_name.charAt(11);

  msg_input_data[16]=node_fw.charAt(0);
  msg_input_data[17]=node_fw.charAt(1);
  msg_input_data[18]=node_fw.charAt(2);
  msg_input_data[19]=node_fw.charAt(3);
 

  msg_input_data[20]=100;//d
  msg_input_data[21]=digital_status[0];
  msg_input_data[22]=digital_status[1];
  msg_input_data[23]=digital_status[2];
  msg_input_data[24]=digital_status[3];
  msg_input_data[25]=digital_status[4];
  msg_input_data[26]=digital_status[5];
  msg_input_data[27]=digital_status[6];
  msg_input_data[28]=digital_status[7];
  msg_input_data[29]=digital_status[8];


  msg_input_data[30]=97;//a

  byte i=0;
  byte k=31;

  while (i<9){
    Serial.print(F("arr ="));
    Serial.println(analog_values[i]);  
    //uint8_t tmp_byte0=analog_values[i]; //tmp_byte0 now contain the half lower 8 bytes from the 16 byte data
    //uint8_t tmp_byte1=highByte(analog_values[i]);  //tmp_byte1 now contain the half upper 8 bytes from the 16
    //a_status_string=a_status_string+char(tmp_byte1);
    msg_input_data[k]=analog_values[i];
 
    i=i+1;
    k=k+1;

  }
  msg_input_data[k+1]='_';
  msg_input_data[k+2]='_';
 



//example :onosProminiA00014.92d000000000a0000000000000000__

  //sendQueryUntilAck("GET /onos_cmd?cmd=setNodeDReg&node_sn="+node_code_name+"&reg="+msg_input_data+"__",'o','k',20);
  #if defined(DEVMODE3)

 // Serial.println(F("msg size:")); 
 // Serial.println(k);

  #endif


  if (client.connect(IPAddress(192,168,101,1),81)){
    client.println("POST /index.html HTTP/1.1"); 
	client.println("Host: 192.168.101.1"); // SERVER ADDRESS HERE TOO
	client.println("Content-Type: onos/form-data"); 
	client.print("Content-Length: "); 
	client.println(msg_input_data_len); 
	client.println(); 
	 
    i=0;
    while (i<41) {
      client.write(msg_input_data[i]);
      i=i+1;
    }


    client.stop();	// DISCONNECT FROM THE SERVER
    //pin_status_to_update=0;  //message sent 
    pin_status_to_update=pin_status_to_update-1;
    //Serial.println(F(" connected to onos "));
	} 

	if (client.connected()) { 
		client.stop();	// DISCONNECT FROM THE SERVER
	}


  Serial.println(F("i send data! "));


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


          if ((mode=='s')&&(isSetup==1)){ // if the mode is servo and it is setup time
            #if defined(DEVMODE2)
             
            Serial.println(F("s"));   //servo output
            #endif
            pinMode(pin_number, OUTPUT); 
            myservo.attach(pin_number);
          }

          if (mode=='b'){
            #if defined(DEVMODE2)
            Serial.println(F("ao"));
            #endif
          }


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
              uint8_t tmp_analog_value=analogRead(pin_number)/4;  
              

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
                
                Serial.println(F("ai=differentttttttttttttttttttttttt                     "));
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
        
        Serial.println();    
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

/*
if (serial_char<10) {  // to add 0 in order to make 0000 like in onosPlug6way0001
serial_number="000"+serial_char;  
}
if ((serial_char>9)&(serial_char<100)){
serial_number="00"+serial_char;  
}

if (serial_char>99){
serial_number="0"+serial_char;  
}
if (node_type=='a'){
node_code_name="Plug6way"+serial_number; 
}

*/
  //node_code_name="ProminiA0001";
  boolean setup_done=0;


  while (setup_done==0){



    Serial.println(F("get setup"));
  
    if (client.connect(IPAddress(192,168,101,1),81)){
//192.168.0.101/onos_cmd?cmd=pinsetup&node_sn=ProminiA0001&node_fw=4.85&node_ip=192.168.0.7__

      client.println("GET /onos_cmd?cmd=pinsetup&node_sn="+node_code_name+"&node_fw="+node_fw+"&node_ip="+Ethernet.localIP()+"__");

      client.println(F( " HTTP/1.1"));
      client.print(F( "Host: " ));
      client.println(F("192.168.101.1"));
      client.println(F( "Connection: close" ));
      client.println();
      client.println();
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


  Serial.begin(115200);
  Serial.print(F("start "));
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
  Serial.print(F("localIP: "));
  Serial.println(Ethernet.localIP());
  Serial.print(F("subnetMask: "));
  Serial.println(Ethernet.subnetMask());
  Serial.print(F("gatewayIP: "));
  Serial.println(Ethernet.gatewayIP());
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



  Serial.println(F("loop"));

  EthernetClient client_request = server.available(); 
  unsigned long diff_time = millis ();

    if (client_request){
   // Serial.println(F("q r"));
      if (client_request.connected()){
        server_handler(client_request);

       }
    //Serial.println(F("q ans"));

  }








  analog_count=0;
  uint8_t k=0;//k is used as register counter..in the arduino mega there are 72 pins , so the register will be 8
  while (k<9){  //for each pin reads the analog and the digital input pin
//    Serial.print(F("k= "));
//    Serial.print(k);
//    Serial.print(F("an reg= "));
//    Serial.println(analog_in_setup[k]);
    usePinSetup(k,digital_setup[k],analog_in_setup[k],used_pins[k],'d',0);//its important to make the digital read before the analog read

    k=k+1;
  } 










  if ((pin_status_to_update>0)&&(!client_request)){//send the data n times
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



    if (client.connect(IPAddress(192,168,101,1),9194)){
      client.println(); 
      Serial.println(F(" connected falsed "));
      client.stop();	// DISCONNECT FROM THE SERVER
	} 

	if (client.connected()) { 
		client.stop();	// DISCONNECT FROM THE SERVER
	}




}






/*

 k=0;
  while (k<9){
    Serial.print(F("an setup= "));
    Serial.println(analog_in_setup[k]);
  k=k+1;
  } 
*/




}
