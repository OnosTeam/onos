  char incomingByte=' ';
  char com_ok='n';
  int pin=0;
  byte pinCentinaia=0;  
  byte pinDecine=0; 
  byte pinUnita=0;
  byte centinaia=0;  
  byte decine=0; 
  byte unita=0;  
  int valore=0;
  
  int val_attuale=-1;
  int val_old=-1;
  
  int pindr=0;
  int  pindi=0;
  byte pinDecinedi=0; 
  byte pinUnitadi=0;  
  byte pinDecinedr=0; 
  byte pinUnitadr=0;  
  byte level=0;
  int analogvalue=0;
  int  tempvalue=0;

  int k=0;
   
  
  void setup() 
  { 
  
  //setto le impostazioni dei pin
    pinMode(12,OUTPUT);
    pinMode(8,OUTPUT);
    pinMode(13,OUTPUT);
    pinMode(7,OUTPUT);
    pinMode(10,OUTPUT);
    pinMode(9,OUTPUT);
    
    
    Serial.begin(115200);
    Serial.println("pronto!");   
  
    
    
    
  
  } 
  
  
  
  void ricevi(){   
        
        
      while (Serial.available() <1) 
        k++;//istruzione inutile
      //aspetta arrivo byte
      
      incomingByte = Serial.read();
      if (incomingByte=='d'){  //digital
        
        
        
        
     
        while (Serial.available() <1) 
          k++;//istruzione inutile
        incomingByte = Serial.read();
     
       
       
       
      if (incomingByte=='w')       //nota che per scriver ad esempio sul pin 4  devi scrivere dw041 o dw040   
        
      {
        while (Serial.available() <1) 
          k++;//istruzione inutile
          
        pinDecine = Serial.read()-48;  
        
        while (Serial.available() <1) 
          k++;//istruzione inutile        
          
        pinUnita = Serial.read()-48;            
        
        pin= pinDecine*10+pinUnita;
         
        while (Serial.available() <1) 
          k++;//istruzione inutile
          
        level = Serial.read()-48;    //contiene il valore con il quale settare il pin 
      
        pinMode(pin,OUTPUT); 
        
        delay(10);        
       
        digitalWrite(pin,level);
        
        
        Serial.print("dw"); 
        Serial.print(pinDecine);
        Serial.print(pinUnita);
        Serial.println(level);                 
          
          
          
       
       }
       
    else
    if (incomingByte=='r')   { //nota che per leggere ad esempio il pin 4  devi scrivere dr04 
    
        while (Serial.available() <1) 
          k++;//istruzione inutile    
  
        pinDecinedr = Serial.read()-48;  
        
        while (Serial.available() <1) 
          k++;//istruzione inutile        
          
        pinUnitadr = Serial.read()-48;            
        
        pindr= pinDecinedr*10+pinUnitadr;  
        
        pinMode(pindr,INPUT);
        
        delay(1); 
        Serial.print("dr"); 
        Serial.print(pinDecinedr);
        Serial.print(pinUnitadr);
        Serial.print(digitalRead(pindr));
        Serial.println();        
        //print for example r041  or r040   based on the state of pin4
         
     //   Serial.print("il pin e':");        
        
      //  Serial.print(pindr,DEC);
      /* 
        if (digitalRead(pindr)==0)
          Serial.print("il valore è 0 ");
          
        if (digitalRead(pindr)==1)
          Serial.print("il valore è 1");          
          
       */

}
    else if (incomingByte=='i')   { //nota che per applicare l'interrupt  ad esempio al pin 4  devi scrivere di04 
    
    
        while (Serial.available() <1) 
          k++;//istruzione inutile    
  
        pinDecinedi = Serial.read()-48;  
        
        while (Serial.available() <1) 
          k++;//istruzione inutile        
          
        pinUnitadi = Serial.read()-48;            
            
        pindi= pinDecinedi*10+pinUnitadi;  
        
        Serial.print('o'); 
        
        pinMode(pindi,INPUT);
        
        val_old=-1;
        
       while (Serial.available()<1 ){
          val_attuale=digitalRead(pindi);
          if ((val_attuale)!=val_old){
            
           while (com_ok!='o'){   // continua fino a che non riceve conferma avvenuta comun
             if (Serial.available()<1 )
               com_ok=Serial.read();
                
             Serial.print('i'); 
             Serial.print(digitalRead(pindi));
             val_old=val_attuale;
          }
        }         
                    
          }        
            
          
}
       

         
     //   Serial.print("il pin e':");        
        
      //  Serial.print(pindr,DEC);
      /* 
        if (digitalRead(pindr)==0)
          Serial.print("il valore è 0 ");
          
        if (digitalRead(pindr)==1)
          Serial.print("il valore è 1");          
          
       */

else 
  return;
               
               
          
 
        
      }//fine digital  
        

// inizio analog







      if (incomingByte=='a'){  //digital
        
        
        
        
     
        while (Serial.available() <1) 
          k++;//istruzione inutile
        incomingByte = Serial.read();
     
       
       
       
      if (incomingByte=='w')       //nota che per scriver ad esempio sul pin 4  devi scrivere aw041 o aw040   
        
      {
        
       pinCentinaia=0;  
       pinDecine=0; 
       pinUnita=0;        
       
             
        
        while (Serial.available() <1) 
          k++;//istruzione inutile
          
        pinDecine = Serial.read()-48;  
        
        while (Serial.available() <1) 
          k++;//istruzione inutile        
          
        pinUnita = Serial.read()-48;            
        
        pin=pinDecine*10+pinUnita;



        
       centinaia=0;  
       decine=0; 
       unita=0;    


        while (Serial.available() <1) 
          k++;//istruzione inutile
          
        centinaia = Serial.read()-48;          
        
        while (Serial.available() <1) 
          k++;//istruzione inutile
          
        decine = Serial.read()-48;  
        
        while (Serial.available() <1) 
          k++;//istruzione inutile        
          
        unita = Serial.read()-48;            
        
        valore=centinaia*100+decine*10+unita;  //contiene il valore con il quale settare il pin 
        
        

      
        pinMode(pin,OUTPUT); 
        
        delay(1);        
       
        analogWrite(pin,valore);
        
      //  Serial.print('o');
        

                 
          
          
          
       
       }
       
    else {
    if (incomingByte=='r')   { //nota che per leggere ad esempio il pin 4  devi scrivere dr04 
    
    
    
    
        while (Serial.available() <1) 
          k++;//istruzione inutile    
  
        pinDecinedr = Serial.read()-48;  
        
        while (Serial.available() <1) 
          k++;//istruzione inutile        
          
        pinUnitadr = Serial.read()-48;            
        
        pindr= pinDecinedr*10+pinUnitadr;  
        
        
      
        analogvalue=analogRead(pindr);
        
        tempvalue=0;
        
        if (analogvalue >999){
        Serial.print('a'); 
        Serial.print(analogvalue);
       
        }
        
        else  if ((analogvalue <1000)&(analogvalue >100)){
        Serial.print('a'); 
        Serial.print('0'); 
        Serial.print(analogvalue);
       
        }
        
        else  if ((analogvalue <100)&(analogvalue >10)){
        Serial.print('a'); 
        Serial.print('0');
        Serial.print('0');
        Serial.print(analogvalue);
       
        }     
     
        else  if (analogvalue <10){
        Serial.print('a'); 
        Serial.print('0');
        Serial.print('0');
        Serial.print('0');        
        Serial.print(analogvalue);
       
        }              
        
        
        
        
        //-----------------------------------------------------
       
        
  
         
     //   Serial.print("il pin e':");        
        
      //  Serial.print(pindr,DEC);
      /* 
        if (digitalRead(pindr)==0)
          Serial.print("il valore è 0 ");
          
        if (digitalRead(pindr)==1)
          Serial.print("il valore è 1");          
          
       */

}
else 
  return;
               
               
    }           









      }  //fine analog
        
          
    

  
  
  }//fine funzione ricevi
  
  
  void loop() {
    
      
      ricevi() ;
      
  
  
  
 }
