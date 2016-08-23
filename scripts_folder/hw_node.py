
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

"""| This module is responsable for the handling of each node in the system.
   | It generates the setup pin configuration to send to the nodes.
   | It stores each node pin setup and last time sync. 
   |  
  
"""



from  globalVar import *



#maxPin  is 20 for arduino 2009/uno   (14+6)  but  on wireless node   5 pin are used for comunication

#note...if you use also only one analog input as a digital pin...you can't use the left pins to read analog values!





#Pin mode description:  
# DOUTPUT=0  -->  digital pin output setted to 0
# DOUTPUT=1  -->  digital pin output setted to 1
# DINPUT=0   -->  digital pin input  readed and the value is 0
# DINPUT=1   -->  digital pin input  readed and the value is 1
# AINPUT=0   -->  analog  pin input  readed and the value is 0
# AINPUT=255 -->  analog  pin input  readed and the value is 255
# AOUTPUT=0   --> pwm  output setted to 0
# AOUTPUT=255 --> pwm  output setted to 255
# SOPUTPUT=180--> servo moved to 180 degreese
#the analog pin can't be used as digital and then reused for analog unless you reboot arduino
#
#
class HwNode:



    __node_name="room0_n0"
    


    def __init__(self,NodeSerialNumber,hwModel,address,node_fw):
      self.NodeSerialNumber=NodeSerialNumber
      self.address=address
      self.node_fw=node_fw
      self.hwModelName=hwModel["hwName"]
      self.maxPin=hwModel["max_pin"] 
      self.hwType=hwModel["hardware_type"]  
      self.timeout=hwModel["timeout"]  #time (in seconds) onos will let pass without contact with the node after which the node will be setted as inactive 
      self.NodeSerialNumber=self.NodeSerialNumber
      self.total_pin={}
      self.last_node_sync=time.time()
      self.isActive=1
      j=0
      while (j<(  (8*9)+1 ) ):  # create all the unused pin #banana to use only the pin used not all till the pin number!
        self.total_pin[j]=j
        j=j+1      
      self.pins_status={}
      self.pins_status_old={}
      self.pins_io_mode=[]
      self.pins_analog_in_mode=[]
      self.pins_analog_out_mode=[]
      self.pins_servo_mode=[]
      self.pins_io_status=[]
      self.used_pin=[]  
      self.used_pin=getListUsedPinsByHardwareModel(self.hwModelName)

      tmp_digital_input_pins=getListPinsConfigByHardwareModel(self.hwModelName,"digital_input")
      tmp_digital_sr_relay_pins=getListPinsConfigByHardwareModel(self.hwModelName,"sr_relay")
      #tmp_digital_output_pins=getListPinsConfigByHardwareModel(self.hwModelName,"digital_output")
      tmp_analog_input_pins=getListPinsConfigByHardwareModel(self.hwModelName,"analog_input")
      tmp_analog_output_pins=getListPinsConfigByHardwareModel(self.hwModelName,"analog_output")
      tmp_servo_pins=getListPinsConfigByHardwareModel(self.hwModelName,"servo_output")
      #tmp_special_pins=getListPinsConfigByHardwareModel(self.hwModelName,"special_pin")

       

      for i in self.total_pin.keys():#banana to use only the pin used not all till the pin number!
        self.pins_status[i]="DOUTPUT=0"   #BY DEFAULT SET ALL PINS AS DIGITAL OUTPUT AND SET THEM TO 0 
        self.pins_status_old[i]=self.pins_status[i]
        self.pins_io_mode.append(1)  #binary mode set as output
        self.pins_io_status.append(0)#binary pin set to 0
        self.pins_servo_mode.append(0)      # set as not used for servo 
        self.pins_analog_in_mode.append(0)  # set as not used for analog input 
        self.pins_analog_out_mode.append(0) # set as not used for anolog out 
        # 1 for output 0 for input



      #banana to add a check in order to block the setup of a pin with multiple modes 
      for i in self.total_pin.keys():   #  i iterates through all  pins (also the unused ones)
        inside_some_category=0
        if i in tmp_digital_input_pins:
          self.pins_status[i]="DINPUT=9999"  # set the pin as digital input ,9999 is a impossible value used as marker
          self.pins_io_mode[i]=0  #binary mode set as input
  
          
        if i in tmp_analog_input_pins:
          self.pins_status[i]="AINPUT=9999"  # set the pin as analog  input ,9999 is a impossible value used as marker
          self.pins_io_mode[i]=0  #binary mode set as not digitalinput need to be so for the arduino digitalread setup code
          self.pins_analog_in_mode[i]=1

          
          
        if i in tmp_servo_pins:
          self.pins_status[i]="SOUTPUT=9999"  # set the pin as servo pin    ,9999 is a impossible value used as marker
          self.pins_io_mode[i]=1  #binary mode set as output
          self.pins_servo_mode[i]=1

          
        if i in tmp_analog_output_pins:
          self.pins_status[i]="AOUTPUT=9999"  # set the pin as analog_output ,9999 is a impossible value used as marker
          self.pins_io_mode[i]=1  #binary mode set as not digitalinput
          self.pins_analog_out_mode[i]=1





    def isPinOk(self,pin):
      """
      Return 1 if the given pin exist in this hardware node, 0 otherwise
      """
      if (pin in self.pins_status):
        return(1) #pin is in the range for the hardware
      else:
        print "error ,the pin is not in the range hardware"
        errorQueue.put("error ,the pin is not in the range hardware" )
        return(0) #pin is NOT in the range for the hardware


    def setNodePinMode(self,pin,mode):  #
 
      """| Given a pin number and a mode, set the pin mode
         |  The options for mode are:

            - "DOUTPUT" : digital     output 
            - "AOUTPUT" : analog      output
            - "SOUTPUT" : servo motor output
            - "DINPUT"  : digital input
            - "AINPUT"  : analog  input
      """
      if type(mode) is not str :
        print "error in setNodePinMode , passed a non string type as mode"
        errorQueue.put("error in setNodePinMode , passed a non string type as mode" )
        return(-1)

      if self.isPinOk(pin):
        try:
          self.pins_status[pin]=mode
          if mode=="DOUTPUT":
            self.pins_io_mode[pin]=1
          if mode=="AOUTPUT":
            self.pins_io_mode[pin]=1

          if mode=="SOUTPUT":          #servo controll pin
            self.pins_io_mode[pin]=1



          if mode=="DINPUT":
            self.pins_io_mode[pin]=0

          if mode=="AINPUT":          #bug  ...error 
            self.pins_io_mode[pin]=0
          return(1)

        except Exception, e :
          print "hw_node() pin setting error in  node:"+self.NodeSerialNumber+"pin:"+str(pin)+" mode:"+str(mode)
          print (e.args)
          errorQueue.put("hw_node() pin setting error in  node:"+self.NodeSerialNumber+"pin:"+str(pin)+" mode:"+str(mode) ) 
          errorQueue.put(e.args)  
          return(-1)
      else:
        print "pin out of range , cannot set the digital input pin status in  node:"+self.NodeSerialNumber
        return(-1)




    def setDigitalPinInputStatus(self,pin,status):#the options for status are an int   obsolete
      """
        Deprecated , not used anymore. 

      """
      if self.isPinOk(pin) :
        try:
          self.pins_status[pin]="DINPUT="+str(status)
          return(1)
        except:
          print "pin not setted as digital input in this in node:"+self.NodeSerialNumber
          return(-1)
      else:
        print "pin out of range , cannot set the digital input pin status "  
        return(-1)





    def setAnalogPinInputStatus(self,pin,status):#the options are from 0 to 255
      """  
        Deprecated , not used anymore. 
          
      """
      if self.isPinOk(pin) :
        try:
          self.pins_status[pin]="AINPUT="+str(status)  #status are from: "AINPUT=0"   to "AINPUT=255"
          return(1)
        except:
          print "pin not setted as digital input in node:"+self.NodeSerialNumber
          return(-1)
      else:
        print "pin out of range , cannot set the digital input pin status "  
        return(-1)




      
    def setDigitalPinOutputStatus(self,pin,status):#the options for status are int value   obsolete method
      """Deprecated , not used anymore """
      if self.isPinOk(pin) :
        try:
          self.pins_status[pin]="DOUTPUT"+str(status)  #status are from: "AINPUT=0"   to "AINPUT=255"
          return(1)
        except:
          print "pin not setted as digital input in node:"+self.NodeSerialNumber
          return(-1)
      else:
        print "pin out of range , cannot set the digital input pin status "  
        return(-1)


