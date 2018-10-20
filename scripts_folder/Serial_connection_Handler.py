# -*- coding: UTF-8 -*-
#   Copyright 2014-2018 Marco Rigoni                                               #
#   ElettronicaOpenSource.com   elettronicaopensource@gmail.com               #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU General Public License as published by      #
#   the Free Software Foundation, either version 3 of the License, or         #
#   (at your option) any later version.                                       # 
#																			  #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU General Public License for more details.                              #
#                                                                             #
#   You should have received a copy of the GNU General Public License         #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #

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
    self.exluded_port_list=[] 
    self.connectSerialPortOrRetry()

   




  def connectSerialPortOrRetry(self):
    logprint("connectSerialPortOrRetry() executed")
    self.exluded_port_list=[]
    self.uart=self.connectToPort()
    self.working=1
    i=0
    while (self.uart ==0) :  #while port is not connected retry to connect   banana to make it clever..
      logprint("retry serial connection number:"+str(i))
      self.uart=self.connectToPort()
      if self.uart==1:
        break
      time.sleep(1)
      if i >1:
        if (self.searchForSerialCable(self.exluded_port_list )=="null"):
          logprint("error serial connection, no serial ports found")
          self.uart==-1
          self.working=0
          return(-1)

      i=i+1

    return(1)#the connection was successful  

  
  def connectToPort(self):
    logprint("connectToPort() executed")
    port=self.searchForSerialCable(self.exluded_port_list ) 
    if port!="null":   # if i found the port then use it
      try:
        #old_port=port       #  [0:len(port)-1] 
        port='/dev/'+port   #  [0:len(port)-1]   #remove /n of ls
        self.ser =arduinoserial.SerialPort(port, baud_rate)     
        logprint ("serial port connected correctly to onos system on port:"+port) 
        return(self.ser)
      except:  #some error occured while using the port i found 
        logprint("port error with port:"+port+" i will retry with another port")
        if port not in self.exluded_port_list:
          self.exluded_port_list.append(port)
        port=self.searchForSerialCable(self.exluded_port_list )  
        if port!="null":   # if i found the port then use it
          try:
            #old_port=port[0:len(port)-1] 
            port='/dev/'+port    #[0:len(port)-1]   #remove /n of ls
            self.ser =arduinoserial.SerialPort(port, baud_rate)     
            logprint("arduino connected correctly to onos system")
            return(self.ser)
          except:
            logprint("error,port problem onos will be only a webserver and will not controll the hardware nodes , please reconnect arduino to the usb port!")
            return(0)
        else:#no port found after the error 
          logprint("error, port not found onos will be only a webserver and will not controll the hardware nodes , please connect an arduino to the usb port!")
          return(0)

    else:# port not found the first time
      logprint("port not found onos will be only a webserver and will not controll the hardware nodes , please connect an arduino to the usb port!")
      return(0)



  def searchForSerialCable(self,list_of_port_to_not_use):
    logprint("searchForSerialCable() executed with self.exluded_port_list= "+str(list_of_port_to_not_use))
    list_of_dev=os.listdir("/dev")


    if router_hardware_type=="RouterOP":  #if the router hardware is orange pi zero
      logprint("orangepi serial port ttyS2 selected")
      if "ttyS2" in  list_of_dev: #for orange pi
        logprint("return ttyS2") 
        return("ttyS2")


    if ("ttyUSB0" in list_of_dev)and('/dev/ttyUSB0' not in list_of_port_to_not_use):
      return("ttyUSB0")

    if ("ttyUSB1" in list_of_dev)and('/dev/ttyUSB1' not in list_of_port_to_not_use):
      return("ttyUSB1")

    if ("ttyUSB2" in list_of_dev)and('/dev/ttyUSB2' not in list_of_port_to_not_use):
      return("ttyUSB2")

    if ("ttyATH0" in list_of_dev)and('/dev/ttyATH0' not in list_of_port_to_not_use):
      return("ttyATH0")

    if ("ttyACM0" in list_of_dev)and('/dev/ttyACM0' not in list_of_port_to_not_use):
      return("ttyACM0")


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
    logprint("class Serial_connection_Handler destroyed")
    #try:
    #  self.ser.close()
    #except:
    #  print("")




