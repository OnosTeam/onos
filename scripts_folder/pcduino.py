# -*- coding: UTF-8 -*-
# per creare l'oggetto si fa  nomeoggetto=pyduino.Pyduino()

#pcduino 2.3

"""

.. warning::

    Never used

This module will interface with an arduino over serial port
         
"""

import arduinoserial
import os
import thread,threading,time,string
from globalVar import *           # import parameter globalVar.py
import urllib2


#old comment not valid anymore...
#for each comunication arduino has to send, arduino will respond with a series of char making "the message", 
#followed by a char that is the sum of all the single char value of the message,
# (if is more than 255 it will sotract n times 255 to the number in order to make it < 255)
#after this control char the arduino will send a '/n' char  that define the end of the message.
#the pc check if the sum of every char received (less the control char and the end of message char)
#are equal to the control char received and then if so respond with the control char.
#otherwise it respond '?' and the arduino will try to send again the message (max 10 times)
#if the pc want to set an arduino pin to a digital status its write 'dw131'+ch  where ch is the control byte.
#the arduino set the pin and then write back to the pc 'dw'+ch+';'+'/n' where ch is the control byte of the received message 
  

pcduino_exit=0
pcduinoTread=1


HIGH=1
LOW=0
ser=0
class Pcduino:
    __baudrate=115200
    __connected=0
    __maxPin=13
    analog1=0
    done=0
    statusInterrupt=0



    def __init__(self):
      
      done=0
      self.object_dict={}
      self.watchPinDict={}  #list of pin to read from the arduino...the keys are the number of pin , the values are the values of the pins
      
      self.buffer=''
      self.write_buffer=''
      self.ser=0
      self.a="a"
      self.__connected=0
      self.readEnable=1
      #self.t0 = threading.Thread(target=self.readSerialThread)
      #self.t0.start()
      self.wait=0
      #self.waitForThread=0

      #thread.start_new_thread(self.readSerialThread,())  
      #print "a="+self.a
      try:

        port=os.popen("ls /dev/ | grep ttyUSB0").read()   #work only if there is only ttyUSB port
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyUSB1").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyUSB2").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyUSB3").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyUSB").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyACM0").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyACM1").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyACM2").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyACM3").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep ttyACM").read()
        old_port=port[0:len(port)-1] 
        port='/dev/'+port[0:len(port)-1]   #remove /n of ls
      
        self.ser =arduinoserial.SerialPort(port, 115200)

        self.__connected=1
        self.a="b"
        #print "a="+self.a
        print 'connection with arduino successful '
      except:
        print 'error in init arduino is not connected to this port , i will try another USB port  '
        port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyUSB0").read()   #work only if there is only ttyUSB port
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyUSB1").read() 
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep -v  | grep ttyUSB2").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyUSB3").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyUSB").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyACM0").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyACM1").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyACM2").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyACM3").read()
        if len (port)<3:
          port=os.popen("ls /dev/ | grep -v "+old_port+" | grep ttyACM").read()

        #port=port[0:len(port)-1]   #remove /n of ls
         #port=string.replace(port,'/n','')
        port='/dev/'+port[0:len(port)-1] 
        #port='/dev/'+port
        print "i try'"+port+"'"
        try:
          self.ser =arduinoserial.SerialPort(port, 115200)

          self.a="c"
          print "a="+self.a

          self.__connected=1 
          print 'connection with arduino successful '
          #print self.ser.isOpen()
        except:
          print 'error arduino is not connected , please connect arduino and retry  '
          self.__connected=0       
       #self.ser = serial.Serial(0)       ls /dev/| grep -v USB1| grep USB

       
      print "a="+self.a
       




    def __del__(self): 
      print "closing pcduino"
      global pcduino_exit
      exit=1
      pcduino_exit=1
      self.ser.close()
      print "pcduino class destroyed"
      
    def end(self):
        print "closing pcduino end()"
        global pcduino_exit
        pcduino_exit=1        
        self.ser.close()

         


    def change_baudrate(self,baud):
        try:
          self.__baudrate=baud
          self.ser.baudrate =self.__baudrate
          print 'baudrate changed to '+str(self.__baudrate)
        except:
          print ' '



        

    def getMaxPin(self):
        return (self.__maxPin)



    def print_baudrate(self):
        return(self.__baudrate)



        
          
         
    def  get_statusInterrupt(self):
      if self.statusInterrupt == "0":
        return(0)
      if self.statusInterrupt == "1":
        return(1)
 
      return(-1)






    def getCheck(self,message):  #will be changed to crc8  check
      print "getCheck executed"
      total=0
      for i in message:
        total=total+ord(i)
      if total>250:
        total=divmod(total,250)[1]  #give the rest from the division between  total and 250
      total=str(total)
      
      print "check ="+str(total)

      return (total)





    def digitalRead(self,pinNumber,object_dict1):
      if self.readEnable==0:
        return (-1)
      self.object_dict=object_dict1
      print "digital read"
      if self.ser.isOpen() : 
        print "connection ok"
      else:     
        print "cannot read digital pin because arduino is not connected, please connect it and retry"
        self.__init__()
        #self.connect()
        return(-1)
      
      if ((pinNumber >self.__maxPin)or (pinNumber<0)):
        print 'error the  pin value is out of range ,use a value from 0 to 13 for arduino2009 or a value from 0 to 52 for arduino mega'
        return()
     
      if pinNumber < 10:
        cmd_pin_read='dr'+'0'+str(pinNumber)
      else:
        cmd_pin_read='dr'+str(pinNumber)        

      l1='a'
      print "try to read pin "+str(pinNumber)      
      if self.ser.isOpen():
        #self.buffer=''  #void rx buffer before to ask data     
        #self.ser.write(cmd_pin_read)
        self.ser.write(cmd_pin_read)
        self.ser.waitForData(50)#wait for incoming data
        l1=self.ser.read() 
        if (l1!='')&(len(l1)>0):
          self.buffer=l1

        i=0   
        while  (pcduino_exit==0)&(i<5)&(self.__connected==1 ):  
          i=i+1
          if (self.buffer=='onos_error') :
            return(-1)
          if (exit==1) :
            return(-1)


          if (len (self.buffer))>0:
            print "input buffer="+self.buffer
            tmp=self.buffer
            self.buffer=''
            pos=string.find(tmp,cmd_pin_read)
            if pos!=-1:  #cmdpin find in serial input buffer
              print "pin status found in input buffer"
              try: 
                pinStatus=tmp[pos+len(cmd_pin_read):pos+len(cmd_pin_read)+1]#read the next char after cmd_pin_read
                if pinStatus=='0':
                  print "pin=0"
                  return(0)      
                if pinStatus=='1':
                  print "pin=1"
                  return(1)      
              except:
                print "not able to read pin status" 

          self.ser.write(cmd_pin_read)
          self.ser.waitForData(50)#wait for incoming data
          l1=self.ser.read() 
          if (l1!='')&(len(l1)>0):
            self.buffer=l1

          #time.sleep(0.1)
    
        

    def updateObjectDict(self,object_dict1):
      self.object_dict=object_dict1

   

    def addPinToCheck(self,pin,typeOfPin):  
      if ((pinNumber >self.__maxPin)or (pinNumber<0)):
        print 'error the  pin value is out of range ,use a value from 0 to 13 for arduino2009 or a value from 0 to 52 for arduino mega'
        return()

      
      self.watchPinDict[pin]=-1   #fill the dictionary with a  new pin for arduino to watching


      if typeOfPin=="digital":
        if pin < 10:
          cmd_pin_check='dc'+'0'+str(pin)
        else:
          cmd_pin_check='dc'+str(pin)            

      if typeOfPin=="analog":
        if pin < 10:
          cmd_pin_check='ac'+'0'+str(pin)
        else:
          cmd_pin_check='ac'+str(pin)     


       #implement the part where the arduino is told to check for a change on the pin status




    def digitalReadPins(self,pinNumber,object_dict1):  #this method is a thread that contantly wait for data from arduino..
      listOfPinStatus=[]

      
      while pcduino_exit==0:
        if self.readEnable==0:
          time.sleep(0.01)
          continue
        tmpObject_dict=self.object_dict
        print "digital read all the pin setted as input"
        try: 
          b=self.ser.isOpen()
        except:     
          print "cannot read digital pin because arduino is not connected, please connect it and retry"
        #self.connect()
          continue
      #self.ser.write(cmd_pin_read)

        self.ser.waitForData(1000)#wait for incoming data
        r1=self.ser.read() 
        if (r1!='')&(len(r1)>0):
          self.buffer=r1
        else:
          self.ser.write("c??")  # ask arduino if is alive
          continue

        checkByte=self.buffer[-2] #byte for check the comunication error  is the second last of the packet..

        if (self.getCheck(self.buffer[pos:pos+len(cmd_pin_read)+3]))==checkByte: #packet received correctly
          print "received a packet fro arduino:"+self.buffer
        else:
          print "error receiving a packet from arduino"
          self.ser.write("r??")  # ask arduino to resend the packet
          continue

        for b in tmpObject_dict.keys():  # iterate every object 
          a=tmpObject_dict[b]
          pinNumber=a.getAttachedPin()
          if (a.getType()=="d_sensor")&(pin!=9999):
            pinNumber=str(pinNumber)
            if len(pinNumber)<2:
              pinNumber='0'+pinNumber
            cmd_pin_read='dr'+pinNumber
            pos=string.find(self.buffer,cmd_pin_read)
            if pos!=-1 :  # found dr+pinnumber in reading buffer 
              pinStatus=tmp[pos+len(cmd_pin_read):pos+len(cmd_pin_read)+1]#read the next char after cmd_pin_read           
              urllib2.urlopen('http://localhost/onos_cmd==setSts_'+b+'=='+pinStatus+'_')  #tell the webserver to set the webobj according to the pin status received from arduino

             
              
               









 

    def digitalWrite(self,hw_node_address,pinNumber,status):
      self.readEnable=0
      try: 
        self.ser.isOpen()
      except:     
        print "cannot write digital pin because arduino is not connected  (error self.ser.isOpen()), please connect it and retry"
        #self.connect()
        self.__init__()
        return(-1)
      
      if ((pinNumber >self.__maxPin)or (pinNumber<0)):
        print 'error the  pin value is out of range ,use a value from 0 to 13 for arduino2009 or a value from 0 to 52 for arduino mega'
        return()
   
         
      if ((status!=0)and(status!=1)):
        print 'error the  digital value is out of range ,use 0 or 1 to set the pin'
        return()
      
      #self.buffer=''  #void rx buffer before to ask data
     
      if 1==1:
        self.wait=1
        #self.ser.write('dw'+str(pinNumber)+str(status))        
        #self.write_buffer=self.write_buffer+'dw'+str(pinNumber)+str(status)
        pinNumber=str(pinNumber)
        if len(pinNumber)<2:
         pinNumber='0'+pinNumber
        ch='0'
        
        ch=self.getCheck('dw'+pinNumber+str(status))
        cmd='dw'+pinNumber+str(status)+ch


        trycount=0
        self.buffer=''
        self.ser.write(cmd)
        self.ser.waitForData(50)#wait for incoming data
        l1=self.ser.read() 
        if (l1!='')&(len(l1)>0):
          self.buffer=l1

        while trycount<10:
          print "pcduino try to write to serial port dw with cmd="+cmd

          
          if (string.find(self.buffer,'dw'+pinNumber)!=-1):
            print "wrote ok"
            print "buffer="+self.buffer
            self.readEnable=1
            return(1)  #write corfimed
          trycount=trycount+1
          print "no dw found ,buffer="+self.buffer
          self.buffer=''
          self.ser.write(cmd)          
          l1=self.ser.read() 
          self.ser.waitForData(50)#wait for incoming data          
          if (l1!='')&(len(l1)>0):
            self.buffer=self.buffer+l1
          #time.sleep(0.01)

        
        self.wait=0
        self.readEnable=1
        return(-1)
      else:#except:
        #self.connect()
        print ('error arduino is not connected , please connect arduino')
        self.wait=0
        self.readEnable=1
        return(-1)  
          
        

     
  
    def analogRead(self,pinNumber):

      try: 
        self.ser.isOpen()
      except:     
        #self.connect()
        print "cannot read digital pin because arduino is not connected, please connect it and retry"
        return(-1)	

      if ((pinNumber >self.__maxPin)or (pinNumber<0)):
        print 'error the  pin value is out of range ,use a value from 0 to 13 for arduino2009 or a value from 0 to 52 for arduino mega'
        return()
      l2='a'
      if self.ser.isOpen():
        while self.ser.read()!='a':

          if pinNumber < 10:
            self.ser.write('ar'+'0'+str(pinNumber))
          else:
            self.ser.write('ar'+str(pinNumber))   
