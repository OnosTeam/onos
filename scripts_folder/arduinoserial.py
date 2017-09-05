#!/usr/bin/env python
#
# Copyright 2007 John Wiseman <jjwiseman@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


#   Copyright 2014 Marco Rigoni                                               #
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
#<http://todbot.com/blog/2006/12/06/arduino-serial-c-code-to-talk-to-arduino/>
# A port of Tod E. Kurt's arduino-serial.c.


"""
    This module will be used to setup the proper serial configurations and to read and write the data from the serial port.
    
 
"""

import termios
import fcntl
import os
import sys
import time
import getopt
from conf import *           # import parameter globalVar.py
import thread,threading,time,string
import serial




write_enable=0


global last_received_packet
global data_to_write
global incomingByteAfterWriteAvaible
global serial_incomingBuffer
global waitTowriteUntilIReceive

msgWasWritten=0


serial_incomingBuffer=""  
#hwNodeDict[0]=hw_node.HwNode("base","arduino_2009",0)  #make the first node , the base station  one


class SerialPort:

  def __init__(self, serialport, bps):
    """Takes the string name of the serial port
    (e.g. "/dev/tty.usbserial","COM1") and a baud rate (bps) and
    connects to that port at that speed and 8N1. Opens the port in
    fully raw mode so you can send binary data.

    """


    self.ser = serial.Serial()
    self.ser.port = serialport
#ser.port = "/dev/port0"
#ser.port = "/dev/ttyS2"
    self.ser.baudrate = bps
    self.ser.bytesize = serial.EIGHTBITS #number of bits per bytes
    self.ser.parity = serial.PARITY_NONE #set parity check: no parity
    self.ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
    self.ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
    self.ser.xonxoff = False     #disable software flow control
    self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
    self.ser.dsrdtr = False       #disable hardware (DSR/DTR) flo






    self.port=serialport
    self.busy=0
#the error controll is done by the arduin_handler.py     
    #self.fd = os.open(serialport, os.O_RDWR | os.O_NOCTTY | os.O_NDELAY)
    self.status=1



    self.readed_packets_list=[]


    self.status=0




    #os.system("cat "+self.port)
    self.usb=""
    #n = os.read(self.fd)


    
    serial_incomingBuffer=''
    self.removeFromInBuffer=''

    
    self.dataAvaible=0
    self.t_read = threading.Thread(target=self.read_data)
    self.t_read.daemon = True  #make the thread a daemon thread
    self.t_read.start()
    self.exit=0
    


    self.ser.open()
    
    self.port_was_opened=0
    




  def read_data(self):   # thread  function
      '''Outputs data from serial port to sys.stdout.'''

      global last_received_packet
      global data_to_write
      global incomingByteAfterWriteAvaible
      global waitTowriteUntilIReceive
      global write_enable
      global msgWasWritten
      logprint("read_data thread executed")
 

      ignore = ''   #'\r'
      filedev=self.port
      self.dataAvaible=0
      self.exit=exit
   

      try: 

        if self.ser.isOpen() == True :  
          self.ser.flushInput() #flush input buffer, discarding all its contents
      except Exception as e :
        message="error can't flush input"
        logprint(message,verbose=5,error_tuple=(e,sys.exc_info())) 


      while (self.exit==0):
          time.sleep(0.03)#0.03 
          
          if self.ser.isOpen() == False :
            logprint("error serial port disconnected in arduinoserial.py",verbose=8)
            try:
              self.ser.open()
              logprint("I tried to reconnect serial port from arduinoserial and I have been succesfull") 
            except:
              logprint("I tried to reconnect serial port from arduinoserial module but I failed")
              #priorityCmdQueue.put( {"cmd":"reconnectSerialPort"})
              self.exit=1
              return()



          if self.exit==1:
            return()
          






           # try:
           #   self.ser.flushInput() #flush input buffer, discarding all its contents
           # except Exception as e :
           #   print "can't flush input"+str(e.args) 
           #   errorQueue.put( "can't flush input"+str(e.args) )
          #msgWasWritten=0

          #if write_enable==1:
           # try:
            #  self.ser.write(data_to_write)
             # print "i have wrote to serial port data_to_write:::::::::::::::::::::::::::::::"+data_to_write
             # time.sleep(0.2) #0.02 
             # write_enable=0
             # msgWasWritten=1
            #except Exception as e :
            #  print "can't write to uart"+str(e.args) 
            #  errorQueue.put( "can't write to uart"+str(e.args) )
            #  return()

            #try:
            #  self.ser.flushOutput()
            #except Exception as e :
            #  print "can't flush output"+str(e.args) 
            #  errorQueue.put( "can't flush output"+str(e.args) )

          #waitTowriteUntilIReceive=0
          self.port_was_opened=1
          buf=''
          next_buf=''
          while (self.exit==0):
            byte=''
            buf=next_buf
            next_buf=''
            time.sleep(0.01) 

            if self.ser.inWaiting()<1:   #skip if there is no incoming data
              time.sleep(0.01) 
              continue
            else: 
