
//prova usando 2 sensori ir GP2Y0A02YK0F sharp da 20 a 150 cm ...




int sensorValue1 = 0; 
int sensorValue2 = 0; 
int sensore1 = 1;    //sensore esterno alla camera
int sensore2 = 0;    //sensore interno alla camera
int threshold=80;
int wait_for_other_ir_to_be_oscured=100;
int delay_between_readings=5; //micro sec
int delay_between_old_and_new_read=2;



boolean t1=0;
boolean t2=0;
int i=0;
int skip=0;





int sensorValue = 0;        // value read from the pot     16.02
int sensorValueOld = 0; 
int sensorValue2Old = 0;
int persone_presenti=0;
int persone_presenti_old=-1;


void setup() {
  // initialize serial communications at 9600 bps:
  pinMode(13, OUTPUT); 
  pinMode(2, OUTPUT);     
  Serial.begin(115200);  
  digitalWrite(13,1);
  delay(1000); 
  Serial.print(persone_presenti); 
  digitalWrite(13,0);

}



int average_read(int analog_pin){
 // delayMicroseconds(delay_between_readings); 
  int sensor_read=0;
  int j=0;
  int readings[21];
  int currentRead=0;
  int bound=100;  
  int previous_values=0;
  int k=0;
  analogRead(analog_pin); 
  while (j<20){
    delayMicroseconds(delay_between_readings); 
    currentRead=analogRead(analog_pin);
    if (currentRead< 25){
   //   Serial.println("                      value deletedddd");           
      continue;
    }
    readings[j]=currentRead;

    
    if (j>4){
      previous_values=(readings[j-1]+readings[j-2]+readings[j-3]+readings[j-4])/4; 
      if ( ( currentRead< (previous_values+bound  ) ) &&( currentRead> (previous_values-bound  ) )){  //to filter noise
        sensor_read=sensor_read+currentRead;
        j=j+1;
      }
      else{
        Serial.println("                      value scartedddddddd:");           
        k=k+1;

        if (k<1){
          continue;
        }

        sensor_read=sensor_read+currentRead;
        k=0;
        j=j+1;
       

      }

    }  
    else{
      j=j+1;
    }
    
    
  }
  sensor_read=sensor_read/j;

  return(sensor_read);



}

void loop() {


restart:

  // read the analog in value:
  sensorValueOld=sensorValue;
  sensorValue2Old=sensorValue2;
  
  sensorValueOld=average_read(sensore1);

  sensorValue2Old=average_read(sensore2);



  delay(delay_between_old_and_new_read);


  
  sensorValue=average_read(sensore1);

  sensorValue2=average_read(sensore2);


  
  
//     delay(50);
  
  /*
   Serial.print(  "sensorValueOld : "); 
   Serial.print(  sensorValueOld);   
  
   Serial.print(  "sensorValue2Old : "); 
   Serial.print(  sensorValue2Old);     
  
 */ 

 //  Serial.println(  "sensorValue : "); 
   Serial.print(  sensorValue);   
  Serial.print( "     ");   
 //  Serial.println(  "sensorValue2 : "); 
   Serial.println(  sensorValue2);   


  // wait 10 milliseconds before the next loop
  // for the analog-to-digital converter to settle
  // after the last reading:
   
   skip=0;


  if (sensorValue2 >(sensorValue2Old+threshold)  ){
         Serial.println("if sensorvalue2");   
       sensorValueOld=sensorValue;
       int k=0;

      while (k<wait_for_other_ir_to_be_oscured){
        k=k+1;
        sensorValue= average_read(sensore1);   
        if (sensorValue >(sensorValueOld+threshold)  ){ 
          k=600;
                       
         if (persone_presenti>0) {
           persone_presenti=persone_presenti-1;  
           
           Serial.print("personeeeeeeeeeeeeeeeeeeeeeeeeeeee:");   
           Serial.println(persone_presenti);              
           delay(300); 
         }
 
 
    
         if ((persone_presenti<1 )&&(persone_presenti_old>0) ){  //if now there is no person in the room
           digitalWrite(13,0);
           digitalWrite(2,1);   
           delay(10);
           digitalWrite(2,0);  
           
         }

  
 
         persone_presenti_old=persone_presenti;
  
         goto restart;
 

       }
       else{
         Serial.println("wait1"); 
       //  Serial.println(k);   
       } 
       
    }
  }   
  
   
  sensorValue= analogRead(sensore1);   

    
  if (sensorValue >(sensorValueOld+threshold)  ){
    Serial.println("if sensorvalue1");  
    sensorValue2Old=sensorValue2;
    int k=0;
    while (k<wait_for_other_ir_to_be_oscured){
      k=k+1;
    
      sensorValue2= average_read(sensore2);   

        
  
      if (sensorValue2 >(sensorValue2Old+threshold)  ){
         
        persone_presenti=persone_presenti+1;  
        Serial.print("personeeeeeeeeeeeeeeeeeeeeeeeeeeee:");   
        Serial.println(persone_presenti);   
        delay(300);    
        i=600;
  
        if ((persone_presenti>0 )&&(persone_presenti_old<1 )){
          digitalWrite(13,1);   
          digitalWrite(2,1);   
          delay(10);
          digitalWrite(2,0);  
        }
 
 
        persone_presenti_old=persone_presenti;

        goto restart;       


        }

        else{
          Serial.println("wait2"); 
         // Serial.println(k);    

    }
       

    
    }




   }
    
  
  
  
  
  
  
}

