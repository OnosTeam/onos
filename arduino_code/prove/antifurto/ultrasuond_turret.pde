/*
  Ultrasonic Sensor turret

  This program reads 3 SRF04 ultrasonic distance sensor
  The SRF04 sensor's pins are connected as described below.
  Created 12 july 2016
  By Marco Rigoni
*/
#include <Servo.h>
#define echoPinSsx 8              // the SRF04's echo pin
#define initPinSsx 7              // the SRF04's init pin

#define echoPinSdx 4              // the SRF04's echo pin
#define initPinSdx 3              // the SRF04's init pin

#define echoPinSf 6           // the SRF04's echo pin
#define initPinSf 5             // the SRF04's init pin

#define servoPin 9



# define  n_element 5  //10   numero acquisizioni per ogni sensore

int  ledPin=A0;

unsigned long pulseTimeSdx = 0;  // variable for reading the pulse
unsigned long pulseTimeSsx = 0;  // variable for reading the pulse
unsigned long pulseTimeSf = 0;  // variable for reading the pulse

unsigned long distanceMax=5000;
unsigned long distanceVeryFar=4000;
unsigned long distanceFar=3000;
unsigned long distanceMidFar=2000;
unsigned long distanceNear=1000;
unsigned long distanceVeryNear=500;
unsigned long distanceClose=100;
unsigned long distanceTooClose=10;

unsigned long time=10;

int sdx[n_element];
int ssx[n_element];
int sf[n_element];
short i=0;
short counter=0;

int sf_med=0;
int sdx_med=0;
int ssx_med=0;


short first_time=0;

/*

to map the area if there is ostacle not removable...to implement...
unsigned long position_scan_Array_Sf[18]; //will contain a value of the distance measured every 10°
unsigned long position_scan_Array_Sdx[18];//will contain a value of the distance measured every 10°
unsigned long position_scan_Array_Ssx[18];//will contain a value of the distance measured every 10°
*/
  
Servo myservo;  // create servo object to control a servo
unsigned long tollerance=10;
//short previous_state=0;
short radar_state=0;
//short time_delay_
short time_led_on=10000; //ms the led will stay on
short servo_default_position=90;
short previous_servo_position=999;
short servo_position=servo_default_position;
short min_servo_position=22;
short max_servo_position=168;