#    def setNodeSerialNumber(self,name):             #set the node name
#      self.NodeSerialNumber=name
#      return(1)


    def setNodeAddress(self,address): 
      """| Set the node address with the string passed 
         |   Example: "192.168.101.10"  
       """
      self.address=address
      return(1)






    def getPinStatus(self,pin):             #return the PinStatus 
      """Deprecated , not used anymore """ 

      if self.isPinOk(pin) :
        try:
          self.pins_status[pin]
          return(self.pins_status[pin])
        except:
          print "pin read problem in node:"+self.NodeSerialNumber
          return(-1)
      else:
        print "read pin out of range in node:"+self.NodeSerialNumber
        return(-1)


         

    def getPinMode(self,pin):             #return the Pin mode 
      """Deprecated , not used anymore """ 

      if self.isPinOk(pin) :
        try:
          #self.pins_status[pin]
          s=string.find (self.pins_status[pin],"=")
          s1=self.pins_status[pin][0:s]
          return(s1)
        except:
          print "pin mode problem in node:"+self.NodeSerialNumber
          return(-1)
      else:
        print " mode pin out of range in node:"+self.NodeSerialNumber
        return(-1) 
   



   



    def getNodeHwModel(self):
      return(self.hwModelName)


    def getHwType(self):
      """ Return the node hardware type like:\n
              - gl.inet_only
              - arduino_promini
              - rasberry_b_rev2_only
              - arduino2009

      """   
      return(self.hwType)

    def setNodeFwVersion(self,nodeVersion):
      """| Set the node firmware version with the given string 
         |   Example "4.15"
      """
      self.node_fw=nodeVersion
      return(self.node_fw)
 
    def getNodeFwVersion(self):
      """| Return a string containing the node firmware version 
         | An example is "5.14" 
      """
      return(self.node_fw)

    def getNodeAddress(self): 
      """Return the node address , if the address is 0 then the node is the arduino over usb (todo)"""
      return(self.address)

    def getNodeSerialNumber(self): 
      """| Return the node serial number.
         |  For example "Plug6way0001" 

      """
      return(self.NodeSerialNumber)

    def getMaxPinNumber(self): 
      """Return the number of pin present in the node"""   
      return(self.maxPin)

    def getUsedPins(self): 
      """Return the list of used pins""" 
      return(self.used_pin)


   
    def updateLastNodeSync(self,time):
      """When called update the time from last node time sync with the given one"""
      self.last_node_sync=time
      return()

    def getLastNodeSync(self):
      """Return the the time from last node time sync"""
      return(self.last_node_sync)

    def getNodeTimeout(self):
      """| Return the time after which the node is declared inactive. 
         | So if getLastNodeSync() is greater than this self.timeout the node will be setted as inactive 
         | self.timeout is readed from hardwareModelDict  in globalVar.py"""
      return(self.timeout)

    def setNodeActivity(self,value):
      """Set the node activity status with the one given.

         :param value: 
           - The value to set the node activity should be a integer of 0 or 1
               | 0 If the node is inactive 
               | 1 If the node is active

       

      """
      self.isActive=value

    def getNodeActivity(self):
      """Return the node activity status. """
      return(self.isActive)

    def setNodeAnalogInputStatusFromReg(self,pin_number,low_byte,high_byte): 
      """ 
      | Given a pin number, and two bytes  return the analog value in an single integer.
      | Since arduino analogRead return a 10 bit analog value to send it I need to split it in two bytes (8 bit each)
      | so arduino will send 2 bytes the low_byte and the high_byte , this function will rebuild the number from those two bytes   

      """

      if self.isPinOk(pin_number) :

        if self.pins_status[pin_number][0:6]=="AINPUT":    #check if the pin is a analog input       
          #  print ("added analog status")
          analog_value=low_byte+(high_byte*256)  #the data is splitted in 2 byte  so to get it i made this math
          analog_value=str(analog_value)
          while len(analog_value) <4 :  #to make the format 0000
            analog_value="0"+analog_value 

          self.pins_status[pin_number]="AINPUT="+str(analog_value) 
          return(analog_value) 
                
        else: # pin not used as analog input           
          print "warning: the pin is not setted as analog input"
          return("9999")



      else:
        print "pin out of range , cannot set the digital input pin status "  
        return("9999")







    def setNodeSectionDInputStatus(self,section_number,status_byte): 
      """| Set the node status pins of a section (8 bit) received from arduino.
         | if the section status is different from the previous one then check
         | what pins changed and ask the webserver.py to change the webobj status of the relative pins
         | i don't need a setNodeSectionDoutputStatus because the output status will be saved in the webobject status. 

      """
      binary_mask=[1,2,4,8,16,32,64,128]   

      pin_to_update={}  
      for i in range(0, 8):  # from 0 to 7  ,for all the pins in the section  
        pin=((section_number*8)+i)        
        print "self.pins_status="
        print self.pins_status[pin]
        print "pin="+str(pin)
        if self.pins_status[pin][0:6]=="DINPUT":    #check if the pin is a digital input
     
           # print self.pins_io_status
          current_state=status_byte & binary_mask[i]  #  make an & in order to get the status of each bit of the byte
          if (current_state>0) :  # to make it boolean ,0 or 1
            current_state=1
          print "pin_status="+str(current_state)  
          print "binary_mask[i]="+str(binary_mask[i])            
          self.pins_io_status[pin]==current_state
          self.pins_status[pin]="DINPUT="+str(current_state)  
          if (self.pins_status[pin]!=self.pins_status_old[pin]):   #if something change from the previous update..    
            self.pins_status_old[pin]=self.pins_status[pin]
            pin_to_update[pin]=str(current_state)
   

            print "pin number"+str(pin)+"of_node:"+self.NodeSerialNumber+"changed status to:"+self.pins_status[pin]
   

      return(pin_to_update)







    def getNodeSectionStatusByPin(self,pin):
      """ Given a pin  return a tuple with: 

            - The number of the section where the pin is located 
            - The the node status register for the section (8 bit) containing that pin

         | Structure:
         | (the section0 is relative to the first 8 pins , from pin 0 to pin 7)   msb    left 
         | (the section1 is relative to the pins from 8 to 15)
         | (the section2 is relative to the pins from 16 to 23 )
         | (the section3 is relative to the pins from 24 to 31)
         | (the section4 is relative to the pins from 32 to 39 )
         | (the section5 is relative to the pins from 40 to 47)
         | (the section6 is relative to the pins from 48 to 55 )
 
      """
      section=pin//8    #get the section that is the division from pin number and 8  without remainder..
      


      status_reg=(self.pins_io_status[section*8])*128
      status_reg=status_reg+(self.pins_io_status[(section*8)+1])*64
      status_reg=status_reg+(self.pins_io_status[(section*8)+2])*32
      status_reg=status_reg+(self.pins_io_status[(section*8)+3])*16
      status_reg=status_reg+(self.pins_io_status[(section*8)+4])*8
      status_reg=status_reg+(self.pins_io_status[(section*8)+5])*4
      status_reg=status_reg+(self.pins_io_status[(section*8)+6])*2
      status_reg=status_reg+(self.pins_io_status[(section*8)+7])*1 #now pins_io_status is a byte containing each pin status.

      status_reg=unichr(status_reg)

      return((section,status_reg))

    
    def getNodeStatusList(self): 
      """
         :warning:  Never used

           Return a list containing the node status for each pin.
         
      """
      return(self.pins_status)

   


    def getPinModeList(self):           
      """
         :warning:  Never used

           Return the Pin mode list containing all the pin mode.

      """
      b=[]
      for a in self.pins_status:

       
        try:

          s=string.find (a,"=")
          s1=a[0:s]
          b.append(s1)
        except:
          print "pin mode problem in node:"+self.NodeSerialNumber
          return(-1)

      return(b)         




    def getNodeSectionMode(self): 
      """
      :warning:  Never used

      |  Return a list containing the node mode for each section (8 bit)
      |  (the section0 is relative to the first 8 pins , from pin 0 to pin 7)   msb    left 
      |  (the section1 is relative to the pins from 8 to 15)
      |  (the section2 is relative to the pins from 16 to 23 )
      |  (the section3 is relative to the pins from 24 to 31)
      |  (the section4 is relative to the pins from 32 to 39 )
      |  (the section5 is relative to the pins from 40 to 47)
      |  (the section6 is relative to the pins from 48 to 55 )

      """
      print "used pins by node="
      print self.used_pin

      section=0
      d_conf_string=""
      s_conf_string=""
      ai_conf_string=""
      ao_conf_string=""
      p_used_string=""

    #  print "len self.pins_servo_mode :"+str(len(self.pins_servo_mode))
    #  print "len self.total_pin :"+str(len(self.total_pin))
    #  print "len self.pins_io_mode :"+str(len(self.pins_io_mode))
    #  print "len self.pins_analog_in_mode :"+str(len(self.pins_analog_in_mode))
    #  print "len self.pins_analog_out_mode :"+str(len(self.pins_analog_out_mode))

      while ((8*section)<(8*9)):
       # print "sectionx8="+str(section*8)
        p_used=0
        p_used=(self.total_pin[section*8] in self.used_pin)*1
        #print "pin0="+str((self.total_pin[section*8] in self.used_pin)*1)
        p_used=p_used+(self.total_pin[section*8+1] in self.used_pin)*2
        #print "pin1="+str((self.total_pin[section*8+1] in self.used_pin)*2)
        p_used=p_used+(self.total_pin[section*8+2] in self.used_pin)*4
        #print "pin2="+str((self.total_pin[section*8+2] in self.used_pin)*4)
        p_used=p_used+(self.total_pin[section*8+3] in self.used_pin)*8
        #print "pin3="+str((self.total_pin[section*8+3] in self.used_pin)*8)
        p_used=p_used+(self.total_pin[section*8+4] in self.used_pin)*16
        #print "pin4="+str((self.total_pin[section*8+4] in self.used_pin)*16)
        p_used=p_used+(self.total_pin[section*8+5] in self.used_pin)*32
        #print "pin5="+str((self.total_pin[section*8+5] in self.used_pin)*32)
        p_used=p_used+(self.total_pin[section*8+6] in self.used_pin)*64
        #print "pin6="+str((self.total_pin[section*8+6] in self.used_pin)*64)
        p_used=p_used+(self.total_pin[section*8+7] in self.used_pin)*128
        #print "pin7="+str((self.total_pin[section*8+7] in self.used_pin)*128)
        #print "p_used int="+str(p_used) 
        p_used=chr(p_used)        
        p_used_string=p_used_string+p_used  
        #print "p_used_string="+p_used_string

        d_setup=0
        d_setup=(self.pins_io_mode[section*8])*1               
        d_setup=d_setup+(self.pins_io_mode[(section*8)+1])*2
        d_setup=d_setup+(self.pins_io_mode[(section*8)+2])*4
        d_setup=d_setup+(self.pins_io_mode[(section*8)+3])*8
        d_setup=d_setup+(self.pins_io_mode[(section*8)+4])*16
        d_setup=d_setup+(self.pins_io_mode[(section*8)+5])*32
        d_setup=d_setup+(self.pins_io_mode[(section*8)+6])*64
        d_setup=d_setup+(self.pins_io_mode[(section*8)+7])*128      
        d_setup=chr(d_setup)
        d_conf_string=d_conf_string+d_setup  

        s_setup=0
        s_setup=(self.pins_servo_mode[section*8])*1                  #servo setup
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+1])*2
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+2])*4
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+3])*8
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+4])*16
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+5])*32
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+6])*64
        s_setup=s_setup+(self.pins_servo_mode[(section*8)+7])*128     
        s_setup=chr(s_setup)
        s_conf_string=s_conf_string+s_setup  


        ai_setup=0
        ai_setup=(self.pins_analog_in_mode[section*8])*1         #analog input setup     
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+1])*2
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+2])*4
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+3])*8
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+4])*16
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+5])*32
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+6])*64
        ai_setup=ai_setup+(self.pins_analog_in_mode[(section*8)+7])*128      
        #print "ai setup for section:"+str(section)+"=="+str(ai_setup)
        ai_setup=chr(ai_setup)
        ai_conf_string=ai_conf_string+ai_setup  

        ao_setup=0
        ao_setup=(self.pins_analog_out_mode[section*8])*1         #analog output setup        
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+1])*2
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+2])*4
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+3])*8
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+4])*16
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+5])*32
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+6])*64
        ao_setup=ao_setup+(self.pins_analog_out_mode[(section*8)+7])*128      
        ao_setup=chr(ao_setup)
        ao_conf_string=ao_conf_string+ao_setup  


        section=section+1



      tmp_dict={}
      tmp_dict["used_pins"]=p_used_string
      tmp_dict["digital_conf"]=d_conf_string
      tmp_dict["servo_conf"]=s_conf_string
      tmp_dict["analog_input_conf"]=ai_conf_string
      tmp_dict["analog_output_conf"]=ao_conf_string
   #   for n in ai_conf_string :    #banana to remove
   #     print "an setup ="+str(ord(n))          #banana to remove

      return(tmp_dict)


    def getSetupMsg(self):

      """Return a encoded string containing the setup mode for the node pins

         I need to encode the pin setup in a sinmple and compact way.
         Here the protocol:

         .. code-block:: python

           start with 's='
           then  add    9 bytes that rappresent the pin used (1 for pin used 0 for not used)   
           after that   9 bytes that rappresent the digital pin setup from pin0 to pin 127
           after that   9 bytes that tell arduino which pin to set as analog input
           after that   9 bytes that tell arduino which pin to set as pwm output
           after that   9 bytes that tell arduino which pin to set as servo output
           then  1   byte for future use , for now '#'
           example:"s=000000000000000000000000000000000000000000000#"  
           the 0 are not 0 but the value corrisponding to ascii '0'
           total 48 byte 
     """

      print "getSetupMsg executed"
      tmp_dict=self.getNodeSectionMode()
      msg="s="
      #msg=msg+"pu"
      msg=msg+tmp_dict["used_pins"]   
      #msg=msg+"ds"
      msg=msg+tmp_dict["digital_conf"]   #get the binary digital io configuration
      #msg=msg+"ai"
      msg=msg+tmp_dict["analog_input_conf"]
      #msg=msg+"ao"
      msg=msg+tmp_dict["analog_output_conf"]
      #msg=msg+"sm"
      msg=msg+tmp_dict["servo_conf"]+"#"
      print "msg="+msg
      print "len msg="+str(len(msg))
      return (msg)








    def getNodeSectionModeByPin(self,pin): 
      """
        Deprecated , not used anymore. 
          Given a pin  return the node mode for the section (8 bit) containing that pin.
          
      """
     #(the section0 is relative to the first 8 pins , from pin 0 to pin 7)   msb    left 
     #(the section1 is relative to the pins from 8 to 15)
     #(the section2 is relative to the pins from 16 to 23 )
     #(the section3 is relative to the pins from 24 to 31)
     #(the section4 is relative to the pins from 32 to 39 )
     #(the section5 is relative to the pins from 40 to 47)
     #(the section6 is relative to the pins from 48 to 55 )

      section=pin//8    #get the section that is the division from pin number and 8  without remainder..


      setup=(self.pins_io_mode[section*8])*128
      setup=setup+(self.pins_io_mode[(section*8)+1])*64
      setup=setup+(self.pins_io_mode[(section*8)+2])*32
      setup=setup+(self.pins_io_mode[(section*8)+3])*16
      setup=setup+(self.pins_io_mode[(section*8)+4])*8
      setup=setup+(self.pins_io_mode[(section*8)+5])*4
      setup=setup+(self.pins_io_mode[(section*8)+6])*2
      setup=setup+(self.pins_io_mode[(section*8)+7])*1
      setup=unichr(setup)

      return(setup)

    def close(self):
      self.exit=1
      print "class hw_node destroyed"



