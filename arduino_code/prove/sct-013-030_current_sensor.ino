/*
  Analog input, analog output, serial output
 
 Reads an analog input pin, maps the result to a range from 0 to 255
 and uses the result to set the pulsewidth modulation (PWM) of an output pin.
 Also prints the results to the serial monitor.
 
 The circuit:
 * potentiometer connected to analog pin 0.
   Center pin of the potentiometer goes to the analog pin.
   side pins of the potentiometer go to +5V and ground
 * LED connected from digital pin 9 to ground
 
 created 29 Dec. 2008
 modified 9 Apr 2012
 by Tom Igoe
 
 This example code is in the public domain.
 
 */

// These constants won't change.  They're used to give names
// to the pins used:

#define NUMBER_OF_READING 500
int readings_array[NUMBER_OF_READING];
int min_value = 1000;
int max_value = 0;
int analog_value = 0;

const int analogInPin = A1;  // Analog input pin that the potentiometer is attached to
const int analogOutPin = 9; // Analog output pin that the LED is attached to

int sensorValue = 0;        // value read from the pot
int outputValue = 0;        // value output to the PWM (analog out)

void setup() {
  // initialize serial communications at 9600 bps:
  Serial.begin(9600); 
}

void loop() {
    
  min_value = 1000;
  max_value = 0;
  // read the analog in value
  for (uint8_t i=0;i<NUMBER_OF_READING;i=i+1){
    analog_value = analogRead(analogInPin);
    //readings_array[i] = analog_value;
    if (analog_value < min_value){ //to find the 0 value..so when the voltage cross 0v
        min_value = analog_value;
    }
    if (analog_value > max_value){ //to find the max value..so when the voltage cross 220v
        max_value = analog_value;
    }    
    
    
  }


  // print the results to the serial monitor:
  
  Serial.print("analog = " );                       
  Serial.print(analogRead(analogInPin));       
  
  Serial.print("min_value = " );                       
  Serial.print(min_value);      
  Serial.print("\t max_value = ");      
  Serial.println(max_value);   

  // wait 2 milliseconds before the next loop
  // for the analog-to-digital converter to settle
  // after the last reading:
  delay(2);                     
}
