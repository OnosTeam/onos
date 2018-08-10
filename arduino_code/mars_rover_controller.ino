#include <PS2X_lib.h>  //for v1.6
#include <OnosMsg.h>
#include <avr/wdt.h>
//this sketch running on arduino connected to a psx controller and via serial port to arduino onos_rfm69_serial_interface 
// will controll via radio a mars rover.
// the mars rover will have 8 objects for the wheels movement 
// 4 digital objects to tell if each wheels motors should move forward or backward
// 4 analog objects to tell the pwm value each motor should use,(for speed controll, from 0 to 255)
// 4 analog object to tell the pivoting servos what angle they should move to (from 0 to 180 degrees)

// there will be a coded message to compress all this data in a single message: 

//  [S_famDAoAoAoAoSoSoSoSox_#]    
//  Where:
//  The fa is the 250 address...
//  The m stand for mars rover
//  The D is a binary where the last 4 bits are the digital object to tell if each wheels motors should move forward or backward 
//  Each Ao is  a hex of the 4 analog objects to tell the pwm value each motor should use,(for speed controll, from 0 to 255)
//  Each So is a hex of the 4 analog object to tell the pivoting servos what angle they should move to (from 0 to 180 degrees)


//#define DEBUG_MODE 1   //uncomment this to enable debug mode






/******************************************************************
 * set pins connected to PS2 controller:
 *   - 1e column: original 
 *   - 2e colmun: Stef?
 * replace pin numbers by the ones you use
 ******************************************************************/
#define PS2_DAT        8  //14    
#define PS2_CMD        11  //15
#define PS2_SEL        10  //16
#define PS2_CLK        12  //17

/******************************************************************
 * select modes of PS2 controller:
 *   - pressures = analog reading of push-butttons 
 *   - rumble    = motor rumbling
 * uncomment 1 of the lines for each mode selection
 ******************************************************************/
#define pressures   true
//#define pressures   false
//#define rumble      true
#define rumble      false

PS2X ps2x; // create PS2 Controller Class

//right now, the library does NOT support hot pluggable controllers, meaning 
//you must always either restart your Arduino after you connect the controller, 
//or call config_gamepad(pins) again after connecting the controller.

int error = 0;
byte type = 0;
byte vibrate = 0;

byte controller_buttons0=B11111111;
byte controller_buttons1=B11111111;  
byte old_controller_buttons0=B11111111;
byte old_controller_buttons1=B11111111;
byte an0=0;
byte an1=0;
byte an2=0;
byte an3=0;

byte an0_old=0;
byte an1_old=0;
byte an2_old=0;
byte an3_old=0;
int analog_threshold=10;

int rx_node_address=250;  //the mars rover address
char str_rx_node_address[3];

const uint8_t syncMessage_lenght = 33;

char syncMessage[syncMessage_lenght];



OnosMsg OnosMsgHandler=OnosMsg();  //create the OnosMsg object





