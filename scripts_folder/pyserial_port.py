#!/usr/bin/python

"""
Obsolete not used.


"""

import serial, time
#initialization and open the port

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
#ser.port = "/dev/port0"
#ser.port = "/dev/ttyS2"
ser.baudrate = 57600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write

rx_timeout=10



try: 
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()


def writeToSerial(data_to_write):
  print "writeToSerial() executed"

  if not ser.isOpen():
    return("error serial_port001")

  try:
    ser.flushInput() #flush input buffer, discarding all its contents
    ser.flushOutput()#flush output buffer, aborting current output 
                 #and discard all that is in buffer

        #write data
    ser.write(data_to_write)
    print("write data:"+data_to_write)

    time.sleep(1)  #give the serial port sometime to receive the data

    numOfLines = 0

    time_start=time.time()
    while True:
      response = ser.read(len(data_to_write)+2)
      print("read data: " + response)

      numOfLines = numOfLines + 1

      if (numOfLines >= 1):
        return(response)

      if (time_start>(time.time()+rx_timeout) ):  
        print "rx timeout0"
        return("error rx001")

    ser.close()
  except Exception, e1:
    print "error communicating...: " + str(e1)




