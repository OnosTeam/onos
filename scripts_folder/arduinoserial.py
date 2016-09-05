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
from globalVar import *           # import parameter globalVar.py
import thread,threading,time,string





# Map from the numbers to the termios constants (which are pretty much
# the same numbers).

BPS_SYMS = {
  4800:   termios.B4800,
  9600:   termios.B9600,
  19200:  termios.B19200,
  38400:  termios.B38400,
  57600:  termios.B57600,
  115200: termios.B115200
  }


# Indices into the termios tuple.

IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6


serial_incomingBuffer=""

def bps_to_termios_sym(bps):
  return BPS_SYMS[bps]

  
#hwNodeDict[0]=hw_node.HwNode("base","arduino_2009",0)  #make the first node , the base station  one


class SerialPort:

  def __init__(self, serialport, bps):
    """Takes the string name of the serial port
    (e.g. "/dev/tty.usbserial","COM1") and a baud rate (bps) and
    connects to that port at that speed and 8N1. Opens the port in
    fully raw mode so you can send binary data.
    """
    self.port=serialport
    self.busy=0
#the error controll is done by the arduin_handler.py     
    #self.fd = os.open(serialport, os.O_RDWR | os.O_NOCTTY | os.O_NDELAY)
    self.status=1

    self.write_to_serial_enable=1  #enable or disable the writing to the port if the port is receiving
    

    try:
      self.usbR = open(self.port, 'r' ,os.O_RDONLY | os.O_NOCTTY | os.O_NDELAY)
      self.usbW = open(self.port, 'w' ,os.O_WRONLY)

      self.status=1
    except:
      print "no device"+self.port+"found"
      self.status=0



    #except:
   #   print "serial arduino error"
   #   self.fd =""
   #   self.status=0

    #attrs = termios.tcgetattr(self.fd)
    attrsR = termios.tcgetattr(self.usbR)
    attrsW = termios.tcgetattr(self.usbW)
    bps_sym = bps_to_termios_sym(bps)
    # Set I/O speed.
    attrsR[ISPEED] = bps_sym
    attrsW[ISPEED] = bps_sym

    attrsR[OSPEED] = bps_sym
    attrsW[OSPEED] = bps_sym

    # 8N1
    attrsR[CFLAG] &= ~termios.PARENB
    attrsW[CFLAG] &= ~termios.PARENB

    attrsR[CFLAG] &= ~termios.CSTOPB
    attrsW[CFLAG] &= ~termios.CSTOPB

    attrsR[CFLAG] &= ~termios.CSIZE
    attrsW[CFLAG] &= ~termios.CSIZE

    attrsR[CFLAG] |= termios.CS8
    attrsW[CFLAG] |= termios.CS8
    # No flow control
    attrsR[CFLAG] &= ~termios.CRTSCTS
    attrsW[CFLAG] &= ~termios.CRTSCTS

    # Turn on READ & ignore contrll lines.
    attrsR[CFLAG] |= termios.CREAD | termios.CLOCAL
    attrsW[CFLAG] |= termios.CREAD | termios.CLOCAL

    # Turn off software flow control.
    attrsR[IFLAG] &= ~(termios.IXON | termios.IXOFF | termios.IXANY)
    attrsW[IFLAG] &= ~(termios.IXON | termios.IXOFF | termios.IXANY)

    # Make raw.
    attrsR[LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    attrsW[LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)


    attrsR[OFLAG] &= ~termios.OPOST
    attrsW[OFLAG] &= ~termios.OPOST

    # It's complicated--See
    # http://unixwiz.net/techtips/termios-vmin-vtime.html
    attrsR[CC][termios.VMIN] = 0;
    attrsW[CC][termios.VMIN] = 0;

    attrsR[CC][termios.VTIME] = 20;
    attrsW[CC][termios.VTIME] = 20;

    #termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
    termios.tcsetattr(self.usbR, termios.TCSANOW, attrsR)
    termios.tcsetattr(self.usbW, termios.TCSANOW, attrsW)

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










  def read_data(self):   # thread  function
      '''Outputs data from serial port to sys.stdout.'''
      print "read_data thread executed"
 
      global serial_incomingBuffer
      global waitTowriteUntilIReceive
      ignore = ''   #'\r'
      filedev=self.port
      self.dataAvaible=0

      while (self.exit==0):

          if self.exit==1:
            break
          buf=''

          done=0
          count=0
          self.write_to_serial_enable=1
    
          while done==0:
            if self.exit==1:
              break
            #if len(self.removeFromInBuffer)>0:
            #  serial_incomingBuffer.replace(self.removeFromInBuffer, "");  #remove from buffer the part just readed
            #  self.removeFromInBuffer=''
            try:
              byte = self.usbR.read(1)
            except:
              byte=-1
              self.status=0
              self.write_to_serial_enable=1
 
              continue


            if not byte:  #nothing on incoming serial buffer
              done=1
              print "end of serial packet1"
              #print "incoming buffer="+serial_incomingBuffer
              continue


            #here the buffer have received at least one byte
            self.write_to_serial_enable=0   #i diseble the write to the serial port since i'm receiving from it



          
            #    end of packet is  "_#]" 




            #if byte:  #nothing on incoming serial buffer
            #  done=1
            #  print "end of serial packet2"
            #  continue
            

            if (ord(byte)==10):  # 10 is the value for new line (\n) end of packet on incoming serial buffer  
              done=1
              print "end of serial packet len=0"
              continue
            else:   
              #print "in byte="+byte+" end of in byte"
              buf=buf+byte
              
              count=len(buf)

              if len(buf)==0:
                done=0
                continue


              if len(buf)>2:
                waitTowriteUntilIReceive=1 
                if ( (buf.find("onos_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
                  done=1
                  print "end of serial packet:_#] "
                  continue 



          #at this point i should have a full packet message
          if len(buf)>0:



           
           
            if ( (buf.find("[S_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
 
              cmd_start=buf.find("[S_")
              cmd_end=buf.find("_#]")
              cmd=buf[cmd_start:cmd_end+3]


              if( (cmd[6]=="s")&(cmd[7]=="y") ): # [S_001sy3.05ProminiS0001_#] 
                print "serial cmd="+cmd

                try:
                  serial_number=numeric_serial_number=cmd[12:24]   
                  node_fw=cmd[8:12]
                  node_address=cmd[3:6]
                  if node_address=="254":  #the node is looking for a free address
                    priorityCmdQueue.put( {"cmd":"sendNewAddressToNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 

                except Exception, e  :               
                  print "error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)  
                  errorQueue.put("error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)   )

                priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 




              if( (cmd[6]=="g")&(cmd[7]=="a") ): #  [S_001ga3.05ProminiS0001_#]
                print "serial cmd="+cmd

                try:
                  numeric_serial_number=cmd[13:25]

                  serial_number=numeric_serial_number=cmd[12:24]   

                  node_fw=cmd[8:12]
                  node_address=cmd[3:6]

                  if node_address=="254":  #the node is looking for a free address
                    priorityCmdQueue.put( {"cmd":"sendNewAddressToNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 


                  priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 



                except Exception, e  :               
                  print "error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)  
                  errorQueue.put("error receiving serial sync message cmd was :"+cmd+ "e:"+str(e.args)   )







           # print "serial input="+buf

            #with lock_serial_input:
            serial_incomingBuffer=buf
            self.dataAvaible=1 
            waitTowriteUntilIReceive=0
            time.sleep(0.18)  #important to not remove..

            timeout=time.time()
            while waitToReceiveUntilIRead==1:
              time.sleep(0.001)
              #print "i wait until you read"
              if (time.time>(timeout+10) ): #timeout to exit the loop
                break

            print "incoming buffer="+serial_incomingBuffer
            buf=""
          else: #len buf ==0
            
            self.dataAvaible=0

      os.close(self.usbR)                  
      print "serial port closed"               




  def waitForData(self,timeout):
    j=0
    self.disable_uart_queue=1  # I disable the auto queue add because I want to read the data directly
    start_time=time.time()
    while self.dataAvaible==0:
      if (time.time>(start_time+timeout) ): #timeout to exit the loop
        return(-1)
      time.sleep(0.001) 
    return(1) 
    




  def write0(self, str):
    print "i write"+str
    os.system("echo "+str+" >> "+self.port)

  
    return()  

  

  def write(self, data):
    global waitToReceiveUntilIRead
    timeout=time.time()
    while waitTowriteUntilIReceive==1 : #wait because there are half packet in serial receiving
      time.sleep(0.001)
      if (time.time>(timeout+10) ): #timeout to exit the loop
        break




    waitToReceiveUntilIRead=1
    time.sleep(0.02) 
    print "i write:"+data
    global serial_incomingBuffer
    #with open(self.port, 'w') as f:   #read the pin status

    tmp="void"
    self.usbW.write(data+'\n')
    if self.waitForData(10)==1:
      #tmp=serial_incomingBuffer
      #self.removeFromInBuffer=tmp

     # with lock_serial_input: 
      tmp=serial_incomingBuffer
      serial_incomingBuffer=""
      waitToReceiveUntilIRead=0


        
    else:
      print "rx timeout0"

    return(tmp)    







  def isOpen(self):
    #print " called  isOpen"
    return(self.status)

  #def open():
  #  return(1)


 # def __del__(self):
 #   print "class arduinoserial destroyed"
 #   try:
 #     os.close(self.fd)
 #   except:
 #     print "tried to close serial port"





  def close(self):
    self.exit=1

    print "class arduinoserial destroyed"
    try:
     
      os.close(self.usbW)     
      os.close(self.usbR)     
    except:
      print "tried to close serial port"