void composeSerialMessage(byte buttons0, byte buttons1,byte analog0,byte analog1, byte analog2, byte analog3 ){
    memset(str_rx_node_address,0,sizeof(str_rx_node_address)); //to clear the array
    str_rx_node_address[0]='0';
    str_rx_node_address[1]='0';
    
    //tmp_char_rx_node_address = rx_node_address ;  //make the cast of int to char
    
    str_rx_node_address[0] = char(OnosMsgHandler.charDecToHex( rx_node_address / 16) );
    str_rx_node_address[1] = char(OnosMsgHandler.charDecToHex( rx_node_address % 16) );
    str_rx_node_address[2] = '\0';
    
    //Serial.println(F("local_address_dec:"));
    //Serial.println(rx_node_address);
    
    //Serial.println(F("local_address_hex:"));
    //Serial.println(str_rx_node_address[0]);
    //Serial.println(str_rx_node_address[1]);
    
    
    
    
    //strcpy(syncMessage, "");
    memset(syncMessage,0,sizeof(syncMessage)); //to clear the array
    strcpy(syncMessage, "[S_");
    strcat(syncMessage, str_rx_node_address);

    //uint8_t  tmp_len = strlen(syncMessage);
    //syncMessage[tmp_len]='m';   // m  for m type of command
    strcat(syncMessage, "m");  // end of message

    
    if ((buttons0 | B11101111) == B11101111){ //up arrow
        #if defined(DEBUG_MODE)
          Serial.println("up arrow detected");
        #endif 
        uint8_t  tmp_len = strlen(syncMessage);
        syncMessage[tmp_len]=B11111111;   // all motors forward
        syncMessage[tmp_len+1]='f';   // motor0 full speed
        syncMessage[tmp_len+2]='f';   // motor0 full speed
        
        syncMessage[tmp_len+3]='f';   // motor1 full speed
        syncMessage[tmp_len+4]='f';   // motor1 full speed
        
        syncMessage[tmp_len+5]='f';   // motor2 full speed
        syncMessage[tmp_len+6]='f';   // motor2 full speed
        
        syncMessage[tmp_len+7]='f';   // motor3 full speed
        syncMessage[tmp_len+8]='f';   // motor3 full speed
        
        syncMessage[tmp_len+8]='5';   // servo motor0 directed forward (90 degree)
        syncMessage[tmp_len+9]='a';   // servo motor0 directed forward (90 degree)
        
        syncMessage[tmp_len+10]='5';  // servo motor1 directed forward (90 degree)
        syncMessage[tmp_len+11]='a';  // servo motor1 directed forward (90 degree)
        
        syncMessage[tmp_len+12]='5';  // servo motor2 directed forward (90 degree)
        syncMessage[tmp_len+13]='a';  // servo motor2 directed forward (90 degree)
        
        syncMessage[tmp_len+14]='5';  // servo motor3 directed forward (90 degree)
        syncMessage[tmp_len+15]='a';  // servo motor3 directed forward (90 degree)
        
    }
    else if ((buttons0 | B01111111) == B01111111){ //down arrow
        #if defined(DEBUG_MODE)
          Serial.println("down arrow detected");
        #endif 
        uint8_t  tmp_len = strlen(syncMessage);
        syncMessage[tmp_len]=B11110000;   // all motors backward
        syncMessage[tmp_len+1]='f';   // motor0 full speed
        syncMessage[tmp_len+2]='f';   // motor0 full speed
        
        syncMessage[tmp_len+3]='f';   // motor1 full speed
        syncMessage[tmp_len+4]='f';   // motor1 full speed
        
        syncMessage[tmp_len+5]='f';   // motor2 full speed
        syncMessage[tmp_len+6]='f';   // motor2 full speed
        
        syncMessage[tmp_len+7]='f';   // motor3 full speed
        syncMessage[tmp_len+8]='f';   // motor3 full speed
        
        syncMessage[tmp_len+8]='5';   // servo motor0 directed forward (90 degree)
        syncMessage[tmp_len+9]='a';   // servo motor0 directed forward (90 degree)
        
        syncMessage[tmp_len+10]='5';  // servo motor1 directed forward (90 degree)
        syncMessage[tmp_len+11]='a';  // servo motor1 directed forward (90 degree)
        
        syncMessage[tmp_len+12]='5';  // servo motor2 directed forward (90 degree)
        syncMessage[tmp_len+13]='a';  // servo motor2 directed forward (90 degree)
        
        syncMessage[tmp_len+14]='5';  // servo motor3 directed forward (90 degree)
        syncMessage[tmp_len+15]='a';  // servo motor3 directed forward (90 degree)
        
    }
    
    else if ((buttons0 | B11011111) == B11011111){ //right arrow
        #if defined(DEBUG_MODE)
          Serial.println("right arrow detected");
        #endif 
        uint8_t  tmp_len = strlen(syncMessage);
        syncMessage[tmp_len]=B11111111;   // all motors forward
        syncMessage[tmp_len+1]='f';   // motor0 full speed
        syncMessage[tmp_len+2]='f';   // motor0 full speed
        
        syncMessage[tmp_len+3]='f';   // motor1 full speed
        syncMessage[tmp_len+4]='f';   // motor1 full speed
        
        syncMessage[tmp_len+5]='f';   // motor2 full speed
        syncMessage[tmp_len+6]='f';   // motor2 full speed
        
        syncMessage[tmp_len+7]='f';   // motor3 full speed
        syncMessage[tmp_len+8]='f';   // motor3 full speed
        
        syncMessage[tmp_len+8]='0';   // servo motor0 directed righ (180 degree)
        syncMessage[tmp_len+9]='0';   // servo motor0 directed righ (180 degree)
        
        syncMessage[tmp_len+10]='0';  // servo motor1 directed righ (180 degree)
        syncMessage[tmp_len+11]='0';  // servo motor1 directed righ (180 degree)
        
        syncMessage[tmp_len+12]='0';  // servo motor2 directed righ (180 degree)
        syncMessage[tmp_len+13]='0';  // servo motor2 directed righ (180 degree)
        
        syncMessage[tmp_len+14]='0';  // servo motor3 directed righ (180 degree)
        syncMessage[tmp_len+15]='0';  // servo motor3 directed righ (180 degree)
        
    }


    else if ((buttons0 | B10111111) == B10111111){ //left arrow
        #if defined(DEBUG_MODE)
          Serial.println("left arrow detected");
        #endif 
        uint8_t  tmp_len = strlen(syncMessage);
        syncMessage[tmp_len]=B11111111;   // all motors forward
        syncMessage[tmp_len+1]='f';   // motor0 full speed
        syncMessage[tmp_len+2]='f';   // motor0 full speed
        
        syncMessage[tmp_len+3]='f';   // motor1 full speed
        syncMessage[tmp_len+4]='f';   // motor1 full speed
        
        syncMessage[tmp_len+5]='f';   // motor2 full speed
        syncMessage[tmp_len+6]='f';   // motor2 full speed
        
        syncMessage[tmp_len+7]='f';   // motor3 full speed
        syncMessage[tmp_len+8]='f';   // motor3 full speed
        
        syncMessage[tmp_len+8]='b ';  // servo motor0 directed left (0 degree)
        syncMessage[tmp_len+9]='4';   // servo motor0 directed left (0 degree)
        
        syncMessage[tmp_len+10]='b';  // servo motor1 directed left (0 degree)
        syncMessage[tmp_len+11]='4';  // servo motor1 directed left (0 degree)
        
        syncMessage[tmp_len+12]='b';  // servo motor2 directed left (0 degree)
        syncMessage[tmp_len+13]='4';  // servo motor2 directed left (0 degree)
        
        syncMessage[tmp_len+14]='b';  // servo motor3 directed left (0 degree)
        syncMessage[tmp_len+15]='4';  // servo motor3 directed left (0 degree)
        
    }
    else if ((buttons0 | B00001111) == B11111111){ //no arrow pressed
        #if defined(DEBUG_MODE)
          Serial.println("no arrow pressed");
        #endif 
        uint8_t  tmp_len = strlen(syncMessage);
        syncMessage[tmp_len]=B11111111;   // all motors forward
        syncMessage[tmp_len+1]='0';   // motor0 stopped
        syncMessage[tmp_len+2]='0';   // motor0 stopped
        
        syncMessage[tmp_len+3]='0';   // motor1 stopped
        syncMessage[tmp_len+4]='0';   // motor1 stopped
        
        syncMessage[tmp_len+5]='0';   // motor2 stopped
        syncMessage[tmp_len+6]='0';   // motor2 stopped
        
        syncMessage[tmp_len+7]='0';   // motor3 stopped
        syncMessage[tmp_len+8]='0';   // motor3 stopped
        
        syncMessage[tmp_len+8]='0';   // servo motor0 directed righ (180 degree)
        syncMessage[tmp_len+9]='0';   // servo motor0 directed righ (180 degree)
        
        syncMessage[tmp_len+10]='0';  // servo motor1 directed righ (180 degree)
        syncMessage[tmp_len+11]='0';  // servo motor1 directed righ (180 degree)
        
        syncMessage[tmp_len+12]='0';  // servo motor2 directed righ (180 degree)
        syncMessage[tmp_len+13]='0';  // servo motor2 directed righ (180 degree)
        
        syncMessage[tmp_len+14]='0';  // servo motor3 directed righ (180 degree)
        syncMessage[tmp_len+15]='0';  // servo motor3 directed righ (180 degree)
                
    }
    uint8_t  tmp_len = strlen(syncMessage);
    syncMessage[tmp_len]=buttons0;      
    syncMessage[tmp_len+1]=buttons1;      
    syncMessage[tmp_len+2]='x';  // casual message value...to implement
    syncMessage[tmp_len+3] = '\0';   
    strcat(syncMessage, "_#]");  // end of message
}

