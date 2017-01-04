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
      print "pin used ="
      print self.router_pin_numbers
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


      if (os.path.exists("/sys/class/gpio")==1) : #if the directory exist ,then the hardware has embedded IO pins
        print "discovered local hardware io pins"
        self.bash_pin_enable=1
      else:
        self.bash_pin_enable=0   #disable embedded pins because the harware hasn't got any
        print "no embedded IO pins founded , are you running onos on a pc?"


      if self.serial_arduino_used==1:
        
        #self.serial_communication=self.connectSerialPort()
        try:
          self.serial_communication=Serial_connection_Handler.Serial_connection_Handler()
          self.serialCommunicationIsWorking=self.serial_communication.working
        except Exception, e:
          print "error in opening arduino serial port e:"+str(e.args)
          errorQueue.put("error in opening arduino serial port e:"+str(e.args))
          self.serialCommunicationIsWorking=0


    
        if self.serialCommunicationIsWorking==1:
          print "serial communication working"
         

          #todo: read nodeFw from the serial arduino node..
          #priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":"ProminiS0001","nodeAdress":"001","nodeFw":"5.23"})  
      


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
          print "too many error command the router pins  , are you running onos on a pc?"
          errorQueue.put("too many error commandi the router pins  , are you running onos on a pc?" )
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
        try:
          serial_communication=Serial_connection_Handler.Serial_connection_Handler()
          self.serialCommunicationIsWorking=serial_communication.working
          return(serial_communication)
        except Exception as e: 

          exc_type, exc_obj, exc_tb = sys.exc_info()
          fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
          print(exc_type, fname, exc_tb.tb_lineno)   
          print str(e.args)
          print "error in opening arduino serial port e:"+str(e.args)
          errorQueue.put("error in opening arduino serial port e:"+str(e.args))
          self.serialCommunicationIsWorking=0


    def getProgressive_msg_id(self):

      """
      | Get a progressive id number to append it to the message in order to make it unique
      | 


      """

      self.progressive_msg_number=self.progressive_msg_number+1

      self.progressive_msg_id=str(self.progressive_msg_number)  #todo  create a progressive number

      if  self.progressive_msg_number>8: #restart the number
        self.progressive_msg_number=0 

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
              priorityCmdQueue.put( {"cmd":"setNodePin","nodeSn":self.router_sn,"pinNumber":int(pin),"status_to_set":int(current_state),"write_to_hw":0,"user":"onos_node","priority":priority,"mail_report_list":[] } )

              



      return(1)




    def composeChangeNodeOutputPinStatusQuery(self,pinNumbers,node_obj,objName,status_to_set,node_serial_number,node_address,out_type,user,priority,mail_report_list) :

      """
      | Compose the correct query to change an output pin status on a remote node.
      | The examples are:
      |
      | WARNING old documentation...  
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

      print "composeChangeNodeOutputPinStatusQuery() executed"
     
    


      address=node_obj.getNodeAddress()
      query="error_compose_query"
      base_query=''           #' ''http://'''+address+''':'''+str(node_webserver_port) not used anymore 
   

      if (out_type=="digital_obj"):
        print "digital_obj compose query"
        #query example:  [S_123wp01x_#]
 
        if status_to_set>1:
          print "error in composeChangeNodeOutputPinStatusQuery in digital_obj section,status_to_set>1"
          errorQueue.put("error in composeChangeNodeOutputPinStatusQuery in digital_obj section,status_to_set>1") 
          return (-1)
        remoteNodeHwModelName=node_obj.getNodeHwModel()

        obj_selected=pinNumbers[0]#in this case the obj selected is passed from the pinNumbers number...
    #    print "obj_selected:"+str(obj_selected)
    #    print "remoteNodeHwModelName"+str(remoteNodeHwModelName)
    #    print "remoteNodeHwModelName[pin_mode][digital_obj].keys():"+str(hardwareModelDict[remoteNodeHwModelName]["pin_mode"]["digital_obj"].keys()[obj_selected])

      

        obj_html_name=hardwareModelDict[remoteNodeHwModelName]["pin_mode"]["digital_obj"].keys()[obj_selected]  
      #  print "obj_html_name"+obj_html_name
        query_placeholder=base_query+hardwareModelDict[remoteNodeHwModelName]["query"]["digital_obj"][obj_html_name]
     #   print "query_placeholder:"+query_placeholder
        query_placeholder=query_placeholder.replace("#_objnumber_#",str(pinNumbers[0]))
      #  print "query_placeholder2:"+query_placeholder
        acceptable_len=0
        value=0

        valuelen_pos=query_placeholder.find("#_valuelen")
        if valuelen_pos != -1:
        #  print "valuelen_pos != -1"    
          value=str(status_to_set)
         # print "try:"+re.search('#_valuelen:(.+?)_#',query_placeholder).group(1)  # get the 1 from wp0#_valuelen:1_#
          desidered_len=int (re.search('#_valuelen:(.+?)_#',query_placeholder).group(1))  # get the 1 from wp0#_valuelen:1_#
         # print "desidered_len:"+str(desidered_len)  
          while len(value)<desidered_len:
            value="0"+value            

          query_placeholder=re.sub(r'#_valuelen:.+?_#',value,query_placeholder) # replace  #_valuelen:1_#  with the value
          #query example:  [S_123wp01x_#]



          query='''[S_'''+node_address+query_placeholder+self.getProgressive_msg_id()+'''_#]'''+'''\n'''
         # print "query:::::"+query
          #valuelen_pos=query_placeholder.find("valuelen")
          #string_to_replace_with_value=query_placeholder[valuelen_pos:valuelen_pos+10]
          #query=query_placeholder.replace(string_to_replace_with_value,value)
           

          print "composed query was:"+query+"mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
          
          errorQueue.put("the query was:"+query) 


      if (out_type=="sr_relay"):
        pin1=str(pinNumbers[1])
        pin0=str(pinNumbers[0])
        if (len (pin0) <2):
          pin0='0'+pin0
        if (len (pin1) <2):
          pin1='0'+pin1

        #  [S_001sr04051_#] 
        query=base_query+'''[S_'''+node_address+'''sr'''+pin0+pin1+str(status_to_set)+self.getProgressive_msg_id()+'''_#]'''+'''\n'''

      if (out_type=="digital_output"):# [S_001dw06001_#]

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin

        
        query=base_query+'''[S_'''+node_address+'''dw'''+pin+'''00'''+str(status_to_set)+self.getProgressive_msg_id()+'''_#]'''+'''\n'''



      # [S_001sm11135_#]
      if (out_type=="servo_output"):

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
      if (out_type=="analog_output"):

        if type(pinNumbers) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
          pinNumbers=[pinNumbers]
        pin=str(pinNumbers[0])
        if (len (pin) <2):
          pin='0'+pin
        status_to_set=str(status_to_set)
        while (len(status_to_set)) <3:
          status_to_set='0'+status_to_set 

        query=base_query+'''[S_'''+node_address+'''aw'''+pin+str(status_to_set)+self.getProgressive_msg_id()+'''_#]'''+'''\n'''



      #if  (len(node_address)==len("001")):#  arduino serial node or a node that communicate by radio serial gateway
      if  (len(node_address)==3):#  arduino serial node or a node that communicate by radio serial gateway
        print "the node is serial"
        print "query to remote node:"+query
        return(query)

      print "query to remote node:"+query


     
      queryToNetworkNodeQueue.put({"node_serial_number":node_serial_number,"address":address,"query":query,"objName":objName,"status_to_set":status_to_set,"user":user,"priority":priority,"mail_report_list":mail_report_list})

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
          tr_handle_new_query_to_remote_node = threading.Thread(target=handle_new_query_to_network_node_thread)
          tr_handle_new_query_to_remote_node.daemon = True  #make the thread a daemon thread
          tr_handle_new_query_to_remote_node.start()   
        else:
          print "too many node_query_threads_executing: ",query_threads_number


      else:#there is already a query thread running for this node  
        print "there is already a query thread running for this node :"+node_serial_number 

      return(query) 









    def setAddressToNode(self,node_serial_number,new_address):

      
      print "new address for the node:"+str(new_address)


      node_address=nodeDict[node_serial_number].getNodeAddress()  
      query="[S_"+node_address+"sa"+new_address+node_serial_number+self.getProgressive_msg_id()+"_#]"+'''\n'''
      #result=make_query_to_radio_node(self.serial_communication,node_serial_number,new_address,msg)
      #if result ==1:
      #  int_address=int(new_address)
      #  if int_address not in next_node_free_address_list:
      #    next_node_free_address_list.append(int_address)

      query_time=time.time()
      number_of_retry_done=0
      priority=99
      query_order=priority
      cmd="set_address"
      objName="set_address"
      status_to_set=new_address
      user="onos_node"
      mail_report_list=[]

      queryToRadioNodeQueue.put((query_order,query,node_serial_number,number_of_retry_done,query_time,objName,status_to_set,user,priority,mail_report_list,cmd))
      if node_query_radio_threads_executing==0:
        if self.serialCommunicationIsWorking==1:
          tr_handle_new_query_to_serial_node = threading.Thread(target=handle_new_query_to_radio_node_thread,args=[self.serial_communication])
          tr_handle_new_query_to_serial_node.daemon = True  #make the thread a daemon thread
          tr_handle_new_query_to_serial_node.start()         
        else:
          print("handle_new_query_to_radio_node_thread from setAddressToNode  not executed because there is not a serial transceiver connected") 
          errorQueue.put("handle_new_query_to_radio_node_thread from setAddressToNode  not executed because there is not a serial transceiver connected")

      return()



    def writeRawMsgToNode(self,node_serial_number,node_address,msg):#deprecated
      if self.serialCommunicationIsWorking==1:
        result=make_query_to_radio_node(self.serial_communication,node_serial_number,node_address,msg)
      else:
        print("make_query_to_radio_node from writeRawMsgToNode not executed because there is not a serial transceiver connected")
        errorQueue.put("make_query_to_radio_node from writeRawMsgToNode not executed because there is not a serial transceiver connected")
        result=-2
 
      return(result)



    

    def outputWrite(self,node_serial_number,pinList,statusList,node_obj,objName,previous_status,statusToSetWebObject,output_type,user,priority,mail_report_list):
      
      
      print "executed router_handler digitalwrite()"
      node_address=node_obj.getNodeAddress()
      remoteNodeHwModelName=node_obj.getNodeHwModel()
      if len(pinList)<1:
        print "error len pinList<1 ,len="+str(len(pinList))
        errorQueue.put( "error len pinList<1 ,len="+str(len(pinList)))

      if len(pinList)!=len(statusList):

        print "warning error in the router handler, len pinlist!=statusList"
        errorQueue.put("warning error in the router handler, len pinlist!=statusList" )
        try: 
          print "len pinlist="+str(len(pinList))+ " len statusList="+str(len(statusList))
        except Exception, e :
          print "can't print len of statusList or pinlist"
          print (e.args) 
        #return(-1) 

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


      
          priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":statusToSetWebObject,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })

          return(1) 
          
        else: #the router has't got  IO pins

          print "the router has no IO pin"
          return (-1)
        

      #(len(node_address)==len("001"))
      if (len(node_address)==3): #a local arduino selected or a node with radio ,that uses the serial gateway
        print "i write to serial arduino node"
        #self.makeChangeWebObjectStatusQuery(objName,statusToSet)   #banana to remove


        if self.serialCommunicationIsWorking!=1: 
          print "error no serial cable"
          errorQueue.put("error no serial cable")  
          #priorityCmdQueue.put( {"cmd":"reconnectSerialPort"}) 
          return(-1)


        else:

          
          if (output_type=="sr_relay"):
            if (len(pinList)!=2):
              print "error number of pins !=2"
              errorQueue.put("error number of pins !=2  in router_handler" ) 
              return(-1)


          query=self.composeChangeNodeOutputPinStatusQuery(pinList,node_obj,objName,statusList[0],node_serial_number,node_address,output_type,user,priority,mail_report_list)
          print "I WRITE THIS QUERY TO SERIAL NODE:"+query+"end"  
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
              print("handle_new_query_to_radio_node_thread from outputWrite not executed because there is not a serial transceiver connected")
              errorQueue.put("handle_new_query_to_radio_node_thread from outputWrite not executed because there is not a serial transceiver connected")

          return()








      else: #str(node_address))!="1" and !=0 --->    remote network node selected
        print "i write to/from a remote node with address:"+str(node_address)

        
        print "len address="+str(len(node_address))
        print "len pinlist="+str(len(pinList))
        

        if (output_type=="sr_relay"):
          if (len(pinList)==2):
            self.composeChangeNodeOutputPinStatusQuery(pinList,node_obj,objName,statusList[0],node_serial_number,node_address,output_type,user,priority,mail_report_list)
            return(1)
          else:
            print "error number of pins !=2"
            errorQueue.put("error number of pins !=2" ) 
            return(-1)
        i=0
        while i <len(pinList) : 
          pinNumber=pinList[i]
          tmp_status_to_set=statusList[i]
          if (pinNumber not in node_obj.getUsedPins()):
            print 'error the  pin value is out of range of node :'+remoteNodeHwModelName+"pin_number="+str(pinNumber)
            errorQueue.put('error the  pin value is out of range of node :'+remoteNodeHwModelName+"pin_number="+str(pinNumber) )
            print "status to set="+str(tmp_status_to_set)
            errorQueue.put("status to set="+str(tmp_status_to_set) )
            print str(pinNumber)
            errorQueue.put(str(pinNumber))
            return(-1)


          self.composeChangeNodeOutputPinStatusQuery(pinNumber,node_obj,objName,tmp_status_to_set,node_serial_number,node_address,output_type,user,priority,mail_report_list)
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












