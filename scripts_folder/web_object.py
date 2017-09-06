#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

#note  i put "banana" where there is code to modify in the next release

#import os

from conf import *           # import parameter globalVar.py
global exit  #if exit ==1 all the program stop and exit

global router_hardware_type









class WebObject(object):   # inherit from object python class
    __slots__ = 'name', 'baz','object_type','start_status','styleDict','htmlDict','cmdDict','note','hardware_pin','HwNodeSerialNumber','spareDict','__dict__'

    global exit  #if exit ==1 all the program stop and exit
    __object_type="b"   #alternative is "s" for status viewer or "t" for timer button  or "sb" for static button  

    __function0=""     
    __function1="" 
    __init_function="" 
    __hw_node_name="local"         #by default the hw_node is the arduino connected to the pc by usb serialport
   
   


    def __init__(self,name,obj_type="b",start_status="0",styleDictionary={},htmlDictionary={},cmdDictionary={},note=" ",hardware_pin=[9999],HwNodeSerialNumber=0,spareDict={}):
      self.__object_type=obj_type
      self.__style0="background-color:red ;"
      self.__style1="background-color:green ;"
      self.styleDict={u"0":self.__style0,u"1":self.__style1,u"onoswait":"background-color:grey ;color black","default_s":"background-color:red ;color black"}
      self.styleDict.update(styleDictionary)
      self.__style0=self.styleDict[u"1"]
      self.__style1=self.styleDict[u"0"]
      #self.style_wait=self.styleDict[u"onoswait"] #banana to remove

      self.htmlDict={u"0":name+"=0",u"1":name+"=1"} 

      self.htmlDict.update(htmlDictionary)

      self.html0=self.htmlDict["0"]     
      self.html1=self.htmlDict["1"] 
      self.htmlDict[u"onoswait"]=name+u"WAIT" 
      #self.html_wait=name+u"WAIT"  
      self.html_error=name+u"has status_not_valid"





      self.cmdDict={u"0":"",u"1":"",u"s_cmd":""}
      self.cmdDict.update(cmdDictionary)
      self.__function0=self.cmdDict[u"0"]   #banana to remove
      self.__function1=self.cmdDict[u"1"]   #banana to remove
      self.init_function=self.cmdDict[u"s_cmd"]
      self.object_name=name


      self.required_priority=0
      self.permissions="111111111"
      self.owner="onos_admin" #name of the owner
      self.group=["web_interface","onos_mail_guest"] #list of users that can change the webobject
      self.mail_report_list=[] #list of mail to send the report



      try:
        self.attachedScenarios=list(set(self.attachedScenarios + spareDict["scenarios"]))
      except:
        self.attachedScenarios=[]  #list of attached scenarios  



      #try:
      #  self.obj_address_in_the_node=spareDict["obj_address_in_the_node"]
      #except:
      #  self.obj_address_in_the_node=9999  # if is 9999 this object is not part of a node





      try:
        self.required_priority=spareDict["priority"]
      except:
        self.required_priority=0   


      try:
        self.permissions=spareDict["perm"]
      except:
        self.permissions="111111111" 


      try:
        self.owner=spareDict["own"]
      except:
        self.owner="onos_admin" #name of the webobject owner 


      try:
        self.group=list(set(self.group + spareDict["grp"]))
      except:
        self.group=["web_interface","onos_mail_guest"] #list of users that can change the webobject
 

      try:
        self.mail_report_list= list(set(self.mail_report_list + spareDict["mail_l"])) 
      except:
        self.mail_report_list=[] #list of mail to send the report
 

      self.start_status=start_status
      self.status="0"
     #self.pre_previous_status=self.status 
      self.previous_status=self.status          
      self.note=note
      self.attachedPins=hardware_pin          #arduino pin associated with the web object 
      self.HwNodeSerialNumber=HwNodeSerialNumber
      self.arduinoWriteError=0
      #self.analog_threshold=512
      #self.__hw_node_name="rasberry_b_rev2_only"  #banana to remove
      self.simply_digital_output_group=["digital_output","b","button"] #makes alias
      self.general_digital_output_group=self.simply_digital_output_group+["sr_relay"]+["digital_obj_out"]
      self.general_analog_output_group=["analog_output","servo_output","numeric_var","analog_obj_out"]
      self.general_out_group=self.general_digital_output_group+self.general_analog_output_group+["string_var"] #all output
      self.simply_digital_input_group=["d_sensor","digital_input"]     #make alias
      self.general_input_group=self.simply_digital_input_group+["analog_obj_in","digital_obj_in"]
      self.analog_value_general_group=["analog_output","analog_input","servo_output","numeric_var","cfg_obj","analog_obj_input","analog_obj_out"]#objtype with num values

      self.isActive=1 #tell onos if the web_object is connected or not


     # os.system("echo classe >> numero_oggetti_classe_webobject.txt")

    def InitFunction(self):
      #os.system(self.init_function+'> logs/cmd_init.log 2>&1 &')
      with lock_bash_cmd: 
        subprocess.call(self.init_function+'> logs/cmd_init.log 2>&1 &', shell=True,close_fds=True)
      logprint(self.init_function)
      if self.status in self.cmdDict.keys():
        if self.cmdDict[self.status]!="":
          os.system(self.cmdDict[self.status]+'> logs/cmd1.log 2>&1 &')
          with lock_bash_cmd:
            subprocess.call(self.cmdDict[self.status]+'> logs/cmd1.log 2>&1 &', shell=True,close_fds=True)
      


    def setStatus(self,status):  # set the new status and execute the relative command
        result=0 #banana  to remove 
        a=0
        #if (self.status==status):
        #  print "the status to set in web_object.py is equal to the previus one so i did nothing"
        #  return(1) 

        if (status=="inactive")or(status=="onoswait"):
          if (self.status!="inactive")&(self.status!="onoswait"):   #if the status is not alredy inactive or is not in onoswait
            self.previous_status=self.status 

          self.status=status

          return(1)  

        if status in self.cmdDict.keys():
            #os.system(self.cmdDict[status]+'> logs/cmd1.log 2>&1 &') 
          if self.cmdDict[status]!="":
            with lock_bash_cmd:
              subprocess.call(self.cmdDict[status]+'> logs/cmd1.log 2>&1 &', shell=True,close_fds=True)
        if (self.status!="inactive")&(self.status!="onoswait"):   # to never write onoswait or inactive in self.previous_status
          self.previous_status=self.status 

        self.status=status
        return(1)


    def setHwNodeSerialNumber(self,HwNodeSerialNumber):  # set the hwnode serial number not used

      self.HwNodeSerialNumber=HwNodeSerialNumber
      return(1)   

    def getHwNodeSerialNumber(self):  # get the hwnode serial number     
      return(self.HwNodeSerialNumber)   

 #   def getHwNodeName(self):  # get the hwnode     
 #     return(self.__hw_node_name)  

    def getObjActivity(self):
      return(self.isActive)

    def setObjActivity(self,value):   
      self.isActive=value  
      return()


    def getNotes(self):
        return(self.note)


    def setNotes(self,note):
        self.note=note 
        return(self.note)

    def getStatus(self):
        return(self.status)


    def getStatusForScenario(self):
      try:
        a=float(self.status)
        return(self.status)  # return    "inactive"  to use it in eval...
      except:
        return('"'+self.status+'"')  # return    "inactive"  to use it in eval...


    def getPreviousStatusForScenario(self):
      try:
        a=float(self.status)
        return(self.status)  # return    "inactive"  to use it in eval...
      except:
        return('"'+self.status+'"')  # return    "inactive"  to use it in eval...

    def getStartStatus(self):
        return(self.start_status)

    def getPreviousStatus(self):
        return(self.previous_status)



    def getStyle(self):             #return the actual style  of the button
        if (self.status==0)|(self.status=="0"):
          return(self.styleDict[u"0"])
        if (self.status=="onoswait"):
          return(self.styleDict[u"onoswait"]) 
        if (self.status==1)|(self.status=="1"):
          return(self.styleDict[u"1"])

        try:
          return(self.styleDict[self.status])
        except:
          return(self.styleDict[u"default_s"])

     #   if (self.status>self.analog_threshold): # for analog type
     #     return(self.__style1)
     #   else:
     #     return(self.__style0)


    def getOtherStyle(self):             #return the opposite  style  respect the actual  of the button
        if (self.status==1)|(self.status=="1"):
          return(self.__style0)
        if (self.status=="onoswait"):
          return(self.styleDict[u"onoswait"]) 
        if (self.status==0)|(self.status=="0"):
          return(self.__style1)

      #  if (self.status<self.analog_threshold): # for analog type
      #    return(self.__style1)
      #  else:
      #    return(self.__style0)

          
          
    def getStyle0(self):             #return the static style0  of the button
          return(self.__style0)



    def setStyle0(self,style):             #set the static style0  of the button
          self.__style0=style
          return(self.__style0)


    def setStyle1(self,style1):             #set the static style1  of the button
          self.__style1=style1
          return(self.__style1)


    def getStyle1(self):             #return the static style1  of the button
          return(self.__style1)
   
   
    
    
    def getHtml(self):             #return the opposite  html  respect the actual  of the web object
        if (self.status==0)|(self.status=="0"):
          return(self.htmlDict[u"0"])
        if (self.status=="onoswait"):
          return(self.htmlDict[u"onoswait"]) 
        if (self.status==1)|(self.status=="1"):
          return(self.htmlDict[u"1"])   
        return (self.object_name+u"="+str(self.status)) #for analog type
          
          
    def getOtherHtml(self):             #return the opposite  html  respect the actual  of the web object ,obsolete
        if (self.status==1)|(self.status=="1"):
          return(self.html0)
        if (self.status=="onoswait"):
          return(self.htmlDict[u"onoswait"]) 
        if (self.status==0)|(self.status=="0"):
          return(self.html1)
        return (str(self.status)) #for analog type


    def getHtml0(self):             #return the static html0  of the button
          return(self.html0)


    def getHtml1(self):             #return the static html1  of the button
          return(self.html1)

    def getHtmlWait(self):             #return the static html1  of the button
          return(self.htmlDict[u"onoswait"])



    def setHtml0(self,html0):             #set the static html0  of the button
          self.html0=html0
          self.htmlDict["0"]=html0 
          return(self.html0)


    def setHtml1(self,html1):             #set the static html1  of the button
          self.html1=html1
          self.htmlDict["1"]=html1 
          return(self.html1)

    def setHtmlWait(self,html_w):             #set the static html0  of the button
          self.htmlDict[u"onoswait"]=html_w
          return(self.htmlDict[u"onoswait"])


    def setHtmlDictValue(self,key,value):             #set the static html1  of the button
          self.htmlDict[key]=value 
          return(self.htmlDict[key])



    def setHtmlDict(self,htmlDict):             #set the static html1  of the button
          self.htmlDict=htmlDict 
          return(1)

    def getHtmlDict(self):             #set the static html1  of the button
          return(self.htmlDict)

    def changeCommand(self,status,cmd):
      self.cmdDict[status]=cmd
      return(self.cmdDict[status])

    def changeCommand0(self,f0):
        self.cmdDict["0"]=f0
        return(self.cmdDict["0"])

    def changeCommand1(self,f1):
        self.cmdDict["1"]=f1
        return(self.cmdDict["1"])


    def getCommand0(self):             #return the static command0  of the button
          return(self.cmdDict["0"])

    def setCommand0(self,command0):             #set the static command0  of the button
          self.cmdDict["0"]=command0
          return(self.cmdDict["0"])


    def getCommand1(self):             #return the static command1  of the button
          return(self.cmdDict["1"])


    def setCommand1(self,command1):             #set the static command0  of the button
          self.cmdDict["1"]=command1
          return(self.cmdDict["1"])


    def replaceAttachedScenario(self,previous_scenario_name,new_scenario_name):             #attaches a scenario to this webobject 
      if previous_scenario_name in self.attachedScenarios:
        self.attachedScenarios.remove(previous_scenario_name)
        if new_scenario_name not in self.attachedScenarios:
          self.attachedScenarios.append(new_scenario_name)
          return(1)
      return(0)


    def removeAttachedScenario(self,scenario):             #attaches a scenario to this webobject 
      if scenario in self.attachedScenarios:
        self.attachedScenarios.remove(scenario)


    def attachScenario(self,scenario):             #attaches a scenario to this webobject 
      logprint("scenario:"+scenario+" attached to webobject")
      if scenario not in self.attachedScenarios:
        self.attachedScenarios.append(scenario)
      return(1)


    def getListAttachedScenarios(self):
      return (self.attachedScenarios) 


    def getInitCommand(self):             #return the static init_command  of the button
          return(self.init_function)


    def setInitCommand(self,init_command):             #set the static init_command  of the button
          self.init_function=init_command
          return(self.init_function)



    def setAttachedPin(self,pin):
      self.attachedPins[0]=pin
      self.setType(self.__object_type)
      return (self.attachedPins[0])

    def getAttachedPinList(self):
      """
      |  Return a list containing the object pins used in the hardware and if the webobject is a is a digital_obj 
      |  or an analog_obj or ...obj   it will return the address of this object in the node, 
      |  example:  0 means first object in the node, 1 means second object in the node ...
      |

      """
      return (self.attachedPins)




    def validateStatusToSetObj(self,status):
 #return 1 if the status is compatible with the webobject type and is an output or variable ..
 #return 2 if the status is compatible with the webobject type and is an input
 #return -1 otherwise 

     # if (status==True)or(status=="True"):
     #   status="1"

     # if (status==False)or(status=="False"):
     #   status="0"

      is_number=0 
      is_output=0
      if (status=="inactive") or (status=="onoswait"):
        return(1)

      try:
        status=float(status)
        is_number=1 
      except:
        logprint("the status value passed is not a number is:"+str(status)+"end",verbose=10)
        is_number=0

      if (self.__object_type in self.general_out_group ):
        is_output=1

      if (self.__object_type in self.general_digital_output_group )|(self.__object_type in self.simply_digital_input_group):  #only binary
        if is_number==1:  #the value is a number   
        
  
          if (status>1)|(status<0): # not binary data
            if (self.attachedPins!=[9999]):  # if the obj has a pin
              return (-1)

          if is_output==1:
            return(1)
          else:
            return(2)#is input

        else:
          return(-1)  #not a number



      if self.__object_type in self.analog_value_general_group: # the value must be a float or binary one
        if is_number==1:  #the value is a number      
          if is_output==1:
            return(1)
          else:
            return(2)

        else:
          return(-1)  #not a number
    


      if self.__object_type=="string_var": #text
        return (1)



    def getPermissions(self):
      tmp1=int(self.permissions[0])+int(self.permissions[1])+int(self.permissions[2])   #get 7 from  "111"
      tmp2=int(self.permissions[3])+int(self.permissions[4])+int(self.permissions[5])
      tmp3=int(self.permissions[6])+int(self.permissions[7])+int(self.permissions[8])
      perm=str(tmp1)+str(tmp2)+str(tmp3) 
      return(perm)


    def checkPermissions(self,user,action,priority):  #check the permission for the user and action passed
      if (self.getPermissions()=="777") |(priority==10)|(priority==99) :
        return (1)

      if action=="r":
        if user == self.owner:  #the user is owner
          if  self.permissions[0]=="1" :  #the owner has read access 
            return (1)
        if user in self.group :  #the user is in the group
          if  self.permissions[3]=="1" :  #the group has read access 
            return (1)

        if  self.permissions[6]=="1" :  #anyone has read access 
          return (1)

        return(-1) #the user has not write access

      if action=="w":
        if user == self.owner:  #the user is owner
          if  self.permissions[1]=="1" :  #the owner has write access 
            return (1)
        if user in self.group :  #the user is in the group
          if  self.permissions[4]=="1" :  #the group has write access 
            return (1)

        if  self.permissions[7]=="1" :  #anyone has write access 
            return (1)

        return(-1) #the user has not write access 


      if action=="x":
        if user == self.owner:  #the user is owner
          if  self.permissions[2]=="1" :  #the owner has write access 
            return (1)
        if user in self.group :  #the user is in the group
          if  self.permissions[5]=="1" :  #the group has write access 
            return (1)

        if  self.permissions[8]=="1" :  #anyone has write access 
          return (1)


        return(-1) #the user has not write access
              
      return(-1) #the user has not write access        







    def setPermissions(self,perm):
      perm=bin(int(perm[0]))[2:]+bin(int(perm[1]))[2:]+bin(int(perm[2]))[2:]  #get "111 111 111"  from "777"
      self.permissions=str(perm)
 
      return(self.permissions)


    def setOwner(self,owner):
      self.owner=owner
      return(self.owner)

    def getOwner(self):
      return(self.owner)

    def addToGroup(self,username):
      if username not in self.group:
        self.group.append(username)
      return(self.group)

    def removeFromGroup(self,username):
      if username in group :
        self.group.remove(username)

      return(self.group)


    def getMailReport(self):
      #print "report mail list:",self.mail_report_list 
      return(self.mail_report_list)


    def setMailReport(self,mail_to_add_to_list): #add a list of mails to witch onos will send notes about this objec
      self.mail_report_list=self.mail_report_list+mail_to_add_to_list
      self.mail_report_list=list(set(self.mail_report_list))
      #print "set mail report",self.mail_report_list
      return(self.mail_report_list)

    def getGroup(self):
      return(self.group)


    def setRequiredPriority(self,priority):
      self.required_priority=priority
      return(self.required_priority)

    def getRequiredPriority(self):
      return(self.required_priority)

    def checkRequiredPriority(self,agent_priority):  #retutn -1 if the priority the agent has is les than required
      if agent_priority<self.required_priority:
        #print "error ,required priority is "+str(self.required_priority)
        #errorQueue.put("error ,required priority is "+str(self.required_priority) ) 
        return(-1)
      else:
        return(1)



    def getType(self):
      return(self.__object_type)

    def setType(self,current_type):
      self.__object_type=current_type
      #if (self.__object_type=="d_sensor"):
        #hardware.setPinMode(self.__hw_node_name,self.attachedPins[0],"DINPUT")

    #  if (self.__object_type=="sb"): 
       # hardware.setPinMode(self.__hw_node_name,self.attachedPins[0],"DOUTPUT") banana

   #   if (self.__object_type=="b"): 
       # hardware.setPinMode(self.__hw_node_name,self.attachedPins[0],"DOUTPUT")

#to implement  analog sensor  and pwm output  and servo controll

      return(self.__object_type)

    def getName(self):
        return(self.object_name)


    def setName(self,new_name):
        self.object_name=new_name
        return(self.object_name)

        
    def getObjectDictionary(self):
      tmp_dict={u"objname":self.object_name,u"type":self.__object_type,u"status":self.status,u"styleDict":self.styleDict,u"htmlDict":self.htmlDict,u"cmdDict":self.cmdDict,u"notes":self.note,u"node_sn":self.HwNodeSerialNumber,u"pins":self.attachedPins,u"scenarios":self.attachedScenarios,u"priority":self.required_priority,u"perm":self.permissions,u"own":self.owner,u"grp":self.group,u"mail_l":self.mail_report_list}
      return(tmp_dict)
    

         





