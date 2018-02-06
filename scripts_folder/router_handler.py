#!/usr/bin/env python
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
| This Modules handles all the comunication to nodes.
| It will routes the varius commands knowing where to send them based on the node address.
|
| If the node_address of the given receiver is 0 the data will be written to the local OnosCenter pins.
|
| if the node_address of the given receiver is 1 the data will be sent to the OnosCenter serial port to an arduino (not implemented yet)
|
| If the node_address of the given receiver is between 2 to 255 :
|   OnosCenter will send the command to write the data to an arduino wich will then transmit it to the desired wireless node.(not implemented yet)
|
| If the node_address of the given receiver is a string greater than 6 characters:
    The data will be sent over ethernet commmunication.
|




"""




from conf import *
from node_query_handler import *
import arduinoserial,Serial_connection_Handler


# Note for raspberry users, the GPIO numbers that you program here refer to the pins
# of the BCM2835 and *not* the numbers on the pin header. 
# So, if you want to activate GPIO7 on the header you should be 
# using GPIO4 in this script. Likewise if you want to activate GPIO0
# on the header you should be using GPIO17 here.


#echo "24" > /sys/class/gpio/export 
# to clean up a pin exported  : echo "4" > /sys/class/gpio/unexport
#echo "out" > /sys/class/gpio/gpio24/direction
#echo "1" > /sys/class/gpio/gpio24/value

#echo "in" > /sys/class/gpio/gpio23/direction
#cat /sys/class/gpio/gpio23/value




class RouterHandler:

    def __init__(self,hardwareModelDict,router_sn):
      self.router_sn=router_sn
      self.bash_pin_enable=0
    #os.system("echo classe >> numero_classi_raspberry_handler")
      self.pins_mode={}
      self.pins_status={}
      self.old_pins_status={}
      self.hwModelName=hardwareModelDict["hwName"]
      self.__hardware_type=hardwareModelDict["hardware_type"]
      self.__node_name=self.router_sn   # RouterGL0001
      self.progressive_msg_id='0' # to send an unique message identyfier i append a progressive number to the end of the message
      self.progressive_msg_number=0 #used to create self.progressive_msg_id 
      self.serialCommunicationIsWorking=0
      self.exit=0
      self.router_pin_numbers=[]
      #self.read_thread_running=0   
      self.serial_arduino_used=0  
      self.local_pin_enabled=0
    
      self.__maxPin=hardwareModelDict["max_pin"]    #17 -2 used for uart
    
      self.router_pin_numbers=getListUsedPinsByHardwareModel(self.hwModelName)
      logprint ("pin used ="+str(self.router_pin_numbers))

      #print "digital input router pin total number= "
      #print (getListPinsConfigByHardwareModel(self.hwModelName,"digital_input"))
      
      self.router_input_pin=getListPinsConfigByHardwareModel(self.hwModelName,"digital_input")
      self.total_in_pin=len(self.router_input_pin) #get the number of digital inputs


      try:
        self.bash_pin_enable=hardwareModelDict["parameters"]["bash_pin_enable"]
        self.serial_arduino_used=hardwareModelDict["parameters"]["serial_port_enable"]

      except:
        self.bash_pin_enable=0
        self.serial_arduino_used=0


      if self.__hardware_type=="rasberry_b_rev2_only":  #banana to import this from hardwareModelDict
        self.bash_pin_enable=1

      if self.__hardware_type=="gl.inet_only":
        self.bash_pin_enable=1


      if self.__hardware_type=="gl.inet_with_arduino2009":
        self.serial_arduino_used=1
        self.bash_pin_enable=1

      if self.__hardware_type=="pc_with_arduino2009":
        self.serial_arduino_used=1
        self.bash_pin_enable=1

      if enable_usb_serial_port==0:
        self.serial_arduino_used=0


      if (os.path.exists("/sys/class/gpio")==1)&(enable_onosCenter_hw_pins==1) : #if the directory exist ,then the hardware has embedded IO pins
        logprint ("discovered local hardware io pins")
        self.bash_pin_enable=1
      else:
        self.bash_pin_enable=0   #disable embedded pins because the harware hasn't got any
        logprint ("no embedded IO pins founded , are you running onos on a pc?")


      if self.serial_arduino_used==1:
        
        self.initializeArduinoCommunication()
          


   #     except Exception as e:
   #       print "error in opening arduino serial port e:"+str(e.args)

   #       self.serialCommunicationIsWorking=0

    
        if self.serialCommunicationIsWorking==1:
          logprint ("serial communication working")
         

          #todo: read nodeFw from the serial arduino node..
          #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":"ProminiS0001","nodeAdress":"001","nodeFw":"5.23"})  
      


      error_number=0   #count how many errors..
      if self.bash_pin_enable==1:

        for pin in self.router_pin_numbers:
          self.pins_status[pin]=0  # create the pin var in the dictionary
          try:
            logprint ("I try to execute echo "+str(pin)+" > /sys/class/gpio/export ")
            #os.popen('echo '+str(pin)+' > /sys/class/gpio/unexport ').read()  #remove a GPIO file access
            with lock_bash_cmd:
              subprocess.call('echo '+str(pin)+' > /sys/class/gpio/unexport ', shell=True)

            #os.popen('echo '+str(pin)+' > /sys/class/gpio/export ').read()  #Create a GPIO file access
              subprocess.call('echo '+str(pin)+' > /sys/class/gpio/export ', shell=True,close_fds=True)

          except Exception as e:
            error_number=error_number+1
            message="error can't create GPIO pin:"+str(pin)+" and set its mode :"+str(e.args)
            logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
          time.sleep(1)


          if pin in self.router_input_pin:
            self.pins_mode[pin]=0  # set the pin as input
            try:
              #with lock_bash_cmd:
              with open('/sys/class/gpio/gpio'+str(pin)+'/direction', 'w') as f:   #read the pin status
                f.write('in')
                #subprocess.call('echo in > /sys/class/gpio/gpio'+str(pin)+'/direction', shell=True,close_fds=True)   
              #os.popen('echo in > /sys/class/gpio/gpio'+str(pin)+'/direction').read()  #set the GPIO as input  
            except Exception as e :
              message="error trying to read a router pin :"+str(e.args)
              logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
              error_number=error_number+1
            
            time.sleep(1)


            try:
              logprint("i try to read the status with: cat /sys/class/gpio/gpio"+str(pin)+"/value")
              #with lock_bash_cmd:
              with open('/sys/class/gpio/gpio'+str(pin)+'/value', 'r') as f:   #read the pin status
                read_data = f.read()
              status=read_data[0] 
                #status=subprocess.check_output("cat /sys/class/gpio/gpio"+str(pin)+"/value", shell=True,close_fds=True)
              #status=os.popen("cat /sys/class/gpio/gpio"+str(pin)+"/value").read()
              self.pins_status[pin]=int(status)

            except Exception as e  :
              message="error in reading pin"+str(pin)
              logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))

              self.pins_status[pin]=0
              error_number=error_number+1 

          else:
            self.pins_mode[pin]=1  # set the pin as output
            #print "i try to set the pin as output"
            try:
              #with lock_bash_cmd:
              with open('/sys/class/gpio/gpio'+str(pin)+'/direction', 'w') as f:   #read the pin status
                f.write('out')
                #os.popen('echo out > /sys/class/gpio/gpio'+str(pin)+'/direction').read()  #set the GPIO as output 
                #subprocess.call('echo out > /sys/class/gpio/gpio'+str(pin)+'/direction', shell=True,close_fds=True)

            except Exception as e  :
              message="error setting pin"+str(pin)+ "as output"
              logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))


        if error_number >5:
          self.bash_pin_enable=0  #disable the bash pin command if too many error happen
          message="too many error command the router pins  , are you running onos on a pc?"
          logprint(message,verbose=7)
#        if ( (len (self.pin_numbers) >0)&(self.bash_pin_enable==1)): 
#        #if the router hardware has any hardware pins ..then run the thread in order to read them
#          self.exit==0
#          self.tr_read = threading.Thread(target=self.read_router_pins)
#          self.tr_read.daemon = True  #make the thread a daemon thread

#          self.tr_read.start()
#        else:
#          print "i don't start the reading thread because i can't read the hw pins"


    def connectSerialPort(self):
        global Serial_connection_Handler 
        if self.serialCommunicationIsWorking==1:
          return(self.serialCommunicationIsWorking)
        try:
          serial_communication=Serial_connection_Handler.Serial_connection_Handler()
          self.serialCommunicationIsWorking=serial_communication.working
          self.initializeArduinoCommunication()
          return(self.serialCommunicationIsWorking)

        except Exception as e  :
          message="error in opening arduino serial port"
          logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
          self.serialCommunicationIsWorking=0
          return(0)


    def initializeArduinoCommunication(self):

      #try:
      #  del self.serial_communication
      #  print("deleted the reference to serial_communication ") 
      #except:
      #  print("")
  

        #self.serial_communication=self.connectSerialPort()
      try:
        self.serial_communication=Serial_connection_Handler.Serial_connection_Handler()
        self.serialCommunicationIsWorking=self.serial_communication.working
        self.serial_communication.uart.write("[S_01begin_#]\n")
        self.serialCommunicationIsWorking=1
      except Exception as e  :
        message="error in the init of serial port check if is it connected"
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
        self.serialCommunicationIsWorking=0        



      timeout=time.time()+70
      if self.serialCommunicationIsWorking==1:
        retry_start_cmd=0
        serial_problem=1
        received_answer=""
        while retry_start_cmd < 10:

          received_answer=self.serial_communication.uart.write("[S_01begin_#]\n")
          if "[S_" in received_answer:
             self.serialCommunicationIsWorking=1
             serial_problem=0
             logprint("arduino answered on serial port")
             break
          retry_start_cmd=retry_start_cmd+1
          logprint("serial_write begin retry number:"+str(retry_start_cmd))
   
        try:
          self.serial_communication.uart.readed_packets_list.remove(received_answer)  
        except:
          pass
        if serial_problem==1:
          logprint("arduino is not answering on serial port")
          logprint("I will retry other time till "+str(time.time())+" < "+str(timeout) )
          self.serialCommunicationIsWorking=0










 
    def getProgressive_msg_id(self):

      """
      | Get a progressive id number to append it to the message in order to make it unique
      | 


      """

      self.progressive_msg_number=self.progressive_msg_number+1

      if  self.progressive_msg_number>9: #restart the number
        self.progressive_msg_number=0 

      self.progressive_msg_id=str(self.progressive_msg_number)  #todo  create a progressive number



      return(self.progressive_msg_id)

      

    def read_router_pins(self):   
      """
      | Thread  function to read changing of pin status on the embedded linux board (glinet,raspberry ecc)
      | 


      """



      #print "read_router_pins() executed"



      if ( (len (self.router_pin_numbers) >0)&(self.bash_pin_enable==1)): 
        #if the router hardware has any hardware pins ..then run the thread in order to read them
        #print "starting to read pins"
        x=0 #void operation
      else:
        logprint ("I don't start the reading function because i can't read the router hw pins",verbose=8)
        return(-1)

      if (self.total_in_pin<1) :#there is no input pin to read
        logprint ("there is no input pin to read",verbose=6)

        return(-1)

      #time.sleep(3)  #wait for the webserver

      if (self.exit==0): # if is not exiting time

        for pin in self.router_pin_numbers:
          if (self.exit==1):
            return
          #print "pin to read="+str(pin)

          
          if self.pins_mode[pin]==0:  #if the pin is an input one

            current_state=self.pins_status[pin] 
            #total_in_pin=total_in_pin+1 
            #print "foud a input pin in the router, pin number"+str(pin)
            #try:
            #with lock_bash_cmd:
            try:
              with open('/sys/class/gpio/gpio'+str(pin)+'/value', 'r') as f:   #read the pin status
                read_data = f.read()
              status=read_data[0]
              #status=subprocess.check_output("cat /sys/class/gpio/gpio"+str(pin)+"/value", shell=True,close_fds=True)

            except Exception as e  :
              message="error reading router pin status  "+str(pin)
              logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
            

            current_state=int(status)
              #print "the current pin status is: "+str(current_state)
            #except:
            #  print "error in reading pin"+str(pin)
            #  continue  #restart the loop

            if self.pins_status[pin]!=current_state:  #if the value is different from the old one
              self.pins_status[pin]=current_state  # update the old pin status with the current one
              logprint("the router pin: "+str(pin) +" input status changed to: "+str(current_state))


              #priority=99   usersDict["onos_node"]["priority"]               
              priority=99   #99 will allow the x but will not increase the object priority       
              priorityCmdQueue.put( {"cmd":"setNodePin","nodeSn":self.router_sn,"pinNumber":int(pin),"status_to_set":int(current_state),"write_to_hw":0,"user":"onos_node","priority":priority,"mail_report_list":[] } )

              



      return(1)




    def searchObjectBaseName(self,obj_selected,node_serial_number):


      remoteNodeHwModelName=nodeDict[node_serial_number].getNodeHwModel()
      try:

        for a in hardwareModelDict[remoteNodeHwModelName]["object_list"].keys():   
          #a will iterate all the ["object_list"] ..for example will be digital_obj_out from :
          #hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["caldaia"]["object_numbers"]=[0]   #
          for b in  hardwareModelDict[remoteNodeHwModelName]["object_list"][a].keys(): 
            #b will iterate all the obj ..for example will be caldaia from :
            #hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["caldaia"]["object_numbers"]=[0]   #
            for c in hardwareModelDict[remoteNodeHwModelName]["object_list"][a][b]["object_numbers"]:
              #c will iterate all the object adresses ..for example will be 0 from :
              #hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["caldaia"]["object_numbers"]=[0] 
              logprint ("""(hardwareModelDict[remoteNodeHwModelName]["object_list"][a][b]["object_numbers"]) : """)
              logprint (str(hardwareModelDict[remoteNodeHwModelName]["object_list"][a][b]["object_numbers"]) )
              logprint ("c:"+str(c)) 
              logprint ("b:"+str(b)) 

              if c==obj_selected:
                generic_object_name=b
                return(generic_object_name)   


      except Exception as e  :
        message="error searchObjectBaseName() iterating the hardwareModelDict searching the generic_object_name"
        logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))

      return(-1)





    def composeChangeNodeOutputPinStatusQuery(self, pinNumbers, node_obj, objName, status_to_set, node_serial_number,  
                                              node_address, out_type, user, priority, mail_report_list, node_password_dict={}) :

      """
      | Compose the correct query to change an output pin status on a remote node.
      | The examples are:
      |
      | WARNING old documentation... todo update it 
      | "onos_r"+pin0+pin1+"v"+status_to_set+"s"+node_serial_number+"_#]" to set a sr_relay to  status_to_set (0 or 1)
      |   onos_r0607v1sProminiS0001f000_#]  pin6 and 7 used to control a s/r relay and turn it to set 
      |
      | "onos_d"+pin_number+"v"+"00"+status_to_set+"s"+node_serial_number+"_#]" to set a digital pin to 0 or 1 
      |   onos_d07v001sProminiS0001f000_#]  set digital pin7 to 1
      |
      | "onos_s"+pin_number+"v"+status_to_set+"s"+node_serial_number+"_#]" to set a servopin from 0 to 180 
      |   onos_s07v180sProminiS0001f000_#]  set servo pin7 to 180
      |
      | "onos_a"+pin_number+"v"+status_to_set+"s"+node_serial_number+"_#]" to set a analogpin from 0 to 255 
      |   onos_a05v100sProminiS0001f000_#]  set analog pin5 to 100
      |
      | The node_serial_number is a hexadecimal number refering to the node serial number 
      | The node_address is a 3 byte ashii that rappresend the wireless node address(if the node is wireless,otherwise is ignored)
      |   the value must be between 0 and 255 it will be setted to "999" if is not used..

 

      """

      logprint("composeChangeNodeOutputPinStatusQuery() executed")
     
      address=nodeDict[node_serial_number].getNodeAddress()
      query="error_compose_query"
      base_query=''
   

      if (out_type in ("digital_obj_out","cfg_obj","analog_obj_out") ):  #todo remove "analog_obj_out"
        logprint("digital_obj compose query")
        #query example:  [S_01d001x_#] 
 
        if status_to_set not in [0,1]:
          logprint("error in composeChangeNodeOutputPinStatusQuery in obj section,status_to_set:"+str(status_to_set)+", not in (0,1)",verbose=10)
          return (-1)
        remoteNodeHwModelName=nodeDict[node_serial_number].getNodeHwModel()
        #print ( str(nodeDict[node_serial_number].getnodeObjectsDict()) )
        #print ("objName:"+objName+"end")
        try:
          obj_selected=nodeDict[node_serial_number].getNodeObjectAddress(objName)
        except Exception as e  :
          message="error getNodeObjectAddress"
          logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

        logprint ("obj_selected:"+str(obj_selected) )
        generic_object_name=self.searchObjectBaseName(obj_selected,node_serial_number)    
        logprint ("generic_object_name:"+generic_object_name)
   
        query_placeholder=""
        query_expected_answer=""

        try:
          query_placeholder=base_query+hardwareModelDict[remoteNodeHwModelName]["object_list"][out_type][generic_object_name]["query"]
          #now query_placeholder contains the query string got from globalVar.py in the hardwareModelDict{}
          if "query_expected_answer" in hardwareModelDict[remoteNodeHwModelName]["object_list"][out_type][generic_object_name].keys() :

#example: 
#hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["query_expected_answer"][0]="""RESULT = {"POWER":"ON"}"""
#hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["query_expected_answer"][1]="""RESULT = {"POWER":"OFF"}"""
#
#get    """RESULT = {"POWER":"ON"}""" from the dictionary when status_to_set is "0"..
 
            if status_to_set in hardwareModelDict[remoteNodeHwModelName]["object_list"][out_type][generic_object_name]["query_expected_answer"].keys():

              query_expected_answer=hardwareModelDict[remoteNodeHwModelName]["object_list"][out_type][generic_object_name]["query_expected_answer"][status_to_set]


        except Exception as e  :
          message="error in query_placeholder replacing the query from NodeHwModelName for node:"+remoteNodeHwModelName
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 

    #   print "query_placeholder:"+query_placeholder
        if obj_selected<10:
          # I don't need to convert this to hex ascii format because for i <10 decimal and hexadecimal are the same
          query_placeholder=query_placeholder.replace("#_objnumber_#","0"+str(obj_selected))
        else: #warning this is to change if the sonoff node use more than 9 relays..(tasmoda don't use hexadecimal format...
          #  hex(16).replace("0x","") --> '10'
          #  hex(obj_selected).replace("0x","")   get the number expressed in 2 ascii hex format 
          query_placeholder=query_placeholder.replace("#_objnumber_#",hex(obj_selected)[-2:]) 

        #query_placeholder=query_placeholder.replace("#_objnumber00_#","0"+str(obj_selected))
        #query_placeholder=query_placeholder.replace("#_objnumber0_#",str(obj_selected))
        #print "query_placeholder2:"+query_placeholder
        acceptable_len=0

        valuelen_pos=query_placeholder.find("#_valuelen")
        if valuelen_pos != -1:
        #  print "valuelen_pos != -1"   
 
          value = hex(int(status_to_set)).replace("0x","")  #make the value expressed in hexadecimal
          #if (query_placeholder.find("sts_not_"))!=-1:  #if the query must be negated...for object with active low pin..
          #  print ("found sts_not_ in placeholder,i will negate the status")
          #  value=str(int(not (int(status_to_set)))) 
          #  query_placeholder=query_placeholder.replace("sts_not_","")#clear the query from "sts_not_" 

         # print "try:"+re.search('#_valuelen:(.+?)_#',query_placeholder).group(1)  # get the 1 from wp0#_valuelen:1_#
          desidered_len=int (re.search('#_valuelen:(.+?)_#',query_placeholder).group(1))  # get the 1 from wp0#_valuelen:1_#
         # print "desidered_len:"+str(desidered_len)  
          while len(value)<desidered_len:
            value="0"+value            

          query_placeholder=re.sub(r'#_valuelen:.+?_#',value,query_placeholder) # replace  #_valuelen:1_#  with the value
          #query example:  [S_123wp01x_#]


          if (len(node_address)==3): #radio node
            hex_node_address=hex(int(node_address)).replace("0x","")  # get the hexadecimal string of the address
            if len(hex_node_address) < 2:  # to get an address with 2 char
              hex_node_address = "0" + hex_node_address  
             
            logprint("query_placeholder:"+query_placeholder)
            query='''[S_'''+hex_node_address+query_placeholder+self.getProgressive_msg_id()+'''_#]\n'''
            # print "query:::::"+query
            #valuelen_pos=query_placeholder.find("valuelen")
            #string_to_replace_with_value=query_placeholder[valuelen_pos:valuelen_pos+10]
            #query=query_placeholder.replace(string_to_replace_with_value,value)
          else:#network node
            query_placeholder=query_placeholder.replace("#_node_address_#",str(node_address)) 
            message="node_password_dict:"+str(node_password_dict)
            logprint(message,verbose=4) 
 
            if node_serial_number in node_password_dict:  # to use the node password..
              node_password=node_password_dict[node_serial_number]
              query_placeholder=query_placeholder.replace("#_node_password_#",node_password) 
            query=query_placeholder
          
          logprint("composed query was:"+query+"Endquery")
          

      elif (out_type=="sr_relay"):  #not correctly implemented todo:
        pin1=str(pinNumbers[1])
        pin0=str(pinNumbers[0])
        if (len (pin0) <2):
          pin0='0'+pin0
        if (len (pin1) <2):
          pin1='0'+pin1

        #  [S_001sr04051_#] 
        query=base_query+'''[S_'''+node_address+'''sr'''+pin0+pin1+str(status_to_set)+self.getProgressive_msg_id()+'''_#]'''+'''\n'''

      elif (out_type=="digital_output"): #not correctly implemented todo:

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin

        
        query=base_query+'''[S_'''+node_address+'''dw'''+pin+'''00'''+str(status_to_set)+self.getProgressive_msg_id()+'''_#]'''+'''\n'''



      # [S_001sm11135_#]
      elif (out_type=="servo_output"):  #not correctly implemented todo:

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin
        status_to_set=str(status_to_set)
        while (len(status_to_set)) <3:
          status_to_set='0'+status_to_set 

        
        query=base_query+'''[S_'''+node_address+'''sm'''+pin+str(status_to_set)+str(self.query_number)+'''_#]'''+'''\n'''

      #  [S_001aw06155_#] 
      elif (out_type=="analog_output"):  #not correctly implemented todo:

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin
        status_to_set=str(status_to_set)
        while (len(status_to_set)) <3:
          status_to_set='0'+status_to_set 

        query=base_query+'''[S_'''+node_address+'''aw'''+pin+str(status_to_set)+self.getProgressive_msg_id()+'''_#]'''+'''\n'''

      else :
        logprint("error in composeChangeNodeOutputPinStatusQuery,the out_type:"+out_type+" is not yet implemented",verbose=10)
        





      #if  (len(node_address)==len("001")):#  arduino serial node or a node that communicate by radio serial gateway
      if  (len(node_address)==3):#  arduino serial node or a node that communicate by radio serial gateway
        logprint("the node is serial")
        logprint("query to remote node:"+query+"Endquery")
        return(query)


      else:

        logprint("query to network node:"+query)
        return(query,query_expected_answer) 









    def setAddressToNode(self,node_serial_number,old_address,new_address):

      
      logprint("setAddressToNode executed with address:"+str(new_address))
      
      old_hex_node_address=hex(int(old_address)).replace("0x","")  # get the hexadecimal string of the address
      
      if len(old_hex_node_address) < 2:  # to get an address with 2 char
        old_hex_node_address = "0" + old_hex_node_address  

      new_hex_node_address=hex(int(new_address)).replace("0x","")  # get the hexadecimal string of the address
      
      if len(new_hex_node_address) < 2:  # to get an address with 2 char
        new_hex_node_address = "0" + new_hex_node_address  

      #node_address=nodeDict[node_serial_number].getNodeAddress()  
      query="[S_"+old_hex_node_address+"s"+new_hex_node_address+node_serial_number+self.getProgressive_msg_id()+"_#]"+'''\n'''
      #result=make_query_to_radio_node(self.serial_communication,node_serial_number,new_address,msg)
      #if result ==1:
      #  int_address=int(new_address)
      #  if int_address not in node_used_addresses_list:
      #    node_used_addresses_list.append(int_address)

      query_time=time.time()
      number_of_retry_done=0
      priority=10  #99
      query_order=priority
      cmd="set_address"
      objName="set_address"
      status_to_set=new_address
      user="onos_node"
      mail_report_list=[]
   
      logprint("setAddressToNode query:"+query)

      queryToRadioNodeQueue.put((query_order,query,node_serial_number,number_of_retry_done,query_time,objName,status_to_set,user,priority,mail_report_list,cmd))
      if node_query_radio_threads_executing==0:
        if self.serialCommunicationIsWorking==1:
          tr_handle_new_query_to_serial_node = threading.Thread(target=handle_new_query_to_radio_node_thread,args=[self.serial_communication])
          tr_handle_new_query_to_serial_node.daemon = True  #make the thread a daemon thread
          tr_handle_new_query_to_serial_node.start()         
        else:
          logprint("handle_new_query_to_radio_node_thread from setAddressToNode  not executed because there is not a serial transceiver connected",verbose=10) 
       
      return()



    def writeRawMsgToNode(self,node_serial_number,node_address,msg):#deprecated
      if self.serialCommunicationIsWorking==1:
        result=make_query_to_radio_node(self.serial_communication,node_serial_number,node_address,msg)
      else:
        logprint("make_query_to_radio_node from writeRawMsgToNode not executed because there is not a serial transceiver connected",verbose=10)
        result=-2
 
      return(result)



    

    def outputWrite(self,node_serial_number,pinList,statusList,node_obj,objName,previous_status,statusToSetWebObject,output_type,user,priority,mail_report_list,node_password_dict={}):
      #called from changeWebObjectStatus() in  webserver.py 
      
      logprint("executed router_handler digitalwrite()")
      node_address=nodeDict[node_serial_number].getNodeAddress()
      remoteNodeHwModelName=nodeDict[node_serial_number].getNodeHwModel()
      #if len(pinList)<1:
      #  logprint("error len pinList<1 ,len="+str(len(pinList)),verbose=10)

      #if len(pinList)!=len(statusList):

      #  logprint("warning error in the router handler, len pinlist!=statusList",verbose=8)

      #  try: 
      #    print "len pinlist="+str(len(pinList))+ " len statusList="+str(len(statusList))
      #  except Exception as e :
      #    message="can't print len of statusList or pinlist"
      #    logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
        #return(-1) 

   #   if (previous_status==statusToSet): #if nothing needs to be changed...i will return
   #     print "statusToSet equal to previous status.."
   #     return(1)



      if ((str(node_address))=="0"): #if is selected the router as node 
        logprint("the node selected is the router one")     

        if ((output_type=="analog_output")or(output_type=="servo_output")):
          logprint("error the router cannot handle "+output_type+"  type",verbose=8)
          return(-1)


        if (self.bash_pin_enable==1): # if the router has  IO pins
          logprint("the router has the pin io enabled")

          i=0
          logprint("len pinlist="+str(len(pinList)) )
          while i <len(pinList) :
            pinNumber=pinList[i]
            tmp_status_to_set=statusList[i]
            if (pinNumber not in self.router_pin_numbers )or((tmp_status_to_set!=0)and(tmp_status_to_set!=1)):
              message="error the  pin value is out of range of the onosCenter "+self.hwModelName+"pin_number="+str(pinNumber)
              logprint(message,verbose=6 )
              return(-1)

            if self.pins_mode[pinNumber]==0:  # if the pin is setted as input.. then set it as output
              self.pins_mode[pinNumber]=1
              logprint("pin setted as input i try to set it as output",verbose=8)

              try:
                #os.system('echo out > /sys/class/gpio/gpio'+str(pinNumber)+'/direction')  #set the GPIO as output   
                #with lock_bash_cmd:
                with open('/sys/class/gpio/gpio'+str(pinNumber)+'/direction', 'w') as f:   #read the pin status
                  f.write('out')


                  #subprocess.call('echo out > /sys/class/gpio/gpio'+str(pinNumber)+'/direction', shell=True,close_fds=True)
                logprint("pin"+str(pinNumber)+" setted as output ")
              except Exception as e:
                message="error can't configure the pin:"+str(pinNumber)+" as output and set it to "+str(tmp_status_to_set) 
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

                i=i+1
                return(-1)
            try:
              #os.popen('echo '+str(tmp_status_to_set)+' > /sys/class/gpio/gpio'+str(pinNumber)+'/value').read() 
            #  with lock_bash_cmd:

              with open('/sys/class/gpio/gpio'+str(pinNumber)+'/value', 'w') as f:   #read the pin status
                f.write(str(tmp_status_to_set))


                #subprocess.check_output('echo '+str(tmp_status_to_set)+' > /sys/class/gpio/gpio'+str(pinNumber)+'/value', shell=True,close_fds=True) 
              logprint("pin"+str(pinNumber)+" setted to "+str(tmp_status_to_set) )
            except Exception as e:
              message="error can't set the pin:"+str(pinNumber)+" to "+str(tmp_status_to_set)  
              logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

              return(-1)


            i=i+1
          #self.makeChangeWebObjectStatusQuery(objName,statusToSet)


      
          priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":statusToSetWebObject,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })

          return(1) 
          
        else: #the router has't got  IO pins

          logprint("the router has no IO pin")
          return (-1)
        

      #(len(node_address)==len("001"))
      elif (len(node_address)==3): #a local arduino selected or a node with radio ,that uses the serial gateway
        logprint("I write to serial arduino node")
        #self.makeChangeWebObjectStatusQuery(objName,statusToSet)   #banana to remove


        if self.serialCommunicationIsWorking!=1: 
          logprint("error no serial cable",verbose=10)

          #priorityCmdQueue.put( {"cmd":"reconnectSerialPort"}) 
          return(-1)


        else:

          
          if (output_type=="sr_relay"):
            if (len(pinList)!=2):
              logprint("error number of pins !=2")

              return(-1)


          query=self.composeChangeNodeOutputPinStatusQuery(pinList,node_obj,objName,statusList[0],node_serial_number,node_address,output_type,user,priority,mail_report_list,node_password_dict=node_password_dict)
          
          if query=="error_compose_query":
            message="error composed query is not valid,I will not send it to the node"
            logprint(message,verbose=9)
            return(-1)

          logprint("I WRITE THIS QUERY TO SERIAL NODE:"+query+"end")  
          query_time=time.time()
          query_order=priority
          number_of_retry_done=0
          cmd=""
          queryToRadioNodeQueue.put((query_order,query,node_serial_number,number_of_retry_done,query_time,objName,statusToSetWebObject,user,priority,mail_report_list,cmd))

          if node_query_radio_threads_executing==0:
            if self.serialCommunicationIsWorking==1:
              tr_handle_new_query_to_serial_node = threading.Thread(target=handle_new_query_to_radio_node_thread,args=[self.serial_communication])
              tr_handle_new_query_to_serial_node.daemon = True  #make the thread a daemon thread
              tr_handle_new_query_to_serial_node.start()   
            else:
              logprint("handle_new_query_to_radio_node_thread from outputWrite not executed because there is not a serial transceiver connected",verbose=8)


          return()








      else: #str(node_address))!="1" and !=0 --->    remote network node selected
        logprint("I write to/from a remote  network node with address:"+str(node_address) )

        
        logprint("len address="+str(len(node_address)) )
        logprint( "len pinlist="+str(len(pinList)) )
        

        query_composed=self.composeChangeNodeOutputPinStatusQuery(pinList,node_obj,objName,statusList[0],node_serial_number,node_address,output_type,user,priority,mail_report_list,node_password_dict=node_password_dict)


        query_expected_answer=query_composed[1]  #get  query_expected_answer from  return(query,query_expected_answer) 

        query=query_composed[0]  # get query from  return(query,query_expected_answer) 


        queryToNetworkNodeQueue.put({"node_serial_number":node_serial_number,"address":node_address,"query":query,"query_expected_answer":query_expected_answer,"objName":objName,"status_to_set":statusToSetWebObject,"user":user,"priority":priority,"mail_report_list":mail_report_list})

        with lock1_current_node_handler_dict:
          logprint("lock1a from router_handler"+node_serial_number)
          logprint("current_node_handler_dict:"+str(current_node_handler_dict))
          node_not_being_contacted=(node_serial_number not in current_node_handler_dict)

        #with lock2_query_threads:
        #query_threads_number=node_query_network_threads_executing

        if (node_not_being_contacted) : #there is not a query thread running for this node  thread executing 
          logprint("no handler running for this node")



          if (node_query_network_threads_executing<max_number_of_node_query_network_threads_executing): # there are less than x node query thread running
            tr_handle_new_query_to_remote_node = threading.Thread(target=handle_new_query_to_network_node_thread)
            tr_handle_new_query_to_remote_node.daemon = True  #make the thread a daemon thread
            tr_handle_new_query_to_remote_node.start()   
          else:
            logprint("too many node_query_network_threads_executing: "+str(query_threads_number))


        else:#there is already a query thread running for this node  
          print "there is already a query thread running for this node :"+node_serial_number 
          return

    

                       
      return(1) 





    def setHwPinMode(self,node_address,pinNumber,mode):
      logprint("router_handler setHwPinMode() executed")
    
      if node_address=="0" :  #the node is the router itself 

        if pinNumber in self.router_pin_numbers :

          if (self.bash_pin_enable==1):

            if mode=="DOUTPUT":
              self.pins_mode[pinNumber]=1
              try:
                #with lock_bash_cmd:
                with open('/sys/class/gpio/gpio'+str(pinNumber)+'/direction', 'w') as f:   #read the pin status
                  f.write('out')

                  #subprocess.check_output('echo "out" > /sys/class/gpio/gpio'+str(pinNumber)+'/direction', shell=True,close_fds=True)
                #os.popen('echo "out" > /sys/class/gpio/gpio'+str(pinNumber)+'/direction').read()  #set the GPIO as output
              except Exception as e:
                message="error can't set the direction of the pin:  /sys/class/gpio/gpio"+str(pinNumber) 
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))


              for a in self.pins_mode: #check every pin to understand if there are pin setted as input 
                if a==0:
                  self.total_in_pin=self.total_in_pin+1   
                

            if mode=="DINPUT":
              self.pins_mode[pinNumber]=0
              try:
                #with lock_bash_cmd:
                with open('/sys/class/gpio/gpio'+str(pinNumber)+'/direction', 'w') as f:   #read the pin status
                  f.write('in')
                  subprocess.check_output('echo "in" > /sys/class/gpio/gpio'+str(pinNumber)+'/direction', shell=True,close_fds=True)
                #os.popen('echo "in" > /sys/class/gpio/gpio'+str(pinNumber)+'/direction').read()  #set the GPIO as input  
              except Exception as e:
                message="error can't set the direction of the pin:  /sys/class/gpio/gpio"+str(pinNumber)
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))


              #if self.read_thread_running==0:  #if the thread is not running then run it
              #  self.tr_read = threading.Thread(target=self.read_router_pins)
              #  self.tr_read.daemon = True  #make the thread a daemon thread
              #  self.tr_read.start()
                
          else:
            logprint("the router has no IO pin",verbose=8)
            return(-1)
        else:
          logprint("pinNumber out of range",verbose=8)  
          return(-1)

      else:  #banana  make there the configuration pin of remote nodes
        logprint("the node address to write to is "+str(node_address) )       


    def getRouterName(self):
      return(self.hwModelName)



    def close(self):
      self.exit=1
      logprint("class router_handler destroyed")
      try:
        os.close(self.fd)
      except :
        logprint ("tried to close serial port")