#fine while
        self.done=0
        while (self.done==0):
          try:
            l2=0+1000*int(self.ser.read()) 
            l2=l2+100*int(self.ser.read()) 
            l2=l2+10*int(self.ser.read()) 
            l2=l2+1*int(self.ser.read())  
            self.done=1
          except:
            self.done=0 

            if pinNumber < 10:
              self.write_buffer='ar'+'0'+str(pinNumber)
            else:
              self.write_buffer='ar'+str(pinNumber)  



               
        print l2
        self.buffer=''  #void rx buffer before to ask data
        return(l2)
      else:
        #self.connect()
        print ('error arduino is not connected , please connect arduino')






    
    def analogWrite(self,pinNumber,value):
      try: 
        self.ser.isOpen()
      except:     
        #self.connect()
        print "cannot write analog pin because arduino is not connected, please connect it and retry"
        return(-1)

      if ((value >255)or(value<0)):
        print 'error the  analog value is out of range ,use a value from 0 to 255'
        return()
      if ((pinNumber >self.__maxPin)or (pinNumber<0)):
        print 'error the  pin value is out of range ,use a value from 0 to 13 for arduino2009 or a value from 0 to 52 for arduino mega'
        return()
   


      if self.ser.isOpen():
  

        if pinNumber < 10:
          pinNumber="0"+str(pinNumber)
        else:
          pinNumber=str(pinNumber)
             

        if (value>99) and (value<999):
          self.ser.write('aw'+pinNumber+str(value))

        elif (value>9) and (value<99):
          self.ser.write('aw'+pinNumber+'0'+str(value))

        elif (value>-1) and (value<9):
          self.ser.write('aw'+pinNumber+'00'+str(value))

      else:
        #self.connect()
        print ('error arduino is not connected , please connect arduino')   


      return(value) 





    def getRouterName(self):
      return(-1)  # to implement











    def readSerialThread(self):

      global pcduinoTread
     

      print "wait for connection to serial port"
      while (self.__connected==0 ):
        time.sleep(1)

      self.wait=1
      #print "readSerialThread"
      while pcduino_exit==0:
        j=11
        while (self.wait==1)&(pcduino_exit==0):#if pcduino is writing on serial port...not used for now
          j=j+1
          if j>25:
            print "thread read paused"
            j=0
          time.sleep(0.01)
   
        #print " write buffer2="+self.write_buffer
        #self.waitForThread=1
        if (len (self.write_buffer)>0)&(self.wait==0) :
          #print "write"+self.write_buffer+"to the serial port"
          #time.sleep(0.01)
          try:
            #tmp_bf=string.split(self.path,";") # split each command and creeate a list of commands named tmp_bf
            #for a in  tmp_bf:             
            
            self.ser.write(self.write_buffer) 
            self.write_buffer=''
            #self.waitForThread=0
          except:
            print 'error cant write to serial port'
            #self.waitForThread=0
        else:
          x=0
          #print "nothing to write to the serial port" 

        #try:
          #print "read serial"
        try:

          l1=self.ser.read() 
          if (l1!='')&(len(l1)>0):
            self.buffer=self.buffer+l1
          else:
            print "nothing received by the serial port"
            #print "input buffer >0"
        except:
          self.buffer='onos_error'
          print "reading serial port error" 


        if pcduino_exit==1:   #exit
          pcduinoTread=0
          print "pcduino reading thread closed"
          self.ser.close()
          return    

         
        #if len (self.watchPinDict.keys())>0:
        #  for b in self.watchPinDict.keys():
        #    a=self.watchPinDict[b]
        #    if string.find(self.buffer,"an"+b) :  #found a change of status pin in the input buffer
        #      x=0

      if pcduino_exit==1:   #exit
        pcduinoTread=0
        print "pcduino reading thread closed"
        self.ser.close()
        return    



        #  print "serial error"

          #print 'serial comunication reading error in thread read'
          
        #print "hkeys----------------------------------------------------------------------------------------------"
        #print object_dict.keys()

         #for b in object_dict.keys() : #for every web obj
       #   a=object_dict[b]
        #  pin=a.getAttachedPin()
       #   if (a.getType()=="d_sensor")&(pin!=9999):
        #print "webobj status set reading arduino pin to"
    #        tmp_buffer=self.buffer
            
     #       if pin <10:
     #         find=string.find(tmp_buffer,"dr0"+str(pin))
     #         if (find!=-1):   # found the reading of the pin in the input buffer
     #           try:
     #             a.setStatus(int(tmp_buffer[find+3:find+4]))   # find a way to update the real object...
                  
     #             print "status setteddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd<10"
                  #break
     #           except:
     #             print "cant' set the status to the web object"+tmp_buffer[find:find+1]
     #             x=0  # void command

     #       else:#pin >9
     #         find=string.find(tmp_buffer,"dr"+str(pin))
     #         if (find!=-1):   # found the reading of the pin in the input buffer
     #           try:
     #             a.setStatus(int(tmp_buffer[find+4:find+5]))
     #             print "status setteddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd>9"
                 # break
     #           except:
     #             print "cant' set the status to the web object"+tmp_buffer[find:find+1]
     #             x=0  # void command


  













 


