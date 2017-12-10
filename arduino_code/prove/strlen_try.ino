
 
void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(115200);

  // prints title with ending line break
  Serial.println("prova");
}


void loop() {
  //memset(syncMessage,0,sizeof(syncMessage)); //to clear the array
  char syncMessage [20] = "prova123333333333";

  //memset(syncMessage,0,sizeof(syncMessage)); //to clear the array

  syncMessage[0]='0';
  syncMessage[1]='1';
  syncMessage[2]='2';
  syncMessage[3]='3';
  syncMessage[4]='4';
  syncMessage[5]='5';  
  syncMessage[6]='6';
  syncMessage[strlen(syncMessage)]='7';  //without the memset 0 this will fail...because there is no teminating null character
  syncMessage[strlen(syncMessage)]='8';  //without the memset 0 this will fail...because there is no teminating null character  
  Serial.print("start1:");  
  Serial.print(syncMessage[0]);
  Serial.print(syncMessage[1]);
  Serial.print(syncMessage[2]);
  Serial.print(syncMessage[3]);
  Serial.print(syncMessage[4]);
  Serial.print(syncMessage[5]);
  Serial.print(syncMessage[6]);
  Serial.print(syncMessage[7]);  
  Serial.print(syncMessage[8]);
  Serial.print(syncMessage[9]);
  Serial.print(syncMessage[10]);    
  Serial.println("end1");  
  
  
//methond that work just because there is memset to 0... :  
  memset(syncMessage,0,sizeof(syncMessage)); //to clear the array
  syncMessage[0]='0';
  syncMessage[1]='1';
  syncMessage[2]='2';
  syncMessage[3]='3';
  syncMessage[4]='4';
  syncMessage[5]='5';  
  syncMessage[6]='6';
  syncMessage[strlen(syncMessage)]='7';  //without the memset 0 this will fail...because there is no teminating null character
  syncMessage[strlen(syncMessage)]='8';  //without the memset 0 this will fail...because there is no teminating null character  
  Serial.print("start2:");  
  Serial.print(syncMessage[0]);
  Serial.print(syncMessage[1]);
  Serial.print(syncMessage[2]);
  Serial.print(syncMessage[3]);
  Serial.print(syncMessage[4]);
  Serial.print(syncMessage[5]);
  Serial.print(syncMessage[6]);
  Serial.print(syncMessage[7]);  
  Serial.print(syncMessage[8]);
  Serial.print(syncMessage[9]);
  Serial.print(syncMessage[10]);    
  Serial.println("end2");    




// method that works because I put a null character manually

  char syncMessage2 [20] = "prova123333333333";

  
  syncMessage2[0]='0';
  syncMessage2[1]='1';
  syncMessage2[2]='2';
  syncMessage2[3]='3';
  syncMessage2[4]='4';
  syncMessage2[5]='5';  
  syncMessage2[6]='6';
  syncMessage2[7]='\0';   // I put the null character at the end ... 
  uint8_t msg_len=  strlen(syncMessage2);
  syncMessage2[msg_len]='7';  
  syncMessage2[msg_len+1]='\0';  // I update the end of the string putting a null character... 
  msg_len=  strlen(syncMessage2);
  syncMessage2[msg_len]='8';  
  syncMessage2[msg_len+1]='\0';  // I update the end of the string putting a null character... 
  
  Serial.print("start3:");  
  Serial.print(syncMessage2[0]);
  Serial.print(syncMessage2[1]);
  Serial.print(syncMessage2[2]);
  Serial.print(syncMessage2[3]);
  Serial.print(syncMessage2[4]);
  Serial.print(syncMessage2[5]);
  Serial.print(syncMessage2[6]);
  Serial.print(syncMessage2[7]);  
  Serial.print(syncMessage2[8]);
  Serial.print(syncMessage2[9]);
  Serial.print(syncMessage2[10]);    
  Serial.println("end3");    
  
  while (1){
  }
  

}
