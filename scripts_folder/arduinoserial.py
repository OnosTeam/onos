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
    






  def read_data(self):   # thread  function
      '''Outputs data from serial port to sys.stdout.'''

      global last_received_packet
      global data_to_write
      global incomingByteAfterWriteAvaible
      global waitTowriteUntilIReceive
      global write_enable
      print "read_data thread executed"
 

      ignore = ''   #'\r'
      filedev=self.port
      self.dataAvaible=0
      self.exit=exit


      try:
        self.ser.flushInput() #flush input buffer, discarding all its contents
      except Exception, e :
        print "can't flush input"+str(e.args) 
        errorQueue.put( "can't flush input"+str(e.args) )


      while (self.exit==0):
          time.sleep(0.03)#0.03 
          
          if self.ser.isOpen() == False :
            print "error serial port disconnected in arduinoserial.py"
            errorQueue.put("error serial port disconnected in arduinoserial.py")
            try:
              self.ser.open()
              print "I tried to reconnect serial port from arduinoserial and I have been succesfull" 
              errorQueue.put("I tried to reconnect serial port from arduinoserial and I have been succesfull")
            except:
              print "I tried to reconnect serial port from arduinoserial module but I failed" 
              errorQueue.put("I tried to reconnect serial port from arduinoserial module but I failed")
              #priorityCmdQueue.put( {"cmd":"reconnectSerialPort"})
              self.exit=1


          if self.exit==1:
            break
          buf=''






           # try:
           #   self.ser.flushInput() #flush input buffer, discarding all its contents
           # except Exception, e :
           #   print "can't flush input"+str(e.args) 
           #   errorQueue.put( "can't flush input"+str(e.args) )
          msgWasWritten=0

          if write_enable==1:
            try:
              self.ser.write(data_to_write)
              print "i have wrote to serial port data_to_write:::::::::::::::::::::::::::::::"+data_to_write
                #time.sleep(0.1) #0.02 
              write_enable=0
              msgWasWritten=1
            except Exception, e :
              print "can't write to uart"+str(e.args) 
              errorQueue.put( "can't write to uart"+str(e.args) )

            try:
              self.ser.flushOutput()
            except Exception, e :
              print "can't flush output"+str(e.args) 
              errorQueue.put( "can't flush output"+str(e.args) )

          waitTowriteUntilIReceive=0
          while (self.exit==0):
            #time.sleep(0.1) 

            if self.ser.inWaiting()<1:   #skip if there is no incoming data
              time.sleep(0.1) 
              continue
            else: 
