int sensorValue0 = 0; 
int sensorValue1 = 0; 
int sensorValue2 = 0; 
int sensorValue3 = 0; 
int sensorValue4 = 0; 
int sensorValue5 = 0;
int sensorValue6 = 0; 
int sensorValue7 = 0; 
int sensorValue8 = 0; 
int sensorValue9 = 0; 
int sensore1 = 1;    //sensore esterno alla camera
int sensore2 = 0;    //sensore interno alla camera
int threshold=80;
int wait_for_other_ir_to_be_oscured=50;
int delay_between_readings=1;
int delay_between_old_and_new_read=10;




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

void loop() {


restart:

  // read the analog in value:
  sensorValueOld=sensorValue;
  sensorValue2Old=sensorValue2;
  
  //delay(20); 
  analogRead(sensore1); 
  sensorValueOld= analogRead(sensore1); 
  delay(delay_between_readings); 
  sensorValueOld=(sensorValueOld+analogRead(sensore1))/2; //fai la media
  
//  delay(20); 
  analogRead(sensore2); 
  sensorValue2Old= analogRead(sensore2);   
  delay(delay_between_readings); 
  sensorValue2Old=(sensorValue2Old+analogRead(sensore2))/2; //fai la media

  
  delay(delay_between_old_and_new_read);
  
  
  analogRead(sensore1);   
  sensorValue= analogRead(sensore1); 
  delay(delay_between_readings);   
  sensorValue=(sensorValue+analogRead(sensore1))/2; 
  
//  delay(20); 
  analogRead(sensore2); 
  sensorValue2= analogRead(sensore2);   
  delay(delay_between_readings);   
  sensorValue2=(sensorValue2+analogRead(sensore2))/2; 

  
  
  
  
  
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
       i=0;
      analogRead(sensore1); 
      while (i<wait_for_other_ir_to_be_oscured){
        i=i+1;
        sensorValue= analogRead(sensore1);   
        delay(delay_between_readings); 
        if (sensorValue >(sensorValueOld+threshold)  ){ 
          i=600;
                       
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
         Serial.println(i);   
       } 
       
    }
  }   
  
   
  sensorValue= analogRead(sensore1);   

    
  if (sensorValue >(sensorValueOld+threshold)  ){
    Serial.println("if sensorvalue1");  
    sensorValue2Old=sensorValue2;
    i=0;
    analogRead(sensore2);
    while (i<wait_for_other_ir_to_be_oscured){
      i=i+1;
    
      sensorValue2= analogRead(sensore2);   
      delay(delay_between_readings); 
        
  
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
          Serial.println(i);    

    }
       

    
    }




   }
    
  
  
  
  
  
  
}