void setup(){

      
  Serial.begin(115200);
  
  delay(300);  //added delay to give wireless ps2 module some time to startup, before configuring it
   
  //CHANGES for v1.6 HERE!!! **************PAY ATTENTION*************
  
  //setup pins and settings: GamePad(clock, command, attention, data, Pressures?, Rumble?) check for error
  error = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_SEL, PS2_DAT, pressures, rumble);
  
  if(error == 0){
    Serial.print("Found Controller, configured successful ");
    Serial.print("pressures = ");
	if (pressures)
	  Serial.println("true ");
	else
	  Serial.println("false");
	Serial.print("rumble = ");
	if (rumble)
	  Serial.println("true)");
	else
	  Serial.println("false");
/*
    Serial.println("Try out all the buttons, X will vibrate the controller, faster as you press harder;");
    Serial.println("holding L1 or R1 will print out the analog stick values.");
    Serial.println("Note: Go to www.billporter.info for updates and to report bugs.");
*/
  }  
  else if(error == 1)
    Serial.println("No controller found, check wiring, see readme.txt to enable debug. visit www.billporter.info for troubleshooting tips");
   
  else if(error == 2)
    Serial.println("Controller found but not accepting commands. see readme.txt to enable debug. Visit www.billporter.info for troubleshooting tips");

  else if(error == 3)
    Serial.println("Controller refusing to enter Pressures mode, may not support it. ");
  