##################################################################
              try:
                byte = self.ser.read(1)   #  self.usbR.read(1)
                #print byte
              except:
                byte=-1
                self.status=0
                continue

              if byte=="\x00":
                continue

              if (ord(byte)==10):  # 10 is the value for new line (\n) end of packet on incoming serial buffer  
                print "end of serial packet for /n"
                break
              else:   
                #print "in byte="+byte+" end of in byte"
                buf=buf+byte
              

              if len(buf)>5:
                waitTowriteUntilIReceive=1 
                if ( (buf.find("[S_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
                  print "end of serial packet:_#] "
                  break 


              if (buf.find("\n")!=-1):
                print ("end of line received but no onoscmd found")
                break

              print(buf) 


##################################################################




          #at this point i should have a full packet message
          if len(buf)>3:

            buf=buf.replace("\n", "")  #to remove \n
            buf=buf.replace("\r", "")  #to remove \r




            cmd_start=buf.find("[S_")
            cmd_end=buf.find("_#]")
           
            if ( (cmd_start!=-1)&(cmd_end!=-1) ): #there is a full onos command packet

              print "AAAAAAAAAAAAAAAAAAAAAAAApacket 232 input :"+buf
              #time.sleep(1) #todo remove,justfordebug
              if msgWasWritten==1:
                last_received_packet=buf
                msgWasWritten=0 
                incomingByteAfterWriteAvaible=1 
                print "packet received after the write is :"+last_received_packet

 

              cmd=buf[cmd_start:cmd_end+3]



              if( (cmd[2]=="o")&(cmd[3]=="k") ): # S_ok003dw060005_#  i received a confirm from the node
                

                #with lock_serial_input:              
                serial_incomingBuffer=buf
                self.readed_packets_list.append(buf)
                buf=""
                self.dataAvaible=1 
                waitTowriteUntilIReceive=0
                continue

              if( (cmd[6]=="s")&(cmd[7]=="y") )or((cmd[6]=="u")&(cmd[7]=="l")) :
              # [S_001sy3.05ProminiS0001_#]   or [S_123ul5.24WPlugAvx000810000_#]

                print "serial rx cmd="+cmd
                buf=""
                try:
                  serial_number=cmd[12:24]   
                  node_fw=cmd[8:12]
                  node_address=cmd[3:6]

                  if ((cmd[6]=="u")&(cmd[7]=="l")):  #todo  sensor value data extraction [S_123ul5.24WPlugAvx000810000_#]
                    obj_value=cmd[24]
                    obj_number_to_update="0"
                    priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":{obj_number_to_update:obj_value} }) 

                    #todo update the first node obj reading the name from hardwaremodel




                  if node_address=="254":  #the node is looking for a free address
                    priorityCmdQueue.put( {"cmd":"sendNewAddressToNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 

                except Exception, e  :               
                  print "error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)  
                  errorQueue.put("error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)   )

                priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 
                waitTowriteUntilIReceive=0
                continue



              if( (cmd[6]=="g")&(cmd[7]=="a") ): #  [S_001ga3.05ProminiS0001x_#]
                print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLserial rx cmd="+cmd
                buf=""
                try:
                  numeric_serial_number=cmd[13:25]

                  serial_number=numeric_serial_number=cmd[12:24]   

                  node_fw=cmd[8:12]
                  node_address=cmd[3:6]

                  if node_address=="254" or node_address=="001" :  #the node is looking for a free address or to a confirm for first contact
                    priorityCmdQueue.put( {"cmd":"sendNewAddressToNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 

               
                  priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw })               
                  waitTowriteUntilIReceive=0  
                  continue


                except Exception, e  :               
                  print "error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)  
                  errorQueue.put("error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)   )
        






           # print "serial input="+buf

              #with lock_serial_input:              
              serial_incomingBuffer=buf
              self.readed_packets_list.append(buf)

              self.dataAvaible=1 
              waitTowriteUntilIReceive=0
            #time.sleep(0.18)  #important to not remove..

           # timeout=time.time()
           # while waitToReceiveUntilIRead==1:
          #    time.sleep(0.001)
              #print "i wait until you read"
          #    if (time.time>(timeout+10) ): #timeout to exit the loop
           #     break

              print "incoming buffer="+serial_incomingBuffer
              buf=""
            else: #len buf ==0
            
              self.dataAvaible=0


      print "serial port closed"               
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
    




  def write0(self, str):#deprecated
    print "i write"+str
    os.system("echo "+str+" >> "+self.port)


    print "write_to_serial_packet_ready==1"

    return()  

  


  def removeFromPackets_list(self,packet):
    if packet in self.readed_packets_list:
      self.readed_packets_list.remove(packet) 


#  def portWrite(self,data):
#    print "portWrite executed"
#    self.usbW.write(data)

  def write(self, data):#test..
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
    time.sleep(0.02) 
    self.ser.write(data)   

    self.ser.flush()
    #while self.ser.inWaiting()<5:
    #  time.sleep(0.01)

    time.sleep(0.5)
   
   #answer=self.ser.read(self.ser.inWaiting())
   # if len(self.readed_packets_list)>0:
   #   answer=self.readed_packets_list[-1]
   # else:
    answer="answer"
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
    print "data_to_write:"+data_to_write  
 
    start_time=time.time()
    while incomingByteAfterWriteAvaible==1:
      time.sleep(0.01) 

      if (time.time()>(start_time+0.5) ):#2 #timeout to exit the loop
        print "rx after write timeout0"
        incomingByteAfterWriteAvaible=0
        return("error_reception")
    
   
    return(last_received_packet)











  def isOpen(self):
    #print " called  isOpen"
    return(self.status)

  #def open():
  #  return(1)


  def __del__(self):
    print "class arduinoserial destroyed"
 #   try:
 #     os.close(self.fd)
 #   except:
 #     print "tried to close serial port"





  def close(self):
    self.exit=1

    print "class arduinoserial destroyed by close()"
#    try:
 #     os.close(self.ser)     
  #  except:
   #   print "tried to close serial port"


