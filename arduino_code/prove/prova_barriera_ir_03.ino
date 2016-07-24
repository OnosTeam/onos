
//prova usando 2 sensori ir GP2Y0A02YK0F sharp da 20 a 150 cm ...


//there are 4 states : 00,01,11,10




String currentSystemState="00";

String oldSystemState="XX";




int sensor1Avarage=0;
int sensor2Avarage=0;

int sensor1Derivate=0;
int sensor2Derivate=0;
int count=0;

 
int sensore1 = 1;    //sensore esterno alla camera
int sensore2 = 0;    //sensore interno alla camera
int threshold=60;
int negative_threshold=-60;
int wait_for_other_ir_to_be_oscured=100;
int delay_between_readings=2; //micro sec
int delay_between_old_and_new_read=2;



boolean t1=0;
boolean t2=0;
int i=0;






int sensor1Value = 0;        // value read from the pot     16.02
int sensor2Value = 0;        // value read from the pot     16.02
int sensor1ValueOld = 0; 
int sensor2ValueOld = 0;
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
  int readings[13];
  int currentRead=0;
  int bound=150;  
  int previous_values=0;
  int k=0;
  analogRead(analog_pin); 
  while (j<12){
    delayMicroseconds(delay_between_readings); 
    currentRead=analogRead(analog_pin);
    if (currentRead< 20){
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
        Serial.println("                 value scartedddddddd:");           
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




void getDerivate(){


  count=0;
  int sensor1Array[37];
  int sensor2Array[37];
  int r1=0;
  int r2=0;
  while (count<35){
    r1=average_read(sensore1);
    r2=average_read(sensore2);
    sensor1Array[count]=r1;
    sensor2Array[count]=r2;

    sensor1Avarage=sensor1Avarage+r1;       
    sensor2Avarage=sensor2Avarage+r2; 
//    delay(delay_between_old_and_new_read);
    count=count+1;

  }

  sensor1Avarage=sensor1Avarage/count;
  sensor1Value=average_read(sensore1);

  sensor2Avarage=sensor2Avarage/count;
  sensor2Value=average_read(sensore2);


  sensor1Derivate=0;
  sensor2Derivate=0;
  count=0;
  while (count<14){
    sensor1Derivate=sensor1Derivate+sensor1Array[count+1]-sensor1Array[count];
    sensor2Derivate=sensor2Derivate+sensor2Array[count+1]-sensor2Array[count];

    //sensor1Avarage=sensor1Avarage+average_read(sensore1);       
    //sensor2Avarage=sensor2Avarage+average_read(sensore2); 
//    delay(delay_between_old_and_new_read);
    count=count+1;

  }





}



void loop() {


restart:

  // read the analog in value:
  
  getDerivate();

  Serial.print( sensor1Derivate); 
  Serial.print( "     ");   
  Serial.print( sensor1Avarage); 
  Serial.print( "     ");   
  Serial.print(  sensor2Derivate);  
  Serial.print( "     ");  
  Serial.print(sensor2Avarage); 
  Serial.print( "     ");  
  Serial.println(currentSystemState);  

   

  if (currentSystemState=="00"){

    if ((sensor1Derivate >threshold)&&(sensor2Derivate <threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="01";
      goto restart;
    }

    else if ((sensor2Derivate >threshold)&&(sensor1Derivate <threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="10";
      goto restart;
    }



    else if ((sensor2Derivate >threshold)&&(sensor1Derivate >threshold)){
      currentSystemState="11";
      goto restart;
    }




  }



  if (currentSystemState=="01"){


    if ((sensor2Derivate >threshold)&&(sensor1Derivate >negative_threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="11";
      goto restart;
    }


   else if ((sensor2Derivate <threshold)&&(sensor1Derivate <negative_threshold)){
      if ((oldSystemState=="10")||(oldSystemState=="11")){

        if (persone_presenti>0) {
          persone_presenti=persone_presenti-1;            
          Serial.print("personeeeeeeeeeeeeeeeeeeeeeeeeeeee:");   
          Serial.println(persone_presenti);              
          delay(1300); 
        }
 
      }

      oldSystemState=currentSystemState;
      currentSystemState="00";
      goto restart;
    }

    else if ((sensor2Derivate >threshold)&&(sensor1Derivate <negative_threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="10";
      goto restart;
    }





  }



  if (currentSystemState=="10"){


    if ((sensor1Derivate >threshold)&&(sensor2Derivate >negative_threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="11";
      goto restart;
    }


    else if ((sensor1Derivate <threshold)&&(sensor2Derivate <negative_threshold)){
      if ((oldSystemState=="01")||(oldSystemState=="11")){

        persone_presenti=persone_presenti+1;  
          
        Serial.print("personeeeeeeeeeeeeeeeeeeeeeeeeeeee:");   
        Serial.println(persone_presenti);              
        delay(1300); 
        
      }

      oldSystemState=currentSystemState;
      currentSystemState="00";
      goto restart;
    }


    else if ((sensor1Derivate >threshold)&&(sensor2Derivate >negative_threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="01";
      goto restart;
    }



  }



  if (currentSystemState=="11"){


    if ((sensor1Derivate >negative_threshold)&&(sensor2Derivate <negative_threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="01";
      goto restart;
    }


    else if ((sensor1Derivate <negative_threshold)&&(sensor2Derivate <negative_threshold)){
      if (oldSystemState=="01"){
        persone_presenti=persone_presenti+1;            
        Serial.print("personeeeeeeeeeeeeeeeeeeeeeeeeeeee:");   
        Serial.println(persone_presenti);              
        delay(1300);         
      }

      if (oldSystemState=="10"){
        if (persone_presenti>0) {
          persone_presenti=persone_presenti-1;            
          Serial.print("personeeeeeeeeeeeeeeeeeeeeeeeeeeee:");   
          Serial.println(persone_presenti);              
          delay(1300); 
        }     
      }

      oldSystemState=currentSystemState;
      currentSystemState="00";
      goto restart;
    }


    else if ((sensor1Derivate >negative_threshold)&&(sensor2Derivate <negative_threshold)){
      oldSystemState=currentSystemState;
      currentSystemState="10";
      goto restart;
    }



  }


  
//     delay(50);
  
  /*
   Serial.print(  "sensor1ValueOld : "); 
   Serial.print(  sensor1ValueOld);   
  
   Serial.print(  "sensor2ValueOld : "); 
   Serial.print(  sensor2ValueOld);     
  
 */ 

 /*  Serial.println(  "sensor1Value : "); 
   Serial.print(  sensor1Value);   
  Serial.print( "     ");   
 //  Serial.println(  "sensor2Value : "); 
   Serial.println(  sensor2Value);   

 */
  // wait 10 milliseconds before the next loop
  // for the analog-to-digital converter to settle
  // after the last reading:
   
/*


  if (sensor2Value >(sensor2Avarage+threshold)  ){
         Serial.println("if sensor2Value");   
       sensor1ValueOld=sensor1Value;
       int k=0;

      while (k<wait_for_other_ir_to_be_oscured){
        k=k+1;
        sensor1Value= average_read(sensore1);   
        if (sensor1Value >(sensor1Avarage+threshold)  ){ 
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
  
   
  sensor1Value= analogRead(sensore1);   

    
  if (sensor1Value >(sensor1Avarage+threshold)  ){
    Serial.println("if sensor1Value1");  
    sensor2ValueOld=sensor2Value;
    int k=0;
    while (k<wait_for_other_ir_to_be_oscured){
      k=k+1;
    
      sensor2Value= average_read(sensore2);   

        
  
      if (sensor2Value >(sensor2Avarage+threshold)  ){
         
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
    
  
 */ 
  
  
  
  
}

