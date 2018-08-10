#include <SPI.h>
#include <Wire.h>
#include <Adafruit_SSD1306.h>


#define OLED_RESET 4 // not used / nicht genutzt bei diesem Display
Adafruit_SSD1306 display(OLED_RESET);

char inChar;

char automa_state = 0;
int  count = 0;
int count_limit = 20*8 + 5 ; // this will be the limit after that the display will return to the first pixel

String string;


void setup()   { 

        pinMode(13, OUTPUT);
        
        // initialize with the I2C addr 0x3C / mit I2C-Adresse 0x3c initialisieren
        display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
                 
        Serial.begin(115200);
        string.reserve(200);
        
        display.display();
        delay(2000);
        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(INVERSE); 
}

void loop()
{ 
        // the message to send are to be ended with this 3 char:_#]   
        
        
        if (Serial.available())  {
        
                display.clearDisplay();
                inChar = Serial.read();
                string+=inChar;               
                display.setCursor(0,0); 
                display.print(string);               
                display.display();   
                count = count + 1;
                
                if (count > count_limit){
                    count = 0;
                    string="";
                    //delay(1000);
                
                }
                
                // _#] 
                if(inChar == '_'){
                    if(automa_state == 0){
                        automa_state = 1;
                    }
                    else{
                        automa_state = 0;
                    }
                
                }
                else if(inChar == '#'){
                    if(automa_state == 1){
                        automa_state = 2;
                
                    }
                    else{
                        automa_state = 0;
                    }
                
                }
                else if(inChar == ']'){
                    if(automa_state == 2){
                        automa_state = 0;
                        Serial.println("End");                
                        delay(4000);
                        string="";
                
                    }
                }     
                
        
        }
        
        display.display();    

  
}
