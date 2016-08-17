import arduinoserial,time

arduino = arduinoserial.SerialPort('/dev/ttyUSB1', 115200)
time.sleep(5) #wait for arduino to wake up after reset
#print arduino.read_until('\n')
arduino.write('dw131')
while 1:
  time.sleep(0.1)  
  arduino.write('dw131')
  time.sleep(0.1)  
  arduino.write('dw130') 

