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
baud_rate=115200
class Serial_connection_Handler():
  exluded_port_list=[]

  def __init__(self):
    self.exit=0 
    self.uart=self.connectToPort()
    self.working=1
    self.exluded_port_list 
    i=0
    while (self.uart ==0) :  #while port is not connected retry to connect   banana to make it clever..
      print ("retry serial connection number:"+str(i))
      self.uart=self.connectToPort()
      if self.uart==1:
        break
      time.sleep(1)
      if i>2:        #after n tries i increase the time between the tries
        time.sleep(10)
      if i>4:        #after n tries i increase the time between the tries
        time.sleep(30) 

      if i >0:
        if (self.searchForSerialCable(self.exluded_port_list )=="null"):
          print ("error serial connection, no serial ports found")
          self.uart==-1
          self.working=0
          return(-1)

      i=i+1


  def reconnectSerialPort():
    print("reconnectSerialPort() executed")
    self.exluded_port_list=[]
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
        if (self.searchForSerialCable(self.exluded_port_list )=="null"):
          print "error serial reconnection, no serial ports found"
          self.working=0
          return(-1)



  def connectToPort(self):
    print("connectSerialPort() executed")
    port=self.searchForSerialCable(self.exluded_port_list ) 
    if port!="null":   # if i found the port then use it
      try:
        #old_port=port       #  [0:len(port)-1] 
        port='/dev/'+port   #  [0:len(port)-1]   #remove /n of ls
        self.ser =arduinoserial.SerialPort(port, baud_rate)     
        print "arduino connected correctly to onos system" 
        return(self.ser)
      except:  #some error occured while using the port i found 
        print "port error with port:"+port+" i will retry with another port" 
        if port not in self.exluded_port_list:
          self.exluded_port_list.append(port)
        port=self.searchForSerialCable(self.exluded_port_list )  
        if port!="null":   # if i found the port then use it
          try:
            #old_port=port[0:len(port)-1] 
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



  def searchForSerialCable(self,list_of_port_to_not_use):
    print ("searchForSerialCable() executed with self.exluded_port_list= "+str(list_of_port_to_not_use))
    list_of_dev=os.listdir("/dev")

    for dev in  list_of_dev:
      if (dev.find("ttyATH")!=-1)and('/dev/'+dev not in list_of_port_to_not_use):
        return(dev)

    for dev in  list_of_dev:
      if (dev.find("ttyUSB")!=-1)and('/dev/'+dev not in list_of_port_to_not_use):
        return(dev)

    for dev in  list_of_dev:
      if (dev.find("ttyACM")!=-1)and('/dev/'+dev not in list_of_port_to_not_use):
        return(dev)

    for dev in  list_of_dev:
      if (dev.find("ttyS")!=-1)and('/dev/'+dev not in list_of_port_to_not_use):
        return(dev)

    return("null")



    
  def __del__(self):
    print ("class Serial_connection_Handler destroyed")