//  Serial.print(ps2x.Analog(1), HEX);
  
  type = ps2x.readType(); 
  switch(type) {
    case 0:
      Serial.print("Unknown Controller type found ");
      break;
    case 1:
      Serial.print("DualShock Controller found ");
      break;
    case 2:
      Serial.print("GuitarHero Controller found ");
      break;
	case 3:
      Serial.print("Wireless Sony DualShock Controller found ");
      break;
   }
}

void loop() {
  /* You must Read Gamepad to get new values and set vibration values
     ps2x.read_gamepad(small motor on/off, larger motor strenght from 0-255)
     if you don't enable the rumble, use ps2x.read_gamepad(); with no values
     You should call this at least once a second
   */  
   
   
    if(error == 1) //skip loop if no controller found
        return; 
  
    ps2x.read_gamepad(false, vibrate); //read controller and set large motor to spin at 'vibrate' speed
    

    vibrate = ps2x.Analog(PSAB_CROSS);  //this will set the large motor vibrate speed based on how hard you press the blue (X) button
    if (ps2x.NewButtonState()) {        //will be TRUE if any button changes state (on to off, or off to on)

      controller_buttons0 = B11111111; //beginning status  
      if(ps2x.Button(PSB_PAD_UP)) {      //will be TRUE as long as button is pressed
      #if defined(DEBUG_MODE)
        Serial.print("Up held this hard: ");
        Serial.println(ps2x.Analog(PSAB_PAD_UP), DEC);

      #endif 
        controller_buttons0 = controller_buttons0 & B11101111;   
      }
      if(ps2x.Button(PSB_PAD_RIGHT)){
      #if defined(DEBUG_MODE)
        Serial.print("Right held this hard: ");
        Serial.println(ps2x.Analog(PSAB_PAD_RIGHT), DEC);

      #endif 
        controller_buttons0 = controller_buttons0 & B11011111;  
      }
      if(ps2x.Button(PSB_PAD_LEFT)){
      #if defined(DEBUG_MODE)
        Serial.print("LEFT held this hard: ");
        Serial.println(ps2x.Analog(PSAB_PAD_LEFT), DEC);

      #endif         
        controller_buttons0 = controller_buttons0 & B10111111;  
      }
      if(ps2x.Button(PSB_PAD_DOWN)){
      #if defined(DEBUG_MODE)
        Serial.print("DOWN held this hard: ");
        Serial.println(ps2x.Analog(PSAB_PAD_DOWN), DEC);

      #endif    
        controller_buttons0 = controller_buttons0 & B01111111;  
      }     
      if(ps2x.Button(PSB_CROSS)){    
      #if defined(DEBUG_MODE)
        Serial.println("Cross pressed"); 
      #endif    
     //   Serial.println("[S_fad121x_#]"); 
        controller_buttons0 = controller_buttons0 & B11111110;  //x pressed 
      }
      else{
      #if defined(DEBUG_MODE)
        Serial.println("Cross released"); 
      #endif                  
     //   Serial.println("[S_fad120x_#]"); 

      }
      if(ps2x.Button(PSB_SQUARE)){    
      #if defined(DEBUG_MODE)
        Serial.println("Square pressed");  
      #endif                             
     //   Serial.println("[S_faD131x_#]"); 
        controller_buttons0 = controller_buttons0 & B11111101;  //square pressed 
      }
      else{
      #if defined(DEBUG_MODE)
        Serial.println("Square released");  
      #endif                             
       // Serial.println("[S_faD130x_#]"); 
                
      }
      
      
      if(ps2x.Button(PSB_CIRCLE)){   
      #if defined(DEBUG_MODE)
        Serial.println("Circle pressed"); 
      #endif         
        controller_buttons0 = controller_buttons0 & B11111011;  //circle pressed 
      }
      if(ps2x.Button(PSB_TRIANGLE)){   
      #if defined(DEBUG_MODE)
        Serial.println("Triangle pressed");  
      #endif                              
        controller_buttons0 = controller_buttons0 & B11110111;  //triangle pressed 
      }
      if(ps2x.Button(PSB_L1)){   
      #if defined(DEBUG_MODE)
        Serial.println("L1 pressed"); 
      #endif                            
        controller_buttons1 = controller_buttons1 & B11111110;  
      }
      if(ps2x.Button(PSB_R1)){  
      #if defined(DEBUG_MODE)
        Serial.println("R1 pressed"); 
      #endif                         
        controller_buttons1 = controller_buttons1 & B11111101;   
      }
      if(ps2x.Button(PSB_L2)){   
      #if defined(DEBUG_MODE)
        Serial.println("L2 pressed"); 
      #endif                                
        controller_buttons1 = controller_buttons1 & B11111011;   
      }
      if(ps2x.Button(PSB_R2)){  
      #if defined(DEBUG_MODE)
        Serial.println("R2 pressed"); 
      #endif                             
        controller_buttons1 = controller_buttons1 & B11110111;   
      }
      if(ps2x.Button(PSB_L3)){  
      #if defined(DEBUG_MODE)
        Serial.println("L3 pressed"); 
      #endif                          
        controller_buttons1 = controller_buttons1 & B11101111;   
      }
      if(ps2x.Button(PSB_R3)){  
      #if defined(DEBUG_MODE)
        Serial.println("R3 pressed"); 
      #endif                         
        controller_buttons1 = controller_buttons1 & B11011111;   
      }
      if(ps2x.Button(PSB_START)){    
      #if defined(DEBUG_MODE)
        Serial.println("start pressed"); 
      #endif                           
        controller_buttons1 = controller_buttons1 & B10111111;   
      }
      if(ps2x.Button(PSB_SELECT)){   
      #if defined(DEBUG_MODE)
        Serial.println("select pressed"); 
      #endif                          
        controller_buttons1 = controller_buttons1 & B01111111;   
      } 
      
      composeSerialMessage(controller_buttons0, controller_buttons1, an0, an1, an2, an3);
      #if defined(DEBUG_MODE)
        Serial.println("composed msg:");
      #endif        
      Serial.println(syncMessage);
    
    }
    
    else{ // if the buttons are still in the same status...check the analog sticks
        
    /*
    if(ps2x.ButtonPressed(PSB_CIRCLE))               //will be TRUE if button was JUST pressed
      Serial.println("Circle just pressed");
    if(ps2x.NewButtonState(PSB_CROSS))               //will be TRUE if button was JUST pressed OR released
      Serial.println("X just changed");
    if(ps2x.ButtonReleased(PSB_SQUARE))              //will be TRUE if button was JUST released
      Serial.println("Square just released");    
    */
      
      an0=ps2x.Analog(PSS_LY);
      an1=ps2x.Analog(PSS_LX);
      
      an2=ps2x.Analog(PSS_RY);
      an3=ps2x.Analog(PSS_RX);

      if( ((an0<(an0_old-analog_threshold))|(an0>(an0_old+analog_threshold)))|((an1<(an1_old-analog_threshold))|(an1>(an1_old+analog_threshold)))|((an2<(an2_old-analog_threshold))|(an2>(an2_old+analog_threshold)))|((an3<(an3_old-analog_threshold))|(an3>(an3_old+analog_threshold))) ) {
        composeSerialMessage(controller_buttons0, controller_buttons1, an0, an1, an2, an3);
        #if defined(DEBUG_MODE)        
          Serial.println("composed msg:");
        #endif  
        Serial.println(syncMessage);
        an0_old = an0;
        an1_old = an1;
        an2_old = an2;
        an3_old = an3;

      }
  }    
      
  delay(50);  
}
