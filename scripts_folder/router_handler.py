# -*- coding: UTF-8 -*-


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




from globalVar import *
from node_query_handler import *



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

      self.exit=0
      self.router_pin_numbers=[]
      #self.read_thread_running=0   
      self.arduino_used=0  
      self.local_pin_enabled=0
    
      self.__maxPin=hardwareModelDict["max_pin"]    #17 -2 used for uart
    
      self.router_pin_numbers=getListUsedPinsByHardwareModel(self.hwModelName)
      print "pin used ="
      print self.router_pin_numbers
      #print "digital input router pin total number= "
      #print (getListPinsConfigByHardwareModel(self.hwModelName,"digital_input"))
      
      self.router_input_pin=getListPinsConfigByHardwareModel(self.hwModelName,"digital_input")
      self.total_in_pin=len(self.router_input_pin) #get the number of digital inputs

      if self.__hardware_type=="rasberry_b_rev2_only":  #banana to import this from hardwareModelDict
        self.bash_pin_enable=1

      if self.__hardware_type=="gl.inet_only":
        self.bash_pin_enable=1


      if self.__hardware_type=="gl.inet_with_arduino2009":
        self.arduino_used=1
        arduino=arduino_handler.ArduinoHandler()
        self.bash_pin_enable=1


      if (os.path.exists("/sys/class/gpio")==1) : #if the directory exist ,then the hardware has embedded IO pins
        print "discovered local hardware io pins"
        self.bash_pin_enable=1
      else:
        self.bash_pin_enable=0   #disable embedded pins because the harware hasn't got any
        print "no embedded IO pins founded , are you running onos on a pc?"

      error_number=0   #count how many errors..
      if self.bash_pin_enable==1:

        for pin in self.router_pin_numbers:
          self.pins_status[pin]=0  # create the pin var in the dictionary
          try:
            print "i try to execute echo "+str(pin)+" > /sys/class/gpio/export "
            #os.popen('echo '+str(pin)+' > /sys/class/gpio/unexport ').read()  #remove a GPIO file access
            with lock_bash_cmd:
              subprocess.call('echo '+str(pin)+' > /sys/class/gpio/unexport ', shell=True)

            #os.popen('echo '+str(pin)+' > /sys/class/gpio/export ').read()  #Create a GPIO file access
              subprocess.call('echo '+str(pin)+' > /sys/class/gpio/export ', shell=True,close_fds=True)

          except Exception, e :
            error_number=error_number+1
            print "error can't create GPIO pin:"+str(pin)+" and set its mode :"+str(e.args)
            errorQueue.put("error can't create GPIO pin:"+str(pin)+" and set its mode :"+str(e.args))
          time.sleep(1)


          if pin in self.router_input_pin:
            self.pins_mode[pin]=0  # set the pin as input
            try:
              #with lock_bash_cmd:
              with open('/sys/class/gpio/gpio'+str(pin)+'/direction', 'w') as f:   #read the pin status
                f.write('in')
                #subprocess.call('echo in > /sys/class/gpio/gpio'+str(pin)+'/direction', shell=True,close_fds=True)   
              #os.popen('echo in > /sys/class/gpio/gpio'+str(pin)+'/direction').read()  #set the GPIO as input  
            except Exception, e :
              print "error trying to read a router pin :"+str(e.args)
              errorQueue.put( "error trying to read a router pin :"+str(e.args))
              error_number=error_number+1
            
            time.sleep(1)


            try:
              print "i try to read the status with: cat /sys/class/gpio/gpio"+str(pin)+"/value"
              #with lock_bash_cmd:
              with open('/sys/class/gpio/gpio'+str(pin)+'/value', 'r') as f:   #read the pin status
                read_data = f.read()
              status=read_data[0] 
                #status=subprocess.check_output("cat /sys/class/gpio/gpio"+str(pin)+"/value", shell=True,close_fds=True)
              #status=os.popen("cat /sys/class/gpio/gpio"+str(pin)+"/value").read()
              self.pins_status[pin]=int(status)
            except Exception, e :
              self.pins_status[pin]=0
              print "error in reading pin"+str(pin)
              errorQueue.put("error00 in reading pin"+str(pin) ) 
              error_number=error_number+1

          else:
            self.pins_mode[pin]=1  # set the pin as output
            print "i try to set the pin as output"
            try:
              #with lock_bash_cmd:
              with open('/sys/class/gpio/gpio'+str(pin)+'/direction', 'w') as f:   #read the pin status
                f.write('out')
                #os.popen('echo out > /sys/class/gpio/gpio'+str(pin)+'/direction').read()  #set the GPIO as output 
                #subprocess.call('echo out > /sys/class/gpio/gpio'+str(pin)+'/direction', shell=True,close_fds=True)
            except Exception, e :
              error_number=error_number+1
              print "error setting pin"+str(pin)+ "as output"
              errorQueue.put( "error setting pin"+str(pin)+ "as output")
              errorQueue.put(e.args) 
        if error_number >5:
          self.bash_pin_enable=0  #disable the bash pin command if too many error happen
          print "too many error commandi the router pins  , are you running onos on a pc?"
          errorQueue.put("too many error commandi the router pins  , are you running onos on a pc?" )
