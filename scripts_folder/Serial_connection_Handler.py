""" 
  This module will find the first working usb serial port avaible and will try to connect to it.
"""

import arduinoserial
import os
import time,string
from conf import *           # import parameter globalVar.py

exit=0



HIGH=1
LOW=0
ser=0
baud_rate=57600
class Serial_connection_Handler():

  def __init__(self):
    self.exit=0 
    self.uart=self.connectToPort()
    self.working=1
    i=0
    while (self.uart ==0) :  #while port is not connected retry to connect   banana to make it clever..
      self.uart=self.connectToPort()
      if self.uart==1:
        break
      time.sleep(1)
      if i>2:        #after 60 tries i increase the time between the tries
        time.sleep(30)
      if i>4:        #after 120 tries i increase the time between the tries
        time.sleep(60) 

      if i >10:
        if (searchForSerialCable!="null"):
          print "error serial connection, no serial ports found"
          self.working=0
          return(-1)




  def reconnectSerialPort():

    self.uart=self.connectToPort()
    self.working=1
    i=0
    while (self.uart ==0) :  #while port is not connected retry to connect   banana to make it clever..
      self.uart=self.connectToPort()
      if self.uart==1:
        return(1)
      time.sleep(1)
      if i>2:        #after 60 tries i increase the time between the tries
        time.sleep(30)
      if i>4:        #after 120 tries i increase the time between the tries
        time.sleep(60) 

      if i >10:
        if (searchForSerialCable!="null"):
          print "error serial reconnection, no serial ports found"
          self.working=0
          return(-1)




  def verifyPort(self,port_to_search,port_exluded):
    if port_to_search!=port_exluded:
      result=os.path.exists("/dev/"+port_to_search) 
    else:
      return("no")

    #result=os.popen("ls /dev/ | grep -v "+port_exluded+" | grep "+port_to_search).read()
    if result:
      return (port_to_search)
    else:
      return ("no")



  def connectToPort(self):

    port=self.searchForSerialCable("nothing") 
    if port!="null":   # if i found the port then use it
      try:
        old_port=port       #  [0:len(port)-1] 
        port='/dev/'+port   #  [0:len(port)-1]   #remove /n of ls
        self.ser =arduinoserial.SerialPort(port, baud_rate)     
        print "arduino connected correctly to onos system" 
        return(self.ser)
      except:  #some error occured while using the port i found 
        print "port error i will retry with another port" 
        port=self.searchForSerialCable(old_port)  
        if port!="null":   # if i found the port then use it
          try:
            old_port=port[0:len(port)-1] 
            port='/dev/'+port    #[0:len(port)-1]   #remove /n of ls
            self.ser =arduinoserial.SerialPort(port, baud_rate)     
            print "arduino connected correctly to onos system" 
            return(self.ser)
          except:
            print "port problem onos will be only a webserver and will not controll the hardware nodes , please reconnect arduino to the usb port!"
            return(0)
        else:#no port found after the error 
          print "port not found onos will be only a webserver and will not controll the hardware nodes , please connect an arduino to the usb port!" 
          return(0)

    else:# port not found the first time
      print "port not found onos will be only a webserver and will not controll the hardware nodes , please connect an arduino to the usb port!"
      return(0)



  def searchForSerialCable(self,exluded_port):

    list_of_dev=os.listdir("/dev")

    for dev in  list_of_dev:
      if (dev.find("ttyUSB")!=-1)and(dev!=exluded_port):
        return(dev)

    for dev in  list_of_dev:
      if (dev.find("ttyACM")!=-1)and(dev!=exluded_port):
        return(dev)


    port=self.verifyPort("ttyUSB0",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyUSB1",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyUSB2",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyUSB3",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyUSB4",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyUSB",exluded_port)

    if len (port)<3:
      port=self.verifyPort("ttyACM0",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyACM1",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyACM2",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyACM3",exluded_port)
    if len (port)<3:
      port=self.verifyPort("ttyACM",exluded_port)
    if len (port)<3:
      return("null")

    return(port)     

    







