import arduinoserial,time

arduino = arduinoserial.SerialPort('/dev/ttyUSB0', 115200)
time.sleep(5) #wait for arduino to wake up after reset
#print arduino.read_until('\n')
arduino.write('[S_begin_#]')
i = 0
while 1:
  time.sleep(0.5)  
  arduino.write('[S_fed001x_#]')
  i = i + 1 
  time.sleep(0.5)  
  arduino.write('[S_fed000x_#]') 
  i = i + 1
  print("i:"+str(i))


#senza interrupt e senza reset radio:
#impallato:i:12626
#impallato: i:60976
#con interrupt e reset seriale raggiounge e supera 100000 switch on off del relay