##################################################################
              try:
                buf =buf+ self.ser.read(self.ser.inWaiting())   #  self.usbR.read(1)
                #print byte
              except Exception as e  :
                message="error in self.ser.read(self.ser.inWaiting()) "
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  
                continue



              if len(buf)>5:
                #waitTowriteUntilIReceive=1 
                if ( (buf.find("[S_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
                  logprint("end of serial packet:_#] ")
                  break 


              #if (buf.find("\n")!=-1):
              #  print ("end of line received but no onoscmd found")
              #  break

              #if len(buf)>0:   
              #  logprint(buf) 


##################################################################




          #at this point i should have a full packet message
          if len(buf)>5:

            buf=buf.replace("\n", "")  #to remove \n
            buf=buf.replace("\r", "")  #to remove \r

            buf=buf.replace("\x00", "")  #to remove \n


            cmd_start=buf.find("[S_")
            cmd_end=buf.find("_#]",cmd_start) #serch the end of the packet ..starting from the "[S_"

            cmd='' 
            if ( (cmd_start!=-1)&(cmd_end!=-1)): #there is a full onos command packet


              #time.sleep(1) #todo remove,justfordebug
              cmd=buf[cmd_start:cmd_end+3]
              next_buf=buf[cmd_end+3:]
              buf=''              

              logprint("Packet 232 cmd input :"+cmd)







              if( (cmd[2]=="o")&(cmd[3]=="k") ): # S_ok003dw060005_#  i received a confirm from the node
                
                #with lock_serial_input:              
                #serial_incomingBuffer=buf
                self.readed_packets_list.append(cmd)
                buf=""
                self.dataAvaible=1 
                if msgWasWritten==1:
                  last_received_packet=cmd
                  msgWasWritten=0 
                  incomingByteAfterWriteAvaible=1 
                  logprint("packet received after the write is :"+last_received_packet)

                continue

              elif( (cmd[6]=="s")&(cmd[7]=="y") )or((cmd[6]=="u")&(cmd[7]=="l")) :
              # [S_001syProminiS0001_#]   or [S_123ulWPlugAvx000810000_#]

                logprint("serial rx cmd="+cmd)
                try:
                  serial_number=cmd[8:20]   
                  node_address=cmd[3:6]
                  node_fw="def0"  #default
                  if ((cmd[6]=="u")&(cmd[7]=="l")):  #todo  sensor value data extraction [S_003ulWrelay4x000100000u_#]
                    obj_value=cmd[20]
                    obj_address_to_update=0
                    priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":{obj_address_to_update:obj_value} }) 




                  if node_address=="254":  #the node is looking for a free address

                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 
                    continue

                except Exception as e  :               
                  message="error receiving serial sync message cmd was :"+cmd
                  logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  

                #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 
                #waitTowriteUntilIReceive=0
                continue



####reed node

              elif( (cmd[6]=="r")&(cmd[7]=="s") ) :
              #  [S_001rsWreedSaa0001312Lgx_#] 

                logprint("serial rx cmd="+cmd)
                try:
                  serial_number=cmd[8:20]   
                  node_address=cmd[3:6]
                  node_fw="def0"  #default
                  reeds_status=cmd[20]
                  logprint("reeds status received:"+reeds_status) 
                  reed1_status=(reeds_status=="2")or(reeds_status=="3") #get boolean result
                  reed2_status=(reeds_status=="1")or(reeds_status=="3") #get boolean result
                  tempSensor= ord(cmd[21])-1       #-1 is because on the micro side i added 1 to the value to avoid the 0 binary..
                  luminosity_sensor= ord(cmd[22])-1 #-1 is because on the micro side i added 1 to the value to avoid the 0 binary..
                  battery_state= ord(cmd[23])-1 #-1 is because on the micro side i added 1 to the value to avoid the 0 binary..
                  objects_to_update_dict={0:reed1_status,5:reed2_status,3:tempSensor,10:luminosity_sensor,9:battery_state}
                  obj_address_to_update=0
                  priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":objects_to_update_dict }) 
                  if node_address=="254":  #the node is looking for a free address
                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 
                    continue

                except Exception as e  :               
                  message="error receiving serial sync message cmd was :"+cmd
                  logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  
                  #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw })                 #waitTowriteUntilIReceive=0

                continue


####end reed node


#### 4 relay node

              elif( (cmd[6]=="r")&(cmd[7]=="4") ) :
              #  [S_001rsWreedSaa0001312Lgx_#] 

                logprint("serial rx cmd="+cmd)
                try:
                  serial_number=cmd[8:20]   
                  node_address=cmd[3:6]
                  node_fw="def0"  #default
                  relay0_status=cmd[20]
                  relay1_status=cmd[21]
                  relay2_status=cmd[22]
                  relay3_status=cmd[23]

                  objects_to_update_dict={0:relay0_status,1:relay1_status,2:relay2_status,3:relay3_status}
                  obj_address_to_update=0
                  priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":objects_to_update_dict }) 
                  if node_address=="254":  #the node is looking for a free address
                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 
                    continue

                except Exception as e  :               
                  message="error receiving serial sync message cmd was :"+cmd
                  logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  
                  #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw })                 #waitTowriteUntilIReceive=0

                continue


####end reed node


              elif( (cmd[6]=="g")&(cmd[7]=="a") ): #  [S_001ga3.05ProminiS0001x_#]
                logprint("---serial rx cmd="+cmd,verbose=5)
                try:


                  serial_number=cmd[12:24]   

                  node_fw=cmd[8:12]
                  node_address=cmd[3:6]

                  if node_address=="254" or node_address=="001" :  #the node is looking for a free address or to a confirm for first contact
                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 

               
                  priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw })               
                  #waitTowriteUntilIReceive=0  
                  continue


                except Exception as e  :               
                  message="error receiving serial sync message cmd was :" 
                  logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 

                continue 



              else:  # a messege is received but is not started from a node, probably is an answer
                if msgWasWritten==1:
                  last_received_packet=cmd
                  msgWasWritten=0 
                  incomingByteAfterWriteAvaible=1 
                  logprint("_Packet received after the write is :"+last_received_packet)


           # print "serial input="+buf

              #with lock_serial_input:              
              serial_incomingBuffer=cmd
              self.readed_packets_list.append(cmd)

              self.dataAvaible=1 

              logprint("incoming buffer="+serial_incomingBuffer)
            else: #cmd not found
              tmp_buf=buf.decode("utf8","replace")
              tmp_buf.encode("ascii","replace")
              logprint("incoming buffer="+tmp_buf)
              self.dataAvaible=0


      logprint("serial port closed")               
      return()





  def waitForData(self,timeout):  #deprecated
    j=0
    self.disable_uart_queue=1  # I disable the auto queue add because I want to read the data directly
    start_time=time.time()
    while self.dataAvaible==0:
      if (time.time()>(start_time+timeout) ): #timeout to exit the loop
        return(-1)
      time.sleep(0.001) 
    return(1) 
    
  

  def removeFromPackets_list(self,packet):
    if packet in self.readed_packets_list:
      self.readed_packets_list.remove(packet) 


#  def portWrite(self,data):
#    print "portWrite executed"
#    self.usbW.write(data)

  def write(self, data):#test..
    global incomingByteAfterWriteAvaible
    global msgWasWritten
    global last_received_packet
    #self.ser.flushOutput()
    #while self.ser.inWaiting()>0:
    #  time.sleep(0.01)
    #self.ser.flushOutput()
    self.ser.flush()
    #if self.ser.flush()()>0: #if there is something on the output buffer wait a bit
    #time.sleep(0.01) 
    #  print("wait for self.ser.out_waiting self.ser.out_waitingself.ser.out_waitingself.ser.out_waiting")

    
    #start_time=time.time()
    #while waitTowriteUntilIReceive==1:

    #  if (time.time()>(start_time+0.5) ):#2 #timeout to exit the loop
    #    print "rx after write timeout0"
    #time.sleep(0.01) 
    incomingByteAfterWriteAvaible=0 
    self.ser.write(data)   
    msgWasWritten=1
    self.ser.flush()
    #while self.ser.inWaiting()<5:
    #  time.sleep(0.01)

    #time.sleep(0.1)
    rx_after_tx_timeout=time.time()+5  #0.7
    while incomingByteAfterWriteAvaible==0:
      if rx_after_tx_timeout<time.time():
        logprint("i exit the loop because of timeout")
        return("void") 

    logprint ("i exit the loop because i received a message after I have write one")
    answer=last_received_packet
    last_received_packet=''
    return(answer)





  def write2(self, data): #deprecated
    global write_enable
    global last_received_packet
    global data_to_write
    global incomingByteAfterWriteAvaible
    data_to_write=data


    write_enable=1
    last_received_packet=""

                #self.portWrite(data_to_write)
    #self.usbW.write(data_to_write+'\n')
    #os.system("echo "+data_to_write+" >> "+self.port) 
    #self.ser.write(data_to_write)

    incomingByteAfterWriteAvaible=0
    logprint("data_to_write:"+data_to_write)
 
    start_time=time.time()
    while incomingByteAfterWriteAvaible==1:
      time.sleep(0.01) 

      if (time.time()>(start_time+0.5) ):#2 #timeout to exit the loop
        logprint("rx after write timeout0")
        incomingByteAfterWriteAvaible=0
        return("error_reception")
    
   
    return(last_received_packet)











  def isOpen(self):
    #print " called  isOpen"
    return(self.status)

  #def open():
  #  return(1)


  def __del__(self):
    logprint("class arduinoserial destroyed")
    self.exit=1
    #layerExchangeDataQueue.put( {"cmd":"set_serialCommunicationIsWorking=0"}) 
    if self.port_was_opened==1:
      layerExchangeDataQueue.put( {"cmd":"reconnectSerialPort"}) 
      self.port_was_opened=0
    return()

 #   try:
 #     os.close(self.fd)
 #   except:
 #     print "tried to close serial port"





  def close(self):
    self.exit=1
    logprint("class arduinoserial destroyed by close()")
#    try:
 #     os.close(self.ser)     
  #  except:
   #   print "tried to close serial port"


