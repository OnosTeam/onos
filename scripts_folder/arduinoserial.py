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
#from globalVar import *           # import parameter globalVar.py
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
    self.write_to_serial_enable=1  #enable or disable the writing to the port if the port is receiving


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
    #os.system("cat "+self.port)
    self.usb=""
    #n = os.read(self.fd)


    
    self.incomingBuffer=''
    self.removeFromInBuffer=''
    try:
      self.usbR = open(self.port, 'rw')
      self.usbW = open(self.port, 'w')
      self.status=1
    except:
      print "no device"+self.port+"found"
      self.status=0
    
    self.dataAvaible=0
    self.t_read = threading.Thread(target=self.read_data)
    self.t_read.daemon = True  #make the thread a daemon thread
    self.t_read.start()
    self.exit=0





  def read_data0(self):   # read  function

    timeout=1
    old_time=time.time()
    done=0
    count=0
    buf=""
    while done==0:
      if (time.time()-old_time)>timeout:
        done=1 
        print "timeout"  
        return(-1)  #timeout
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




      if (ord(byte)==10):  # 10 is the value for new line (\n) end of packet on incoming serial buffer  
        done=1
        print "end of serial packet len=0"
      else:   
        #print "in byte="+byte+" end of in byte"
        buf=buf+byte
        if len(buf)==0:
          done=0
          continue


        count=count+1
          #at this point i should have a full packet message


      if len(buf)>0:
            
        if ( (buf.find("onos_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
 
          cmd_start=buf.find("onos_")
          cmd_end=buf.find("_#]")
          cmd=buf[cmd_start:cmd_end+3]
          done=1
 
      if len(buf)>3:

        if ( (byte[count-2]=='_')and(byte[count-1]=='#')and(byte[count]==']') ):
          done=1
          print "end of serial packet:_#] " 


        self.dataAvaible=1
        print "serial input="+buf
        self.incomingBuffer=self.incomingBuffer+buf
        print "incoming buffer="+self.incomingBuffer
      else:
        self.dataAvaible=0

    return(buf)  





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
          count=0
          self.write_to_serial_enable=1
          while done==0:
            if self.exit==1:
              break
            try:
              byte = self.usbR.read(1)
            except:
              byte=-1
              self.status=0
              self.write_to_serial_enable=1
 
              continue


            #here the buffer have received at least one byte
            self.write_to_serial_enable=0   #i diseble the write to the serial port since i'm receiving from it



          
            #    end of packet is  "_#]" 


            if not byte:  #nothing on incoming serial buffer
              done=1
              print "end of serial packet1"
              continue

            #if byte:  #nothing on incoming serial buffer
            #  done=1
            #  print "end of serial packet2"
            #  continue
            

            if (ord(byte)==10):  # 10 is the value for new line (\n) end of packet on incoming serial buffer  
              done=1
              print "end of serial packet len=0"
            else:   
              #print "in byte="+byte+" end of in byte"
              buf=buf+byte
              count=len(buf)

              if len(buf)==0:
                done=0
                continue


              if len(buf)>1:
                if ( (buf[count-2]=='_')and(buf[count-1]=='#')and(buf[count-1]==']') ):
                  done=1
                  print "end of serial packet:_#] "
                  continue 



          #at this point i should have a full packet message
          if len(buf)>0:
            




            if ( (buf.find("onos_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
 
              cmd_start=buf.find("onos_")
              cmd_end=buf.find("_#]")
              cmd=buf[cmd_start:cmd_end+3]
              done=1

              #onos_s3.05v1s0001f001_#]
              if (cmd[5]=="s"): #sync message
                numeric_serial_number=cmd[13:17]
                full_sn=nodeNumericSerialTofullSerial[numeric_serial_number]
                node_fw=cmd[6:10]
                node_current_address=cmd[18:21]
                message_to_send="onos_ssyncv1s"+numeric_serial_number+"f"+node_current_address+"_#]"
                if node_current_address=="254":  #the node is looking for a free address
                  new_address=getNextFreeAdress(full_sn)
                  message_to_send="onos_g"+new_address+"v1s"+numeric_serial_number+"f"+node_current_address+"_#]"
                priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":full_sn,"nodeFw":node_fw}) 


              #onos_g3.05v1s0001f001_#]
              if (cmd[5]=="g"):
                numeric_serial_number=cmd[13:17]
                full_sn=nodeNumericSerialTofullSerial[numeric_serial_number]
                node_fw=cmd[6:10]
                node_current_address=cmd[18:21]
                new_address=getNextFreeAdress(full_sn)
                message_to_send="onos_g"+new_address+"v1s"+numeric_serial_number+"f"+node_current_address+"_#]"
                priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":full_sn,"nodeAdress":new_address,"nodeFw":node_fw}) 

                self.write(message_to_send)







            self.dataAvaible=1
            print "serial input="+buf
            self.incomingBuffer=self.incomingBuffer+buf
            print "incoming buffer="+self.incomingBuffer
          else:
            self.dataAvaible=0


  def waitForData(self,times):
    j=0
    self.disable_uart_queue=1  # I disable the auto queue add because I want to read the data directly
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
    self.disable_uart_queue=0           # after the read of the data I reenable the auto queue of the incoming uart data
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


      rx_check_byte=0
      check_byte=-1
      while (rx_check_byte!=check_byte):
        print ("wait for correct answer to dw")
        os.system("echo "+msg+" >> "+self.port) #write the message
        os.system("echo \n >> "+self.port)      #write the closing message byte    \n
        self.waitForData(10)
        rx_check_byte=self.read()
    else:
      print "error address node not in node dictionary" 
    return    




  def write0(self, str):
    print "i write"+str
    os.system("echo "+str+" >> "+self.port)

  
    return()  

  

  def write(self, data):
    print "i write:"+data
    #with open(self.port, 'w') as f:   #read the pin status
    self.usbW.write(data+"\n")
    self.waitForData(10)

    tmp=self.incomingBuffer
    self.removeFromInBuffer=tmp


    return(tmp)    





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





  def close(self):
    self.exit=1

    print "class arduinoserial destroyed"
    try:
      os.close(self.fd)
      os.close(self.usbW)     
      os.close(self.usbR)     
    except:
      print "tried to close serial port"


