import arduinoserial,Serial_connection_Handler,time

#arduino = arduinoserial.SerialPort('/dev/ttyUSB0', 115200)

serial_communication=Serial_connection_Handler.Serial_connection_Handler()

#print arduino.read_until('\n')
oldtime=time.time()

for a in range (0,20):
  time.sleep(0.1)  
#serial_communication.status.write0('dw131xxxxxxxxxxxxxxxxxxxxxx')
 
  data=serial_communication.status.write('onos_d05v001s0001f001_#]\n')
  print(data)
  time.sleep(0.01)   
  data=serial_communication.status.write('onos_d05v000s0001f001_#]\n')
  print(data)
  time.sleep(0.01)  
print "totalTime="+str(time.time()-oldtime)  
time.sleep(0.1)  