unsigned long getSensorValue(int initPin,int echoPin) {
  unsigned long pulseTime=0;
  digitalWrite(initPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(initPin, LOW);
  // wait for the pulse to return. The pulse
  // goes from low to HIGH to low, so we specify
  // that we want a HIGH-going pulse below:
  pulseTime = pulseIn(echoPin, HIGH);
  return(pulseTime);
}

/*
state1   meaning
0-->     starting state micro just turned on 
1-->     rest state all sensor are not detecting anything
2-->     central sensor detects something in distanceVeryFar while the others do not detect anything
3-->     central sensor detects something in distanceMidFar while the others detect longer distance
4-->     central sensor detects something in distanceX while the others detect longer distance
         led turned on
5-->     after state 4 the obstacle is still there but hasn't moved for n seconds turn led off
6-->     the left sensor detect a shorter distance than the other 2 sensors
         moving the servo to the left until central sensor detects shorter distance than others 
         or the obstacle is removed or the servo can't turn left anymore--->turn on light
 
         

7-->     the right sensor detect a shorter distance than the other 2 sensors
         moving the servo to the right until central sensor detect shorter distance than others
         or the obstacle is removed or the servo can't turn right anymore--->turn on light



8-->     servo can't turn left anymore 
         but left sensor is detecting distance shorter than the other two sensors  --->turn on light



9-->     servo can't turn right anymore 
         but right sensor is detecting distance shorter than the other two sensors  --->turn on light




10-->    servo is all the way to the left or all the way to the right 
         and all the sensors are not detecting anything in the last 20 seconds.
         move the servo to center position 

11-->    all the sensor detect the similar distance  and closer than distanceTooClose

*/


short getState(unsigned long distanceSdx,unsigned long distanceSsx,unsigned long distanceSf){

  short current_state=99;
  if ((distanceSdx>distanceMax)&&(distanceSsx>distanceMax)&&(distanceSf>distanceMax)){

    if ((servo_position>max_servo_position)|(servo_position<min_servo_position)){

      current_state=10;
      return (current_state);
    }

  }



  if ((distanceSdx<distanceTooClose)&&(distanceSsx<distanceTooClose)&&(distanceSf<distanceTooClose)){
    current_state=11;
    return (current_state);
    

  }





  if ((distanceSdx>(distanceSf+tollerance))&(distanceSsx>(distanceSf+tollerance))&(distanceSf<distanceNear)){
    //time = millis();
    //turn led on
    if (current_state==4){
      if (millis()>time+time_led_on){
        current_state=5;
      }
    }
    else{
      current_state=4;
    }

    return (current_state);

  }


  if ((distanceSdx>(distanceSf+tollerance))&(distanceSsx>(distanceSf+tollerance))&(distanceSf<distanceMidFar)){
    current_state=3;
    return (current_state);

  }


  if ((distanceSdx>distanceMax)&(distanceSsx>distanceMax)&(distanceSf<distanceMax)){
    current_state=2;
    return (current_state);

  }


  if ((distanceSdx>distanceMax)&(distanceSsx>distanceMax)&(distanceSf>distanceMax)){
    current_state=1;
    return (current_state);//state 1 --> rest state

  }




  if ((distanceSsx<(distanceSf-tollerance))&(distanceSsx<(distanceSdx-tollerance))&(distanceSsx<distanceVeryFar)){
    current_state=6;
    if (servo_position>(max_servo_position-5)){
      current_state=8;
    }

    return (current_state);

  }

  if ((distanceSdx<(distanceSf-tollerance))&(distanceSdx<(distanceSsx-tollerance))&(distanceSdx<distanceVeryFar)){
    current_state=7;
    if (servo_position<(min_servo_position+5)){
      current_state=9;
    }
    return (current_state);

  }

}



void setup() {
 
  
  // make the init pin an output:
  pinMode(initPinSdx, OUTPUT);
  // make the echo pin an input:
  pinMode(echoPinSdx, INPUT);

  // make the init pin an output:
  pinMode(initPinSsx, OUTPUT);
  // make the echo pin an input:
  pinMode(echoPinSsx, INPUT);

  // make the init pin an output:
  pinMode(initPinSf, OUTPUT);
  // make the echo pin an input:
  pinMode(echoPinSf, INPUT);

  myservo.attach(servoPin);  
  myservo.write(servo_position);    
  
  
  pinMode(ledPin, OUTPUT);

  digitalWrite(1,ledPin);
  delayMicroseconds(10000);

  digitalWrite(1,ledPin);

  // initialize the serial port:
  Serial.begin(9600);
    Serial.println("begiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiin");

  
  
}

void loop() {

  delayMicroseconds(100);

  
  pulseTimeSdx=getSensorValue(initPinSdx,echoPinSdx)/49;
  delayMicroseconds(8);

  pulseTimeSsx=getSensorValue(initPinSsx,echoPinSsx)/49;
  delayMicroseconds(8);

  pulseTimeSf=getSensorValue(initPinSf,echoPinSf)/49;  
  delayMicroseconds(5);







  sdx_med=0;
  ssx_med=0;  
  sf_med=0; 
  if (first_time==0){
    first_time=1;
    for (i = 0; i < n_element; i = i + 1) {

      sdx[i]=pulseTimeSdx;
      ssx[i]=pulseTimeSsx;
      sf[i]=pulseTimeSf;
 
  

    }  


  }

  else{
    
    sdx[counter]=pulseTimeSdx;
    ssx[counter]=pulseTimeSsx;
    sf[counter]=pulseTimeSf;
    counter=counter+1;
    if (counter> n_element-1){
      counter=0;
    }

  }




  for (i = 0; i < n_element; i = i + 1) {

    sdx_med=sdx_med+sdx[i];    
    ssx_med=ssx_med+ssx[i];    
    sf_med=sf_med+sf[i];    
  

  }  




  sf_med=sf_med/n_element;
  sdx_med=sdx_med/n_element;
  ssx_med=ssx_med/n_element;
















  radar_state=getState(sdx_med,ssx_med,sf_med);



  switch (radar_state) {

    case 1:{

      if (millis()>time+time_led_on){  //turn off led if nothing detected for n time
        digitalWrite(0,ledPin);

      }

    }


    case 4:{
      digitalWrite(1,ledPin);
      time=millis();
      break;
    }
    case 5:{
      if (time>(millis()+time_led_on)){
        digitalWrite(0,ledPin);
      }
    }
      break;

    case 6:{
      servo_position=servo_position+5; //move servo to the right

      break;

    }


    case 7:{
      servo_position=servo_position-5;//move servo to the left

      break;

    }



    case 8:{
      digitalWrite(1,ledPin);
      time=millis();

      break;

    }



    case 9:{
      digitalWrite(1,ledPin);
      time=millis();

      break;

    }



    case 10:{
      servo_position=servo_default_position;
      if (millis()>time+time_led_on){
        digitalWrite(0,ledPin);
        radar_state=1;

      }

      break;

    }


    default:
      // if nothing else matches, do the default
      // default is optional
    break;
  }


  if (servo_position>max_servo_position){
    servo_position=max_servo_position;
  
  }


  if (servo_position<min_servo_position){
    servo_position=min_servo_position;
  
  }



  if ((previous_servo_position>servo_position+3)||(previous_servo_position<servo_position-3)){
    //myservo.attach(servoPin);  
    myservo.write(servo_position);  
    //myservo.detach();
  }  




  // print out that number
  
  
  Serial.print("radar_state:");
  Serial.print(radar_state, DEC);
  Serial.print(" ;");
  
  
  Serial.print(ssx_med, DEC);
  Serial.print(" ;");
  Serial.print(sf_med, DEC);
  Serial.print(" ;");
  Serial.print(sdx_med, DEC);
  
  Serial.print(" ;  ");

  Serial.print("servo:");
  Serial.println(servo_position,DEC);


  





}
