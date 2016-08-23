import arduinoserial,Serial_connection_Handler,time

#arduino = arduinoserial.SerialPort('/dev/ttyUSB0', 115200)

serial_communication=Serial_connection_Handler.Serial_connection_Handler()

#print arduino.read_until('\n')

for a in range (0,20):
  time.sleep(0.1)  
#serial_communication.status.write0('dw131xxxxxxxxxxxxxxxxxxxxxx')
  data=serial_communication.status.write('onos_d05v001s0001f001_#]')
  time.sleep(0.5)  
  data=serial_communication.status.write('onos_d05v000s0001f001_#]')

#data=serial_communication.status.read_data0()
  print(data)
time.sleep(0.1)  