#        if ( (len (self.pin_numbers) >0)&(self.bash_pin_enable==1)): 
#        #if the router hardware has any hardware pins ..then run the thread in order to read them
#          self.exit==0
#          self.tr_read = threading.Thread(target=self.read_router_pins)
#          self.tr_read.daemon = True  #make the thread a daemon thread

#          self.tr_read.start()
#        else:
#          print "i don't start the reading thread because i can't read the hw pins"






    def read_router_pins(self):   # thread  function to read changing of pin status
      #print "read_router_pins() executed"
      if ( (len (self.router_pin_numbers) >0)&(self.bash_pin_enable==1)): 
        #if the router hardware has any hardware pins ..then run the thread in order to read them
        #print "starting to read pins"
        x=0 #void operation
      else:
        print "i don't start the reading function because i can't read the router hw pins"
        errorQueue.put("i don't start the reading function because i can't read the router hw pins")  
        return(-1)

      if (self.total_in_pin<1) :#there is no input pin to read
        print "there is no input pin to read"
        errorQueue.put("there is no input pin to read")
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
            except Exception, e:
              current_state=-1 
              print "error reading router pin status  "+str(pin)+", e:"+str(e.args)
              errorQueue.put("error reading router pin status  "+str(pin)+", e:"+str(e.args))  
            

            current_state=int(status)
              #print "the current pin status is: "+str(current_state)
            #except:
            #  print "error in reading pin"+str(pin)
            #  continue  #restart the loop

            if self.pins_status[pin]!=current_state:  #if the value is different from the old one
              self.pins_status[pin]=current_state  # update the old pin status with the current one
              print "the router pin: "+str(pin) +" input status changed to: "+str(current_state)


              #priority=99   usersDict["onos_node"]["priority"]               
              priority=99   #99 will allow the x but will not increase the object priority       
              priorityCmdQueue.put( {"cmd":"setNodePin","node_sn":self.router_sn,"pinNumber":int(pin),"status_to_set":int(current_state),"write_to_hw":0,"user":"onos_node","priority":priority,"mail_report_list":[] } )

              



      return(1)




    def composeChangeNodeOutputPinStatusQuery(self,pinNumbers,node_obj,objName,status_to_set,node_serial_number,out_type,user,priority,mail_report_list) :


      print "composeChangeNodeOutputPinStatusQuery() executed"

      numeric_serial_number=node_serial_number[-4:]     # example get 0001  from "ProminiA0001"
      address=node_obj.getNodeAddress()
      base_query=''           #' ''http://'''+address+''':'''+str(node_webserver_port)
      if (out_type=="sr_relay"):
        pin1=str(pinNumbers[0])
        pin0=str(pinNumbers[1])
        if (len (pin0) <2):
          pin0='0'+pin0
        if (len (pin1) <2):
          pin1='0'+pin1

  
        query=base_query+'''onos_r'''+pin0+pin1+'''v'''+str(status_to_set)+'''s'''+numeric_serial_number+'''_#]'''

      if (out_type=="digital_output"):

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin

        #onos_d07v001s0001_#]
        query=base_query+'''onos_d'''+pin+'''v'''+'''00'''+str(status_to_set)+'''s'''+numeric_serial_number+'''_#]'''

      if (out_type=="servo_output"):

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin
        status_to_set=str(status_to_set)
        while (len(status_to_set)) <3:
          status_to_set='0'+status_to_set 

        #onos_s07v180s0001_#]
        query=base_query+'''onos_s'''+pin+'''v'''+status_to_set+'''s'''+numeric_serial_number+'''_#]''' 


      if (out_type=="analog_output"):

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin
        status_to_set=str(status_to_set)
        while (len(status_to_set)) <3:
          status_to_set='0'+status_to_set 

        #onos_a07v100s0001_#]
        query=base_query+'''onos_a'''+pin+'''v'''+status_to_set+'''s'''+numeric_serial_number+'''_#]''' 








      print "query to remote node:"+query

     
      queryToNodeQueue.put({"node_serial_number":node_serial_number,"address":address,"query":query,"objName":objName,"status_to_set":status_to_set,"user":user,"priority":priority,"mail_report_list":mail_report_list})

      with lock1_current_node_handler_list:
        print "lock1a from router_handler"+node_serial_number
        print "current_node_handler_list:",current_node_handler_list
        node_not_being_contacted=(node_serial_number not in current_node_handler_list)

      #with lock2_query_threads:
      #query_threads_number=node_query_threads_executing

      if (node_not_being_contacted) : #there is not a query thread running for this node  thread executing 
        print "no handler running for this node"

        #handle_new_query_to_remote_node(node_serial_number,address,query,objName,status_to_set,user,priority,mail_report_list)

        if (node_query_threads_executing<max_number_of_node_query_threads_executing): # there are less than x node query thread running
          tr_handle_new_query_to_remote_node = threading.Thread(target=handle_new_query_to_remote_node_thread)
          tr_handle_new_query_to_remote_node.daemon = True  #make the thread a daemon thread
          tr_handle_new_query_to_remote_node.start()   
        else:
          print "too many node_query_threads_executing: ",query_threads_number


      else:#there is already a query thread running for this node  
        print "there is already a query thread running for this node :"+node_serial_number 

      return() 














    def outputWrite(self,node_serial_number,pinList,statusList,node_obj,objName,previous_status,statusToSet,output_type,user,priority,mail_report_list):
      
      
      print "executed router_handler digitalwrite()"
      node_address=node_obj.getNodeAddress()
      remoteNodeHwModel=node_obj.getNodeHwModel()
      if len(pinList)<1:
        print "error len pinList<1 ,len="+str(len(pinList))
        errorQueue.put( "error len pinList<1 ,len="+str(len(pinList)))

      if len(pinList)!=len(statusList):

        print "error in the router handler, len pinlist!=statusList"
        errorQueue.put("error in the router handler, len pinlist!=statusList" )
        try: 
          print "len pinlist="+str(len(pinList))+ " len statusList="+str(len(statusList))
        except Exception, e :
          print "can't print len of statusList or pinlist"
          print (e.args) 
        return(-1) 

   #   if (previous_status==statusToSet): #if nothing needs to be changed...i will return
   #     print "statusToSet equal to previous status.."
   #     return(1)



      if ((str(node_address))=="0"): #if is selected the router as node 
        print "the node selected is the router one"      

        if ((output_type=="analog_output")or(output_type=="servo_output")):
          print "error the router cannot handle "+output_type+"  type"
          errorQueue.put( "error the router cannot handle "+output_type+"  type")
          return(-1)


        if (self.bash_pin_enable==1): # if the router has  IO pins
          print "the router has the pin io enabled"

          i=0

          print "len pinlist="+str(len(pinList))
          while i <len(pinList) :
            pinNumber=pinList[i]
            tmp_status_to_set=statusList[i]
            if (pinNumber not in self.router_pin_numbers )or((tmp_status_to_set!=0)and(tmp_status_to_set!=1)):
              print 'error the  pin value is out of range of rasberry '+self.hwModelName+"pin_number="+str(pinNumber)
              errorQueue.put('error the  pin value is out of range of rasberry '+self.hwModelName+"pin_number="+str(pinNumber) )
              print "status to set="+str(tmp_status_to_set)
              errorQueue.put(  "status to set="+str(tmp_status_to_set))
              return(-1)

            if self.pins_mode[pinNumber]==0:  # if the pin is setted as input.. then set it as output
              self.pins_mode[pinNumber]=1
              print "pin setted as input i try to set it as output"
              errorQueue.put("pin setted as input i try to set it as output") 
              try:
                #os.system('echo out > /sys/class/gpio/gpio'+str(pinNumber)+'/direction')  #set the GPIO as output   
                #with lock_bash_cmd:
                with open('/sys/class/gpio/gpio'+str(pinNumber)+'/direction', 'w') as f:   #read the pin status
                  f.write('out')


                  #subprocess.call('echo out > /sys/class/gpio/gpio'+str(pinNumber)+'/direction', shell=True,close_fds=True)
                print "pin"+str(pinNumber)+" setted as output "
              except Exception, e :
                print "error can't configure the pin:"+str(pinNumber)+" as output and set it to "+str(tmp_status_to_set)   
                errorQueue.put("error can't configure the pin:"+str(pinNumber)+" as output and set it to "+str(tmp_status_to_set) )
                errorQueue.put(e.args) 
                i=i+1
                return(-1)
            try:
              #os.popen('echo '+str(tmp_status_to_set)+' > /sys/class/gpio/gpio'+str(pinNumber)+'/value').read() 
            #  with lock_bash_cmd:

              with open('/sys/class/gpio/gpio'+str(pinNumber)+'/value', 'w') as f:   #read the pin status
                f.write(str(tmp_status_to_set))


                #subprocess.check_output('echo '+str(tmp_status_to_set)+' > /sys/class/gpio/gpio'+str(pinNumber)+'/value', shell=True,close_fds=True) 
              print "pin"+str(pinNumber)+" setted to "+str(tmp_status_to_set)
            except Exception, e :
              print "error can't set the pin:"+str(pinNumber)+" to "+str(tmp_status_to_set)   
              errorQueue.put("error can't set the pin:"+str(pinNumber)+" to "+str(tmp_status_to_set)   )
              errorQueue.put(e.args) 
              return(-1)


            i=i+1
          #self.makeChangeWebObjectStatusQuery(objName,statusToSet)


      
          priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":statusToSet,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })
          return(1) 
          
        else: #the router has't got  IO pins

          print "the router has no IO pin"
          return (-1)
        


      if ((str(node_address))=="1"): #a local arduino selected   not implemented yet 
        print "i write to/from a remote node selected"
        #self.makeChangeWebObjectStatusQuery(objName,statusToSet)   #banana to remove
        if ((self.arduino_used==1)&(node_address=="1")):  #check if arduino is enabled correctly and is selected with 1
          print "digital write used on arduino"
          if len(pinList) >1: 
            print "i have to set more than a pin at the same time"
              
            packet_list=[]
              
            i=0 
            pinList=pinList.sort() #order the list by pin number
            previus_section=-1
            section=previus_section
            while (i<len(pinList)):
              section=node_obj.getNodeSectionStatusByPin(pinList[i])[0]
              if(section!=previus_section):
                previus_section=section
                section_status=node_obj.getNodeSectionStatusByPin(pinList[i])[1]#get the section status 
                packet_list.append(section,section_status)
              i=i+1
              #now inside  packet_list i have a tuple 
              #where the first element is the pin byte section and the second the data is the status byte for that section
            i=0
            for a in packet_list:  #write to arduino all the registers
              arduino.digitalWriteSection(node_address,a[0],a[1],objName,previous_status,statusToSet)


          else: #only one pin to set           
            arduino.digitalWrite(node_address,pinList[0],statusList[0],objName,previous_status,statusToSet)#write to arduino to set a pin        



      else: #str(node_address))!="1" and !=0 --->    remote node selected
        print "i write to/from a remote node with address:"+str(node_address)

        i=0
        print "len address="+str(len(node_address))
        print "len pinlist="+str(len(pinList))
        

        if (output_type=="sr_relay"):
          if (len(pinList)==2):
            self.composeChangeNodeOutputPinStatusQuery(pinList,node_obj,objName,statusToSet,node_serial_number,output_type,user,priority,mail_report_list)
            return(1)
          else:
            print "error number of pins !=2"
            errorQueue.put("error number of pins !=2" ) 
            return(-1)

        while i <len(pinList) :
          pinNumber=pinList[i]
          tmp_status_to_set=statusList[i]
          if (pinNumber not in node_obj.getUsedPins()):
            print 'error the  pin value is out of range of node :'+remoteNodeHwModel+"pin_number="+str(pinNumber)
            errorQueue.put('error the  pin value is out of range of node :'+remoteNodeHwModel+"pin_number="+str(pinNumber) )
            print "status to set="+str(tmp_status_to_set)
            errorQueue.put("status to set="+str(tmp_status_to_set) )
            print str(pinNumber)
            errorQueue.put(str(pinNumber))
            return(-1)


          self.composeChangeNodeOutputPinStatusQuery(pinNumber,node_obj,objName,tmp_status_to_set,node_serial_number,output_type,user,priority,mail_report_list)
          i=i+1
        #start a thread query to the node

                        

      return(1) 





    def setHwPinMode(self,node_address,pinNumber,mode):
      print "router_handler setHwPinMode() executed"
    
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
              except Exception, e :
                print "error can't set the direction of the pin:  /sys/class/gpio/gpio"+str(pinNumber)
                errorQueue.put("error can't set the direction of the pin:  /sys/class/gpio/gpio"+str(pinNumber) )
                errorQueue.put(e.args) 
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
              except Exception, e :
                print "error can't set the direction of the pin:  /sys/class/gpio/gpio"+str(pinNumber)
                errorQueue.put( "error can't set the direction of the pin:  /sys/class/gpio/gpio"+str(pinNumber)) 
                errorQueue.put(e.args) 
              #if self.read_thread_running==0:  #if the thread is not running then run it
              #  self.tr_read = threading.Thread(target=self.read_router_pins)
              #  self.tr_read.daemon = True  #make the thread a daemon thread
              #  self.tr_read.start()
                
          else:
            print "the router has no IO pin"
            return(-1)
        else:
          print "pinNumber out of range"   
          return(-1)

      else:  #banana  make there the configuration pin of remote nodes
        print "the node address to write to is "+str(node_address)       


    def getRouterName(self):
      return(self.hwModelName)



    def close(self):
      self.exit=1
      print "class router_handler destroyed"
      try:
        os.close(self.fd)
      except :
        print "tried to close serial port"












