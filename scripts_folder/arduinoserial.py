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

"""

..Note::

    Module not used , deprecated and to implement in the future


A port of Tod E. Kurt's arduino-serial.c.
<http://todbot.com/blog/2006/12/06/arduino-serial-c-code-to-talk-to-arduino/>



"""

import termios
import fcntl
import os
import sys
import time
import getopt
from globalVar import *           # import parameter globalVar.py
import thread,threading,time,string
import hw_node

hwNodeDict={}     #dictionary containing all the hw nodes objects   the key is the node address



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
    self.fd = os.open(serialport, os.O_RDWR | os.O_NOCTTY | os.O_NDELAY)
    self.status=1



    #except:
   #   print "serial arduino error"
   #   self.fd =""
   #   self.status=0

    attrs = termios.tcgetattr(self.fd)
    bps_sym = bps_to_termios_sym(bps)
    # Set I/O speed.
    attrs[ISPEED] = bps_sym
    attrs[OSPEED] = bps_sym

    # 8N1
    attrs[CFLAG] &= ~termios.PARENB
    attrs[CFLAG] &= ~termios.CSTOPB
    attrs[CFLAG] &= ~termios.CSIZE
    attrs[CFLAG] |= termios.CS8
    # No flow control
    attrs[CFLAG] &= ~termios.CRTSCTS

    # Turn on READ & ignore contrll lines.
    attrs[CFLAG] |= termios.CREAD | termios.CLOCAL
    # Turn off software flow control.
    attrs[IFLAG] &= ~(termios.IXON | termios.IXOFF | termios.IXANY)

    # Make raw.
    attrs[LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    attrs[OFLAG] &= ~termios.OPOST

    # It's complicated--See
    # http://unixwiz.net/techtips/termios-vmin-vtime.html
    attrs[CC][termios.VMIN] = 0;
    attrs[CC][termios.VTIME] = 20;
    termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
    os.system("cat "+self.port)
    self.usb=""
    #n = os.read(self.fd)


    
    self.incomingBuffer=''
    self.removeFromInBuffer=''
    try:
      self.usb = open(self.port, 'rw')
      self.status=1
    except:
      print "no device"+self.port+"found"
      self.status=0
    
    self.dataAvaible=0
    self.t_read = threading.Thread(target=self.read_data)
    self.t_read.daemon = True  #make the thread a daemon thread
    self.t_read.start()
    self.exit=0





  def read_data(self):   # thread  function
      '''Outputs data from serial port to sys.stdout.'''
      print "read_data thread executed"
      ignore = ''   #'\r'
      filedev=self.port
      self.dataAvaible=0
      
      while (self.exit==0):

          if self.exit==1:
            break
          tmpRm=self.removeFromInBuffer
          buf=''
          if len(tmpRm)>0:
            self.incomingBuffer.replace(tmpRm, "");  #remove from buffer the part just readed
            self.removeFromInBuffer=''
          buf=''
          done=0
          while done==0:
            if self.exit==1:
              break
            try:
              byte = self.usb.read(1)
            except:
              byte=-1
              self.status=0
              continue
          

            if byte in ignore:
              continue

            if not byte:  #nothing on incoming serial buffer
              done=1
              print "end of serial packet"

            if (ord(byte)==10):  # 10 is the value for new line (\n) end of packet on incoming serial buffer  
              done=1
              print "end of serial packet len=0"
            else:   
              #print "in byte="+byte+" end of in byte"
              buf=buf+byte
          #at this point i should have a full packet message
          if len(buf)>0:

            #a=bin(a)

            if len(buf)>5:

              if (buf[0]=='U')&(buf[2]=='r'):    #arduino is sending a digital status pins byte
                received_node_address=buf[1]
                section_index=buf[3]
                data_register=buf[4]
                rx_check_byte=buf[5]
                check_byte=checksum(('U',received_node_address,'r',section_index,data_register))
                if check_byte==rx_check_byte:
                  print "check ok"



                answer_byte='U'+node_address+'C'+check_byte
                self.write(answer_byte)  #send the check byte



            if len(buf)>4:

              if (buf[0]=='U')&(buf[2]=='q'):    #arduino is asking for pins mode configuration (input or output)
                received_node_address=buf[1]
                hw_type=buf[3]
                rx_check_byte=buf[4]

                if received_node_address in hwNodeDict:  # a node with that address exist yet
                  pin_mode_list=hwNodeDict[received_node_address].getNodeSectionMode()
                  k=0
                  for a in pin_mode_list:   #for each section of the pin mode list send it to arduino
                    check_byte=checksum(('U',received_node_address,'m',k,a))
                    self.write('U'+received_node_address+'m'+k+a+check_byte)
                    k=k+1
                else: # address not in the dictionary
                  if hw_type==0:
                    hw_type="arduino_2009"
                  if hw_type==1:
                    hw_type="arduino_promini"
                  #a=hw_node.HwNode('new_node'+received_node_address,hw_type,received_node_address)
                  #hwNodeDict[received_node_address]=a
                  #banana insert here a url query to create the node
                  pin_mode_list=hwNodeDict[received_node_address].getNodeSectionMode()
                  k=0
                  for b in pin_mode_list:   #for each section of the pin mode list send it to arduino
                    check_byte=checksum(('U',received_node_address,'m',k,b))
                    self.write('U'+received_node_address+'m'+k+b+check_byte)
                    k=k+1
                check_byte=checksum(('U',received_node_address,'f')) #tell arduino that the pins configuration is ended 
                self.write('U'+received_node_address+'f'+check_byte)
     
                  
              #self.write(byte)  send the configuration
              #self.write('\n')


            self.dataAvaible=1
            print "serial input="+buf
            self.incomingBuffer=self.incomingBuffer+buf
            print "incoming buffer="+self.incomingBuffer
          else:
            self.dataAvaible=0


  def waitForData(self,times):
    j=0
    while j<(times*1000000):
      if (self.dataAvaible==1):
        return(1)
      if (self.exit==1):
        return(-1)
      
      j=j+0.1
    return(-1) 
    



  def read(self):
    print "arduinoserial read executed"
    #buf = ""
    #buf=os.popen("cat < "+self.port).read()
    
    tmp=self.incomingBuffer
    self.removeFromInBuffer=self.removeFromInBuffer+tmp
    self.incomingBuffer=''
    print "readed serial port="+tmp
    return tmp



  def sendDigitalWrite(self,node_address,pin,status):
    # tells arduino to write  the register pins as readed from the hw_node class where the status of the pin is modified
    # according the parameter passed to sendDigitalWrite()
    if node_address in hwNodeDict.keys():
      hwNodeDict[node_address].setDigitalPinOutputStatus(pin,status)  #set the pin status in the class according to the parameter received
      section=pin//8
      section_pins_status=str(hwNodeDict[node_address].getNodeSectionStatusByPin(pin))
      msg="U0s"+str(section)+section_pins_status+'0'
      print "writing register to arduino pin"

      while (rx_check_byte!=check_byte):
        print ("wait for correct answer to dw")
        os.system("echo "+msg+" >> "+self.port) #write the message
        os.system("echo \n >> "+self.port)      #write the closing message byte    \n
        self.waitForData(10)
        rx_check_byte=self.read()
    else:
      print "error address node not in node dictionary" 
    return    

  def write(self, str):

    if str[0:2]=="dw":    #if the cmd is to set arduino pins...then make sure arduino answer ok
      print "writing to arduino pin"
      #check_byte=checksum(str2....)
      while (rx_check_byte!=check_byte):
        print ("wait for correct answer to dw")
        os.system("echo "+str+" >> "+self.port)
        os.system("echo \n >> "+self.port)
        self.waitForData(10)
        rx_check_byte=self.read()
      return    


    if (str[0]=='U')&(str[2]=='m'):    #if the cmd is to change pin mode of arduino...then make sure arduino answer ok
      print "writing  pin configuration to arduino"
      #check_byte=checksum(str2....)
      rx_check_byte=0
      j=0
      while (rx_check_byte!=check_byte)&(j<15):
        j=j+1
        os.system("echo "+str+" >> "+self.port)
        os.system("echo \n >> "+self.port)
        self.waitForData(10)
        rx_message=self.read()
        rx_check_byte=rx_message[3]  
      return  


    if (str[0]=='U')&(str[2]=='f'):    #if the cmd is to write end of the change pin mode of arduino...then make sure arduino answer ok
      print "writing  pin configuration to arduino"
      #check_byte=checksum(str2....)
      rx_check_byte=0
      j=0
      while (rx_check_byte!=check_byte)&(j<15):
        j=j+1
        os.system("echo "+str+" >> "+self.port)
        os.system("echo \n >> "+self.port)
        self.waitForData(10)
        rx_message=self.read()
        rx_check_byte=rx_message[3]  
      return    
    


     #os.write(self.fd, str)
#    while self.busy==1:
#      time.sleep(0.01)
#    self.busy=1
    #os.system("echo "+str+" >> "+self.port)
    #self.busy=0
    return



  def digitalWriteSection(self,node_address,section,section_status):
    print "i write a section status to arduino"
    
 

 # def write_byte(self, byte):
 #   os.write(self.fd, chr(byte))

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


  def make_new_node(self,node_name,hwType,node_address):  
    if node_address not in hwNodeDict:
      hwNodeDict[node_address]=hw_node.HwNode(node_name,hwType,node_address)
      return(1)
    else:
      print "address already used"
      return(-1)



  def setPinMode(self,node_address,pinNumber,mode):
    if node_address in hwNodeDict:
      hwNodeDict[node_address].setPinMode(pinNumber,mode)  #set the pin mode in the hardware_node
      self.sendPinModeToArduino() # to implement

    else:
      print "error node address not found in the dictionary"
      return (-1)      









  def close(self):
    self.exit=1

    print "class arduinoserial destroyed"
    try:
      os.close(self.fd)
    except:
      print "tried to close serial port"


