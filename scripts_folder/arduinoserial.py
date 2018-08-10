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
#ser.timeout = None                    #block read
        self.ser.timeout = 1                        #non-block read
#ser.timeout = 2                            #timeout block read
        self.ser.xonxoff = False         #disable software flow control
        self.ser.rtscts = False         #disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False             #disable hardware (DSR/DTR) flo
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

        self.removeFromInBuffer=''
        self.dataAvaible=0
        self.t_read = threading.Thread(target=self.read_data)
        self.t_read.daemon = True    #make the thread a daemon thread
        self.t_read.start()
        self.exit=0
        self.ser.open()
        self.port_was_opened=0


    def read_data(self):     # thread    function
        '''Outputs data from serial port to sys.stdout.'''
    
        logprint("read_data thread executed")
        ignore = ''     #'\r'
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

            self.port_was_opened=1
            buf=''
            next_buf=''
            while (self.exit==0):
                if self.ser.inWaiting()<1:     #skip if there is no incoming data
                    time.sleep(0.01) 
                    continue
                else: 
##################################################################
                    byte = ''
                    buf = next_buf
                    next_buf = ''

                    try:
                        buf = buf + self.ser.read(self.ser.inWaiting())     #    self.usbR.read(1)
                        #print byte
                    except Exception as e    :
                        message="error in self.ser.read(self.ser.inWaiting()) "
                        if (str(e.args) ).find("readiness")!=-1:     # if the error is :device reports readiness to read but returned no data is lower priority 
                            verbose=5
                        elif((str(e.args) ).find("temporarily")!=-1):
                            verbose=5
                        else:
                            verbose=8
                        logprint(message,verbose,error_tuple=(e,sys.exc_info()))    
                        continue


                    if len(buf)>5:

                        if ( (buf.find("[S_")!=-1)&(buf.find("_#]")!=-1) ): #there is a full onos command packet
                            logprint("end of serial packet:_#] ")
                            break 

                    #if (buf.find("\n")!=-1):
                    #    print ("end of line received but no onoscmd found")
                    #    break

                    #if len(buf)>0:     
                    #    logprint(buf) 

##################################################################
                #at this point i should have a full packet message
            if len(buf)>5:

                buf=buf.replace("\n", "")    #to remove \n
                buf=buf.replace("\r", "")    #to remove \r
                buf=buf.replace("\x00", "")    #to remove \n
                cmd_start=buf.find("[S_")
                cmd_end=buf.find("_#]",cmd_start) #serch the end of the packet ..starting from the "[S_"
                cmd='' 
                if ( (cmd_start!=-1)&(cmd_end!=-1)): #there is a full onos command packet
                    #time.sleep(1) #todo remove,justfordebug
                    cmd=buf[cmd_start:cmd_end+3]
                    next_buf=buf[cmd_end+3:]
                    buf=''                            
                    logprint("232PacketInput:"+cmd) # +"cmd[3]cmd[4]="+cmd[3]+cmd[4])


                    if( (cmd[3]=="o")&(cmd[4]=="k") ): # [S_okd061x_#]    i received a confirm from the node
                        serial_answer_readyQueue.put(cmd)    
                        #with lock_serial_input:                            
                        self.readed_packets_list.append(cmd)
                        buf=""
                        #self.dataAvaible=1 
                        continue
    
                    elif(cmd[5] == "g"):
                    # [S_01g05ProminiS0001x_#]
                        logprint("232Rxg=" + cmd)
                        try:
                            serial_number = cmd[8:20]
                            node_address = '%03d' %(int(cmd[3:5], 16) )    # get the address in decimal format,example:get "010" from the hexadecimal "0a"    
                                                                           # the '%03d' %    will fill with '0' the left part.. 2 will become a string ='002'
                            node_fw = '%03d' %(int(cmd[6:8], 16) ) # "df0"    #default    

                            if node_address == "254":    #the node is looking for a free address
                                logprint("node_fw=" + node_fw)
                                priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired", "nodeSn":serial_number, "nodeAddress":node_address, "nodeFw":node_fw}) 
                                continue
    
                        except Exception as e    :                             
                            message="errorRx232 g_sync msg was:" + cmd
                            logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))    
    
                        #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 
                        continue
    
    
                    elif(cmd[5] == "u" ):
                        #[S_01uWreedSaa000132Lgx_#]

                        logprint("232Rxu=" + cmd[0:18]+"+bin part")
                        try:
                            serial_number = cmd[6:18]
                            node_address = '%03d' %(int(cmd[3:5], 16) )    # get the address in decimal format,example:get "010" from the hexadecimal "0a"    
                                                                         # the '%03d' %    will fill with '0' the left part.. 2 will become a string ='002'
                            node_fw = "df0"    #default    
                            node_type = cmd[6:14]     #get WreedSaa from    [S_01uWreedSaa000132Lgx_#]
                            
                            if node_type == "WreedSaa":    # if the node is a reed node
                                reeds_status=cmd[18]
                                logprint("reeds status received:"+reeds_status) 
                                reed1_status=(reeds_status=="2")or(reeds_status=="3") #get boolean result
                                reed2_status=(reeds_status=="1")or(reeds_status=="3") #get boolean result
                                tempSensor= ord(cmd[19])-1             #-1 is because on the micro side i added 1 to the value to avoid the 0 binary..
                                luminosity_sensor= ord(cmd[20])-1 #-1 is because on the micro side i added 1 to the value to avoid the 0 binary..
                                battery_state= ord(cmd[21])-1 #-1 is because on the micro side i added 1 to the value to avoid the 0 binary..
                                objects_to_update_dict={0:reed1_status,5:reed2_status,3:tempSensor,10:luminosity_sensor,9:battery_state}
                                #obj_address_to_update=0
                                priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":objects_to_update_dict }) 
                                if node_address=="254":    #the node is looking for a free address
                                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 
                                    continue
    
    
                            elif node_type == "Wrelay4x":
                                #    [S_01uWrelay4x00010011x_#]

                                relay0_status=cmd[18]
                                relay1_status=cmd[19]
                                relay2_status=cmd[20]
                                relay3_status=cmd[21]
    
                                objects_to_update_dict={0:relay0_status,1:relay1_status,2:relay2_status,3:relay3_status}
                                #obj_address_to_update=0
                                priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":objects_to_update_dict }) 
                                if node_address=="254":    #the node is looking for a free address
                                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 
                                    continue

    
                            elif node_type == "WPlug1vx":
                                #    [S_01uWPlug1vx00091x_#]
    
                                relay0_status=cmd[18]
    
                                objects_to_update_dict={0:relay0_status}
                                #obj_address_to_update=0
                                priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":objects_to_update_dict }) 
                                if node_address=="254":    #the node is looking for a free address
                                    priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 
                                    continue
    
    
                        except Exception as e:                             
                            message="errorRx232 u_sync msg was:" + cmd
                            logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))    
                            #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw }
                            continue
    
    
    
                    else:    # a messege is received but is not started from a node, probably is an answer
                        if( (cmd[3]=="n")&(cmd[4]=="o") )or (cmd[3]=="e")&(cmd[4]=="r") : #[S_nocmd1_#][S_nocmd2_#][S_ertx1_#][S_er0_status_#]er_ac_status_#]er_ac_obj_number_#]er_dc_obj_number_#]er_do_status_#]er1_sn er2_sn_#]
                            self.readed_packets_list.append(cmd)
                            buf=""
                            serial_answer_readyQueue.put(cmd)    
                            continue    
                    #print "serial input="+buf
                    #with lock_serial_input:                            
    
                    self.readed_packets_list.append(cmd)
                    self.dataAvaible=1 
                    logprint("incoming buffer="+cmd)
                else: # msg received has not start or stop markers
                    tmp_buf=buf.decode("utf8","replace")
                    tmp_buf.encode("ascii","replace")
                    logprint("incoming buffer="+tmp_buf)
                    self.dataAvaible=0
                    serial_answer_readyQueue.put(tmp_buf)

        logprint("serial port closed")                             
        return()



    def waitForData(self,timeout):    #deprecated
        j=0
        self.disable_uart_queue=1    # I disable the auto queue add because I want to read the data directly
        start_time=time.time()
        while self.dataAvaible==0:
            if (time.time()>(start_time+timeout) ): #timeout to exit the loop
                return(-1)
            time.sleep(0.001) 
        return(1) 


    def removeFromPackets_list(self,packet):
        with lock_serial_input:    
            if packet in self.readed_packets_list:
                self.readed_packets_list.remove(packet) 


#    def portWrite(self,data):
#        print "portWrite executed"
#        self.usbW.write(data)

    def write(self, data):#test..


        startTime=time.time()
        serial_answer_readyQueue.queue.clear() # empty the queue before using it
        logprint("serial write executed with:"+data)

        #self.ser.flushOutput()
        self.ser.flush()
        self.ser.write(data)     
        self.ser.flush()
        logprint("time spent writing:"+str(time.time()-startTime)) 

        rx_after_tx_timeout=time.time()+3    #0.7

        while serial_answer_readyQueue.empty():
            if rx_after_tx_timeout<time.time():
                logprint("I exit the loop    serial write because of timeout,the message I wanted to send was:"+data,verbose=6)
                logprint("time spent:"+str(time.time()-startTime)) 
                return("void") 
        
        answer=serial_answer_readyQueue.get()
        logprint ("i exit the loop because i received a message after I have write one")
        logprint("time spent:"+str(time.time()-startTime))

        return(answer)






    def isOpen(self):
        #print " called    isOpen"
        return(self.status)

    #def open():
    #    return(1)


    def __del__(self):
        logprint("class arduinoserial destroyed")
        self.exit=1
        #layerExchangeDataQueue.put( {"cmd":"set_serialCommunicationIsWorking=0"}) 
        if self.port_was_opened==1:
            layerExchangeDataQueue.put( {"cmd":"reconnectSerialPort"}) 
            self.port_was_opened=0
        return()

 #     try:
 #         os.close(self.fd)
 #     except:
 #         print "tried to close serial port"





    def close(self):
        self.exit=1
        logprint("class arduinoserial destroyed by close()")
#        try:
 #         os.close(self.ser)         
    #    except:
     #     print "tried to close serial port"


