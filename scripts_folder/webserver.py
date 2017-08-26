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

#a way to run it on back ground:  sudo python webserver.py >file.log 2>&1



#usefull sources  http://en.wikipedia.org/wiki/List_of_HTTP_status_codes



from conf import *           # import parameter from conf.py  which will read the data from the  json 
from mail_agent import *

global scenarioDict
global objectDict
global zoneDict
global exit  #exit is on conf.py  f exit ==1 all the program stop and exit
global hardware
global nodeDict
global scenarios_enable
global accept_only_from_white_list  
global enable_mail_service
global enable_mail_output_service
global logTimeout 
global login_required 
global mail_whiteList
global online_server_enable
global online_usersDict
global timezone
global enable_onos_auto_update
global conf_options
global node_password_dict





exit=0
check_log_len_time=1

default_new_zone_value="TYPE_NEW_ROOM_HERE_AND_CLICK_SUBMIT"
default_new_obj_value="TYPE A NEW OBJECT NAME HERE"
default_new_obj_value2="TYPE_A_NEW_OBJECT_NAME_HERE"
default_rename_zone_value="RENAME IT AND CLICK SUBMIT"
default_rename_zone_value2="RENAME_IT_AND_CLICK_SUBMIT"
#new_head_meta='<meta http-equiv="Refresh" content="1">'
new_head_meta=''''''
in_file=''
onos_automatic_javascript=''
try:
  with codecs.open("refreshPage.html",'r',encoding='utf8') as f:
      in_file = f.read()
      onos_automatic_javascript=in_file

except Exception as e :
  logprint("error I can't find refreshPage.html")
  onos_automatic_javascript="error_loading refreshPage.html"

#in_file=open("refreshPage.html","r")     #get the javascript code to reload the webpages
#new_javascript= in_file.read()
#onos_automatic_javascript=in_file

#document.getElementById("content").innerHTML = "whatever";

web_page_not_found='<html><head><style type="text/css"></style></head><body>error  no index.html found in the  directory </body></html>' 


print ("fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")





get_zone_manager_inner_html='''<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/css/zone-setup-css.css" type="text/css" media="all" />
  <meta name="viewport" content="width=device-width" , initial-scale=1, maximum-scale=1"> 
  <meta charset="utf-8">
  <title>O.N.O.S</title>
<script type="text/javascript" language="javascript">function SelectAll(id){    document.getElementById(id).focus();   document.getElementById(id).select();}</script>
</head>
<body>
<form action="" method="POST"><input type="hidden" name="zone_manager" value="/setup/zone_manager">

  
<div id="buttons">
  <input type="submit" value="Submit">
  <a href="/"><div id="home">HOME</div></a>
  <a href="/setup/"><div id="back">BACK</div></a>

</div>
  

 <div id="header">ZONE SETUP</div>


<div id="riga">

<input type="text" id="new_room_form"  name="new_room" onclick="SelectAll('new_room_form')";  value="TYPE NEW ROOM HERE AND CLICK SUBMIT">

</div>
'''





oldpag=" "
#old_zoneDict={}
#old_objectDict={}
#old_web_page=" "

baseDir=""

nothing_changed=0






#objectDict  contain all the web_object  and the key of the dictionary for each web_object is the name of the web_object


notes="Enter_The_Web_Object_Notes"
no_pin_selected="no_pin"
type_b="checked"
type_sb=""
type_l=""
current_status0=" "
current_status1=" "
style0="/*Enter here the style you want your web object to have when its status is 0 */"
style1="/*Enter here the style you want your web object to have when its status is 0 */"
html0="<!-- Enter here the html you want your web object to display when its status is 0  -->"
html1="<!-- Enter here the html you want your web object to display when its status is 1  -->"
autoCssIndicator='/*soacdnrtc start of automatic css,do not remove this comment*/'
reload_page_indicator='<!--soacdnrtc start of the part reloaded by the browser by javascript --> <div id="ReloadThis" >'
reload_page_end_indicator='<!--soacdnrtc end of the part reloaded by the browser by javascript--></div>'
command0=" "
command1=" "
init_command=" "



 


#os.system('''ntpd -q -p 0.openwrt.pool.ntp.org''') 

#try:
  
#  prof = open('/etc/profile', 'r')
#  profile=prof.read()
#  prof.close()
   #print profile
#  if (string.find(profile,timezone)== -1) :
#    os.system('echo "export TZ='+timezone+'">> /etc/profile') ##export TZ="CET-1CEST,M3.5.0,M10.5.0/3"
#    print " onos set the timezone to:"+timezone
#    os.system("source /etc/profile") #reload the profile to update time
#  else:
#    print "timezone ok"
  #banana to add the change of the line to change the timezone
#except:
#  print "error onos can't set the timezone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"





def compareText(a,b): #return true if a==b
  ret=0 
  try:
    a.decode('UTF-8')==b.decode('UTF-8')
    ret=1
  except:
    ret=-1  
    logprint( "error can't decode:"+str(a)+" or cant decode:"+str(b))


   
  return (ret)


def sortZonesByOrderNumber():
  logprint ("sortZonesByOrderNumber() executed")
  zone_list=[]
  logprint("zoneDict:"+str(zoneDict),verbose=1)
 

  for a in range (0,len(zoneDict.keys())):
    for b in zoneDict.keys():
      if (a==zoneDict[b]["order"]) :  # select the next zone by the order number
        zone_list.append(b)
  logprint ("list returned:"+str(zone_list) )
  return(zone_list)
   






def transform_object_to_dict(object_dictionary):


  obj_tmp_dict={}

  for b in object_dictionary.keys():
    a=object_dictionary[b]   #bug  return ascii and not unicode?
    name=a.getName()
    obj_tmp_dict[name]={u"objname":name,u"obj_type":a.getType(),u"obj_status":a.getStatus(),u"obj_style0":a.getStyle0(),u"obj_style1":a.getStyle1(),u"obj_html0":a.getHtml0(),u"obj_html1":a.getHtml1(),u"obj_cmd0":a.getCommand0(),u"obj_cmd1":a.getCommand1(),u"obj_init_cmd":a.getInitCommand(),u"obj_notes":a.getNotes(),u"node_serial_number":a.getHwNodeSerialNumber(),u"obj_Pins":a.getAttachedPinList()}
  return (obj_tmp_dict)  


def transform_object_to_dict_to_backup(object_dictionary):


  obj_tmp_dict={}

  for b in object_dictionary.keys():
    a=object_dictionary[b]   #bug  return ascii and not unicode?
    name=a.getName()
    obj_tmp_dict[name]=a.getObjectDictionary()
  return (obj_tmp_dict)  



def updateJson(object_dictionary,nodeDictionary,zoneDictionary,scenarioDictionary,conf_options_dictionary):  # save the current config to a json file named data.json

  logprint("updateJson executed")

#json doesn't support saving objects  ..so i save all the variables of each objects
#to get back the pin of the object you have to write:
#  dictionary_group[u"objectDictionary"][u"name_of_the_object"][u"obj_pin"] 
  obj_tmp_dict=transform_object_to_dict_to_backup(object_dictionary)


  node_tmp_Dict={}
  for a in nodeDictionary.keys():
    try: 
      sn=nodeDictionary[a].getNodeSerialNumber() 
      node_tmp_Dict[sn]={u"node_serial_number":sn,u"hwModelName":nodeDictionary[a].getNodeHwModel(),u"nodeAddress":nodeDictionary[a].getNodeAddress(),u"nodeObjectsDict":nodeDictionary[a].getnodeObjectsDict()}
    except Exception as e  :
      message="error in updateJson, with node:"+str(a)
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

    # note that the i/o modes for the node pins will be saved in the relative webobjects .
    # the pins not used by a webobject will be configured as output and cleared to 0 
        



  #print object_dictionary
  #print roomDictionary
  dictionary_group={"dictionaries":{u"objectDictionary":obj_tmp_dict,u"zoneDictionary":zoneDictionary,u"nodeDictionary":node_tmp_Dict,u"scenarioDictionary":scenarioDictionary}} #combined dictionary
  #to add a new dictionary just add it in dictionary_group

  #print dictionary_group
  #note base_cfg_path is in the globalVar.py 

  make_fs_ready_to_write()
  try:
    dictionary_group_json=json.dumps(dictionary_group, indent=2,sort_keys=True) #make the json structure
    file_to_save =codecs.open(base_cfg_path+"config_files/data.json","w","utf8")     #utf8 is a type of  encoding for unicode strings
    file_to_save.write(dictionary_group_json)
    file_to_save.close()
    os.chmod(base_cfg_path+"config_files/data.json", 0o777)

    json_conf_options_dict={"conf_options_dictionary":conf_options_dictionary}
    conf_options_json=json.dumps(json_conf_options_dict, indent=2,sort_keys=True) #make the json structure
    file_to_save2 =codecs.open(base_cfg_path+"config_files/cfg.json","w","utf8")     #utf8 is a type of  encoding for unicode strings
    file_to_save2.write(conf_options_json)
    file_to_save2.close()
    os.chmod(base_cfg_path+"config_files/cfg.json", 0o777)

  except Exception as e :
    message="error in updateJson()"+" e:"+str(e.args)
    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

  make_fs_readonly()










def updateNodeAddress(node_sn,uart_router_sn,node_address,node_fw):
  """,
  Given a node serialnumber and an address, updates the node in the nodeDict with the given address. 

  """
  logprint("updateNodeAddress() executed with node_sn:"+node_sn,verbose=3)
  try: #if (node_sn in nodeDict.keys()):


    nodeDict[node_sn].updateLastNodeSync(time.time())
#    if nodeDict[node_sn].getNodeActivity()==0 or nodeDict[node_sn].getNodeActivity()==2: #the node was not connected but now it is
#      nodeDict[node_sn].setNodeActivity(1)  #set the node as active
#    for b in nodeDict[node_sn].getnodeObjectsDict().values():#for each object in the node 
#      logprint("objectDict[b].getHwNodeSerialNumber():"+str(objectDict[b].getHwNodeSerialNumber()) )
#      logprint("webobject:"+b+"returned active",verbose=5)  
#      object_type=objectDict[b].getType()
#      if object_type in ("digital_obj_in","analog_obj_in","cfg_obj"): #skip input objects  todo:remove cfg_obj
#        continue
#      current_s=objectDict[b].getStatus()
#      if ((current_s=="inactive") or (current_s=="onoswait") ): 
#        prev_s=objectDict[b].getStartStatus()      #if the current status is "inactive" set it to the previous status
#        logprint("the new status will be:"+str(prev_s) )
#        layerExchangeDataQueue.put( {"cmd":"setSts","webObjectName":b,"status_to_set":"0","write_to_hw":1,"user":"onos_node","priority":99,"mail_report_list":[]})


    if len(node_address)==3:  #if is a radio node
      logprint("the node to update is a radio node",verbose=3)
      numeric_address=int(node_address)
      if numeric_address not in next_node_free_address_list: 
        logprint("numeric_address not in list,I add it",verbose=1)
        next_node_free_address_list.append(numeric_address)  
      else :
        for node in nodeDict.keys():
          if nodeDict[node].getNodeAddress()==node_address:
            
            if node!=node_sn:  #found another node with the same address! I will therefore assing another one to this node..
              message="warning I have found another node with the same address,I will therefore assing another one to this node:"+node_sn
              logprint(message,verbose=5)

              priorityCmdQueue.put( {"cmd":"NewAddressToNodeRequired","nodeSn":node_sn,"nodeAddress":node_address,"nodeFw":node_fw}) 
         

      #if node_address !="254": #if the node have already an address


      if uart_router_sn in nodeDict.keys():
        nodeDict[uart_router_sn].updateLastNodeSync(time.time())  #I update also the uart_router last time sync since it is him that sent the remote node message

    if (nodeDict[node_sn].getNodeAddress())!=node_address:
      logprint("node "+node_sn+" address changed to "+node_address)
      nodeDict[node_sn].setNodeAddress(node_address)
      updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) #save all the new data

      
    else:
      logprint("the node has still the same address")

  except Exception as e  :
    message="error in updateNodeAddress() node_sn was:"+node_sn+" address was:"+node_address
    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))


  return()


def getNextFreeAddress(node_sn,uart_router_sn,node_fw):# get the next free address 
  """
  | Given a node serialnumber this function will return the first free address to assign to the node. 
  | If there are no free addresses left it will check if there are nodes disconnected to which steal the address.
  | Used only for the radio nodes since the ethernet nodes 
  """

  logprint("getNextFreeAddress executed with node_sn:"+str(node_sn) )

  #logprint(next_node_free_address_list) 
  
  #if the node has already an address..reuse it
  node_address=nodeDict[node_sn].getNodeAddress() 
  repeated_address=0
  for node in nodeDict.keys():  #read all nodes
    tmp_address=nodeDict[node].getNodeAddress()   #get all nodes addresses
    if (len(tmp_address)==3)&(node!=node_sn): #if radio node
      if nodeDict[node].getNodeAddress()==node_address:           
          if node!=node_sn:  #found another node with the same address! I will therefore assing another one to this node..
            repeated_address=1

  if repeated_address==0: #the address is still the same and is not used by others nodes
    if node_address!="254":
      logprint("the address is still:"+str(node_address)+" the same and is not used by others nodes")
      return(node_address)  


  for number in range(2,254):
    if number not in next_node_free_address_list:
      for node in nodeDict:
        free_address=1
        tmp_address=nodeDict[node].getNodeAddress() 
        if tmp_address==number:
          free_address=0
          break

      if free_address==1:
        str_address=str(number)
        while (len(str_address)<3):
          str_address="0"+str_address
        next_node_free_address_list.append(number)
        return(str_address)

  for node in nodeDict.keys(): #todo test it!
    address=nodeDict[node].getNodeAddress()
    if (  (  (time.time()-nodeDict[node].getLastNodeSync() )>nodeDict[node].getNodeTimeout()  )&(len(address)<=3)) : #the node is not connected
        #updateNodeAddress(node_sn,address) 
      updateNodeAddress(node,uart_router_sn,"reassigned",node_fw)
      logprint( "I had finished all the free addresses so I recycled a not used one",verbose=5) 
      return(address)

    logprint("I had finished all the free addresses I'm sorry but you have to disconnect one node to connect another one",verbose=10)
    return("254")










def changeWebObjectType(objName,typeToSet):#

  """
  | change the type of webobject and the relative pin mode in hardware_node class
  | Todo: remove this function

  """

  logprint("executed changeWebObjectType() with :"+objName)
  if objName in objectDict.keys(): #if the web object exist
    objectDict[objName].setType(typeToSet)
    pinList=objectDict[objName].getAttachedPinList()

    if pinList!=[9999] : #if there is a pin attached to this webobject

      obj_type=objectDict[objName].getType()
      SerialNumber=objectDict[objName].getHwNodeSerialNumber()
      pins_to_set=objectDict[objName].getAttachedPinList()
      node_address=nodeDict[SerialNumber].getNodeAddress()
      if (obj_type=="sr_relay"):
        if len (pins_to_set)!=2:
          logprint("error , number of pins different from 2 for sr_relay type ",verbose=7)
          return(-1)   

        hardware.setHwPinMode(node_address,pins_to_set[0],"DOUTPUT")
        hardware.setHwPinMode(node_address,pins_to_set[1],"DOUTPUT")
        nodeDict[SerialNumber].setNodePinMode(pins_to_set[0],"DOUTPUT") 
        nodeDict[SerialNumber].setNodePinMode(pins_to_set[1],"DOUTPUT") 

        return(1)

      if len (pins_to_set)!=1:   # under this i put every object with one single hardware pin 
          logprint("warning , number of pins different from 1 for this obj type ",verbose=4)
          return(-1)   

      if ((typeToSet=="b")|(typeToSet=="sb")):
        hardware.setHwPinMode(node_address,pins_to_set[0],"DOUTPUT")
        nodeDict[SerialNumber].setNodePinMode(pins_to_set[0],"DOUTPUT")  
      if (typeToSet=="d_sensor"): 
        hardware.setHwPinMode(node_address,pins_to_set[0],"DINPUT") 
        nodeDict[SerialNumber].setNodePinMode(pins_to_set[0],"DINPUT") 
      if (typeToSet=="a_sensor"):  
        hardware.setHwPinMode(node_address,pins_to_set[0],"AINPUT") 
        nodeDict[SerialNumber].setNodePinMode(pins_to_set[0],"AINPUT") 
      if (typeToSet=="pwm_output"):  
        hardware.setHwPinMode(node_address,pins_to_set[0],"AOUTPUT") 
        nodeDict[SerialNumber].setNodePinMode(pins_to_set[0],"AOUTPUT") 






  else:
    logprint("the webobject:"+objName+" doesn't exist",verbose=7)

  return()


def replace_functions(scenario_functions,scenario_name):#given a string ,replace web_object names with their value  obsolete


  scenario_functions=scenario_functions.replace("!","not ")  

  while 1:  # until all the objects are replaced by their value

    try:
      objname=re.search(r"#_.+?_#",scenario_functions).group(0)[2:-2]
    except Exception as e :
      message="no objects found in the scenario_functions or scenario_functions fully analyzed" 
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
      #errorQueue.put("no objects found in the scenario_functions or scenario_functions fully analyzed "+" e:"+str(e.args)) 
      break
        #errorQueue.put("error00 in the scenario operation search ,scenario_functions: "+scenario_functions)

    if objname is None:
      logprint ("error002 in the scenario operation search ,nonetype "+scenario_functions,verbose=9)
      return(-1)
 
    try:
      scenario_functions=scenario_functions.replace("#_"+objname+"_#",str(objectDict[objname].getStatusForScenario()))      
    except Exception as e :
      message="error01f the webobject does not exist in the dict, i close the scenario check,objname: "
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))


      return(-1)
 # now all the obj value are replaced

  try:# replace all the #p_webobjectname_# with the previous webobject status value
    scenario_functions=re.sub(r'#p_.+?_#',lambda x: str( objectDict[x.group(0)[3:-2]].getPreviousStatusForScenario()),scenario_functions)
  except Exception as e :
    message="error1 the webobject does not exist in the dict, i close the scenario check: scenario_condition:"+scenario_functions+",scenario_name"+scenario_name
    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()) )
    return(-1)
  logprint("scenario_functions replaced:"+str(scenario_functions) )
  return(scenario_functions)




def replace_conditions(scenario_conditions,scenario_name):#given a string ,replace web_object names with their value 

  obj_list=[]
  #scenario_conditions=scenario_conditions.replace("!","not ")  
  while 1:  # until all the objects are replaced by their value
    objname_prev=""




    try:
      objname=re.search(r"#_.+?_#",scenario_conditions).group(0)[2:-2]
      
    except : #ended the simple objects status

      #errorQueue.put("no objects found in the scenario_conditions or scenario_conditions fully analyzed "+" e:"+str(e.args)) 
      try:
        objname_prev=re.search(r"#p_.+?_#",scenario_conditions).group(0)[3:-2]
      except Exception as e :         #no previus object status found , serch terminated
        objname_prev=""
        message="no objects found in the scenario_conditions or scenario_conditions fully analyzed,conditions:"+scenario_conditions
        logprint(message,verbose=2,error_tuple=(e,sys.exc_info()) )
        break
        #errorQueue.put("error00 in the scenario operation search ,scenario_conditions: "+scenario_conditions)


    if objname is None:
      logprint ("error003 in the scenario operation search ,nonetype "+scenario_conditions,verbose=9)
      return(-1)



 
    try:
      if objname=="select_an_element":
        scenario_conditions=scenario_conditions.replace("#_"+objname+"_#","1")   
      else:
        scenario_conditions=scenario_conditions.replace("#_"+objname+"_#",str(objectDict[objname].getStatusForScenario()))   
        obj_list.append(objname)   
        if (len(objname_prev)>0 )&(objname_prev!="")&(objname_prev not in obj_list ):  #if there is a #p_objectName_#
          obj_list.append(objname)
       


    except Exception as e :
      message="error01c the webobject does not exist in the dict, I close the scenario check,objname: "+objname+" e:"+str(e.args)
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
      return(-1)
 # now all the obj value are replaced

  try:# replace all the #p_webobjectname_# with the previous webobject status value
    scenario_conditions=re.sub(r'#p_.+?_#',lambda x: str( objectDict[x.group(0)[3:-2]].getPreviousStatusForScenario()),scenario_conditions)
  except Exception as e :
    message="error1 the webobject does not exist in the dict, i close the scenario check: scenario_condition:"+scenario_conditions+",scenario_name"+scenario_name
    logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))

    return(-1)
  logprint("scenario_conditions replaced:"+str(scenario_conditions) )
  return([scenario_conditions,obj_list])




def checkwebObjectScenarios(scenario_name):#check all the webobjects in the scenario passed
  logprint("checkwebObjectScenarios() executed")
  if conf_options["scenarios_enable"]==0 :
    logprint("scenario disabled")
    return()



  try:
    scenario_to_check=scenarioDict[scenario_name]#get the scenario from the dictionary
  except KeyError:
    message="error scenarioname:"+scenario_name+" not found in the dict"
    logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
    return()

#scenario dictionary structure:

#     webObjectScenarios["change_lampobj"]{"enabled":1,"setType":"condition_to_set_status","one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":[cond1&cond2|cond3],"math":"","functionsToRun":[lamp1=0,lamp2=#_lamp2_#+1...],"afterDelayFunctionsToRun":[],"delayTime":0,"priority":0}

#  try:  #if the index exist
#    scenario_web_obj_to_read=scenario_to_check["web_obj_to_read"]
#  except IndexError:#set the value to default
#    print "warning no object found in this scenario condition or math"
#    scenario_web_obj_to_read=[]

  try:  #if the reference exist
    scenario_enabled=scenario_to_check["enabled"]
  except KeyError:#set the value to default
    scenario_enabled=1

  if scenario_enabled!=1:# if the scenario is disabled  exit
    logprint("scenario:"+scenario_name+" is disabled")
    return()

#  try:   #if the reference exist
#    scenario_set_type=scenario_to_check["setType"]
#  except KeyError:
#    print "error scenario_set_type not in the scenario dictionary"

  try:   #if the reference exist
    type_after_run=scenario_to_check["type_after_run"]
  except KeyError:#set the value to default
    type_after_run="0"

  try:  #if the reference exist
    scenario_priority=scenario_to_check["priority"]
  except KeyError:#set the value to default
    scenario_priority=0

#  try:  #if the reference exist
#    scenario_math=scenario_to_check["math"]
#  except KeyError: #set the value to default
#    scenario_math=""

  try:  #if the reference exist
    scenario_conditions=scenario_to_check["conditions"]

  except KeyError:#set the value to default
    logprint("error conditions not in scenario dictionary",verbose=6)
    scenario_conditions="0"

  if len(scenario_conditions)<1:
    scenario_conditions="0"
    logprint("error scenario conditions of "+scenario_name+"are a void string",verbose=6)



  logprint("scenario scenario_conditions : "+str(scenario_conditions) ) 
  if (scenario_conditions!="0")and(scenario_conditions!="1"):
    scenario_conditions=replace_conditions(scenario_conditions,scenario_name)[0]
  if scenario_conditions==-1:
    return(-1)
  
  logprint("scenario conditions after replace : "+str(scenario_conditions) )
  cond=0  #if the conditions are a void string ..
  try:
    cond=eval(scenario_conditions)
  except Exception as e :
    message="error in eval("+scenario_name+"), scenario_conditions="+str(scenario_conditions)
    logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))

  if (cond==1):  #the condition are true , onos will execute the operations

    logprint("scenario conditions are true")

#    try:# replace all #_webobjectname_# with the webobjectname status value
#      scenario_math=re.sub(r'#_.+?_#',lambda x: str(objectDict[x.group(0)[2:-2]].getStatus()),scenario_math)
#    except:
#      print "error the webobject does not exist in the dict, i close the scenario scenario_math check"
#      errorQueue.put("error2 the webobject does not exist in the dict, i close the scenario check: scenario_math:"+scenario_math)
#      return()

#    try:# and all the #p_webobjectname_# with the previous webobject status value
#      scenario_math=re.sub(r'#p_.+?_#',lambda x: str(objectDict[x.group(0)[3:-2]].getPreviousStatus()),scenario_math)
#    except :
#      print "error the webobject does not exist in the dict, i close the scenario scenario_math check"
#      errorQueue.put("error3 the webobject does not exist in the dict, i close the scenario check: #scenario_math:"+scenario_math)
#      return()



#    print "scenario scenario_math: ",scenario_math
#    if len(scenario_math)> 1: 
#      try:
#        mathResultValue=str(eval(scenario_math))   #calculating the math expression from scenario_math
#      except:
#        print "error in eval(scenario_math) ,scenario_math="+str(scenario_math)
#        errorQueue.put("error in eval(scenario_math) ,scenario_math="+str(scenario_math))
#    else:
#      mathResultValue=""

    executionList=[]

    #if "functions_to_run" in scenario_to_check.keys():  #if the reference exist
    try:
      scenario_functions_to_run=scenario_to_check["functionsToRun"]
    except Exception as e :
      message="scenario_functions_to_run of "+scenario_name+ " scenario is empty"
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
      scenario_functions_to_run=[]

    #if "afterDelayFunctionsToRun" in scenario_to_check.keys():  #if the reference exist
    try:  #todo not implemented in the gui..
      afterDelayFunctionsToRun=scenario_to_check["afterDelayFunctionsToRun"]
    except KeyError:#set the value to default
      afterDelayFunctionsToRun=[]

    try:
      delayTime=scenario_to_check["delayTime"]
    except KeyError:#set the value to default
      delayTime=0


      
    for f in scenario_functions_to_run:   #for each line of the functions_to_run
        #f=f.replace("#condvalue#","1")  
      #f=f.replace("#mathvalue#",mathResultValue)   
      f=f.replace("==","=")    #replace == with =
      f=f.replace("!","not ")   
      point=f.find("=")
      f_before_equal_sign=f[0:point]
      f_before_equal_sign=f_before_equal_sign.replace("#_","")
      f_before_equal_sign=f_before_equal_sign.replace("#p_","")
      f_before_equal_sign=f_before_equal_sign.replace("_#","")

      f=f[point+1:]
      

      while 1:  # untill all the objects are replaced by their value

        try:
          objname=re.search(r"#_.+?_#",f).group(0)[2:-2]
        except:
          logprint("no objects found in the function_to_run  or function_to_run fully analyzed ")
          break
          #errorQueue.put("error00 in the scenario operation search ,scenario_conditions: "+scenario_conditions)

        if objname is None:
          logprint("error003 in the scenario operation search ,nonetype "+f,verbose=7)
          break
 
        try:
          f=f.replace("#_"+objname+"_#",str(objectDict[objname].getStatusForScenario()))      
        except Exception as e :
          message="error003 the webobject does not exist in the dict, i close the scenario check of:"+scenario_name+",objname: "+objname
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
          return()
 # now all the obj value are replaced



      #try:# replace all #_webobjectname_# with the webobjectname status value
      #  f=re.sub(r'#_.+?_#',lambda x: str(objectDict[x.group(0)[2:-2]].getStatus()),f)
      #except KeyError:
      #  print "error0 the webobject does not exist in the dict, i close the scenario check,operation:"+f
      #  errorQueue.put(" error0 the webobject does not exist in the dict, i close the scenario check,operation:"+f)
      #  return()

      try:# replcace all the #p_webobjectname_# with the previous webobject status value
        f=re.sub(r'#p_.+?_#',lambda x: str(objectDict[x.group(0)[3:-2]].getPreviousStatusForScenario()),f)
      except Exception as e :
        message="error2 the webobject does not exist in the dict, i close the scenario function to run check"+" e:"+str(e.args)
        logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
        return()
      
      executionList.append(f_before_equal_sign+"="+f)

   # if (scenario_set_type=="condition_to_set_status") :  # scenario_set_type  is  condition_to_set_status
      #execute the  executionList
    logprint("conditions verified and true, i execute the executionList ")
       
    statusToSet="void"
    try: 
      for op in executionList:
        message="operation to execute: "+op
        logprint(message,verbose=3)
        obj_to_change="void"
        str_status="void"

        try:
          obj_to_change=op.split("=" )[0]
          str_status=op.split("=" )[1]
        except Exception as e :
          message="error in the split of op in executionList ,op="+op+"obj_to_change:"+obj_to_change+",str_status:"+str_status
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))

  
        
        try:
          statusToSet= str(eval(str_status))

        except Exception as e :  #happens if statusToSet=  inactive or  onoswait
          statusToSet=str_status
          message="error in the eval of for op in executionList :str_status="+str(str_status)+",op="+op+" e:"+str(e.args)
          logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 



        if (statusToSet==True)or(statusToSet=="True"):
          statusToSet="1"

        if (statusToSet==False)or(statusToSet=="False"):
          statusToSet="0"

        if (objectDict[obj_to_change].validateStatusToSetObj(statusToSet)==1):  #the status to set is valid for the object

          if obj_to_change in objectDict:
            logprint("scenario act to change the weboject: "+str(obj_to_change) )
            layerExchangeDataQueue.put( {"cmd":"setSts","webObjectName":obj_to_change,"status_to_set":statusToSet,"write_to_hw":1,"user":"scenario","priority":scenario_priority,"mail_report_list":[]})
        else:
          logprint("error in scenario op,statusToSet is :"+statusToSet,verbose=8 )



    except Exception as e :
      message="error in the scenario for loop (for op in executionList) "
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))




    if delayTime>0:
      logprint("create a new scenario...banana")

      currentDayTime=objectDict["dayTime"].getStatusForScenario()
  
      if (delayTime+currentDayTime) < 1440:    #  1440 is 24 * 60   the max number of minuts in a day
        selectedMinutes=str(currentDayTime+delayTime)
      else:
        selectedMinutes=str((currentDayTime+delayTime)-1440 )   # restart the count from 0 minutes
    
      new_scenario_name="delay_from"+scenario_name
      c=0
      while new_scenario_name in scenarioDict.keys():  # if the name already exist  try another
          new_scenario_name=str(c)+"delay_from"+scenario_name
          c=c+1

  
      logprint("created delay scenario named:"+new_scenario_name+"with conditions:dayTime=="+selectedMinutes)
      logprint("now real time is "+str((datetime.datetime.today().minute+(datetime.datetime.today().hour)*60 ))+" obj time is"+str(currentDayTime) )
         
      scenarioDict[new_scenario_name]={"enabled":1,"type_after_run":"autodelete","conditions":"#_dayTime_#=="+selectedMinutes,"functionsToRun":afterDelayFunctionsToRun,"afterDelayFunctionsToRun":[],"delayTime":0,"priority":scenario_priority}
      objectDict["dayTime"].attachScenario(new_scenario_name)
 
    if type_after_run=="autodelete":
      del scenarioDict[scenario_name] 
      for a in objectDict.keys():   # delete the reference to this scenario from all the webobjects 
        objectDict[a].removeAttachedScenario(scenario_name) 
   
    if type_after_run=="one_time_shot":
      logprint("iI disable the one_time_shot :"+scenario_name)
      scenarioDict[scenario_name]["enabled"]=0    


  else: # #the condition are false 
   logprint("the scenarios  condition are false")



     




  #print "end of checkwebObjectScenarios"
  return()     

  









def compose_error_mail(error_type,objName=""):
  logprint("compose_error_mail executed")
  mailtext=""
  if error_type=="so_priority":
    obj_previous_status=objectDict[objName].getStatus()
    mailtext="onos_report_message,"+objName+",error_so_priority,obj stays,"+str(obj_previous_status)

  if error_type=="so_permissions":
    obj_previous_status=objectDict[objName].getStatus()
    mailtext="onos_report_message,"+objName+",error_so_permission,obj stays,"+str(obj_previous_status)

  if error_type=="wrong_password":
    mailtext="onos_report_message,error_password,the password you send is wrong please check it"

  if error_type=="wrong_username":
    mailtext="onos_report_message,error_username,your username does not exist  please add it from local web interface"

  if error_type=="white_list":
    mailtext="onos_report_message,error_white_list,your mail is not in the white_list  please add it from local web interface"


  if error_type=="so_obj_not_exist":
    mailtext="onos_report_message,"+objName+",not_exist, webobject name does not exist please check it"


  if error_type=="so_value":
    mailtext="onos_report_message,error_so_value,value not compatible with webobject please check it"



  if error_type=="parse_mail":
    mailtext="onos_report_message,error_mail_parse,please check your mail syntax"


  mailtext=mailtext+"\n"


  return(mailtext)


def changeWebObjectStatus(objName,statusToSet,write_to_hardware,user="onos_sys",priority=0,mail_report_list=[]):#change a webobj status and its relative pin in the hardware_node class.

  logprint("changeWebObjectStatus executed with obj="+objName)

  if objName not in objectDict.keys(): #if the web object does not exist exit
    logprint("error the webobject does NOT exist in the dictionary objectDict ",verbose=9)

    return(-1)

  obj_previous_status=objectDict[objName].getStatus()



#  if (obj_previous_status==statusToSet): #&(write_to_hardware==1) :  #the obj status didn't change
#    print "the webobject "+objName+"has already the status value you want to set "
#    errorQueue.put("the webobject "+objName+" has already the status value you want to set ")
#    return(1)

  logprint("write_to_hardware="+str(write_to_hardware) )
  #print "attached pin0 ="+str(objectDict[objName].getAttachedPinList())+";"    
  global nodeDict 



  #print "24444444444444444444444444444444444444444444444444444444444",objectDict[objName].getMailReport()
  mail_report_list=mail_report_list+objectDict[objName].getMailReport() #summ the 2 list


  mail_report_list=list(set(mail_report_list))   #removes duplicates
  #print "2222222222222222222222222222222222222222222222222222222222222",mail_report_list

  if objectDict[objName].checkRequiredPriority(priority)==1:   #check priority 
    logprint("priority ok")
  else:

    #obj_previous_status=objectDict[objName].getStatus()
    mailText=compose_error_mail("so_priority",objName)
    mailSubject="onos_report_error"+objName
    for m in mail_report_list:
      #sendMail(m,mailtext,mailSubject,onos_mail_conf,smtplib,string)
      mailQueue.put({"mail_address":m,"mailText":mailText,"mailSubject":mailSubject})

    logprint("error ,required priority is "+str(objectDict[objName].required_priority()),verbose=10)
 

    return(-1)

  if objectDict[objName].checkPermissions(user,"x",priority):   #check permission  
    logprint("permission ok, i set the obj")
  else:
    #obj_previous_status=objectDict[objName].getStatus()
    mailText=compose_error_mail("so_permissions",objName)
    mailSubject="onos_report_error"+objName
    for m in mail_report_list:
      #sendMail(m,mailtext,mailSubject,onos_mail_conf,smtplib,string)
      mailQueue.put({"mail_address":m,"mailText":mailText,"mailSubject":mailSubject})

    logprint("error Permissions not sufficent to change"+objName+",required required permission is "+str(objectDict[objName].getPermissions()),verbose=10 )

    return(-1)






#  global objectDict  #banana  to remove?


  if ( objectDict[objName].getAttachedPinList() )==[9999] : #if there is no pins attached to this webobject

    logprint("no pin attached to this webobject , I change its status")
    if objectDict[objName].getType() not in ["digital_obj_out","analog_obj_out","cfg_obj"]:
      write_to_hardware=0





  if (write_to_hardware==0):

    logprint("i change the webobject status")


    if objectDict[objName].getStatus()=="onoswait":
      if (user=="onos_node"):
        if (objectDict[objName].getType() in objectDict[objName].general_out_group):
          logprint("[objName].getType() :"+objectDict[objName].getType())
          logprint("general_out_group:"+str(objectDict[objName].general_out_group))
          logprint("I will not set the status because the change is from a node")
          return(-1)


    objectDict[objName].setStatus(statusToSet)#set the web object status 
    if (priority!=99):  #if priority == 99 will not write to webobject the new priority
      objectDict[objName].setRequiredPriority(priority) #set the webobject priority
    

    if len(mail_report_list)>0:
      logprint("mail_report,"+objName+" changed to "+str(statusToSet) )

      mailText="onos_report_message,"+objName+",changed to:"+str(statusToSet)
      mailSubject="onos_report_about"+objName
      for m in mail_report_list:
        #sendMail(m,mailtext,mailSubject,onos_mail_conf,smtplib,string)
        mailQueue.put({"mail_address":m,"mailText":mailText,"mailSubject":mailSubject})


    scenarios_list=[]
    scenarios_list=objectDict[objName].getListAttachedScenarios()  #get the list of scenarios where there is a reference to this webobject
    logprint("scenarios_list:"+str(scenarios_list) )
    for tmp_scenario in scenarios_list:
      logprint("scenario name:"+tmp_scenario)
      #banana to add to queue
      layerExchangeDataQueue.put( {"cmd":"scen_check","scenarioName":tmp_scenario})
      #checkwebObjectScenarios(tmp_scenario)


    return(1)


 




 #if write_to_hardware==1 then


  logprint("write_to_hardware="+str(write_to_hardware) )
  try:# objName in objectDict.keys(): #if the web object exist    banana to remove
    logprint("the web object:"+objName+" exist in the dict")

    nodeSerialNumber=objectDict[objName].getHwNodeSerialNumber()
    if  nodeDict[nodeSerialNumber].getNodeActivity()==0:
      message="the web_object"+objName+" belongs to a disconnected node, i will not set it"
      logprint(message,verbose=9)  
      return(-1)

    

    #except:
    #  print "statusToSet "+statusToSet+"can't be converted to a number "
    #  errorQueue.put("statusToSet "+statusToSet+"can't be converted to a number, obj:"+objName)



    if (objectDict[objName].validateStatusToSetObj(statusToSet)<1):
      logprint("error the state"+str(statusToSet)+"is not valid for the obj:"+objName,verbose=10)
      return(-1)  

    statusToSet=int(statusToSet)  #int not float otherwise there will be errors


    #obj_previous_status=objectDict[objName].getStatus()
    #if statusToSet==obj_previous_status:
    #  print "nothing to change,the webobject status is already :"+str(obj_previous_status)
    #  return(1)


    

    #if True:  # to remove..
    logprint("there are one or more pins attached to this webobject")
    objectDict[objName].setStatus("onoswait")#set the wait status
    pins_to_set=objectDict[objName].getAttachedPinList()
    #single_pin=pins_to_set[0]
    #nodeSerialNumber=objectDict[objName].getHwNodeSerialNumber()
    #print nodeDict[nodeSerialNumber].getNodeName()
    logprint("obj node="+str(nodeSerialNumber)+"pins_to_set="+str(pins_to_set) +str(statusToSet) )


    obj_type=objectDict[objName].getType()

    logprint("obj_name="+objName)
    logprint("obj_type="+obj_type)
      #nodeAddress=nodeDict[nodeSerialNumber].getNodeAddress()
    if (obj_type=="sr_relay"):
      if len (pins_to_set)!=2:
        message="error , number of pins different from 2 for sr_relay type "
        logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
        return(-1)      

      

      if statusToSet==1:    # set to 5 volt the set coil of the relay and reset the reset coil of the relay
        #note  the set coil command is the first pin in the list , the second is the reset coil command
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[0],1)
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[1],0)

        try:
          hardware.outputWrite(nodeSerialNumber,pins_to_set,[1,0],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list)

        except Exception as e:   
          message="error in the outputWrite"
          logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
          
# note that  hardware=router_handler.RouterHandler(router_hardware,router_sn)   in conf.py
          # put to rest the relay coil (the relay will continue to been mechanical activated)
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[0],0)
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[1],0)
      if statusToSet==0:    # set to 5 volt the reset coil of the relay and put to 0v the set coil of the relay
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[0],0)
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[1],1)
        try:
          hardware.outputWrite(nodeSerialNumber,pins_to_set,[0,1],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list)

        except Exception as e:
          message="error in the outputWrite2"
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 

             
          # put to rest the relay coil (the relay will continue to been mechanical activated)
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[0],0)
        #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[1],0)

    if (obj_type=="analog_output"):
      logprint("analog output still to develop")  #banana to implement
      hardware.outputWrite(nodeSerialNumber,pins_to_set,[statusToSet],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list,node_password_dict=node_password_dict)
      return(1)


    if (obj_type=="servo_output"):
      logprint("servo_output still to develop")  #banana to implement
      hardware.outputWrite(nodeSerialNumber,pins_to_set,[statusToSet],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list,node_password_dict=node_password_dict)

      return(1)

        
    if (obj_type in ("digital_obj_out","cfg_obj","digital_obj_in","analog_obj_in","analog_obj_out")): #general digital object (for example a plug node)  todo remove cfg_obj..
     # status_list=[statusToSet] 
      #while len(pins_to_set)!=len(status_list): #to make the same len...to bypass check in routerhandler..
      #  status_list.append(statusToSet)
      logprint("pins_to_set_digital_obj:"+str(pins_to_set) )
      logprint("len pins_to_set="+str(len(pins_to_set)) )
      logprint("statusToSet_digital_obj:"+str(statusToSet) )
      logprint("nodeSerialNumber_digital_obj:"+str(nodeSerialNumber) ) 
      #logprint("nodeDict[nodeSerialNumber]:"+str(nodeDict[nodeSerialNumber]) )
      logprint("obj_type_digital_obj:"+str(obj_type) )
    
      logprint (str((nodeSerialNumber,pins_to_set,[statusToSet],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list)))


      hardware.outputWrite(nodeSerialNumber,pins_to_set,[statusToSet],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list,node_password_dict=node_password_dict)
      return(1)   

    if ((obj_type=="b")|(obj_type=="sb")|(obj_type=="digital_output")): #banana to check and leave only digital_output
      if (len (pins_to_set))!=1:
        logprint("error , number of pins different from 1 for button type ",verbose=10)
        return(-1)      
      #nodeDict[nodeSerialNumber].setDigitalPinOutputStatus(pins_to_set[0],statusToSet)
        #if (write_to_hardware==1): #only if you tell to write to hardware
      hardware.outputWrite(nodeSerialNumber,pins_to_set,[statusToSet],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list,node_password_dict=node_password_dict)
      return(1)


    if (obj_type=="d_sensor")|(obj_type=="digital_input"): #banana to check and leave only digital_input
      if (len (pins_to_set))!=1:
        logprint("error , number of pins different from 1 for d_sensor type ",verbose=10)
        return(-1)  
      #nodeDict[nodeSerialNumber].setDigitalPinInputStatus(pins_to_set[0],statusToSet)
      #if (write_to_hardware==1): #only if you tell to write to hardware
      hardware.outputWrite(nodeSerialNumber,pins_to_set,[statusToSet],nodeDict[nodeSerialNumber],objName,obj_previous_status,statusToSet,obj_type,user,priority,mail_report_list,node_password_dict=node_password_dict)

      return(1)    


    else:
      logprint("error in changeWebObjectStatus(),the out_type"+obj_type+" is not yet implemented",verbose=10) 





  except Exception as e  : # the webobject does not exist
    message="the webobject:"+objName+" doesn't exist,or others error happened"
    logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
    return(-1)

  return(1)


def NodePinToWebObject(node_sn,pin_number,pin_status):#change the webobject status given a node ,a pin and a status to set
  write_hw_enable=0

  for a in objectDict.keys():
    #print objectDict[a].getHwNodeSerialNumber()
    if (objectDict[a].getHwNodeSerialNumber()==node_sn):
      #print "node exist"
      if objectDict[a].getAttachedPinList()[0]==int(pin_number):
        if (len(objectDict[a].getAttachedPinList())==1):#the sensor object must have only a pin attached

 

          if (objectDict[a].validateStatusToSetObj(pin_status)<1):
            logprint("error NodePinToWebObject the state"+str(pin_status)+"is not valid for the obj:"+a,verbose=10)

          else:#the status is legit with the webobj type
            objName=objectDict[a].getName()                      
            #changeWebObjectStatus(objName,int (pin_status),write_hw_enable) #banana add to queue
            layerExchangeDataQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":str (pin_status),"write_to_hw":write_hw_enable,"user":"onos_node","priority":99,"mail_report_list":[]})

            logprint("pin changed from external node")                      

        else:
          logprint("error number of pin in the NodePinToWebObject section",verbose=10)

          
  return()



def setWebObjectDigitalStatusFromReg(node_sn_tmp,section_number,status_byte):
  #change the webobject digital status given a node ,a number of section and the digital status register 
  pinToWrite=nodeDict[node_sn_tmp].setNodeSectionDInputStatus(section_number,ord(status_byte))
  if pinToWrite is not None:
    for pin in pinToWrite.keys():
      status=pinToWrite[pin]
      NodePinToWebObject(node_sn_tmp,pin,status)
  else:
    logprint("void register")


  return()


#def setWebObjectAnalogStatusFromReg(node_sn_tmp,analog_pin,analog_byte0,analog_byte1):
def setWebObjectAnalogStatusFromReg(node_sn_tmp,analog_pin,analog_byte0):
  #change the webobject analog status given a node ,an analog pin number and 2 byte register containing the analog value 
  #analogvalue=nodeDict[node_sn_tmp].setNodeAnalogInputStatusFromReg(analog_pin,ord(analog_byte0),ord(analog_byte1))
  analogvalue=nodeDict[node_sn_tmp].setNodeAnalogInputStatusFromReg(analog_pin,ord(analog_byte0),0)
  if analogvalue is not None:
      NodePinToWebObject(node_sn_tmp,analog_pin,analogvalue)
  else:
    logprint("void register2")

  return()


def updateNodeInputStatusFromReg(node_sn,register):  # deprecated
#decode the data register and then change the web objects status 
# and update the node status values 
  logprint("updateNodeInputStatusFromReg excuted with data="+register)
  logprint("first byte= "+str(ord(register[0])) )
  logprint("len reg="+str(len(register)) )
  setWebObjectDigitalStatusFromReg(node_sn,0,register[0])  
  setWebObjectDigitalStatusFromReg(node_sn,1,register[1])  
  setWebObjectDigitalStatusFromReg(node_sn,2,register[2])  
  setWebObjectDigitalStatusFromReg(node_sn,3,register[3])  
  setWebObjectDigitalStatusFromReg(node_sn,4,register[4])  
  setWebObjectDigitalStatusFromReg(node_sn,5,register[5])  
  setWebObjectDigitalStatusFromReg(node_sn,6,register[6])  
  setWebObjectDigitalStatusFromReg(node_sn,7,register[7])  
  setWebObjectDigitalStatusFromReg(node_sn,8,register[8]) 
  msgr=" "
  for b in range (0,len(register)):
    msgr=msgr+str(ord(register[b]))+","
  logprint("rx reg:"+msgr)

 # time.sleep(3)#banana to remove

  first_analog_pin=14
  last_analog_pin=19
  node_hw_type=nodeDict[node_sn].getHwType()
  if ( (node_hw_type=="arduino2009")or(node_hw_type=="arduino_promini")or(node_hw_type=="arduino_uno")):
    first_analog_pin=14
    last_analog_pin=19


  if ((node_hw_type=="arduino_mega1280")or(node_hw_type=="arduino_mega2560") ):
    first_analog_pin=54
    last_analog_pin=69 
  #on k=9 there is 'a' 
  k=10
  for a_pin in range (first_analog_pin,last_analog_pin+1):   #for each analog pin in the hardware (2 bytes)
    if "analog_input" in (hardwareModelDict["ProminiA"]["pin_mode"]):
      if "a_sensor" in (hardwareModelDict["ProminiA"]["pin_mode"]["analog_input"]):
        if a_pin in (hardwareModelDict["ProminiA"]["pin_mode"]["analog_input"]["a_sensor"]):
        #if the pin is used as analog input then read its value and set it in the node
          try:
           # setWebObjectAnalogStatusFromReg(node_sn,a_pin,register[k+1],register[k])
            setWebObjectAnalogStatusFromReg(node_sn,a_pin,register[k])
            #print "analog register=first:"+str(ord(register[k]))+" second:"+str(ord(register[k+1]))
            logprint("analog register=first:"+str(ord(register[k])) )
            logprint("analog real value="+str((ord(register[k]))) )
          except:#banana ? error?
            logprint("end of analog")
            return()  
    logprint("k="+str(k) )
    #k=k+2
    k=k+1
  return()    








def createNewWebObjFromNode(hwType0,node_sn):
  """
  | Given an hardware type and a node serial number it will create a new zone and the webobjects in that zone .
  |
  |
  """

  #progressive_number=node_sn          #   [-4:]   #get 0001 from Plug6way0001 ,now get the full serial Plug6way0001
  logprint("createNewWebObjFromNode executed with node_sn:"+node_sn+"and hwType0:"+hwType0)
  global zoneDict
  global objectDict
  logprint(hardwareModelDict.keys())
  if hwType0 in hardwareModelDict.keys():  #if the type exist in the hardwareModelDict
#hardwareModelDict["onosPlug6way"]["pin_mode"]["sr_relay"][0]
    logprint("I will create a new "+hwType0+" node ")

#hardwareModelDict["onosPlug6way"]={"max_pin":12,"hardware_type":"arduino_2009","pin_mode":{"sr_relay":{"socket":[(1,2),(3,4),(5,6),(7,8),(9,10),(11,12)]}  }    }

    if "object_list" in  hardwareModelDict[hwType0]:

      try:#hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["object_numbers"]=[2,3]#see globalVar.py
        list_of_different_object_type=hardwareModelDict[hwType0]["object_list"].keys() #get a list of different obj  
        for a in list_of_different_object_type: 
 # a will be for example "digital_obj_out" from hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["object_numbers"]=[2,3] 
          objType=a  


          for b in hardwareModelDict[hwType0]["object_list"][a].keys():
# b will be for example "relay" from hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["object_numbers"]=[2,3]

            progressive_number=0
            logprint ("""hardwareModelDict[hwType0]["object_list"][a]""")
            logprint (str(hardwareModelDict[hwType0]["object_list"][a])) 

            logprint ("""hardwareModelDict[hwType0]["object_list"][a][b]["object_numbers"]:""")
            logprint (str(hardwareModelDict[hwType0]["object_list"][a][b]["object_numbers"])) 

            for c in hardwareModelDict[hwType0]["object_list"][a][b]["object_numbers"]:
# c will be for example 2 from hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["object_numbers"]=[2,3]

              object_address_in_the_node=c

              new_obj_name=b+"_"+node_sn 

              if len (hardwareModelDict[hwType0]["object_list"][a][b]["object_numbers"]) >1: #there is more than 1 object with this name
                new_obj_name=b+str(progressive_number)+"_"+node_sn   
                progressive_number=progressive_number+1

              else:
                new_obj_name=b+"_"+node_sn  
      
              logprint ("new object name="+new_obj_name)
              #print ("object_address_in_the_node:"+str(type(object_address_in_the_node)))
              nodeDict[node_sn].setNodeObjectAddress(object_address_in_the_node,new_obj_name)#set the new object address in the

              if new_obj_name not in (zoneDict[node_sn]["objects"]):
                zoneDict[node_sn]["objects"].append(new_obj_name)   #add the object name to the zone
              else:
                logprint("warning000 the object "+new_obj_name+" already exist in the zoneDict ") 
      
              if new_obj_name not in  objectDict.keys():  #if the object does not exist yet, create it: 
                logprint("added new webobj from node")        
                objectDict[new_obj_name]=newNodeWebObj(new_obj_name,objType,node_sn)
              else:
                logprint("warning001  the object "+new_obj_name+" already exist in the objectDict") 
        logprint("now the object dict of the node:"+str(objectDict.keys()))

      except Exception as e:
        message="error createNewWebObjFromNode in the object part"
        logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))




    try:# todo test if this part still works ..


      list_of_different_pin_type=hardwareModelDict[hwType0]["pin_mode"].keys() #get a list of different obj 
      logprint("list_of_different_pin_type:"+str(list_of_different_pin_type))


    
      for a in list_of_different_pin_type:
        #now i'm inside #for example  hardwareModelDict["Wrelay4x"]["pin_mode"]
        # so the first a will be "digital_obj_out"
        objType=a 
        i=0


        for b in hardwareModelDict[hwType0]["pin_mode"][a]:
          #now i'm inside #for example  hardwareModelDict["Wrelay4x"]["pin_mode"]["digital_obj_out"]
          #print hardwareModelDict[hwType0]["pin_mode"][a][b]
          #so the first b will be "relay"
        
          list_of_different_webobject_names=hardwareModelDict[hwType0]["pin_mode"][a][b]
         
          progressive_number=0
          for c in list_of_different_webobject_names: 
                     
            logprint (c)
            #now i'm inside the last dictionary  
            #c will be for example (0,1)  and then (2) from{"plug":[(0,1)],"plug2":[(2)]}
            #in this example there aren't other webobject names...


            if type(c) not in (tuple, list):  #if c is not a list , trasform it in a list of one element
              c=[c]

            #note_to_myself now probably the sr_relay will not work anymore...
            
            new_obj_name=b+str(i)+"_"+node_sn  #progressive_number
            progressive_number=progressive_number+1   
            logprint("new_obj_name:"+new_obj_name)   
            logprint("zoneDict:"+str(zoneDict))       
            if new_obj_name not in (zoneDict[node_sn]["objects"]):
              zoneDict[node_sn]["objects"].append(new_obj_name)   #add the object name to the zone
            else:
              logprint("warning000 the object "+new_obj_name+" already exist in the zoneDict ") 
      
            if new_obj_name not in  objectDict.keys():  #if the object does not exist yet, create it: 
              logprint("added new webobj from node")      
              objectDict[new_obj_name]=newNodeWebObj(new_obj_name,objType,node_sn,c)
            else:
              logprint("warning001  the object "+new_obj_name+" already exist in the objectDict")
         
        
    except Exception as e:
      message="error createNewWebObjFromNode in the pin part"
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))



  else:
    logprint("no hardware of this type in hardwareModelDict",verbose=10)


  if node_sn in zoneDict:
    updateOneZone(node_sn)  #update the index.html file in the folder named as the zone..



  return()











for a in objectList :                # append to dictionary all the web object
  objectDict[a.getName()]=a
  changeWebObjectType(a.getName(),a.getType())  #i call this in order to setup the node io conf for the webobjects
  a.InitFunction()
  s=a.getStartStatus()
  a.setStatus(s)
  obj_node_address=a.getHwNodeSerialNumber()
  if obj_node_address in nodeDict.keys():
    if nodeDict[obj_node_address].getNodeTimeout()!="never": 
      #at startup set as inactive all the nodes that has a timeout value,later when the node contact onos,onos will reactive and 
      # change all the node object to the saved values
      a.setStatus("inactive")
      nodeDict[obj_node_address].updateLastNodeSync(99999)








for a in objectDict.keys():#check and remove the not used scenarios from web_object attachedScenarios
  for b in scenarioDict.keys():
    if scenarioDict[b]["conditions"].find(a+"_#")==-1: 
     # if the object is not in the conditions then remove it from web_object attachedScenarios
      objectDict[a].removeAttachedScenario(b)
    else:
      objectDict[a].attachScenario(b)   








#objectDict["dayTime"].attachScenario("scenario1")   #banana to remove

#objectDict["hours"].attachScenario("scenario10")   #banana to remove

#objectDict["minutes"].attachScenario("scenario2")   #banana to remove
#objectDict["minutes"].attachScenario("scenario3")   #banana to remove
#objectDict["minutes"].attachScenario("scenario4")   #banana to remove
#objectDict["minutes"].attachScenario("scenario5")   #banana to remove
#objectDict["minutes"].attachScenario("scenario6")   #banana to remove
#objectDict["minutes"].attachScenario("scenario7")   #banana to remove
#objectDict["minutes"].attachScenario("scenario8")   #banana to remove
#objectDict["wifi0_Plug6way0001"].attachScenario("scenario9")   #banana to remove

#objectDict["Wifi_netgear"].attachScenario("scenario10")   #banana to remove
#objectDict["Caldaia"].attachScenario("scenario11")   #banana to remove
#objectDict["button0_RouterGL0000"].setMailReport(["electronicflame@gmail.com"]) #banana to remove
#objectDict["wifi0_Plug6way0001=0"].setMailReport(["electronicflame@gmail.com"]) #banana to remove
#print "room dict="
#print zoneDict











def formParse(text):

  text=string.replace(text, "%20", " ")   #removes the %20 that were created instead of the spaces
  text=string.replace(text, ',&%', '\n') 
  text=string.replace(text, '%7D', '}') 
  text=string.replace(text, '%7B', '{') 
  return (text)


#if there is a css of a web_object and option is to remove this web_object then find it and remove the css part  #web_object
#then find the id=web_object  and remove it 
#if the option is "add" then find the "/*start of automatic css,do not remove this comment*/" and add after this the reative css
#add also the id=web_object  on the end of the body

def findZoneName(path,roomDictionary):
  logprint("findZoneName()  executed")
  if (len(path)>0):
    address_list=string.split(path,"/")  
    if address_list[1] in roomDictionary.keys() :    #if  the path is   /anyroomname/....   take the room name
      room=address_list[1]    
      return(room)
    else: 
      logprint("no room name found")
      return (-1) #no room found

  return(-1)



def modPage(htmlPag,WebObjectdictionary,zone,zoneDictionary):


  #print "java"+onos_automatic_javascript
  #print htmlPag
  onos_automatic_meta='''<meta charset="utf-8"> <meta name="viewport" content="width=device-width">'''  
  onos_automatic_css_style=''


  logprint("modPage()  executed with zone:"+str(zone))
  #if zone in zoneDictionary:
  zoneObjList=zoneDictionary[zone]["objects"]
  #else:
  #  logprint("zone not in the system"+ str(zone) )
  #  zoneObjList=[]
  #  return(htmlPag)
  tmp_pag=htmlPag

  if zone+'_body' in WebObjectdictionary.keys():
    try:
      onos_automatic_body_style=''' body {'''+WebObjectdictionary[zone+'_body'].getStyle()+'''}'''
    except:
      onos_automatic_body_style=' '
  else:
    onos_automatic_body_style=' '


    #print "no  body obj found in zone"+zone
  #print zoneObjList



  #zoneObjList.sort()
  for obj in zoneObjList :
    onos_automatic_css_style=onos_automatic_css_style+'''#'''+obj+'''{'''+WebObjectdictionary[obj].getStyle()+'''}'''

    

     #print "zone+body="+zone+'_body'
    if string.find(obj,zone+"_body")!=-1:#skip to display the body obj
      continue   
    #print 'obj='+obj      
    status=WebObjectdictionary[obj].getStatus() 
    onos_automatic_local_style='''style="'''+WebObjectdictionary[obj].getStyle()+'''"'''     
    if (status==0)|(status=="0"): #banana to implement  a method to allow analog status
      status_to_set="1"
      img_html='''<!--start_img'''+obj+'''--><img class="flex" src="/img/on.png" class="image" />  <!--end_img'''+obj+'''-->'''
    else:
      status_to_set="0"
      img_html='''<!--start_img'''+obj+'''--><img class="flex" src="/img/off.png" class="image" />  <!--end_img'''+obj+'''-->'''

    onos_automatic_object_html=WebObjectdictionary[obj].getHtml()
    onos_automatic_object_id=''' id="'''+obj+'''" '''

    objType=WebObjectdictionary[obj].getType() 
    if objType in ("b","sb","digital_obj_out","cfg_obj","sr_relay","digital_output"):  #banana to use group and to update the online php server with digital_obj...
      onos_automatic_object_href='''href="?'''+obj+'''='''+status_to_set+'''"'''
      onos_automatic_object= '''<a id="'''+obj+'''" onmousedown="stopUpdate()" onmouseout="restartUpdate()" '''+ onos_automatic_object_href+''' > '''+onos_automatic_object_html+'''</a>'''
      onos_automatic_object_a='''<a id="'''+obj+'''" onmousedown="stopUpdate()" onmouseout="restartUpdate()" '''+ onos_automatic_object_href+'''>'''

    elif objType in  ("analog_obj_in","numeric_var","digital_obj_in","servo_output","analog_output"):  #banana to use group and to update the onlyne php server with digital_obj...
      onos_automatic_object_href='''href="#"'''
      onos_automatic_object= '''<a id="'''+obj+'''" onmousedown="stopUpdate()" onmouseout="restartUpdate()" '''+ onos_automatic_object_href+''' > '''+onos_automatic_object_html+'''</a>'''
      onos_automatic_object_a='''<a id="'''+obj+'''" onmousedown="stopUpdate()" onmouseout="restartUpdate()" '''+ onos_automatic_object_href+'''>'''


    else:
      onos_automatic_object_href=''
      onos_automatic_object= '''<a id="'''+obj+'''" > '''+onos_automatic_object_html+'''</a>'''
      onos_automatic_object_a=''


 

    #current_time_hours=(int(strftime("%M", gmtime()))+time_gap+( int(strftime("%H", gmtime())) )*60)//60 
    #current_time_minutes=(int(strftime("%M", gmtime()))+time_gap+(int(strftime("%H", gmtime())))*60)%60
    #tmp_pag=tmp_pag.replace('''<!--onos_system_time-->''',str(current_time_hours)+":"+str(current_time_minutes)+":"+str(time.timezone),1)

    tmp_pag=tmp_pag.replace('''<!--onos_system_time-->''',str(time.localtime()[3])+":"+str(time.localtime()[4]),1)

    tmp_pag=tmp_pag.replace('''<!--onos_automatic_local_style-->''',onos_automatic_local_style, 1)
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object-->''',onos_automatic_object, 1)
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_a-->''',onos_automatic_object_a, 1) 
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_id-->''',onos_automatic_object_id, 1) 
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_href-->''',onos_automatic_object_href, 1) 
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_html-->''',onos_automatic_object_html, 1) 

    tmp_pag=tmp_pag.replace('''<!--start_img'''+obj+'''--><img class="flex" src="/img/on.png" class="image" />  <!--end_img'''+obj+'''-->''',img_html, 1)     
    tmp_pag=tmp_pag.replace('''<!--start_img'''+obj+'''--><img class="flex" src="/img/off.png" class="image" />  <!--end_img'''+obj+'''-->''',img_html, 1)     

    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object='''+obj+'''-->''',onos_automatic_object)  
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_href='''+obj+'''-->''',onos_automatic_object_href)  
    tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_html='''+obj+'''-->''',onos_automatic_object_html) 
 
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_body_style-->''',onos_automatic_body_style, 1)    
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_meta-->''',onos_automatic_meta);
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_javascript-->''',onos_automatic_javascript)
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_css_style-->''',onos_automatic_css_style)


# remove the unused reference

  tmp_pag=tmp_pag.replace('''<!--onos_automatic_local_style-->''',' ')
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_object-->''',' ') 
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_id-->''',' ')
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_href-->''',' ')  
  tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_html-->''',' ')  

  tmp_pag=tmp_pag.replace('''<!--onos_automatic_object_a-->''','''style="visibility: hidden"''') #hide the unused <a>
  #because there are more request than the number of webobject in the zone ,hide the html for the empty ones..


  return (tmp_pag)













def getRoomHtml(room,objectDictionary,path,roomDictionary):  #render the html to insert in the index.html of a room directory  which must be inside the baseRoomPath directory, modify to read the html ..
  logprint("getRoomHtml()executed")

  logprint("zone passed="+room)
  x=baseRoomPath+room+"/index.html"
  #x=string.replace(x, ',&%', '') 
  #x=string.replace(x, '\n', '') 
  readed_html="nothing"
  logprint("file to open="+x)
    
  try:
    in_file=open(x,"r")
    readed_html = in_file.read()
    in_file.close()
 
      #readed_html =os.popen("cat "+x).read()   # don't use the standard method because the file is opened  otherwere
      
  except:
    logprint("can't open file:"+x+"end")


  #print "readed htm="+readed_html+"end"


 
  if (len(readed_html)>10)&(string.find(readed_html,'<!--onos_automatic_page-->')==-1):  #if the file exist and is not automatic then serve it as it is 
    logprint("readed_htmlis mod from user",verbose=5)
    #roomHtml=readed_html
    return(readed_html)
    #print "html parsed "
    #if (string.find(readed_html,'<!--onos_automatic_page-->')!=-1):
      #roomHtml=modPage(readed_html,objectDictionary,room,roomDictionary) 
    #  return(roomHtml)
    #else:
    #  print " readed_html is:not <!--onos_automatic_page-->"
    #  return(roomHtml)

  else:  #modify or update the page 
    logprint("readed_html is: <!--onos_automatic_page-->",verbose=5)

  #if the file does not exist
  #roomHtml=play_zone_start_html+ '''<div id="header">'''+room.upper()+'''</div>'''
  
  if room in zoneDict.keys():  
    cgi_name="gui/display_zone_objects.py"
    #zone=zoneDict[room]
    namespace={"zone":room} 
    web_page=""
    roomHtml="error executing /gui/display_zone_objects.py"
    try:
      #execfile(cgi_name,locals(),namespace)  #execute external script /gui/display_zone_objects.py
      exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)   
      roomHtml=namespace["web_page"]  
    except Exception as e: 
      message="error executing /gui/display_zone_objects.py e:"
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

    return(roomHtml)


def updateOneZone(zone):
  html_file_location=baseRoomPath+zone+"/index.html"
  logprint("updateOneZone()  executed  with zone:"+zone+";")
  if os.path.isfile(html_file_location):   #if the file in the directory exist don't create it
    logprint(zone+" exist so i don't create it")
    fileToWrite=getRoomHtml(zone,objectDict,"",zoneDict)
    make_fs_ready_to_write()
    file0 = open(baseRoomPath+zone+"/index.html", "w")
    file0.write(fileToWrite)
    file0.close()
    #os.system("chmod 777 "+html_file_location)
    #with lock_bash_cmd:
    #  subprocess.call("chmod 777 "+html_file_location, shell=True,close_fds=True)
    os.chmod(html_file_location, 0o777)
    make_fs_readonly()

  else:
    logprint("I make the directory:"+zone)
    #os.system("mkdir "+baseRoomPath+zone) 
    #with lock_bash_cmd:
    #  subprocess.call("mkdir "+baseRoomPath+zone, shell=True,close_fds=True) 
    make_fs_ready_to_write()
    try:
      if os.path.isdir(baseRoomPath+zone)!=1:         #if the directory doesn't exist create it
        os.mkdir(baseRoomPath+zone)  
    except Exception as e: 
      message="error executing os.mkdir(baseRoomPath+zone)"
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

    fileToWrite=getRoomHtml(zone,objectDict,"",zoneDict)
    file0 = open(baseRoomPath+zone+"/index.html", "w")
    file0.write(fileToWrite)
    file0.close()
    #os.system("chmod 777 "+html_file_location)
    #with lock_bash_cmd:
    #  subprocess.call("chmod 777 "+html_file_location, shell=True,close_fds=True)  
    os.chmod(html_file_location, 0o777)
    make_fs_readonly()
  return

def updateDir():
  retval = os.getcwd()
  logprint("updateDir()  executed")

  for zone  in zoneDict.keys() :  #will be call updateOneZone()   ....onosimprove
    
  
    index=retval+"/"+baseRoomPath+zone+"/index.html"
    if os.path.isfile(index):   #if the directory exist don't create it
      logprint(zone+" exist so i don't create it")
      fileToWrite=getRoomHtml(zone,objectDict,"",zoneDict)
      make_fs_ready_to_write()
      file0 = open(baseRoomPath+zone+"/index.html", "w")
      file0.write(fileToWrite)
      file0.close()
      #os.system("chmod 777 "+baseRoomPath+zone+"/index.html")
      #with lock_bash_cmd:
      #  subprocess.call("chmod 777 "+baseRoomPath+zone+"/index.html", shell=True,close_fds=True)  
      os.chmod(baseRoomPath+zone, 0o777)
      make_fs_readonly()
    else:
      logprint("create the file"+index)
      #os.system("mkdir "+baseRoomPath+zone)
      #with lock_bash_cmd: 
      #  subprocess.call("mkdir "+baseRoomPath+zone, shell=True,close_fds=True)  

      make_fs_ready_to_write()
      try:
        os.stat(baseRoomPath+zone)
      except:
        os.mkdir(baseRoomPath+zone) 

      fileToWrite=getRoomHtml(zone,objectDict,"",zoneDict)

      try:
        file0 = open(index, "w")
        file0.write(fileToWrite)
        file0.close()
        #with lock_bash_cmd: 
        #  subprocess.call("chmod 777 "+baseRoomPath+zone+"/index.html", shell=True,close_fds=True)  
        os.chmod(baseRoomPath+zone, 0o777)
      except Exception as e: 
        message="error creating "+baseRoomPath+zone+"/index.html"
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
      make_fs_readonly()

      #os.system("chmod 777 "+baseRoomPath+zone+"/index.html")


  return







def createNewNode(node_sn,node_address,node_fw):
  logprint("0createNewNode() executed with :"+node_sn)
  global uart_router_sn
  global node_password_dict
  global conf_options
  msg=""
  if node_address=="001":  #uart_node
    uart_router_sn=node_sn

  hwType=node_sn[0:-4]  #get Plug6way  from Plug6way0001

  #createNewWebObjFromNode(hwType,node_sn)

  if (node_sn in nodeDict.keys()): #&(force_recreate==0):
    logprint("found node in the dict")

    #nodeDict[node_sn].setNodeAddress(node_address)
    #if len(nodeDict[node_sn].getnodeObjectsDict())==0 :
    #  print("I force a node update")
    #  createNewNode(node_sn,node_address,node_fw,1) 
      # if the node doesn't have any object it means there is a problem so will force an update

    updateNodeAddress(node_sn,uart_router_sn,node_address,node_fw)


    msg=nodeDict[node_sn].getSetupMsg() 
  else: #create a new node
    logprint("requested setup for a node not existing yet ")                 

     #cut the last 4 char which are the numeric sn, in order to get only the type of hardware

    if (hwType in hardwareModelDict.keys()):  #if the hardware is in the list 
      logprint("added node_hw from query :"+hwType)

      createNewWebObjFromNode(hwType,node_sn)
      #if((len(node_sn)>0)&((node_sn)!=" ")): 
      hardware_node_model=hardwareModelDict[hwType]  
      nodeDict[node_sn]=hw_node.HwNode(node_sn,hardware_node_model,node_address,node_fw) 

      if node_sn not in node_password_dict:
 
        if ("password" in hardwareModelDict[hwType]["parameters"] ):  # to use the standard node password..
          node_password=hardwareModelDict[hwType]["parameters"]["password"]         
          node_password_dict[node_sn]=node_password
          conf_options["node_password_dict"]=node_password_dict  # todo delete the password when the node is deleted..
          updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 


        #nodeDict[node_sn].updateLastNodeSync(time.time())
    else:
      logprint("error creating new node the hardware:"+hwType+" is not listed on the hardwareModelDict ",verbose=10)
      return(-1)
      

        #if the room doesn't exist yet ...then:
  if (node_sn in zoneDict.keys()):
    logprint("the node:"+node_sn+" already exist in the zoneDict") 
  else:
    # if (node_sn+"_body" in objectDict.keys()):
    #   print "the node body already exist in the web_object_dict" 
    # else:
    #   objectDict[node_sn+"_body"]=newDefaultWebObjBody(node_sn+"_body")
    #zoneDict[node_sn]=[node_sn+"_body"]  # modify to update also the webobject dict and list 
    zoneDict[node_sn]={"objects":[],"order":len(zoneDict.keys()),"permissions":"777","group":[],"owner":"onos_sys","hidden":0}

    createNewWebObjFromNode(hwType,node_sn)
    updateNodeAddress(node_sn,uart_router_sn,node_address,node_fw)  
    msg=nodeDict[node_sn].getSetupMsg() 
    updateOneZone(node_sn)  #update the index.html file in the folder named as the zone..

    try:
      os.stat(baseRoomPath+node_sn)
    except:
      os.mkdir(baseRoomPath+node_sn)  

    try:
      text_file = open(baseRoomPath+node_sn+"/index.html", "w")
      text_file.write(getRoomHtml(node_sn,objectDict,"",zoneDict))
      text_file.close()
    except Exception as e: 
      message= "error creating new node index file  "+node_sn+" e:"+str(e.args)
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
      os.chmod(baseRoomPath+node_sn, 0o777)
      logprint("create a new zone"+node_sn)
      #print zoneDict
      updateOneZone(node_sn) 


  return(msg)




def setNodePin(node_sn,pin_number,pin_status,write_hw_enable):  # equal to NodePinToWebObject()
  #to change all the webobjects status that have the node and the pin given:
  logprint("setNodePin() executed")

  if node_sn not in nodeDict.keys():
    logprint("the serial number is not in the dictionary...so i add  the new node")
    return("error_the_node_does_not_exist")
  found=0
  for a in objectDict.keys():
    logprint(objectDict[a].getHwNodeSerialNumber() )
    if (objectDict[a].getHwNodeSerialNumber()==node_sn):
      logprint("node exist")
      if objectDict[a].getAttachedPinList()[0]==int(pin_number):
        found=1  
        if (len(objectDict[a].getAttachedPinList())==1):#the sensor object must have only a pin attached
          objName=objectDict[a].getName()                      
          #changeWebObjectStatus(objName,int (pin_status),write_hw_enable) #banana add to queue
          layerExchangeDataQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":str(pin_status),"write_to_hw":write_hw_enable })  
                

          logprint("pin"+str(pin_number)+" changed from setNodePin to:"+str(pin_status))                      

        else:
          logprint("error number of pin in the setNodePin section",verbose=10)
          return("error_no_pin_found_in_the_node")
  if found==0:
    logprint("error_no_pin_found_in_the_node",verbose=10)
    return("error_no_pin_found_in_the_node")
  else:
    return("ok")








#router_sn is in globalVar.py

createNewNode(router_sn,"0",router_hardware_fw_version) #make the router node







        
#moved to conf.py
#def newDefaultWebObj(name):
#  return(WebObject(name,"b",0,"/*background-color:green;*/","/*background-color:red;*/",name+"=0",name+"=1"," "," "," "," ",9999))


updateDir()








def getUserFromIp(ipUserAddress):
  logprint("getUserFromIp() executed")
  if ipUserAddress in user_active_time_dict.keys(): # the ip is in the dict
      username=user_active_time_dict[ipUserAddress][0]
      old_active_time=user_active_time_dict[ipUserAddress][1]
      current_time=(datetime.datetime.today().minute+(datetime.datetime.today().hour)*60 )
      if (current_time >(old_active_time+conf_options["logTimeout"]) ):   #timeout
      #if user was not active in the last 10 minutes logout
        logprint("user:"+username+"logged out for timeout")
        del user_active_time_dict[ipUserAddress] #remove the ip from the dict   
        logprint("deleted ip from user_active_time_dict ")
        return ("nobody")
      else:
        logprint("user:" +username+"is still active")
        user_active_time_dict[ipUserAddress][1]=current_time
        return(username)
  else:
    logprint("ipaddress not in list")
    return("nobody")





class MyHandler(BaseHTTPRequestHandler):
    #global objectDict  
    #global roomDict
    

    def log_message(self, format, *args):  #remove the print of each request..comment this method to make it print..
      return




    def finish_request(self, request, client_address):# i don't know if usefull to close client timout connections
      logprint("finish_request() executed") 
      request.settimeout(30)
      # "super" can not be used because BaseServer is not created from object
      BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)


    wbufsize = -1
    # Disable Nagle's Algorithm (Python 2.7/3.2 and later).
    disable_nagle_algorithm = True

    if not hasattr(BaseHTTPRequestHandler, 'disable_nagle_algorithm'):   #http://pydoc.net/Python/mrs-mapreduce/0.9/mrs.http/  https://aboutsimon.com/index.html%3Fp=85.html
        def setup(self):
            BaseHTTPRequestHandler.setup(self)
            if self.disable_nagle_algorithm:
              self.connection.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY, True)

            BaseHTTPServer.BaseHTTPRequestHandler.setup(self)# i don't know if usefull to close client timout connections
            self.request.settimeout(30)# i don't know if usefull to close client timout connections




    def finish(self,*args,**kw):
      #print "finish function called to close socket"
      
      #if not self.wfile.closed:
      #  self.wfile.flush()

      #self.wfile.close()
      #self.rfile.close()

      if not self.wfile.closed:
        try:
          self.wfile.flush()
          self.wfile.close()
        except :
          logprint("error in flush finish() socket closed ")
          pass  #ignore the error

          try:
            self.wfile.close()
          except:
            logprint("error in self.wfile.close() finish() socket closed ")
            pass  #ignore the error

      try:  
        self.rfile.close()
      except:
        logprint("error in self.wfile.close()  self.rfile.close()  socket closed ")
        pass
      return        

    def clear_PostData(self,data):
      if len(data)==0:
        logprint("empty form")
        return ("")
      tmp_data=data
      i=0
      en=0
      while ((i<len(data))&(data[i]==" ")):  #remove all the starting spacing
        i=i+1
      tmp_data=data[i:] 
      i=len(tmp_data)-1
      while ((i>0)&(tmp_data[i]==" ")): #remove all the spacing after the end of string
        i=i-1
      tmp_data=tmp_data[0:i+1]
      tmp_data=string.replace(tmp_data, " ", "_")
      return(tmp_data)  
           



       #         self.path=string.replace(self.path, "%20", " ")   #rimuovo i %20 che si formano al posto degli spazii
        #        self.path=string.replace(self.path, ',&%', '\n') 
        #        self.path=string.replace(self.path, '%7D', '}') 
         #       self.path=string.replace(self.path, '%7B', '{') 




    def get_login(self): 
      #self.send_response(301)
      #self.send_header('Location','/login.html')
      #self.end_headers()
      try:             
        h = open("gui/login.html",'r')  
        web_page=h.read()
        h.close()
      except:
        logprint("no index.html found in root directory")
        web_page=web_page_not_found   
      try:
        self.send_response(200)
        self.send_header('Content-type',	'text/html')
        self.end_headers()
        self.wfile.write(web_page) 
      except:
        logprint("error1 in send_header")
        pass
      return   






    def get_WebOjectManager(self,obj_Dict): 
    
      

      html_page='''<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/css/objects_manager.css" type="text/css" media="all" />
  <meta charset="utf-8">
  <title>Web Objects Manager</title>

<script type="text/javascript" language="javascript">function SelectAll(id){    document.getElementById(id).focus();   document.getElementById(id).select();}</script>
</head>
<body>
  
<form action="" method="POST"><input type="hidden" name="objs_manager" value="/setup/objs_manager">

  
<div id="buttons">
   
  <a href="/"><div id="home">HOME</div></a>
  <a href="/setup/"><div id="back">BACK</div></a>
 
</div>
 <div id="header">WEB OBJECTS MANAGER</div>

  
<div id="testo">
   
<input type="text" id="create_web_obj"  onclick="SelectAll('create_web_obj')"; name="new_web_object" value="TYPE A NEW OBJECT NAME HERE">
<input type="submit" value="CREATE">
</form>

</div>



  ''' 


      l=obj_Dict.keys()
      l.sort()
      for a in l:
             
        html_page=html_page+'''
<div id="riga">
<div id="NOMEOGGETTO">'''+a+'''</div>
<a href="/setup/web_obj_modifier/'''+a+'''" ><div id="SETUP">SETUP</div></a>
<a href="/setup/web_obj_modifier/delete_item/'''+a+'''"><div id="DELETE">DELETE</div></a>
</div>
  '''

      html_page=html_page+'''
<div id="riga" style=" visibility: hidden;">
<div id="NOMEOGGETTO"></div>
<div id="SETUP"></div>
<div id="DELETE"></div>
</div>
  '''

      html_page=html_page+'''</body></html>'''

      return(html_page)











    def get_zone_manager(self,r_Dict):
    
      
      r_list=r_Dict.keys()
      r_list.sort() #sort room by name
      html=''
      for a in r_list :
        html=html+'''<div id="riga">
   
<div id="nomezona">'''+a+'''</div>
<input type="text" id="'''+a+'''" name="'''+a+'''" value="RENAME IT AND CLICK SUBMIT">
  
  
  <div id="deletebox">
    <div id="DELETE">DELETE</div>
    <input id="'''+a+'''" type="checkbox" name="delete_room_'''+a+'''" />
  </div>
	
  <a href="/zone_objects_setup/'''+a+'''"><div id="oggetti">Objects</div> </a>  


</div>
  '''

      html_p=get_zone_manager_inner_html+html+'''</form> 
</body>
</html>'''         
      return (html_p) 






      

    def get_Zone_Objects_Setup(self,current_path,objectDictionary,zone):         
      logprint("current_path"+current_path)
      if string.find(current_path,"/setup")!=-1:
        link_back="/setup/zone_manager/"
      else:
        link_back="/zone_list"

      html_page='''<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="/css/zone_object_setup_css.css" type="text/css" media="all" />

  <meta name="viewport" content="width=device-width"  >
  <meta charset="utf-8">
  <title>Zone_object_setup</title>
<script type="text/javascript" language="javascript">function SelectAll(id){    document.getElementById(id).focus();   document.getElementById(id).select();}</script>
</head>
<body>
<form action="" method="POST"><input type="hidden" name="zone_objects_setup" value="'''+zone+'''">
  
<div id="buttons">
  <input type="submit" value="SUBMIT">
  <a href="/"><div id="home">HOME</div></a>
  <a href="'''+link_back+'''"><div id="back">BACK</div></a>
 
</div>
  
  
  

  
 <div id="header">'''+zone+''' objects setup</div>
  
  
<div id="testo">
   

<input type="text" name="new_objects" id="create_zone_web_obj"  onclick="SelectAll('create_zone_web_obj')";  value="TYPE_NEW_OBJECT_HERE">



</div>'''  



      if zone  in zoneDict.keys() :

        logprint("zone in zoneDict")
        obj_name_list=zoneDict[zone]["objects"]
      
        tmp_html='<tr><td class="web_obj_name">No web object present in this room</td><td></td><td class="web_obj_name"></td></tr>'


        obj_name_list.sort()

        for a in obj_name_list :
          c=a
          #c=string.replace(a, "_p_"+zone, "_p") 
          #c=string.replace(c,zone+"_body", zone+"_b_") 
          html_page=html_page+'''
<div id="riga">
<div id="object">'''+c+'''</div>
<div id="used">  
  ADD
  <input type="checkbox" name="'''+a+'''_sel_obj" checked="checked" />
  </div>
</div>
  '''
     






        l=[]
        l=objectDictionary.keys()
        l.sort()
        for b in l:


          body_found=string.find(b,"_body")
          part_without_body=" "
          en=1

          if (body_found!=-1):
            logprint("found a body:"+b)
            part_without_body=string.replace(b, "_body", "")   #b[0:body_found]
            if (part_without_body==zone):
              logprint("body enabled")
              en=1                            #allow the display of the same body of the zone
            else: 
              logprint("body rejected")
              en=0                              #block the display of the body of others zones


          private_found=string.find(b,"_p_")  #private object to show only in its zone
          part_without_private=" "
          en2=1
          if (private_found!=-1):

            part_without_private=b[private_found+3:]
            if (part_without_private==zone):
                en2=1                            #allow the display of private object of the zone
            else: 
              en2=0                              #block the display of private object of others zones



          if (b not in obj_name_list)&(en==1)&(en2==1) :
            c=b
            #c=string.replace(b, "_p_"+zone, "_p") 
            #c=string.replace(c,zone+"_body", zone+"_b_") 
            html_page=html_page+'''

<div id="riga">

   

<div id="object">'''+c+'''</div>
<div id="add">
  ADD
  <input type="checkbox" name="'''+b+'''_sel_obj" />
  </div>
</div>
  ''' 
        html_page=html_page+'''<div id="riga" style=" visibility: hidden;" ><div id="object"></div><div id="add" style="border: 1px"></div></div>'''  
        #to make the last element void in order to not be hidden a webobject under the submit button
    

      else:      #zone not the room object      
        logprint("not a room")


      html_page=html_page+'''</form></body></html>'''

      return(html_page)






    def get_RoomObjectList(self,room,objectDictionary):#return the html for the web_objects form present in a room

      #room_index=roomList.index(room)
      #updateOneZone(room)          if uncommented make the htmlobj double...
      html_tmp='''<html><head><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="/css/zone_object_list_config.css" type="text/css" media="all" /><style> </style><script type="text/javascript" language="javascript">function SelectAll(id){    document.getElementById(id).focus();   document.getElementById(id).select();}</script></head><body><form action="" method="POST"><input type="hidden" name="current_room" value="'''+room+'''"> <table border="1" style="width:100%"><tr class="web_obj_title"> <td>Room web objects , click them to modify:</td><td>Html example to use the web object on a html page</td></tr>'''
      html=''
      if room  in zoneDict.keys() :
        #print "room in zoneDict"
        obj_name_list=zoneDict[room]["objects"]
        i=0
        tmp_html='<tr><td class="web_obj_name">No web object present in this room</td><td></td><td class="web_obj_name"></td></tr>'
        for a in obj_name_list :
          tmp_html=''           
        
          #print "web obj in the room ="+a
          html=html+'<tr><td class="web_obj_name"><a    href="'+self.path+'/'+a+'">'+a+'</a></td><td class="web_obj_code" ><xmp ><a id="'+a+'"  href="?'+a+'=0">'+a+'</a> </xmp></td><td class="web_obj_name">Remove this web object from this Room <input type="checkbox" name="rm_obj_'+a+'_from_'+room+'" value="'+a+'"></td></tr>'
      if (len(tmp_html)>4) :
        html=html+tmp_html
      html=html+'</table>'
      html=html+'<table border="1" style="width:100%"><tr><br/></tr><tr class="web_obj_title" ><td>Manage the web object not present in the room</td></tr></table>'
      html=html+'<table border="1" style="width:100%"><tr><td class="web_obj_name">Add an existing web object to this room</td><td class="web_obj_name">' 


      #print "room dict values:"
      #print zoneDict.values()
      #print zoneDict.values()[0][0]

      html=html+'<table border="1" style="width:100%;text-align:center">'
      


      for s in  objectDictionary.keys():
        body_found=string.find(s,"_body")
        part_without_body=" "
        en=1
        if (body_found!=-1):
          part_without_body=s[0:body_found]
          if (part_without_body==room):
              en=1                            #allow the display of the same body of the room
          else: 
            en=0                              #block the display of the body of others rooms

        

        if (objectDictionary[s].getName() not in zoneDict[room]["objects" ])& (en==1): #if web object not yet present in the room make possible to add it 

          html=html+'<tr><td>Add Web Object</td><td>'+objectDictionary[s].getName()+' </td><td>To This Room <input type="checkbox" name="add_obj_to_room'+objectDictionary[s].getName()+'" value="'+objectDictionary[s].getName()+'"> </td></tr> '

      html=html+'</table>'
      html=html+'''<tr><td class="web_obj_name">Create a new web object</td><td><input type="text" onClick="SelectAll('new_object_text')";  id="new_object_text"  name="new_web_object" value="'''+default_new_obj_value+'''"  size="50" >   </td> </tr>'''
      html=html+'''</table><input type="submit" value="Submit" ></form>''' 
      #print "stanza" 
      #print room
      html=html+'''<table border="1" style="width:100%"><tr><td class="web_obj_title">Modify the room html </td></tr><tr><td class="web_obj_name"><a  href="/'''+baseDir+room+'''/index.html/?=" >Click Here to go to the room web page </a> </td></tr>'''

      

      html=html+'<tr><td><form action="" method="POST"><input type="hidden" name="current_room_text_area" value="'+room+'"><textarea name="html_room_mod" cols=1 rows=5  style="width:100%" >'+getRoomHtml(room,objectDictionary,"",zoneDict)+'</textarea></td></tr>'
            
      pag=html_tmp+html+'</table><input type="submit" value="Submit_textarea" ></form></body></html>' 

      self.path="/"
      return(pag)



    def get_WebObjForm(self,web_obj):#return the html web form to modify a web object 
      style=web_obj.getStyle()
      name=web_obj.getName()
      html_obj=web_obj.getHtml()

      templateFile = open('setup/ModifyWebObjForm.template.html','rb') #get the template to use in order to render the page
      ModObjFormPage=templateFile.read()
      templateFile.close()

      notes="Enter_The_Web_Object_Notes"
      hardwarePin=no_pin_selected  #string display when no pin has been assigned yet containing "no_pin"
      type_b=""
      type_sb=""
      type_l=""
      type_d_sensor=""
      type_a_sensor=""
      current_status0=" "
      current_status1=" "
      style0="/*Enter here the style you want your web object to have when its status is 0 */"
      style1="/*Enter here the style you want your web object to have when its status is 0 */"
      html0="<!-- Enter here the html you want your web object to display when its status is 0  -->"
      html1="<!-- Enter here the html you want your web object to display when its status is 1  -->"
      command0=" "
      command1=" "
      init_command=" "

      if web_obj.getNotes()!=" " :
        notes=web_obj.getNotes() 

      if web_obj.getAttachedPinList()[0]!=9999 :
        hardwarePin=str(web_obj.getAttachedPinList()[0]) 

      if web_obj.getType()=="b" :
        type_b="checked"


      if web_obj.getType()=="sb" :
        type_sb="checked"


      if web_obj.getType()=="l" :
        type_l="checked"

      if web_obj.getType()=="d_sensor" :
        type_d_sensor="checked"

      if web_obj.getType()=="a_sensor" :
        type_a_sensor="checked"

      if web_obj.getStatus()==0 :
        current_status0="checked"
        current_status1=""
        status_link="1"
      else:
        current_status0=""
        current_status1="checked"
        status_link="0"

      if web_obj.getStyle0()!=" " :
        style0=web_obj.getStyle0()

      if web_obj.getStyle1()!=" " :
        style1=web_obj.getStyle1()

      if web_obj.getHtml0()!=" " :
        html0=web_obj.getHtml0()

      if web_obj.getHtml1()!=" " :
        html1=web_obj.getHtml1()

      if web_obj.getCommand0()!=" " :
        command0=web_obj.getCommand0()

      if web_obj.getCommand1()!=" " :
        command1=web_obj.getCommand1()

      if web_obj.getInitCommand()!=" " :
        init_command=web_obj.getInitCommand()


 
      try:
        "style="+style
      except:
        style=" "

      #use the template and replace the parts ONOS+name parts  with the right parts from system
      ModObjFormPage=ModObjFormPage.replace("+ONOSstyle+",style);
      ModObjFormPage=ModObjFormPage.replace("ONOSself.path+",self.path);
      ModObjFormPage=ModObjFormPage.replace("+ONOSname+",name);
      ModObjFormPage=ModObjFormPage.replace("+ONOSnotes+",notes);
      ModObjFormPage=ModObjFormPage.replace("+ONOSpin+",hardwarePin);
      ModObjFormPage=ModObjFormPage.replace("+ONOStype_b+",type_b);
      ModObjFormPage=ModObjFormPage.replace("+ONOStype_sb+",type_sb);
      ModObjFormPage=ModObjFormPage.replace("+ONOStype_l+",type_l);
      ModObjFormPage=ModObjFormPage.replace("+ONOStype_d_sensor+",type_d_sensor);
      ModObjFormPage=ModObjFormPage.replace("+ONOStype_a_sensor+",type_a_sensor);
      ModObjFormPage=ModObjFormPage.replace("+ONOScurrent_status0+",current_status0);
      ModObjFormPage=ModObjFormPage.replace("+ONOScurrent_status1+",current_status1);
      ModObjFormPage=ModObjFormPage.replace("+ONOSstatus_link+",status_link);
      ModObjFormPage=ModObjFormPage.replace("+ONOShtml_obj+",html_obj);
      ModObjFormPage=ModObjFormPage.replace("+ONOSstyle0+",style0);
      ModObjFormPage=ModObjFormPage.replace("+ONOSstyle1+",style1);
      ModObjFormPage=ModObjFormPage.replace("+ONOShtml0+",html0);
      ModObjFormPage=ModObjFormPage.replace("+ONOShtml1+",html1);
      ModObjFormPage=ModObjFormPage.replace("+ONOScommand0+",command0);
      ModObjFormPage=ModObjFormPage.replace("+ONOScommand1+",command1);
      ModObjFormPage=ModObjFormPage.replace("+ONOSinit_command+",init_command);



     # pag='<html><head><style type="text/css">.text{font-size:110%} .title{color: red;font-size:120%}'+style+'</style></head><body><form action="" method="POST"><input type="hidden" name="mod_object" value="'+self.path+'"><table border="1" style="width:100%"><tr><td><div class="title"> Web Object Name: </div><br/><input type="text" name="obj_name"  value="'+name+'"  size="50" style="width:100%"><br/><br/></td><td><div class="title">Web Object Notes: </div><br/><input type="text" name="obj_notes"  value="'+notes+'"  size="50"  style="width:100%"><br/><br/></td></tr><tr><td><div class="title"> Web Object Type </div><ul><input type="radio" name="obj_type" value="b" '+type_b+'>Normal Button</ul><ul><input type="radio" name="obj_type" value="sb" '+type_sb+'>Static Button</ul><ul><input type="radio" name="obj_type"value="l" '+type_l+' >Web Label</ul><br/><br/><br/></td><td><div class="title"> Web Object Current Status </div><ul><input type="radio" name="obj_current_status" value="0" '+current_status0+'  >0</ul><ul><input type="radio" name="obj_current_status" value="1" '+current_status1+' >1</ul><br/> <a id="'+name+'"  href="/?'+name+'='+status_link+'">'+html_obj+'</a> <br/><xmp ><a id="'+name+'"  href="/?'+name+'='+status_link+'">'+html_obj+'</a></xmp >  <br/></td></tr><br/><tr><td class="title">First Web Object Style &nbsp;</td><td class="title">Second Web Object Style</td></tr><tr><td>  <textarea name="obj_style0" cols=1 rows=15 style="width:100%" >'+style0+'</textarea></td> <td>    <textarea name="obj_style1" cols=1 rows=15 style="width:100%">'+style1+'</textarea></td></tr><tr><td> <div class="title">First Web Object Html </div> Html displayed on web page when the web object status is 0</td><td><div class="title">Second Web Object Html</div>Html displayed on web page when the web object status is 1</td></tr><tr><td> <textarea name="obj_html0" cols=1 rows=15 style="width:100%">'+html0+'</textarea></td> <td>    <textarea name="obj_html1" cols=1 rows=15 style="width:100%">'+html1+'</textarea></td> </tr><tr> <td><div class="title">First Web Object Command</div>Bash command executed when the web object status changes from 1 to 0 </td><td><div class="title">Second Web Object Command</div>Bash command executed when the web object status changes from 0 to 1 </td> </tr><tr> <td> <textarea name="obj_cmd0" cols=1 rows=5 style="width:100%">'+command0+'</textarea></td> <td>    <textarea name="obj_cmd1" cols=1 rows=5 style="width:100%">'+command1+'</textarea></td> </tr><tr><table border="1" style="width:100%"><tr><td style="width:15%" ><div class="title" > Web Object Init Command</div>Command executed once only when you start the webserver</td> <td>    <textarea name="obj_init_cmd" cols=1 rows=5 style="width:100%">'+init_command+'</textarea></td></tr></table></tr></table></div><br/><br/><br/> <input type="submit" value="Submit"><input type="reset" value="Reset"></form></body></html>'


      return(ModObjFormPage)








  


 

    def do_GET(self):
        self.current_username="nobody"
        logprint("current_url:"+self.path+":end_url")

        try:


            if (self.path=="/"):
              #print "rrrrrrrrrrrrrrrrrrrrrooooooooooooooooooooooot"
              namespace={}
              cgi_name="gui/home.py"       
              #execfile(cgi_name,globals(),namespace)
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
              web_page=namespace["web_page"]


              try:     
                logprint(self.path)      
                #h = open("index.html",'r')  
                #web_page=h.read()
                #h.close()

              except:
                logprint("no index.html found in root directory")
                web_page=web_page_not_found   
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except:
                logprint("error2 in send_header ")
                errorQueue.put( "error2 in send_header ")  
              return
            

             
            if (     (string.find(self.path,"info_hash=")!=-1)):  # if the address contain info_hash= then discard it 
              logprint("address discarded ")
              return




            if (string.find(self.path,"sonoffOTA")!=-1):  # if the url contain onos_cmd
              #localhost/sonoffOTA/Sonoff1P0001.ino.bin
              logprint("requested a firmware upgrade:"+self.path,verbose=5)
              #filepath="sonoffOTA/Sonoff1P0001.ino.bin
              #f = open(self.path[1:],'rb')
              #binFile=f.read()
              #f.close()
              #self.send_response(200)
              #self.send_header('Content-type',	'application/octet-stream')
              #self.send_header("Content-Disposition", 'attachment; filename="Sonoff1P0001.ino.bin"')
              #self.wfile.write(binFile) 
              #self.end_headers()
              FILEPATH=self.path[1:]
              with open(FILEPATH, 'rb') as f:
                self.send_response(200)
                self.send_header("Content-Disposition", 'attachment; filename="Sonoff1P0001.ino.bin"')
                fs = os.fstat(f.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)


            if ((string.find(self.path,"onos_cmd")!=-1)|(string.find(self.path,"cmd=")!=-1)   ):  # if the url contain onos_cmd then parse it 

#example1:
#localhost/onos_cmd?cmd=setSts&obj=sensor1&status=1&hw=0__  this change only the webobject,use it to change sensor value..
#example2:
#localhost/onos_cmd?cmd=setSts&obj=sensor1&status=1&hw=1__  this change both , the webobject and the hardware status
#   
#
              url=self.path
              logprint("onos_cmd received"+url)

              #example: /onos_cmd?cmd=setSts&obj=sensor1&status=1&hw=0__
              if string.find(url,"cmd=setSts&obj=")!=-1:
                msg="ok"
                #start_obj_name=string.find(url,'obj=')+4
                #end_obj_name=string.find(url,'&',start_obj_name)
                #webobjName=url[start_obj_name:end_obj_name]


                try:
                  objName=re.search('setSts&obj=(.+?)&',self.path).group(1)
             
                #start_status=string.find(url,'&status=')+8
                #end_status=string.find(url,'&',start_status)
                #status_to_set=url[start_status:end_status]
                  status_to_set=re.search('&status=(.+?)&',self.path).group(1)

                #start_hw_flag=string.find(url,'&hw=')+4
                #end_hw_flag=string.find(url,'__',start_hw_flag)
                #hw_flag=url[start_hw_flag:end_hw_flag]
                  hw_flag=re.search('&hw=(.+?)__',self.path).group(1)


                except Exception as e: 

                  message="error in re.search 1   on onos_cmd url  "+url
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))





                try:
                  write_hw_enable=int(hw_flag)
                except Exception as e: 
                  message="error in write_hw_enable  on onos_cmd url  "+" e:"+str(e.args)
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  write_hw_enable=1

                logprint("------set "+objName+"to"+status_to_set)
                  
                #if objName in objectDict.keys():
                #try:
                  #changeWebObjectStatus(objName,int (status_to_set),write_hw_enable) 
                layerExchangeDataQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":write_hw_enable })  
                
                #except:
                #  print "error objName not in the dict "
                #  errorQueue.put("error objName not in the dict " )  
                #  msg="error objName not in the dict " 

                #banana to add also the status check 
                try:
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(msg) 
                except Exception as e  :
                  message="error3 in send_header"
                  logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
                  pass
                return





              # localhost/cmd=ou&sn=Sonoff1P0001&f=5.28&obj=0&s=1__
              # set a object status from a node 

              if string.find(self.path,"cmd=ou&")!=-1:
                logprint("received a onos_cmd?cmd=ou  query")

                serial_number=re.search('&sn=(.+?)&',self.path).group(1)
                logprint("node_sn="+serial_number)    

                node_fw=re.search('&f=(.+?)&',self.path).group(1)
                logprint("node_fw="+node_fw)        

                obj_address_to_update=re.search('&obj=(.+?)&',self.path).group(1)
                logprint("obj_number="+obj_address_to_update)

                obj_value=re.search('&s=(.+?)__',self.path).group(1)
                logprint( "obj_status="+obj_value)

                node_address=str(self.client_address[0])
                logprint("node_ip="+node_address)


                #now i have to check in all the web obj which one is connected to the pin of this node


                #answer=setNodePin(node_sn,pin_number,pin_status,write_hw_enable)
                priorityCmdQueue.put( {"cmd":"updateObjFromNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw,"objects_to_update":{obj_address_to_update:obj_value} })  


                answer="[S_ok_#]"

                try:
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(answer) 
                except Exception as e  :
                  message= "error4 in send_header "
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                return






              #localhost/cmd=sa&sn=Sonoff1P0001&f=5.28__

              #set address of the new node, first time connection..
              if string.find(self.path,"cmd=sa&")!=-1:
                logprint("received a onos_cmd?cmd=chObj  query")

                serial_number=re.search('&sn=(.+?)&',self.path).group(1)
                logprint("node_sn="+serial_number)    

                node_fw=re.search('&f=(.+?)__',self.path).group(1)
                logprint("node_fw="+node_fw)        

                node_address=str(self.client_address[0])
                logprint("node_ip="+node_address)


                priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":serial_number,"nodeAddress":node_address,"nodeFw":node_fw })     


                

                answer="[S_ok_#]"

                try:
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(answer) 
                except Exception as e  :
                  message= "error4 in send_header "
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                return





#write here the msg get setup__
#example: 
#localhost/onos_cmd?cmd=pinsetup&node_sn=Plug6way0001&node_fw=4.85__
#localhost/onos_cmd?cmd=pinsetup&node_sn=Plug6way0002&node_fw=4.85__
#localhost/onos_cmd?cmd=pinsetup&node_sn=ProminiA0001&node_fw=4.85__
#localhost/onos_cmd?cmd=pinsetup&node_sn=ProminiA0002&node_fw=4.85__



              if string.find(url,"onos_cmd?cmd=pinsetup&")!=-1:
                logprint("received a onos_cmd?cmd=pinsetup  query")
                #start_node_sn=string.find(url,'node_sn=')+8
                #end_node_sn=string.find(url,'&',start_node_sn)
                #node_sn=url[start_node_sn:end_node_sn]
                node_sn=re.search('&node_sn=(.+?)&',self.path).group(1)
                logprint("node_sn="+node_sn)

                #start_node_fw=string.find(url,'node_fw=')+8
                #end_node_fw=string.find(url,'&',start_node_fw)
                #node_fw=url[start_node_fw:end_node_fw]
                node_fw=re.search('&node_fw=(.+?)__',self.path).group(1)
                logprint("node_fw="+node_fw)
                 
               # start_node_ip=string.find(url,'node_ip=')+8
               # end_node_ip=string.find(url,'__',start_node_ip)
                #node_ip=url[start_node_ip:end_node_ip]
                node_ip=str(self.client_address[0])
                logprint("node_ip="+node_ip)

                msg="ok"
                msg=createNewNode(node_sn,node_ip,node_fw)

                logprint("i try to send msg: "+msg)
                try:
                  self.send_response(200)
                  self.send_header('Content-Type: application/octet-stream','text/plain')
                  self.end_headers()
                  self.wfile.write(msg) 
                except Exception as e  :              
                  message="error6 in send_header onos cmd 001"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                  pass
                return



#  // http://192.168.1.102/onos_cmd=sy&sn=ProminiA0002&fw=5.28&

              if string.find(url,"onos_cmd=sy&")!=-1:
                logprint("received a onos_cmd?cmd=sync  query")
                #start_node_sn=string.find(url,'node_sn=')+8
                #end_node_sn=string.find(url,'&',start_node_sn)
                #node_sn=url[start_node_sn:end_node_sn]
                node_sn=re.search('&sn=(.+?)&',self.path).group(1)
                logprint("node_sn="+node_sn)

                #start_node_fw=string.find(url,'node_fw=')+8
                #end_node_fw=string.find(url,'&',start_node_fw)
                #node_fw=url[start_node_fw:end_node_fw]
                node_fw=re.search('&fw=(.+?)&',self.path).group(1)
                logprint("node_fw="+node_fw)
                 
               # start_node_ip=string.find(url,'node_ip=')+8
               # end_node_ip=string.find(url,'__',start_node_ip)
                #node_ip=url[start_node_ip:end_node_ip]
                node_ip=str(self.client_address[0])
                logprint("node_ip="+node_ip)


                msg=createNewNode(node_sn,node_ip,node_fw)


                msg="ok"
                logprint("i try to send msg: "+msg)
                try:
                  self.send_response(200)
                  self.send_header('Content-Type: application/octet-stream','text/plain')
                  self.end_headers()
                  self.wfile.write(msg) 
                except Exception as e  :
                  message="error7 in send_header onos cmd 001"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pass
                return


    #          try:
    #            self.send_response(200)
    #            self.send_header('Content-type',	'text/html')
    #            self.end_headers()
    #            self.wfile.write("error_onos_cmd") 
    #          except:
    #            pass
    #            print "error in send_header "
    #          return   


            if (self.path=="/login.html"):
              
              
              try:             
                h = open("login.html",'r')  
                web_page=h.read()
                h.close()
              except:
                logprint("no login.html found in root directory")
                web_page=web_page_not_found   


              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :

                message="error8 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              return   





            if ((self.path.endswith(".jpg"))|(self.path.endswith(".gif"))|(self.path.endswith(".png"))|(self.path.endswith(".JPG"))|(self.path.endswith(".PNG")) |(self.path.endswith(".ico")) ):
                f = open(curdir + sep + self.path,'rb') #self.path has /test.html
                photoFile=f.read()
                f.close()


#note that this potentially makes every file on your computer readable by the internet
                

                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'image/png')
                  self.send_header('Cache-Control',        'max-age=31536000')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(photoFile)
                except Exception as e  :
                  message="error in send_header img"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                  pass
                return



            if (self.path.endswith(".css"))|(self.path.endswith(".CSS")):
                f = open(curdir + sep + self.path,'rb') #self.path has /test.html
                cssFile=f.read()
                f.close()
#note that this potentially makes every file on your computer readable by the internet
                
                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'text/css')
                  self.send_header('Cache-Control',        'max-age=1')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(cssFile)
                  #print "served a css file"
                except Exception as e  :
                  message="error9a in send_header "
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pass
                return


            if (self.path.find(".svg")!=-1):  #example:  Onos.woff?d21qig'
                fileName=curdir + sep + self.path.split(".svg")[0]+".svg"       #get only the filename without parameters 
                with open(fileName, 'rb') as f:   #read the pin status
                  askedFile=f.read()
#note that this potentially makes every file on your computer readable by the internet
                
                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'application/font-woff')
                  self.send_header('Cache-Control',        'max-age=1')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(askedFile)
                  #print "served a css file"
                except Exception as e  :
                  message="error9b in send_header "
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                  pass
                return



            if (self.path.find(".woff")!=-1):  #example:  Onos.woff?d21qig'
                fileName=curdir + sep + self.path.split(".woff")[0]+".woff"       #get only the filename without parameters 
                with open(fileName, 'rb') as f:   #read the pin status
                  askedFile=f.read()
#note that this potentially makes every file on your computer readable by the internet
                
                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'application/font-woff')
                  self.send_header('Cache-Control',        'max-age=1')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(askedFile)
                  #print "served a css file"
                except Exception as e  :
                  message="error9c in send_header "
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                  pass
                return



            if (self.path.find(".eot")!=-1):  #example:  Onos.woff?d21qig'
                fileName=curdir + sep + self.path.split(".eot")[0]+".eot"       #get only the filename without parameters 
                with open(fileName, 'rb') as f:   #read the pin status
                  askedFile=f.read()
#note that this potentially makes every file on your computer readable by the internet
                
                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'application/font-woff')
                  self.send_header('Cache-Control',        'max-age=1')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(askedFile)
                  #print "served a css file"
                except Exception as e  :
                  message="error9d in send_header "  
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pass               
                return



            if ((self.path.find(".ttf")!=-1))|((self.path.find(".TTF")!=-1)):
                fileName=curdir + sep + self.path.split(".ttf")[0]+".ttf"       #get only the filename without parameters 
                with open(fileName, 'rb') as f:   #read the pin status
                  askedFile=f.read()
#note that this potentially makes every file on your computer readable by the internet
                
                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'application/x-font-ttf')
                  self.send_header('Cache-Control',        'max-age=1')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(askedFile)
                  #print "served a css file"
                except Exception as e  :
                  message="error9e in send_header "   
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))    
                  pass
                return





            if (self.path.endswith(".js"))| (self.path.endswith(".JS")):
                f = open(curdir + sep + self.path,'rb') #self.path has /test.html
                javaFile=f.read()
                f.close()
#note that this potentially makes every file on your computer readable by the internet
                try:
                  self.send_response(200)
                  self.send_header('Content-type',        'text/javascript')
                  self.send_header('Cache-Control',        'max-age=1')  #set the cache of the image to a long time to prevent background image flipping
                  self.end_headers()
                  self.wfile.write(javaFile)
                except Exception as e  :
                  message="error10 in send_header " 
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
                  pass               
                return









            #from here to the end the login is required , the above part is for the onos node use.
            self.current_username="nobody"
            if (conf_options["login_required"]==1):
              self.current_username=getUserFromIp(self.client_address[0])

              if (self.current_username=="nobody") : #user not logged
                logprint("user not logged ,i show login page")
                self.get_login()  #show login page
                return()






                
                



            if (len (self.path)<2):
              logprint("main address..")
                #print stato_led1

              try:   

                namespace={}   
                cgi_name="/gui/home.py"       
                #execfile(cgi_name,globals(),namespace)
                exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                web_page=namespace["web_page"]

                #h = open("index.html",'r')  
                #web_page=h.read()
                #h.close()
              except:
                logprint("no index.html found in root directory")
                web_page=web_page_not_found  

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
                logprint("percorso="+self.path+"end")


              except Exception as e  :
                message="error11 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))      
                pass                
              return


   
            
            if  ( string.find(self.path,"zone_list"))!=-1:
                #print "indirizzo a pag principale.."
                #print stato_led1 
                #address_list=string.split(self.path,"/") 
                home='/'   #the home page of onos
                #back=address_list[0]
                html='''<!DOCTYPE html><html> <head><link rel="stylesheet" href="/css/zone_list.css" type="text/css" media="all" /><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">    <meta charset="utf-8">    <title>O.N.O.S</title></head>  <body><div id="buttons"> <a  href="'''+home+'''"><div id="home">HOME</div><a  href="'''+home+'''"><div id="back">BACK</div></div>  <div id="header">ZONES</div><div id="riga">'''
                end_html='''</div></body></html>''' 

                l=[]
                logprint ("string.find(self.path zone_list")
                l=sortZonesByOrderNumber()
                for a in l :             

                  if (zoneDict[a]["hidden"]!=0):  #skip the hidden elements
                    continue     
                  #html=html+'<div><a href="/'+a+'/index.html?=">'+a+'</a></div>'
                  html=html+'''<a href="/'''+a+'''/index.html?="><div id="zone">'''+a+'''</div></a>'''
                  html=html+'''<a href="/zone_objects_setup/'''+a+'''"><div id="setup">    setup</div></a>'''

                html=html+'''<div id="zone" style=" visibility: hidden;"></div></a>''' #void elements to make space
                html=html+'''<div id="setup" style=" visibility: hidden;">  </div></a>'''#void elements to make space
                

 
                pag=html+end_html      #+'<a    href="/setup/">Rooms Configuration  </a><br/>'


                try:
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(pag) 
                  logprint("percorso="+self.path+"end")
                except Exception as e  :
                  message="error12 in send_header "   
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
                  pass                
                return









            #/RouterGL0001/index.html?=r_onos_s12

            if  ( string.find(self.path,"r_onos_s")!=-1)& ( string.find(self.path,"?")!=-1)& ( string.find(self.path,"=")!=-1):   #if is the javascript on the page asking to update the webpage             /
                 #   global objectDict
              
              global oldpag
              global nothing_changed
              logprint("r_onos_s found0")
                 #   global  old_zoneDict
                 #   global  old_objectDict
                 #   global  old_web_page
              end_file_name=0
              end_file_name=string.find(self.path,".html")+5
              web_page=''

              try:       

                with open(baseRoomPath+self.path[1:end_file_name] , 'r') as b1:       
                  web_page=b1.read()    

              except:
                logprint("error opening the file" )  



                   
              #if True : #to implement a check to not execute modPag if the dictionary are equal
              pag=modPage(web_page,objectDict,findZoneName(self.path,zoneDict),zoneDict)
              p_start=string.find(pag,'<div id="ReloadThis" >')
                
              pag=pag[p_start+len('<div id="ReloadThis" >'):] #send only the part of page to update 

                      #old_zoneDict=zoneDict
                      #old_objectDict=objectDict
                      #old_web_page=web_page
                     
                #if (1):#  (oldpag!=pag):  removed the not updating part for problem with arduino update
              nothing_changed=0
                #print "web page changed" 

              try:
                self.send_response(202)
                self.send_header('Content-type',	'text/html')
                self.end_headers() 
                self.wfile.write("ok"+strftime("%S", gmtime())+pag) 
              except Exception as e  :
                pass
                message="error in send_header r_onos_s  0 "+" e:"+str(e.args)     
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              oldpag=pag
                        
                #else:
                #  print "web page not changed 1"  
                #  nothing_changed=nothing_changed+1
                #  try:
                #    self.send_response(200)
                #    self.send_header('Content-type',	'text/html')
                #    self.end_headers() 
                #    try:
                #      self.wfile.write("ok"+strftime("%S", gmtime())+pag)
                #    except Exception as e  :
                #      pass
                #      print "error in send_header  r_onos_s 2"+" e:"+str(e.args)  
                #      errorQueue.put("error in send_header  r_onos_s 2"+" e:"+str(e.args) )  
                       

                 #except Exception as e  :
                 #   pass
                 #   print "error in send_header r_onos_s 3"+" e:"+str(e.args)     
                 #   errorQueue.put("error in send_header r_onos_s 3"+" e:"+str(e.args)   )  
                 # return

              #else:        #never  executed for now
              #  print "web page not changed 2"  
              #  try:
              #    self.send_response(200)
              #    self.send_header('Content-type',	'text/html')
                 #self.send_header('Location', self.path)
              #    self.end_headers() 
              #    self.wfile.write("ok"+strftime("%S", gmtime())+"nonews")   #remove comment to send page
                  #self.wfile.write("oknothing_changed")   #remove comment to send page only when it change

              #  except Exception as e  :
              #    pass
              #    print "error in send_header r_onos_s 4 "+" e:"+str(e.args)   
              #    errorQueue.put( "error in send_header r_onos_s 4 "+" e:"+str(e.args))  
  
              return



            if (self.path.endswith("=")&( string.find(self.path,"?")!=-1)&((string.find(self.path,".html")!=-1))): # not an object change but just a webpage show 

                
              html_filename=re.search('/(.+?).html',self.path).group(1)+".html"
              logprint("html_filename=",html_filename)


              try:              
                  #b1 = open(baseRoomPath+self.path[1:end_file_name] ,'r')    
                b1 = open(baseRoomPath+html_filename ,'r')    
                web_page=b1.read()    
                b1.close()
              except Exception as e  :
                message="error opening the htlm file"
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                web_page="error no html found"

              try:              
                pag=modPage(web_page,objectDict,findZoneName(self.path,zoneDict),zoneDict)
              except Exception as e  :
                message="error modPage "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pag="error modPage "


              try:
                self.send_response(202)
                self.send_header('Content-type',	'text/html')
                self.end_headers() 
                self.wfile.write(pag) 
        #      print "percorso="+self.path+"fine percorso"   
              except Exception as e  :
                message="error11 in send_header "      
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              return



            if (    ( string.find(self.path,"?")!=-1)&(string.find(self.path,"=")!=-1)&(string.find(self.path,"r_onos_s")==-1)):
              logprint("get query found")
              end_file_name=0
              if (  (string.find(self.path,".html")!=-1) ):  #if a html file is called
             
                #start_file_name=""
                
                #x=(string.find(self.path,"/")) 
                
                html_filename=re.search('/(.+?).html',self.path).group(1)+".html"
                logprint("html_filename=",html_filename)
                #end_file_name=string.find(self.path,".html")+5

                #print "addressbar1= "+self.path
                #print "file:"+self.path[1:end_file_name]  
                try:              
                  #b1 = open(baseRoomPath+self.path[1:end_file_name] ,'r')    
                  b1 = open(baseRoomPath+html_filename ,'r')    
                  web_page=b1.read()    
                  b1.close()
                except Exception as e  :
                  message="error opening the htlm file"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  web_page="error no html found"
                #print web_page
                
              else: #no .html in the address bar
                k=0
                last_bar=len(self.path)
                while ((string.find(self.path,"/",k))!=-1):   #search for the last / in the address bar
                  last_bar=string.find(self.path,"/",k)
                  k=last_bar+1
              
              
                logprint("local address bar ="+self.path[0:last_bar+1])
                try:              
                  b1 = open(baseRoomPath+self.path[1:last_bar+1] +"index.html" ,'r')   
                  
                  web_page=b1.read()    
                  b1.close()
                except Exception as e  :
                  message="error opening the file local address bar ="+self.path[0:last_bar+1] 
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

                  web_page=web_page_not_found
                #print web_page
            
                                  
                    
             
              address_bar=self.path[end_file_name:]
              #print "a---"+address_bar
              #banana use regex to read all the obj and status to set
              address_bar=address_bar[string.find(address_bar,"?")+1:]

              equal_position=string.find(address_bar,"=")
              next_point_position=string.find(address_bar,"&",equal_position)
              objName=address_bar[0: equal_position]

              if (next_point_position!=-1):
                status_to_set=(  address_bar[(equal_position+1):(next_point_position)]  )
                logprint("value="+(status_to_set) )
              else:                     
                status_to_set=(address_bar[(equal_position+1):])
                logprint("value="+(status_to_set) )

              if status_to_set=="!":  # to make a not of the current status
                 #print "make the opposite"
                status_to_set=not (objectDict[objName].getStatus())

              if (  objName  in objectDict ):
                #print "pulsante trovato in dizionario"                
             
                if status_to_set=="!":  # to make a not of the current status
                    #print "make the opposite"
                  status_to_set=not (objectDict[objName].getStatus())


                priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":1,"priority":99,"user":self.current_username,"mail_report_list":[]})  
 

                logprint("i set"+objName+" to :"+str(status_to_set) )

              else:
                logprint("the objName :"+objName+" not in dictionary 2")


              address_bar=address_bar[next_point_position-2:]

              #address_bar example  "http://192.168.0.100/RouterGL0000/index.html?socket0_RouterGL0000=0&socket0_RouterGL0020=1&socket0_ttgg0000=69"
              while ( ( string.find(address_bar,"&")!=-1)&(len(address_bar)>1 )):
                point_position=string.find(address_bar,"&")
                equal_position=string.find(address_bar,"=",point_position)
                next_point_position=string.find(address_bar,"&",equal_position)
                objName=address_bar[point_position+1: equal_position]
                
                #print "cmd:"+cmd
                #print "a:"+address_bar[(equal_position):]
                 
                try :
                  if (next_point_position!=-1):
                    status_to_set=(  address_bar[(equal_position+1):(next_point_position)]  )
                    logprint("value="+(status_to_set) )
                  else:                     
                    status_to_set=(address_bar[(equal_position+1):])
                    logprint("value="+(status_to_set) )

                except Exception as e  :
                
                  message="error in the status_to_set_value in the address bar"+address_bar[(equal_position+2):]
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                  #logprint("next:"+str(next_point_position)+address_bar[equal_position+2:] )
                  status_to_set=-1

                if (  objName  in objectDict ):
                #print "pulsante trovato in dizionario"                
             
                  if status_to_set=="!":  # to make a not of the current status
                    #print "make the opposite"
                    status_to_set=not (objectDict[objName].getStatus())

                  logprint("path="+address_bar)
                  #changeWebObjectStatus(objectName,status_to_set,1)  #banana to add usr,priority,mail_list_to_report_to
                  priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":1,"priority":99,"user":current_username,"mail_report_list":[]})    

                  logprint ("i set"+objName+" to :"+str(status_to_set))

                else:
                  logprint ("objName :"+objName+" not in dictionary 1")
                

                address_bar=address_bar[(equal_position+1):] #remove the first '?'
                #print "addressbar= "+address_bar

              
              pag=modPage(web_page,objectDict,findZoneName(self.path,zoneDict),zoneDict)

              try:
                self.send_response(202)
                self.send_header('Content-type',	'text/html')
                self.end_headers() 
                self.wfile.write(pag) 
        #      print "percorso="+self.path+"fine percorso"   
              except Exception as e  :
                message="error11 in send_header "     
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                pass
              return










            if self.path.endswith(".json"):
                f = open(curdir + sep + self.path) #self.path has /test.html
                tmpF=f.read()
                f.close()
#note that this potentially makes every file on your computer readable by the internet
                try:
                  self.send_response(200)
                  self.send_header('Content-Disposition: attachment',	'filename="config_files/data.json"')
                  self.send_header('Content-Type: application/octet-stream','text/json' )
                  self.end_headers()
                  self.wfile.write(tmpF)
                except Exception as e  :
                  message="error12 in send_header "    
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pass
                f.close()
                return
                
  
            if self.path.endswith("gui/new_user.py"): # render  
              namespace={}
              message=""
              cgi_name="gui/new_user.py"       
              #execfile(cgi_name,globals(),namespace)
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
              web_page=namespace["web_page"]

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error12a in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
              return



            if self.path.endswith("scenarios_list/"): # render the scenario list 
              namespace={"current_username":self.current_username}
              cgi_name="gui/scenarios_list.py" 
              #execfile(cgi_name,globals(),namespace)
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)

              web_page=namespace["web_page"]

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13a in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
              return


            if self.path.endswith("scenario_creation/"): # render the scenario list 
              namespace={"current_username":self.current_username}
              cgi_name="gui/scenario_creation.py" 
              #execfile(cgi_name,globals(),namespace)
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)

              web_page=namespace["web_page"]

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13a0 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
              return

            if self.path.find("scenario_creation_conditions/")!=-1: # render the scenario list 
              namespace={"current_username":self.current_username,"scenario_to_mod":self.path.split("/")[2],"path":self.path}
              cgi_name="gui/scenario_creation_conditions.py" 
              #execfile(cgi_name,globals(),namespace)
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)

              web_page=namespace["web_page"]

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13a0 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
              return



            if self.path.find("scenario_operations/")!=-1: # render the scenario list 
              namespace={"current_username":self.current_username,"scenario_to_mod":self.path.split("/")[2],"path":self.path}
              cgi_name="gui/scenario_operations.py" 
              #execfile(cgi_name,globals(),namespace)
              #logprint(str(namespace))
              logprint(scenarioDict[namespace["scenario_to_mod"]]["functionsToRun"])
             
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)

              web_page=namespace["web_page"]

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13a0 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
              return






############################## old scenario mod part used for advanced settings

            scenario_to_mod=""
            if (  string.find(self.path,"/mod_scenario/")!=-1): # render the mod scenario setup menu
              logprint("scenario_to_mod",self.path.split("/")[2])
              web_page="error, scenario name does not exist "
              try:
                if (self.path.split("/")[2])in scenarioDict.keys():
                  namespace={"scenario_to_mod":self.path.split("/")[2],"path":self.path}
                  scenario_to_mod=(self.path.split("/"))[2]
                  cgi_name="gui/mod_scenario.py"       
                  #execfile(cgi_name,globals(),namespace)
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                  web_page=namespace["web_page"]                  

              except Exception as e  :
                message="error, scenario name does not exist "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                web_page="error, scenario name does not exist "


              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13a in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
              return


            if (  string.find(self.path,"/scenario_conditions/")!=-1): # render the conditions mod scenario setup menu
              
              try:
                if (self.path.split("/")[2])in scenarioDict.keys():
                  namespace={"current_username":self.current_username,"scenario_to_mod":self.path.split("/")[2],"path":self.path}
                  scenario_to_mod=(self.path.split("/"))[2]
                  cgi_name="gui/scenario_creation_conditions.py"                      
                  #execfile(cgi_name,globals(),namespace)
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                  web_page=namespace["web_page"]

              except Exception as e  :
                message="error, scenario name does not exist "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 

                web_page="error, scenario name does not exist "


              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message= "error13ab in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
              return



            if (  string.find(self.path,"/function_to_run/")!=-1): # render the conditions mod scenario setup menu
              
              try:
                if (self.path.split("/")[2])in scenarioDict.keys():
                  namespace={"scenario_to_mod":self.path.split("/")[2]}
                  scenario_to_mod=(self.path.split("/"))[2]
                  cgi_name="gui/scenario_f_to_run.py"       
                  
                  #execfile(cgi_name,globals(),namespace)
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                  web_page=namespace["web_page"]

                  

              except Exception as e  :
                message="error, scenario name does not exist "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  

                web_page="error, scenario name does not exist "


              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13ab in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
              return



##############################end old scenario mod part used for advanced settings



            if self.path.endswith("setup/"): # render the setup menu
              #print "enter in  room setup"
              try:              
                b1 = open('setup/select_config_menu.html','r')    
                web_page=b1.read()    
                b1.close()
              except Exception as e  :
                message="error a1 opening the file"
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                web_page="ERROR LOADING SELECT CONFIG MENU"

              try:    
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error13 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
                pass            
              return



            if self.path.endswith("setup/obj_manager/"): 
              logprint("enter in  obj_manager")
              html_page=self.get_WebOjectManager(objectDict)
                  
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(html_page) 
              except Exception as e  :
                message="error14 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))   
                pass          
              return



            if ((  string.find(self.path,"cgi/")!=-1)&(  string.find(self.path,".py")!=-1)):
              
              cgi_module_name_start=string.find(self.path,"cgi/")
              #cgi_module_name_stop=len(self.path)-3    #remove the ".py"
              cgi_name=(self.path[cgi_module_name_start:])
              namespace={}
              web_page="cgi import or execute error"
              logprint("cgi_name:"+str(cgi_name) )

              if (debug>0):  # in debug mode ..

                #execfile(cgi_name,globals(),namespace)
                exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                web_page=namespace["web_page"]

              else:

                try:
                
                  #execfile(cgi_name,globals(),namespace)
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                  web_page=namespace["web_page"]
                except Exception as e  :
                  message="error importing a module in cgi directory, cgi name:"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error15 in send_header "            
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              return 




            if self.path.find("/zone_creation/")!=-1: # render the scenario list 
              namespace={"current_username":self.current_username,"zone_to_mod":self.path.split("/")[2],"path":self.path}
              cgi_name="gui/mod_zone.py" 
              #execfile(cgi_name,globals(),namespace)
              exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)

              web_page=namespace["web_page"]

              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error16a in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
              return


            if  ( string.find(self.path,"/zone_objects_setup/")!=-1): # 

              logprint("enter in  obj_manager")
              zone=''

              if (len(self.path)>0):
                address_list=string.split(self.path,"/")  
                if address_list[-1] in zoneDict.keys() :    #if  the path is   setup/zone_objects_setup/anyzonename....   take the room name
                  zone=address_list[-1]  
                else: 
                  logprint("no room name found")
                
              else: 
                logprint("no room name found")
      


              html_page= self.get_Zone_Objects_Setup(self.path,objectDict,zone)
              try:    
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(html_page) 
              except Exception as e  :
                message="error16 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))       
                pass        
              return










            if self.path.endswith("setup/save_configuration/"): #     
              logprint("json saved",verbose=1)
              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options)
                  
              try:              
                b1 = open('setup/select_config_menu.html','r')    
                web_page=b1.read()    
                b1.close()
              except Exception as e  :
                message="error2 opening the file"
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                web_page="ERROR LOADING SELECT CONFIG MENU"
              
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
                pass
              return




            if self.path.endswith("setup/restore_default_conf/"): #     
              logprint("JSON RESTORED TO DEFAULT")
              #os.system('cp -f config_files/default.json config_files/data.json')
             # with lock_bash_cmd:               
             #   subprocess.check_output('cp -f config_files/default.json config_files/data.json', shell=True,close_fds=True)    
              shutil.copyfile("config_files/default.json", "config_files/data.json")

              try:              
                b1 = open('setup/restored_configuration.html','r')    
                web_page=b1.read()    
                b1.close()
              except Exception as e  :
                message="error3 opening the file"
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                web_page="ERROR LOADING SELECT CONFIG MENU"
              
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(web_page) 
              except Exception as e  :
                message="error18 in send_header "   
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              #os.execl(sys.executable, *([sys.executable]+sys.argv))
              global exit
              exit=1
              #raise KeyboardInterrupt
              return


            if self.path.endswith("setup/zone_manager/"): # render the html list of room with the link to modify them   
              logprint("enter in  zone_manager")
              html_page=self.get_zone_manager(zoneDict)
                  
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(html_page) 
              except Exception as e  :
                message="error19 in send_header " 
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                pass             
              return


            if ((string.find(self.path,"/setup/web_obj_modifier/")!=-1)):#render the web_object_form  to modify a webobj
              lista=[]
              lista=string.split(self.path,"/") #split the path in a list of element divided by "/" 
              
              pag="no_web_object_to_modify"
              if ((len(lista))==4):
                if ((lista[3] in objectDict.keys())):
                  logprint("edit a web object")
                  pag=self.get_WebObjForm(objectDict[lista[3]])


              if ((len(lista))==5):
                if ((lista[4] in objectDict.keys())&(lista[3]=="delete_item")):
                  logprint("deleted web object"+lista[4])
                  objectDict.pop(lista[4],None)   #bug
                  index=-1
                  for b in zoneDict.keys():
                    if lista[4] in zoneDict[b]["objects"]: 
                      index=zoneDict[b]["objects"].index(lista[4])
                      zoneDict[b]["objects"].pop(index)

   



                  #zoneDict=zoneDictMod 
                  #zoneDict.remove()
                  pag=self.get_WebOjectManager(objectDict)

                  updateDir()          
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(pag) 
              except Exception as e  :
                pass
                message="error20 in send_header "
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))    
                pass
              return


            lista=[]
            setup_start=string.find(self.path,"setup/")
            lista=string.split(self.path,"/") #split the path in a list of element divided by "/" 
            if (len(lista))>2:
              room_t=lista[2]
            else:
              room_t="not_A_room"
            #if (setup_start!=-1)&((len(self.path)-setup_start)==11): # if path is like  /setup/Room0
            if (setup_start!=-1)&(room_t in zoneDict.keys())&(len(lista)<4): # if path is like  /setup/Room0

              #print len(self.path)-setup_start
              #print self.path
              #print self.path[setup_start+6:]
              
              for a in zoneDict.keys() :
                if (self.path[(setup_start+6):]==a):  #found a room in the address bar
                  logprint("found a room in the address bar")
                  
                  pag=self.get_RoomObjectList(a,objectDict) 
                  try:
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()
                    self.wfile.write(pag) 
                  except Exception as e  :
                    message="error21 in send_header "
                    logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
                    pass
                  return

              pag=""   
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()

                self.wfile.write(pag) 
              except Exception as e  :
                message="error22 in send_header "+" e:"+str(e.args)  
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))  
                pass             
              return

            else: 
             
           
              if ( (setup_start!=-1)&(len(lista)==4)): #if path is like  /setup/Room0/body
                logprint("not show room modifier but obj modifier")
                if (lista[3] in objectDict.keys()):
                  logprint("edit a web object")
                  pag=self.get_WebObjForm(objectDict[lista[3]])
                  try:
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()
                    self.wfile.write(pag) 
                  except Exception as e  :
                    message="error23 in send_header " 
                    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                    pass
                  return
              #else:
                #print " '/setup' not found  or len list= "+str(len(lista))  
                  

#############experimental use only todo: to remove later#####################################

            #path example: localhost/cmd=mvobj&old=caldaia&new=caldaia2


            if ((string.find(self.path,"mvobj")!=-1)&(string.find(self.path,"old=")!=-1)&(string.find(self.path,"new=")!=-1)  ):
              logprint("found rename object query")
              current_obj_name=""

              try:              
                current_obj_name=re.search('old=(.+?)&',self.path).group(1)
                new_obj_name_start=string.find(self.path,"new=")+4 
                new_obj_name=self.path[new_obj_name_start:]

                logprint("current_obj_name="+current_obj_name+"end")
                logprint("new_obj_name="+new_obj_name+"end")
                pag="ok"


              except Exception as e  :
                message="error4.1 search"
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pag=message


              if current_obj_name not in objectDict.keys():
                pag="error renaming webobject not in dict"
                #print (objectDict.keys())
                logprint(pag)

              else:  

            
                try:        

                  for a in zoneDict.keys() : 
                    for b in range(len(zoneDict[a]["objects"])):
                      if zoneDict[a]["objects"][b]==current_obj_name: # if there is the webobject in this zone I replace it with the new one
                        zoneDict[a]["objects"][b]=new_obj_name

                  pag="ok"


                except Exception as e  :
                  message="error4.2 rename obj in zone"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pag=message


                try:             

                  objectDict[current_obj_name].setName(new_obj_name)    #rename the object_name in the object..
                  tmp_htmlDict=objectDict[current_obj_name].getHtmlDict()

                  for a in tmp_htmlDict.keys():
                    tmp_htmlDict[a]=tmp_htmlDict[a].replace(current_obj_name+"=",new_obj_name+"=") 
                  tmp_htmlDict["onoswait"]=new_obj_name+u"WAIT"  
                  objectDict[current_obj_name].setHtmlDict(tmp_htmlDict)
                  objectDict[new_obj_name]=objectDict[current_obj_name]  #copy the old dictionary key to the new one
                  del objectDict[current_obj_name] #delete the old key

                  pag="ok"

                #todo  save all to json
                except Exception as e  :
                  message="error4.3 rename obj in objectDict"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pag=message

                try:             

                  for a in nodeDict.keys():
                    if current_obj_name in nodeDict[a].getnodeObjectsDict().values():
                      node_object_address_of_the_old_name=nodeDict[a].getNodeObjectAddress(current_obj_name)
                      nodeDict[a].setNodeObjectAddress(node_object_address_of_the_old_name,new_obj_name)
                      

                  pag="ok"


                except Exception as e  :
                  message="error4.4 rename obj in node_dict"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pag=message




                try:             

                  for a in scenarioDict.keys():#for each scenario replace everywhere the old webobject name with the new one 
                    scenarioDict[a]["conditions"]=scenarioDict[a]["conditions"].replace("#_"+current_obj_name+"_#","#_"+new_obj_name+"_#")  

                    for b in range(len(scenarioDict[a]["functionsToRun"])):
                      scenarioDict[a]["functionsToRun"][b]=scenarioDict[a]["functionsToRun"][b].replace(current_obj_name+"=",new_obj_name+"=")  


                    if "afterDelayFunctionsToRun" in scenarioDict[a]: 
                      for b in range(len(scenarioDict[a]["afterDelayFunctionsToRun"])):                        
                        scenarioDict[a]["afterDelayFunctionsToRun"][b]=scenarioDict[a]["afterDelayFunctionsToRun"][b].replace(current_obj_name+"=",new_obj_name+"=")  



                  pag="ok"


                except Exception as e  :
                  message="error4.5 rename obj in scenarioDict"
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pag=message

           
              try:
                self.send_response(202)
                self.send_header('Content-type',	'text/html')
                self.end_headers()          
                self.wfile.write(pag) 
              except Exception as e  :
                message="error24 in send_header "    
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              return

########################################################################### end experimental code


            elif self.path.endswith(".html"):
                f = open(curdir + sep + self.path) #self.path has /test.html
                tmpF=f.read()
                f.close()
#note that this potentially makes every file on your computer readable by the internet
                try:
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(tmpF)
                except Exception as e  :
                  message="error25 in send_header "+" e:"+str(e.args)     
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pass
                f.close()
                return
                
                
            elif self.path.endswith("/"): #the address bar end with /  so by default i try open the index.html in this directory
                logprint("indirizzo a pag principale..")


                try:              
                    b1 = open(self.path[1:]+"index.html" ,'r')   
                  
                    web_page=b1.read()    
                    b1.close()
                except Exception as e  :      
                    message="error5 opening the file,local address bar ="+self.path+"index.html" 
                    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                    web_page=web_page_not_found
                logprint(web_page)



                try:
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  pag=modPage(web_page,objectDict,findZoneName(self.path,zoneDict),zoneDict)
                  self.wfile.write(pag) 
                except Exception as e  :
                  message="error26 in send_header "+" e:"+str(e.args)                     
                  logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                  pass
                #print "percorso="
                #print self.path     
                #print "fine percorso"
                
                return   
                
                
                
                
                
            return
                
        except Exception as e  :
            message="Generic error in Get method"
            self.send_error(404,'File Not Found: %s' % self.path)
            logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 



              
                
    def do_POST(self):  #get posts data 

        try:
          ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        except Exception as e  :
          message="some error occurred in post connection "+" e:"+str(e.args)
          logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
          return

        if ctype == 'onos/form-data':
          logprint("received arduino post data!")
          length = int(self.headers.getheader('content-length'))
          postvars = cgi.urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
          node_ip=str(self.client_address[0])


          try:        
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write("ok")  
          except Exception as e  :
            pass
            logprint("error in send_header "+" e:"+str(e.args))     
            errorQueue.put("error in send_header "+" e:"+str(e.args)  )
            
          logprint("postvars="+str(postvars.items())+" data_received,len data= "+str(len(postvars.keys()[0] ) ) )  
    
          logprint(postvars.keys()[0]) 
          if (postvars.keys()[0][0:4]=="onos"): 
            node_sn=postvars.keys()[0][4:16]
            node_fw =postvars.keys()[0][16:20]
            input_status_register=postvars.keys()[0][21:]  #from 21 till the end
            logprint("onos node input pin received from: "+node_sn+" with ip: "+node_ip+"and fw="+node_fw)    


            if node_sn in nodeDict.keys():
              logprint("the node exist so i update the pin input status")
              updateNodeAddress(node_sn,uart_router_sn,node_ip,node_fw)# update the node ip 
              
            else:
              msg=createNewNode(node_sn,node_ip,node_fw)
              logprint("the serial number is not in the dictionary...so i add  the new node")

            updateNodeInputStatusFromReg(node_sn,input_status_register) # decode and update the data from the node







        if ctype == 'multipart/form-data':
            #postvars = cgi.parse_multipart(self.rfile, pdict)
            query=cgi.parse_multipart(self.rfile, pdict)

            try:
              self.send_response(301)
              self.end_headers()
            except Exception as e  :
              message="error27 in send_header " 
              logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
              pass
            upfilecontent = query.get('upfile')
            logprint("filecontent"+str(upfilecontent[0]))

            if len (upfilecontent[0])>10:
              try:
                self.wfile.write("<HTML>POST OK WAIT 2 SECONDS THEN GO BACK TO HOME<BR><BR>");
                self.wfile.write(upfilecontent[0]);
              except Exception as e  :
                message="error28 in send_header " 
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                pass
              try:
                file0 = open('config_files/data.json', "w")
                file0.write(upfilecontent[0])
                file0.close()
                global exit
                exit=1   #reboot the webserver 
              except Exception as e  :
                message="error importing json from user"
                logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
                self.wfile.write("<HTML>error importing file<BR><BR>");
            else:
              self.wfile.write("<HTML>error importing file<BR><BR>");

############################logprint todotodo continue from here...


        elif ctype == 'application/x-www-form-urlencoded':   #post data from onos web form
            length = int(self.headers.getheader('content-length'))
            postvars = cgi.urlparse.parse_qs(self.rfile.read(length), keep_blank_values=1)
            
            logprint("postvars="+str(postvars.items()) )
            for a in postvars.keys():
              for b in range(len(postvars[a])):
                logprint(postvars[a][b])

                postvars[a][b]=postvars[a][b].decode("utf8","replace")

                postvars[a][b]=postvars[a][b].encode("ascii","replace")

                postvars[a][b]=postvars[a][b].replace("?", "_")
                postvars[a][b]=postvars[a][b].replace(".", "_")

                #postvars[a][b]=postvars[a][b].replace(";", "_")                 

                #postvars[a][b]=postvars[a][b].replace("^", "_")
                #postvars[a][b]=postvars[a][b].replace("!", "_")
                #postvars[a][b]=postvars[a][b].replace('"', "_")
                #postvars[a][b]=postvars[a][b].replace("'", "_")
                #postvars[a][b]=postvars[a][b].replace("/", "_")
                #postvars[a][b]=postvars[a][b].replace("%", "_")
                #postvars[a][b]=postvars[a][b].replace("&", "_")
                #postvars[a][b]=postvars[a][b].replace(':', "_")
               # postvars[a][b]=postvars[a][b].replace('*', "_")
                #postvars[a][b]=postvars[a][b].replace('[', "_")
               # postvars[a][b]=postvars[a][b].replace(']', "_")       




 #postvars is a dictionary that contain all the data sended by the user..the keys are each <input>  name..
 #the data are the value of the input 

            data_to_update=0
            #logprint("POST:"+str(postvars.keys()) )
            
#<form action="" method="POST"><input type="hidden" name="zone_manager" value="/setup/zone_manager">
            location="zone_manager"
            if location in postvars:   #if the path is ...
              i=0
             
              for room in zoneDict.keys() : #for every room..read if the name of the room is being modify from user
                # room=roomList[i]
                 if (room in postvars):
                   #print "trovata:"+room
                   #print postvars[room][0]
                   new_name=self.clear_PostData(postvars[room][0])#the new name of the directory
                   new_name=new_name.replace("/","_")
                   if ((new_name!=default_rename_zone_value)&(new_name!=default_rename_zone_value2)&(new_name!=default_new_zone_value)&(new_name!=room)&(postvars[room]!=" ")&(len(new_name)>0)&(new_name not in zoneDict.keys())) : #value modified by the user
                     #roomList[i]=name


          

                                 
                     if (room+"_body" in objectDict.keys()) :
                       objectDict[new_name+"_body"]=objectDict[room+"_body"]  #copy the body object from the old name

                       objectDict.pop(room+"_body",None)#del objectDict[room+"_body"]         #and delete the old key
                       if  room+"_body"  in zoneDict[room]["objects"] :
                         logprint("i try to remove the object"+room+"_body  from zone"+room)
                         index=zoneDict[room]["objects"].index(room+"_body")   
                         zoneDict[room]["objects"][index]=new_name+"_body"   #rename the webobj in the room
                       else:
                         logprint("object not removed from zone beacuse not present there")


                       data_to_update=1  
                        
                     zoneDict[new_name] = zoneDict[room]   #update the zoneDict with the new key
                     zoneDict.pop(room, None)  # del zoneDict[room]            #and delete the old key
                     #except:
                      # print "can't remove object from objectDict"


                     try : 
                       #os.system("mv "+baseRoomPath+room+" "+baseRoomPath+new_name)   #rename the directory
                       #with lock_bash_cmd:
                       #  subprocess.check_output("mv "+baseRoomPath+room+" "+baseRoomPath+new_name, shell=True,close_fds=True) 

                       make_fs_ready_to_write()
                       os.rename(baseRoomPath+room, baseRoomPath+new_name,)
                       make_fs_readonly()
                       updateOneZone(new_name)
                       updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
                       logprint("mv "+room+" "+new_name) 
                     except Exception as e  :
                       message="can't rename directory to"+new_name
                       logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  

                # i=i+1
              
              if "new_room" in postvars: #the user wants to create a new room 
                logprint(postvars["new_room"][0])
                new_name=self.clear_PostData(postvars["new_room"][0])
                new_name=new_name.replace("/", "_")
                #print new_name
                if((new_name!=default_new_zone_value)&(new_name!=default_rename_zone_value)&(new_name!=default_rename_zone_value2)&(len(new_name)>0)&((new_name)!=" ")&(new_name not in zoneDict.keys())&(new_name+"_body" not in objectDict.keys() )): 
                  #roomList.append(new_name) #create a new room 
                  zoneDict[new_name]={"objects":[],"order":len(zoneDict.keys()),"permissions":"777","group":[],"owner":"onos_sys","hidden":0}
                  zoneDict[new_name]["objects"]=[new_name+"_body"]  # modify to update also the webobject dict and list 
                  objectDict[new_name+"_body"]=newDefaultWebObjBody(new_name+"_body") #create a new web_object and insert only his name          
                  #objectList.append(objectDict[new_name+"_body"])
                  #os.system("mkdir "+baseRoomPath+new_name) 
                  #os.system("cat "+getRoomHtml(new_name,objectDict,"",zoneDict)+" >> "+baseRoomPath+new_name+"/index.html")
                  #os.system("chmod 777 "+new_name)
                  make_fs_ready_to_write()
                  try:
                    os.stat(baseRoomPath+new_name)
                  except:
                    os.mkdir(baseRoomPath+new_name)  


                  with open(baseRoomPath+new_name+"/index.html", 'w') as f:
                    f.write(getRoomHtml(new_name,objectDict,"",zoneDict))

                  os.chmod(baseRoomPath+new_name+"/index.html", 0o777)
                  make_fs_readonly()
                  updateOneZone(new_name) 
                  updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options)       
                  logprint("create a new room"+new_name)
                  data_to_update=1

              logprint("search in all the zones")
              for a in zoneDict.keys() :  #banana very slow..

                if ("delete_room_"+a) in postvars: 
                  logprint("delete room:"+postvars["delete_room_"+a][0])
                  if postvars["delete_room_"+a][0]=='on':
                    delete=a


                  #  obj_name_list1=zoneDict[a]
                 #   if a+"_body"  in  obj_name_list1:
                 #     print "i try to remove the object "+a+"_body  from the zone"+a
                 #     index=zoneDict[a].index(a+"_body")
                 #     zoneDict[a].pop(index)

                    zoneDict.pop(a,None)
                    objectDict.pop(a+"_body",None)  # remove also the web_obj body of the pag from the dict
                    
                    #os.system("rm "+baseRoomPath+a+"/*")
                    #os.system("rmdir "+baseRoomPath+a)

                    make_fs_ready_to_write()
                    try:
                      shutil.rmtree(baseRoomPath+a)
                    except Exception as e  :
                      message="error deleting folder:"+baseRoomPath+a 
                      logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
                    make_fs_readonly()
                    updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 

                    #with lock_bash_cmd:
                    #  subprocess.check_output("rm "+baseRoomPath+a+"/*", shell=True,close_fds=True)  
                    #  subprocess.check_output("rmdir "+baseRoomPath+a, shell=True,close_fds=True)  
                    data_to_update=1
  




              postvars = {} 
              
              pag=self.get_zone_manager(zoneDict)  
              try:        
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(pag)  
              except Exception as e  :
                message="error29 in send_header "
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  
                pass    
              #updateJson()
              updateDir()     
     







            elif "zone_setup_manager" in postvars:   #   to add or remove objects to a zone 
              zone=self.clear_PostData(postvars["zone_setup_manager"][0])
              logprint("zone_objects_setup page send a post to mode zone:"+zone)   

              if "new_zone_to_create" in postvars:   #  
                new_zone_name=self.clear_PostData(postvars["new_zone_to_create"][0])
                new_zone_name=new_zone_name.replace("/", "_")
                if new_zone_name!="" and new_zone_name!="Scrivi il nome della zona":
                  if zone!="" and new_zone_name!=zone :   # if I have to rename a zone
                     zoneDict[new_zone_name] = zoneDict[zone]   #update the zoneDict with the new key
                     zoneDict.pop(zone, None)  # del zoneDict[zone]            #and delete the old key                  
                 
                  elif new_zone_name!=zone: # if I have to create a new zone...                  
                    zoneDict[new_zone_name]={"objects":[],"order":len(zoneDict.keys()),"permissions":"777","group":[],"owner":"onos_sys","hidden":0}

                    if new_zone_name+"_body" not in objectDict:#create the body object if doesn't exist
                      objectDict[new_zone_name+"_body"]=newDefaultWebObjBody(new_zone_name+"_body")  
                     
                    zoneDict[new_zone_name]["objects"]=[new_zone_name+"_body"]  # modify to update also the webobject dict and list 
                    #objectDict[new_zone_name+"_body"]=newDefaultWebObjBody(new_zone_name+"_body") #create a new web_object and insert only his name          
                    make_fs_ready_to_write()
                    try:
                      os.stat(baseRoomPath+new_zone_name)
                    except:
                      os.mkdir(baseRoomPath+new_zone_name)  
                    with open(baseRoomPath+new_zone_name+"/index.html", 'w') as f:
                      f.write(getRoomHtml(new_zone_name,objectDict,"",zoneDict))
                    os.chmod(baseRoomPath+new_zone_name+"/index.html", 0o777)
                    updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
                    make_fs_readonly() 
                    #updateOneZone(new_zone_name)       
                    logprint("create a new zone:"+new_zone_name)
                    data_to_update=1
                else:# new_zone_name is not valid
                  new_zone_name=zone
  
              obj_name_list=zoneDict[new_zone_name]["objects"]
              logprint("obj_name_list:"+str())

              for a in  objectDict.keys():


                if (a+"_sel_obj" in postvars): 
                  
                  if a not in obj_name_list:
                    logprint("add obj to zone :"+a)
                    zoneDict[new_zone_name]["objects"].append(a)   #add the 

                else: # not checked , so remove the  object from the zone if it is there
                  
                  if a in  obj_name_list:
                    logprint("i try to remove the object "+a+"from the zone"+zone)
                    index=zoneDict[new_zone_name]["objects"].index(a)
                    zoneDict[new_zone_name]["objects"].pop(index)
                updateOneZone(new_zone_name)
                updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 


              if "save_and_reload_this_page" in postvars:
                logprint("i reload the page.......................")
                current_page=self.clear_PostData(postvars["save_and_reload_this_page"][0])
                self.send_response(301)
                self.send_header('Location',current_page)
                self.end_headers()
                return 

              
              self.send_response(301)
              self.send_header('Location','/')
              self.end_headers()
              return    







            elif "zone_objects_setup" in postvars:   # OLD GUI  to add or remove objects to a zone old gui..
                        
              zone=self.clear_PostData(postvars["zone_objects_setup"][0])
              logprint("zone_objects_setup page send a post to mode zone"+zone)     
              obj_name_list=zoneDict[zone]["objects"]

              for a in  objectDict.keys():

                

                if (1):
                  if (a+"_sel_obj" in postvars): 
                  
                    #if (postvars[a+"_sel_obj"][0]=='on'):
                    if a not in obj_name_list:
                      logprint("OLD GUI add obj to the zone:"+a)
                      zoneDict[zone]["objects"].append(a)   #add the 
                    #else:# not checked , so remove the  object from the zone if it is there
                    #  if a in  obj_name_list: 
                    #    logprint("i try to remove the object "+a+"from the zone"+zone)
                    #    index=zoneDict[zone]["objects"].index(a)
                    #    zoneDict[zone]["objects"].pop(index)

                  else: # not checked , so remove the  object from the zone if it is there
                  
                    if a in  obj_name_list:
                      logprint("i try to remove the object "+a+"from the zone"+zone)
                      index=zoneDict[zone]["objects"].index(a)
                      zoneDict[zone]["objects"].pop(index)
                      updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options)  



              if ("new_objects" in postvars):
                new_obj0=self.clear_PostData(postvars["new_objects"][0])
                 
                new_obj=new_obj0+'_p_'+zone
                if  ( (new_obj0 !="TYPE_NEW_OBJECT_HERE")&(new_obj not in objectDict.keys())&(len(new_obj)>0)&(new_obj!=" ")   ):           
                  objectDict[new_obj]=newDefaultWebObj(new_obj) #create a new object and insert it in the dictionary  
                  zoneDict[zone]["objects"].append(new_obj)   #add the object name to the zone


              postvars={}
              updateOneZone(zone)#to update the zone with the new objects
              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
              webpag=self.get_Zone_Objects_Setup(self.path,objectDict,zone)
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(webpag)     
              except Exception as e  :
                message="error30 in send_header "
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
                pass


            elif "objs_manager" in postvars:
              objs_manager=self.clear_PostData(postvars["objs_manager"][0])
              logprint("objs_manager"+objs_manager)
              q="new_web_object"
              if q in postvars:   
                new_obj=self.clear_PostData(postvars[q][0])
                logprint("try to create a new webobj"+new_obj)
                if((new_obj!=default_new_obj_value)&(new_obj!=default_new_obj_value2)&(len(new_obj)>0)&((new_obj)!=" ")&(  new_obj not in objectDict.keys() ) ): 
                  objectDict[new_obj]=newDefaultWebObj(new_obj) #create a new web_object and insert only his name 
                 # objectList.append(objectDict[new_obj])
                  logprint("created a new web object "+objectDict[new_obj].getName() )
                  data_to_update=1  
                  
              postvars = {}
              pag=self.get_WebOjectManager(objectDict)
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(pag)  
              except Exception as e  :
                message="error31 in send_header "
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
                pass

              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options)       

            elif "current_room" in postvars:#if the current location is /setup/AnyRoomName  because "current_room"  is a post of that page
              currentRoom=self.clear_PostData(postvars["current_room"][0])
              q="new_web_object"
              if q in postvars:   
                new_obj=self.clear_PostData(postvars[q][0])

                if((new_obj!=default_new_obj_value)&(new_obj!=default_new_obj_value2)&(len(new_obj)>0)&((new_obj)!=" ")&(  new_obj not in objectDict.keys() ) ): 
                  objectDict[new_obj]=newDefaultWebObj(new_obj) #create a new web_object and insert only his name 

                 # objectList.append(objectDict[new_obj])
                  logprint("created a new web object "+objectDict[new_obj].getName() )
                  data_to_update=1  
                  
              
              base_rm="rm_obj_"
              end_rm="_from_"+currentRoom
              #enabledToWrite=0  #tell the system if the textarea html has to be ignored or written to the file

              for a in postvars.keys() :
                logprint("postvars="+str(postvars[a]))

                
                if ((string.find(a,"add_obj_to_room")!=-1)&((postvars[a][0]) in objectDict.keys())&(postvars[a][0]not in zoneDict[currentRoom]["objects"]  )):  #add a obj to the room
                  zoneDict[currentRoom]["objects"].append(postvars[a][0])
                  updateOneZone(currentRoom)
                  #html_to_write=getRoomHtml(currentRoom,objectDict,"",zoneDict)
                  #file0 = open(currentRoom+"/index.html", "w")
                  #file0.write(html_to_write) 
                  #file0.close()

                  logprint("found a add_obj post")
                   
                logprint("room list"+zoneDict[currentRoom]["objects"])

                
                if (string.find(a,"rm_obj_")!=-1)&((postvars[a][0]) in zoneDict[currentRoom]["objects"]  ):  #remove obj from the room
                  index=zoneDict[currentRoom]["objects"].index(postvars[a][0])
                  zoneDict[currentRoom]["objects"].pop(index)
                  logprint("found a rm_obj post now the room is this:"+zoneDict[currentRoom]["objects"])
                  data_to_update=1  
                else:
                  logprint("error obj to remove not found ",verbose=8)

                #updateOneZone(currentRoom)           
              if data_to_update==1:    #update the html removing the webobj removed by the form 
                html_to_write=getRoomHtml(currentRoom,objectDict,"",zoneDict)
               # file0 = open(baseRoomPath+currentRoom+"/index.html", "w")
               # file0.write(html_to_write) 
               # file0.close()
                data_to_update=0
                logprint("object removed from html")

              postvars = {}               
              #print "actual room: "+currentRoom
              
              pag=self.get_RoomObjectList(currentRoom,objectDict)  
              try: 
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(pag)  
              except Exception as e  :
                message="error32 in send_header " 
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
                pass
              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
              #updateOneZone(currentRoom)        
              

     
            elif "current_room_text_area" in postvars:
              currentRoom=self.clear_PostData(postvars["current_room_text_area"][0])
              if currentRoom not in zoneDict.keys():
                logprint("currentRoom:"+currentRoom+" not in zonedict",verbose=8)
                return(-1)
              new_html_room=postvars["html_room_mod"][0]
              logprint("new_html_room="+new_html_room)

              logprint("currentroom_modhtml="+currentRoom)
              #updateOneZone(currentRoom)
              html_to_write=modPage(new_html_room,objectDict,currentRoom,zoneDict)
              logprint("html wrote to the file "+currentRoom+"/index.html="+html_to_write)
              logprint("correction..not wrote because commented part")
              #file0 = open(baseRoomPath+currentRoom+"/index.html", "w")
              #file0.write(html_to_write) 
              #file0.close()
              postvars = {}
              pag=self.get_RoomObjectList(currentRoom,objectDict)  
              try: 
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(pag)   
              except Exception as e  :
                message="error33 in send_header "
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
                pass
              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 



            elif "mod_object" in postvars:#if the current page is /setup/AnyRoomName/Anywebobject  because "mod_object"  is a post of that page     
              path=postvars["mod_object"][0]
              logprint("found a mod_object request with path:"+path)
              web_object_name=string.split(path,"/")[3]  #split the path in a list of string  
              logprint("modify the web object:"+web_object_name)
              for a in postvars.keys() :
                if (postvars["obj_notes"]!=notes):
                  objectDict[web_object_name].setNotes(postvars["obj_notes"][0])


                if (postvars["obj_hardware_pin"]!=no_pin_selected)&(len(postvars["obj_hardware_pin"])>0):
                  try:
                    objectDict[web_object_name].setAttachedPin(int (postvars["obj_hardware_pin"][0]))
                  except:
                    objectDict[web_object_name].setAttachedPin(9999)


               # if (postvars["obj_type"]!=objectDict[web_object_name].getType()):
               #   changeWebObjectType(web_object_name,postvars["obj_type"][0])
                  #objectDict[web_object_name].setType(postvars["obj_type"][0])
                  

                if (postvars["obj_current_status"]!=int (objectDict[web_object_name].getStatus())):

                  #objectDict[web_object_name].setStatus(int(postvars["obj_current_status"][0]))
                  changeWebObjectStatus(web_object_name,int (postvars["obj_current_status"][0]),1)#banana add to queue



                if (postvars["obj_style0"]!=style0):
                  objectDict[web_object_name].setStyle0(postvars["obj_style0"][0])

                if (postvars["obj_style1"]!=style1):
                  objectDict[web_object_name].setStyle1(postvars["obj_style1"][0])

                if (postvars["obj_html0"]!=html0):
                  objectDict[web_object_name].setHtml0(postvars["obj_html0"][0])

                if (postvars["obj_html1"]!=html1):
                  objectDict[web_object_name].setHtml1(postvars["obj_html1"][0])


                if (postvars["obj_cmd0"]!=" "):
                  objectDict[web_object_name].setCommand0(formParse(postvars["obj_cmd0"][0]))

                if (postvars["obj_cmd1"]!=" "):
                  objectDict[web_object_name].setCommand1(formParse(postvars["obj_cmd1"][0]))


                if (postvars["obj_init_cmd"]!=" "):
                  objectDict[web_object_name].setInitCommand(formParse(postvars["obj_init_cmd"][0]))
                  objectDict[web_object_name].InitFunction()  #execute the new init command

              postvars = {}
              data_to_update=1 
              pag=self.get_WebObjForm(objectDict[web_object_name])
              try:
                self.send_response(200)
                self.send_header('Content-type',	'text/html')
                self.end_headers()
                self.wfile.write(pag) 
              except Exception as e  :
                message="error34 in send_header "  
                logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
                pass

              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
              updateDir()


##############start of scenario form data receiver ################################
                

            elif "scenario_creation" in postvars:#if the current page is /scenario_creation/  because "scenario_creation"  is the hidden form name
            # <input type="hidden" name="scenario_creation" value="/scenario_creation/">


              pag=""
              if (postvars["new_scenario_name"]!=" "):
                new_scenario_name=self.clear_PostData(postvars["new_scenario_name"][0])
                if new_scenario_name not in scenarioDict.keys(): #if scenario name doesn't exist already
                  scenarioDict[new_scenario_name]={"enabled":0,"type_after_run":"0","conditions":"0","functionsToRun":[],"delayTime":0,"priority":0}
                  self.send_response(301)
                  self.send_header('Location','/scenario_creation_conditions/'+new_scenario_name+'/')
                  self.end_headers()
                  conditions=""
                  for a in postvars.keys() :
                    if (postvars[a][0].endswith("_checkbox")):  #every checkbox name ends with _checkbox..
                      logprint("found a checkbox:"+a)
                      web_object_name=a.replace("_checkbox","")
                      if len(conditions) >0:
                        conditions=conditions+"&"      
                      conditions=conditions+'''(#_'''+web_object_name+'''_#==select_an_object)'''

                  if len (scenarioDict[new_scenario_name]["conditions"]) >0:
                    if len(conditions) >0:
                      scenarioDict[new_scenario_name]["conditions"]=conditions
                      updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
                    else:
                      conditions='''(#_select_an_element_#==select_an_object)'''
                      logprint("error_scenario_creation0 no objects passed",verbose=8)
                      scenarioDict[new_scenario_name]["conditions"]=conditions
                  else:
                    logprint("error_scenario_creation1 the scenario has already conditions",verbose=8)


                  return











            elif "new_scenario" in postvars:#old implementation..if the current page is /scenarios_list/  because "new_scenario"  is the hidden form name
            #<input type="hidden" name="new_scenario" value="/scenarios_list/">

              pag=""
              if (postvars["new_scenario_name"]!=" "):
                new_scenario_name=self.clear_PostData(postvars["new_scenario_name"][0])
                if new_scenario_name not in scenarioDict.keys(): #if scenario name doesn't exist already
                  scenarioDict[new_scenario_name]={"enabled":0,"type_after_run":"0","conditions":"0","functionsToRun":[],"delayTime":0,"priority":0}

                  self.send_response(301)
                  self.send_header('Location','/mod_scenario/'+new_scenario_name+'/')
                  self.end_headers()

                  return



            elif "delete_scenario" in postvars:# old implementation

              if(postvars["delete_scenario"][0]!=" "):

                logprint("received delete_scenario" , postvars["delete_scenario"][0])

                del_scenario_name=self.clear_PostData(postvars["delete_scenario"][0])

                for post in postvars.keys() :
                  if (post.find("delete_check_")!=-1):  #every checkbox name starts with delete_check_
                    del_scenario_name=post.replace("delete_check_","")
                    logprint("I have found a scenario to delete:"+del_scenario_name)


                    if del_scenario_name in scenarioDict.keys(): #if scenario name doesn't exist  
                
                      for a in objectDict.keys():#check and remove the not used scenarios from web_object attachedScenarios
                        tmp_list_scenarios=objectDict[a].getListAttachedScenarios()
                        if del_scenario_name in tmp_list_scenarios: 
                          objectDict[a].removeAttachedScenario(del_scenario_name)
                      del scenarioDict[del_scenario_name]  

                updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
                self.send_response(301)
                self.send_header('Location','/scenarios_list/')
                self.end_headers()
                  

                return
                






            elif "mod_scenario" in postvars:# old implementation if the current page is /mod_scenario/scenario name  because "mod_scenario"  is the hidden form name
            #<input type="hidden" name="mod_scenario" value="/scenarios_list/mod_scenario/">

              pag=""
              if (postvars["mod_scenario"]!=" "):
                scenario_start_name=self.clear_PostData(postvars["mod_scenario"][0])#get the current scenario name 

              if (postvars["new_scenario_name"][0]!=" "):
                scenario_name=self.clear_PostData(postvars["new_scenario_name"][0])#get the current scenario name

                if scenario_start_name in scenarioDict: #if the name exist in the dict
                  if scenario_name != scenario_start_name :  #the scenario was renamed
                    if scenario_name not in scenarioDict:
                      scenarioDict[scenario_name]=scenarioDict[scenario_start_name]
                      del scenarioDict[scenario_start_name]
                      for obj in objectDict.keys():
                        objectDict[obj].replaceAttachedScenario(scenario_start_name,scenario_name) #replace the reference in the web object with the new one
                  
                      


                  if "enabling" in postvars:
                    if self.clear_PostData(postvars["enabling"][0])=="on":
                      scenarioDict[scenario_name]['enabled']=1
                    else:
                      scenarioDict[scenario_name]['enabled']=0 
                      #print "scenario disabled"

                  else:
                    scenarioDict[scenario_name]['enabled']=0 
                    #print "scenario disabled"
                   

                  if "set_type_after_run" in postvars:
                    logprint("select:",postvars["set_type_after_run"])
                    logprint("select2:",postvars["set_type_after_run"][0])


                    if self.clear_PostData(postvars["set_type_after_run"][0])=="autodelete":
                      scenarioDict[scenario_name]["type_after_run"]="autodelete"
                    elif self.clear_PostData(postvars["set_type_after_run"][0])=="one_time_shot":
                      scenarioDict[scenario_name]["type_after_run"]="one_time_shot"
                    else:
                      scenarioDict[scenario_name]["type_after_run"]="0" 


                  if "delay_time" in postvars:
                      delay=self.clear_PostData(postvars["delay_time"][0])
                      try:
                        delay=int(delay)
                        scenarioDict[scenario_name]["delayTime"]=delay
                      except Exception as e  :
                        message="error in mod_scenario delay_time form post parse  "
                        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))

                  if "priority" in postvars:
                      priority=self.clear_PostData(postvars["priority"][0])
                      try:
                        priority=int(priority)
                        scenarioDict[scenario_name]["priority"]=priority
                      except Exception as e  :
                        message="error in mod_scenario priority form post parse  " 
                        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))


                  if "conditions" in postvars:
                      conditions=self.clear_PostData(postvars["conditions"][0])
                      try:# deny the user to use a void string..
                         
                        a=eval(replace_conditions(conditions,scenario_name)[0])
                        scenarioDict[scenario_name]["conditions"]=conditions




                        for a in objectDict.keys():#check and remove the not used scenarios from web_object attachedScenarios
                          tmp_list_scenarios=objectDict[a].getListAttachedScenarios()
                          for b in tmp_list_scenarios:
                            if scenarioDict[b]["conditions"].find(a+"_#")==-1: 
                             # if the object is not in the conditions then remove it from web_object attachedScenarios
                              objectDict[a].removeAttachedScenario(b)
                      
                            


                        list_of_object_inside_conditions=replace_conditions(conditions,scenario_name)[1] 
                        for a in list_of_object_inside_conditions :# add the scenario to each web_object attachedScenarios    
                          if a in objectDict.keys():  
                            objectDict[a].attachScenario(scenario_name)  
                            #if the scenario is not included in the web_object attachedScenarios


                      except Exception as e  :
                        message="error in mod_scenario conditions form post parse ,the contions were:"+conditions
                        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))




                  if "functions" in postvars:
                      functions=self.clear_PostData(postvars["functions"][0])
                      try:
                         
                        #a=eval(replace_functions(functions,scenario_name))
                        logprint("functionsToRun=",functions.split(';;;') )
                        scenarioDict[scenario_name]["functionsToRun"]=functions.split(';;;')  #banana no check if the functions are right
                      except Exception as e  :
                        message="error in mod_scenario functions form post parse  "
                        logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 





                 # except Exception as e  :
                
                  #  print "error in mod_scenario form post parse  "+" e:"+str(e.args)  
                   # errorQueue.put( "error in mod_scenario form post parse "+" e:"+str(e.args))


                  #scenarioDict[scenario_name]={"enabled":0,"type_after_run":"0","conditions":"0","functionsToRun":[],"delayTime":0,"priority":0}

                  updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 

                  if "save_and_reload_this_page" in postvars:
                    logprint("i reload the page.......................")
                    current_page=self.clear_PostData(postvars["save_and_reload_this_page"][0])
                    self.send_response(301)
                    self.send_header('Location',current_page)
                    self.end_headers()
                    return 


                  elif "set_conditions_submit" in postvars:

                    self.send_response(301)
                    self.send_header('Location','/scenario_conditions/'+scenario_name)
                    self.end_headers()

                  elif "set_function_submit" in postvars:

                    self.send_response(301)
                    self.send_header('Location','/scenario_operations/'+scenario_name)
                    self.end_headers()

                  elif "finish_scenario_setup" in postvars:

                    self.send_response(301)
                    self.send_header('Location','/scenarios_list/')
                    self.end_headers()




                  return



            elif ("mod_conditions" in postvars) :#old implemenatation if the current page is /mod_conditions/scenario name  because "mod_scenario"  is the hidden form name
            #<input type="hidden" name="mod_conditions" value="">

              logprint("found a form mod_conditions ")
              scenario_name=self.clear_PostData(postvars["mod_conditions"][0])#get the current scenario name 

              if scenario_name not in scenarioDict:
                return(-1)

              if (postvars["menu_number"]!=" "):
                menu_number=int(self.clear_PostData(postvars["menu_number"][0]))
                logprint("gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"+str(menu_number))
              else:
                return(-1)

              #print "menu_number",menu_number
              conditions=""
              #if "scenario_creation_conditions" in postvars:  # scenario_creation_conditions ha one row less..
              #  menu_number=menu_number-1
              for i in range(1,menu_number+1):
                try:
                  left_element="#_"+self.clear_PostData(postvars["select_l"+str(i)][0])+"_#"
                  operator=self.clear_PostData(postvars["select_op"+str(i)][0])
                  if operator=="=":
                    operator="=="
                  right_element=self.clear_PostData(postvars["select_r"+str(i)][0])

                  if "numeric_value_field"+str(i) in postvars:   #if there is a text field with value i will read it
                    right_element_text_value=self.clear_PostData(postvars["numeric_value_field"+str(i)][0])
                    try:  #test if the value is a number         
                      right_element=str(int(self.clear_PostData(postvars["numeric_value_field"+str(i)][0]) ) )     
                    except:
                      right_element=self.clear_PostData(postvars["select_r"+str(i)][0])    

       

                  try:#detect if is a number
                    a=int(right_element)  #was float
                  except:
                    right_element="#_"+right_element+"_#"

                  if  right_element=="":
                    right_element="-99999"   


                  if  left_element=="":
                    left_element="error_object"   


                  if i==1: #first time don't add "&"
                    conditions="("+left_element+operator+right_element+")"
                  else:
                    conditions=conditions+"&("+left_element+operator+right_element+")"
                except Exception as e  :
                  message="error get cond menu"
                  logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
                  #left_element="error_object" 
                  #right_element="-99999"
                  #conditions=conditions+"&("+left_element+operator+right_element+")" 

              if "select_new_l" in postvars:

                try:  
                  l="#_"+self.clear_PostData(postvars["select_new_l"][0])+"_#"
                  o=self.clear_PostData(postvars["select_new_o"][0])

                  if o=="=":
                    o="=="
                  r=self.clear_PostData(postvars["select_new_r"][0])
                  try:#detect if is a number
                    a=int(r) #was float
                  except:
                    r="#_"+r+"_#"

                  if (l!="#_select_an_element_#")&(r!="#_select_an_element_#"):
                    if menu_number<1:
                      conditions=conditions+"("+l+o+r+")"   
                    else:
                      conditions=conditions+"&("+l+o+r+")"   
                except Exception as e  :  
                  message="error2 get cond menu"
                  logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 

              scenarioDict[scenario_name]["conditions"]=conditions

              logprint("conditions"+str(conditions) )


              for a in objectDict.keys():#check and remove the not used scenarios from web_object attachedScenarios
                tmp_list_scenarios=objectDict[a].getListAttachedScenarios()
                for b in tmp_list_scenarios:
                  if scenarioDict[b]["conditions"].find(a+"_#")==-1: 
                # if the object is not in the conditions then remove it from web_object attachedScenarios
                    objectDict[a].removeAttachedScenario(b)
                  else:
                    objectDict[a].attachScenario(b)  


              list_of_object_inside_conditions=replace_conditions(conditions,scenario_name)[1] 
              for a in list_of_object_inside_conditions :# add the scenario to each web_object attachedScenarios    
                if a in objectDict.keys():  
                  objectDict[a].attachScenario(scenario_name)  
                  #if the scenario is not included in the web_object attachedScenarios



              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options)   



              if "save_and_reload_this_page" in postvars:
                logprint("i reload the page.......................")
                current_page=self.clear_PostData(postvars["save_and_reload_this_page"][0])
                self.send_response(301)
                self.send_header('Location',current_page)
                self.end_headers()
                return         
                                 
              if "condition_mod_add_submit" in postvars:
                if menu_number<1:
                  conditions=conditions+"(#_select_an_element_#==#_select_an_element_#)"   
                else:
                  conditions=conditions+"&(#_select_an_element_#==#_select_an_element_#)"  
                scenarioDict[scenario_name]["conditions"]=conditions

                self.send_response(301)
                self.send_header('Location','/scenario_conditions/'+scenario_name)
                self.end_headers()
                return              
 

              if "condition_add_submit" in postvars:
                if menu_number<1:
                  conditions=conditions+"(#_select_an_element_#==#_select_an_element_#)"   
                else:
                  conditions=conditions+"&(#_select_an_element_#==#_select_an_element_#)"  
                scenarioDict[scenario_name]["conditions"]=conditions

                self.send_response(301)
                self.send_header('Location','/scenario_creation_conditions/'+scenario_name)
                self.end_headers()
                return 


              elif "finish_conditions_setup" in postvars:

                self.send_response(301)
                self.send_header('Location','/mod_scenario/'+scenario_name)
                self.end_headers()
                return 


              elif "goto_operations" in postvars:
     
                self.send_response(301)
                self.send_header('Location','/scenario_operations/'+scenario_name)
                self.end_headers()
                return 

              else:
                logprint("error non submit button post found on mod_conditions page ")



            elif "function_to_run_1" in postvars:# if the current page is /function_to_run/scenario name  because "function_to_run_1"  is the hidden form name
            #<input type="hidden" name="mod_functions1a" value="">
              logprint("function_to_run_1 post received ")

              scenario_name=self.clear_PostData(postvars["function_to_run_1"][0])#get the current scenario name 

              if scenario_name not in scenarioDict:
                return(-1)

              if (postvars["menu_number"]!=" "):
                menu_number=int(self.clear_PostData(postvars["menu_number"][0]))
              else:
                return(-1)

              logprint("menu_number"+str(menu_number) )
              functions_list=[]
              for i in range(1,menu_number+1):
                try:
                  left_element="#_"+self.clear_PostData(postvars["select_l"+str(i)][0])+"_#"
                  operator=self.clear_PostData(postvars["select_op"+str(i)][0])
                  right_element=self.clear_PostData(postvars["select_r"+str(i)][0])  
                  if "second_op"+str(i) in postvars:
                    if "third_element"+str(i) in postvars:
                      second_operator=self.clear_PostData(postvars["second_op"+str(i)][0])   
                      third_element=self.clear_PostData(postvars["third_element"+str(i)][0])
                    else:
                      second_operator=""
                      third_element=""

                  if right_element=="variabile_numerica":
                    if "text_area1_"+str(i) in postvars:
                      right_element=self.clear_PostData(postvars["text_area1_"+str(i)][0])
                    else:
                      right_element=""

                  if third_element=="variabile_numerica":
                    if "text_area2_"+str(i) in postvars:
                      third_element=self.clear_PostData(postvars["text_area2_"+str(i)][0])
                    else:
                      third_element=""

                  if operator=="==":
                    operator="="  


                  try:#detect if is a number
                    a=int(right_element) #was float
                  except:
                    right_element="#_"+right_element+"_#"

                  if (third_element!="")&(third_element!=" ")&(second_operator!="")&(second_operator!=" ")&(third_element!="#_select_an_element_#"):
                    try:#detect if is a number
                      a=int(third_element) #was float
                    except:
                      third_element="#_"+third_element+"_#"
                    functions_list.append(left_element+operator+right_element+second_operator+third_element)
                  else:
                    functions_list.append(left_element+operator+right_element)

                except Exception as e  :
                  message="error get func menu"
                  logprint(message,verbose=7,error_tuple=(e,sys.exc_info())) 

              try:  
                left_element_new="#_"+self.clear_PostData(postvars["select_new_l"][0])+"_#"
                operator_new=self.clear_PostData(postvars["select_operator_new"][0])
                right_element_new=self.clear_PostData(postvars["select_new_r"][0])

                if "second_operator_new" in postvars:
                  if "select_new_third_element" in postvars:
                    second_operator_new=self.clear_PostData(postvars["second_operator_new"][0])
                    third_element_new=self.clear_PostData(postvars["select_new_third_element"][0])
                  else:
                    second_operator_new=""
                    third_element_new=""

                if operator_new=="==":
                  operator_new="="
                if second_operator_new=="==":
                  second_operator_new="="


                if right_element_new=="variabile_numerica":
                  if "text_area1new" in postvars:
                    right_element_new=self.clear_PostData(postvars["text_area1new"][0])
                  else:
                    right_element_new=""


                if third_element_new=="variabile_numerica":
                  if "text_area2new" in postvars:
                    third_element_new=self.clear_PostData(postvars["text_area2new"][0])
                  else:
                    third_element_new=""




                if (left_element_new!="#_select_an_element_#")&(right_element_new!="#_select_an_element_#"):
                  if (third_element_new!="")&(third_element_new!=" ")&(second_operator_new!="")&(second_operator_new!=" ")&(third_element_new!="#_select_an_element_#"):

                    try:#detect if is a number and so it don't need the #__#
                      a=int(right_element_new) #was float
                    except:
                      r="#_"+right_element_new+"_#"
                    try:#detect if is a number
                      a=int(third_element_new) #was float
                    except:
                      third_element_new="#_"+third_element_new+"_#"

                    functions_list.append(left_element_new+operator_new+right_element_new+second_operator_new+third_element_new) 
                  else:
                    functions_list.append(left_element_new+operator_new+right_element_new)     
                else:
                  logprint("no new operations found in the post")


              except Exception as e  :
                message="error2 get cond menu"
                logprint(message,verbose=7,error_tuple=(e,sys.exc_info())) 




              scenarioDict[scenario_name]["functionsToRun"]=functions_list
              logprint("functions"+str(functions_list) ) 

              updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 

  
              if "save_and_reload_this_page" in postvars:
                logprint("i reload the page.......................")
                current_page=self.clear_PostData(postvars["save_and_reload_this_page"][0])
                self.send_response(301)
                self.send_header('Location',current_page)
                self.end_headers()
                return  

              elif "condition_add_submit" in postvars:
                self.send_response(301)
                self.send_header('Location','/function_to_run/'+scenario_name)
                self.end_headers()
                return 

              elif "function_add_submit" in postvars:
                self.send_response(301)
                self.send_header('Location','/mod_scenario/'+scenario_name)
                self.end_headers()
                return 

              elif "scenario_operations_add_submit" in postvars:
                self.send_response(301)
                self.send_header('Location','/scenario_operations/'+scenario_name)
                self.end_headers()
                return 

              elif "finish_operation_setup" in postvars:
                self.send_response(301)
                self.send_header('Location','/mod_scenario/'+scenario_name)
                self.end_headers()
                return 
##############end of scenario form data receiver ################################






            elif "login_form" in postvars:#if the current page is /login.html  because "login_form"  is the hidden form name
            #<form action="" method="POST"><input type="hidden" name="login_form" value="/login">

              pag=""
              if ((postvars["username_form"]!=" ")&(postvars["password_form"]!=" ")):
                username=self.clear_PostData(postvars["username_form"][0])
                password=self.clear_PostData(postvars["password_form"][0])

                if (username in usersDict.keys()):  #if the username exist
                  if usersDict[username]["pw"]==password : #if the password is correct
                    user_active_time_dict[self.client_address[0]]=[username,datetime.datetime.today().minute+(datetime.datetime.today().hour)*60 ]
                    logprint("user ip is:"+str(self.client_address[0]) )

                    #logprint(user_active_time_dict)
                    logprint("user :"+username+"logged succesfully")
                    #pag="successfully logged"
                    self.send_response(301)
                    self.send_header('Location','/')
                    self.end_headers()
                    return

                  else:
                    logprint("error user :"+username+"cant't log because of wrong password",verbose=10)

                    #pag="wrong password"
                    self.send_response(301)
                    self.send_header('Location','/gui/password_error.html')
                    self.end_headers()
                    return
                else:
                  logprint("error an user tried to log in with a wrong username",verbose=10)
                  self.send_response(301)
                  self.send_header('Location','/gui/user_error.html')
                  self.end_headers()
                  return
                  #pag="wrong username"


            elif "new_user_form" in postvars:#if the current page is /create_user.html  because "new_user_form"  is the hidden form name
            #  <form action="" method="POST"><input type="hidden" name="new_user_form" value="">

              pag=""
              if ((postvars["create_user_form"]!=" ")&(postvars["create_password_form"]!=" ")&(postvars["repeat_password_form"]!=" ")):
                username=self.clear_PostData(postvars["create_user_form"][0])
                password=self.clear_PostData(postvars["create_password_form"][0])
                repeated_password=self.clear_PostData(postvars["repeat_password_form"][0])
                mail=self.clear_PostData(postvars["create_mail_form"][0])
                 




                if (password!=repeated_password): #wrong password entered
   
                  message="error the two passwords entered are not the same, please retype"
                  logprint(message,verbose=9)
                  cgi_name="gui/new_user.py"

                  namespace={} 
                  web_page=""
                  #execfile(cgi_name,locals(),namespace)  #execute external script 
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)                 
                  web_page=namespace["web_page"]
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(web_page) 
                  return



                if (internet_connection!=1):  # no internet connection
                  message="error internet connection lost while creating onos online user, please connect onos center to internet"
                  logprint(message,verbose=9)
                  cgi_name="gui/new_user.py"

                  namespace={} 
                  web_page=""
                  #execfile(cgi_name,locals(),namespace)  #execute external script 
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                  web_page=namespace["web_page"]
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(web_page) 
                  return







                if (username not in usersDict.keys()):  #if the username does not alredy exist in the local dictionary
                  

  
                  site_query=onos_online_site_url+"create_new_onos_user.php"
                  params = {'username':username, 'onos_key':onos_online_key,"user_pass":password,"onos_password":onos_online_password}     
                  try :

                    f=url_request_manager.request_encode_body('POST',site_query,params,timeout=Timeout(total=20))
                    result=f.data
                    logprint(result)

                  except Exception as e  :

                    message="server online query to create new user failed,please check connection and retry"+" e:"+str(e.args)
                    logprint(message,verbose=10)
                    cgi_name="gui/new_user.py"

                    namespace={} 
                    web_page=""
                    #execfile(cgi_name,locals(),namespace)  #execute external script /gui/new_user.py
                    exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                    web_page=namespace["web_page"]
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()
                    self.wfile.write(web_page) 
                    return


                  if (result.find("syntax error")!=-1)or (result.find("error_")!=-1):
   
                    message="error in the server answer while creating onos online user, please retry"
                    logprint(message,verbose=10)
                    cgi_name="gui/new_user.py"

                    namespace={} 
                    web_page=""
                    #execfile(cgi_name,locals(),namespace)  #execute external script /gui/new_user.py   
                    exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)              
                    web_page=namespace["web_page"]
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()
                    self.wfile.write(web_page) 
                    return

                  if (result.find("#_onos_online_user_created")!=-1): #the username was created in the online server
                  
                    usersDict[username]={"pw":password,"mail_control_password":password,"priority":0,"user_mail":mail}

                    updateJson(objectDict,nodeDict,zoneDict,scenarioDict,conf_options) 
                    
                    message="username created in the online server and in the onos server"
                    logprint(message,verbose=5)
                    cgi_name="gui/new_user.py"

                    namespace={} 
                    web_page=""
                    #execfile(cgi_name,locals(),namespace)  #execute external script /gui/new_user.py
                    exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)
                    web_page=namespace["web_page"]
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()
                    self.wfile.write(web_page) 


                  else:  #username already used on online server  

                    message="error the username is already used in the online server,please choose another username and retry,result:"+result
                    logprint(message,verbose=10)
                    cgi_name="gui/new_user.py"
                    namespace={} 
                    web_page=""
                    #execfile(cgi_name,locals(),namespace)  #execute external script /gui/new_user.py  
                    exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)                
                    web_page=namespace["web_page"]
                    self.send_response(200)
                    self.send_header('Content-type',	'text/html')
                    self.end_headers()
                    self.wfile.write(web_page) 
                    return

                else:
                  message="error the username is already used in the onosCenter,please choose another username and retry"
                  logprint(message,verbose=10)
                  cgi_name="gui/new_user.py"
                  namespace={} 
                  web_page=""
                  #execfile(cgi_name,locals(),namespace)  #execute external script /gui/new_user.py   
                  exec(compile(open(cgi_name, "rb").read(), cgi_name, 'exec'), globals(), namespace)             
                  web_page=namespace["web_page"]
                  self.send_response(200)
                  self.send_header('Content-type',	'text/html')
                  self.end_headers()
                  self.wfile.write(web_page) 
                  return



      


            elif "post0" in postvars:
              logprint("received post0:"+str(postvars["post0"][0]) )  #  print the first post variable
  

            if (data_to_update==100):
              #updateJson()
              updateDir()
              data_to_update=0   
             
        else:
            postvars = {}
        

#a timeout  
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):  # i don't know if usefull to close client timout connections

  logprint("class RequestHandler executed()")  


  def setup(self):# i don't know if usefull to close client timout connections
    
    BaseHTTPServer.BaseHTTPRequestHandler.setup(self)
    self.request.settimeout(30)

  def finish_request(self, request, client_address):# i don't know if usefull to close client timout connections
    logprint("finish_request() executed")
    request.settimeout(30)
    # "super" can not be used because BaseServer is not created from object
    BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)




 #another timeout 
#class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):# i don't know if usefull to close client timout
#  def __init__(self, request, client_address, server):
#    BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)   
#    print "classsee eseguitaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  




def onlineServerSync():
  logprint("onlineServerSync() excuted")
  global onlineServerSyncThreadIsrunning
  global online_first_contact
  global online_usersDict
  global force_online_sync_users
  global online_zone_dict
  global online_object_dict
  global last_internet_check
  result=""
  while (exit==0): #if exit ==1  then close the service    
    onlineServerSyncThreadIsrunning=1


 #   try:
 #     urllib2.urlopen("http://www.google.com")  
 #   except:
 #     print "no internet connection"
 #     errorQueue.put("no internet connection" )  
      #time.sleep(30) #wait 60 seconds
#      return
     

    try:
      object_tmp_dict=transform_object_to_dict(objectDict) 
    except Exception as e  :
      message="error executing transform_object_to_dict()"
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))   


    if (online_first_contact==1) :

      zone_json_dictionary=json.dumps(zoneDict)
      
      object_json_dictionary=json.dumps(object_tmp_dict)

      #site_query=onos_online_site_url+"create_new_onos_center.php"
      #params = urllib.urlencode({'onos_key': onos_online_key, 'pass':onos_online_password,'hw_fw_version':router_hardware_fw_version})
      #f = urllib.urlopen(site_query, params)
      #print f.read()  #banana check the answer to see if the database was created
      

      #update all objects and zones
      site_query=onos_online_site_url+"db_sync_with_onos.php"
      params = {'onos_key': onos_online_key, 'onos_password':onos_online_password,"zone_sync":"1","zone_dict":zone_json_dictionary,"obj_sync":"all","obj_dict":object_json_dictionary}     
      try :
        #f = urllib2.urlopen(site_query, params,timeout = 5)
        f=url_request_manager.request_encode_body('POST',site_query,params,timeout=Timeout(total=20))
        result=f.data
        logprint(result)
        online_first_contact=0
        online_object_dict=object_json_dictionary
        online_zone_dict=zone_json_dictionary
        last_internet_check=time.time() #if it has connected to the server then also internet is working...
      except Exception as e  :
        message="first online contact failed"
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))   
        continue

      if (result.find("syntax error")!=-1)or (result.find("error_")!=-1):
        online_object_dict=""
        online_zone_dict=""
        online_first_contact=1

      #time.sleep(online_server_delay)
      #onlineServerSyncThreadIsrunning=0
      #return
      continue

    


    #if (cmp(online_usersDict,online_synced_user_dict))!=0 : #the dictionaries are different banana, to get this value from the server
    if (force_online_sync_users==1):
      #create a copy of all the local users in the online db
      logprint("i create the remote users")
      site_query=onos_online_site_url+"create_new_onos_user.php"
      for a in online_usersDict.keys():  # for each local username    
        params = {'onos_key': onos_online_key, 'onos_password':onos_online_password,"username":a,"user_pass":online_usersDict[a]["pw"]}
        try:
          #f = urllib2.urlopen(site_query, params,timeout = 5)
          f=url_request_manager.request_encode_body('POST',site_query,params,timeout=Timeout(total=20))
          result=f.data
          logprint(result)
          force_online_sync_users=0
          last_internet_check=time.time() #if it has connected to the server then also internet is working...
        except Exception as e  :
          message="error creating online user "
          logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 

         

        if (result.find("syntax error")!=-1)or (result.find("error_")!=-1):
          force_online_sync_users=1




    object_json_dictionary=json.dumps(object_tmp_dict)
    if (object_json_dictionary!=online_object_dict): #the dictionaries are different 
      logprint("i sync the remote object dict")  

      #print "object_json_dictionary:"+object_json_dictionary

      site_query=onos_online_site_url+"db_sync_with_onos.php"
      params = {'onos_key': onos_online_key, 'onos_password':onos_online_password,"zone_sync":"0","obj_sync":"all","obj_dict":object_json_dictionary}

      try:
        #f = urllib2.urlopen(site_query, params,timeout = 5)
        #result=f.read()
        f=url_request_manager.request_encode_body('POST',site_query,params,timeout=Timeout(total=20))
        result=f.data
        #print result
        last_internet_check=time.time() #if it has connected to the server then also internet is working...
        online_object_dict=object_json_dictionary
      except Exception as e  :
        message="error in the remote object update"
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
        online_object_dict=""
        continue
      if (result.find("syntax error")!=-1)or (result.find("error_")!=-1):
        online_object_dict=""
        continue





    zone_json_dictionary=json.dumps(zoneDict)
    #print "cmp  zone----------------------------------------",cmp(zone_json_dictionary,online_zone_dict)
    if (zone_json_dictionary!=online_zone_dict) : #the dictionaries are different  banana, to get this value from the server
      logprint("i sync the remote zone dict")
 

      site_query=onos_online_site_url+"db_sync_with_onos.php"
      params = {'onos_key': onos_online_key, 'onos_password':onos_online_password,"zone_sync":"1","zone_dict":zone_json_dictionary,"obj_sync":"0"}
      try:
        #f = urllib2.urlopen(site_query, params,timeout = 5)
        #result=f.read()
        f=url_request_manager.request_encode_body('POST',site_query,params,timeout=Timeout(total=20))
        result=f.data
        logprint(result)
        online_zone_dict=zone_json_dictionary  #banana, to get this value from the server
        last_internet_check=time.time() #if it has connected to the server then also internet is working...
      except Exception as e  :
        message="error in the remote object update"
        logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
        online_zone_dict=""
        continue
      if (result.find("syntax error")!=-1)or (result.find("error_")!=-1):
        online_zone_dict=""
        continue
    #time_sync=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")   # '2015-08-19-09-15-18'   time to allow the server detect when the onos center is online
    site_query=onos_online_site_url+"get_sync_messages.php"
    params = {'onos_key': onos_online_key, 'onos_password': onos_online_password,'hw_fw_version':router_hardware_fw_version}
    try:
      #f = urllib2.urlopen(site_query, params,timeout = 5)
      #sync_message=f.read()
      f=url_request_manager.request_encode_body('POST',site_query,params,timeout=Timeout(total=20))
      result=f.data
      sync_message=result
      logprint(sync_message)
      last_internet_check=time.time() #if it has connected to the server then also internet is working...
    except Exception as e  :
      message="error contacting the online server to get sync message"
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
      onlineServerSyncThreadIsrunning=0
      return()

#message example :
# old  '#start@#_@onosuser#_@obj_ch#_@obj1#_@objstatus_to_set#_#stop@"      message for online obj changed to objstatus_to_set
    try:
      ###json_filtered_msg=re.match(r'#_cmd_.+?_cmd_#',sync_message).group(1)
      #re.search('#_cmd_(.+?)_cmd_#',sync_message).group(1)
      #json_filtered_msg=sync_message.partition("#_cmd_")[2].partition("_cmd_#")[0]
      json_filtered_msg=re.search('#_cmd_(.+?)_cmd_#',sync_message).group(1)
      logprint("filtered sync_message :"+json_filtered_msg)
      cmd_list=json.loads(json_filtered_msg)
      logprint("json_cmd_list:"+str(cmd_list) )
      for a in cmd_list :  #iterate the list
        cmd_split=a.split("#_@")  #split    using #_@  as delimiter
        logprint("cmd_split"+str(cmd_split) )
        username=cmd_split[1]
        if username not in usersDict.keys():
          logprint("error online username not in local users Dict",verbose=10)

          continue
        cmd_code=cmd_split[2]
        logprint("online username:"+username+" cmd code="+cmd_code)

        if cmd_code=="obj_ch":
          obj_name=cmd_split[3]
          status_to_set=cmd_split[4]
          priority=usersDict[username]["priority"]
          priorityCmdQueue.put( {"cmd":"setSts","webObjectName":obj_name,"status_to_set":status_to_set,"write_to_hw":1,"priority":priority,"user":username,"mail_report_list":[] })  

    except Exception as e  :
      message="sync_message decoding error,sync_message:"
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
    onlineServerSyncThreadIsrunning=0
    return()



  onlineServerSyncThreadIsrunning=0
  return()


def mailOutputHandler():
  global errorQueue
  global mailOutputHandler_is_running

  mailOutputHandler_is_running=1
  logprint("mailOutputHandler thread executed")


  while not mailQueue.empty(): #until there are no more mail to send

    
    mail_to_send = mailQueue.get()
    #mailQueue.task_done()
    mail_address=mail_to_send["mail_address"]
    mailText=mail_to_send["mailText"]
    mailSubject=mail_to_send["mailSubject"]
    mail_sent=sendMail(mail_address,mailText,mailSubject,onos_mail_conf,smtplib,string)
    if mail_sent!=1 : #mail error , onos was not able to send the mail and will try again
      logprint("error cant send mail"+mail_sent,verbose=8)
     
      mailQueue.put(mail_to_send)  #read the mail to the queue for further try
      #mailQueue.put({"mail_address":mail_address,"mailText":mailText,"mailSubject":mailSubject})

      time.sleep(mail_retry_timeout) # wait before retry...to not overuse the cpu
      

  mailOutputHandler_is_running=0
  return


def mailCheckThread():
  logprint("mailCheckThread() excuted")
  global mailCheckThreadIsrunning  
  mailCheckThreadIsrunning=1


  if (exit==0):   #if exit ==1  then close the webserver

    #time.sleep(1)  #wait
    try:
      mailList=receiveMail(onos_mail_conf,imaplib,email)  #a list of list where the data are (msg_sender,msg_subject,msg_text)
    except Exception as e:
      message="error in  mailagent"
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
      mailList=-1

    if mailList==-1:
      logprint("error mailagent ,  wrong username/password or no internet connection,i disable the incoming mail service",verbose=10)
      conf_options["enable_mail_service"]=0  
      return() 

    if len(mailList)>0:  #there are mails
      for rx_mail in mailList:
        #print "rx mail=",rx_mail
        m_sender=rx_mail[0]
        m_subject=rx_mail[1]
        m_text=rx_mail[2]

        rx_mail_lines=m_text.splitlines() #split by lines  
        #answer_mail=[] 
        mailText="" #answer mail text
        mailSubject="onos_report" #answer mail subject


        for l in rx_mail_lines:  #for each line there will be a command...
          l=l.strip()#remove start and end spaces 
          onos_usr="onos_mail_guest"
          usr_onos_mail_pw=usersDict[onos_usr]["mail_control_password"]
          cmd_type=""
          cmd_argument=""
          priority=""
          log_enable=0 
          scenario_enable=""
          status="" 
   

          
  # example : onos=cmd:so,arg:button1_RouterGL0000,st:1,      note the end ","  must be used          
          if 1: 
            tmp_split=l.split(",")

            for t_arg in tmp_split:
              if (t_arg.find(u"usr:"))!=-1:
                onos_usr=t_arg.split(u":")[1]  #get onos_usr from  "usr:onos_usr"
              if (t_arg.find(u"pw:"))!=-1:
                usr_onos_mail_pw=t_arg.split(u":")[1]  #get onos_pw from  "pw:onos_pw"
              if (t_arg.find(u"cmd:"))!=-1:
                cmd_type=t_arg.split(u":")[1]  
              if (t_arg.find(u"st:"))!=-1:
                status=t_arg.split(u":")[1]  
              if (t_arg.find(u"arg:"))!=-1:
                cmd_argument=t_arg.split(u":")[1]  
              if (t_arg.find(u"priority:"))!=-1:
                priority=t_arg.split(u":")[1]  


            if onos_usr not in usersDict.keys() :
              logprint("error mail user  not in user list",verbose=9)
              mailText=mailText+compose_error_mail("wrong_username")
              continue   


            if compareText(usr_onos_mail_pw,usersDict[onos_usr]["mail_control_password"])!=1 :
              logprint("error mail user password not correct",verbose=9)    
              mailText=mailText+compose_error_mail("wrong_password")
              continue   


            if compareText(onos_usr,onos_usr)==1: #if the username is the default mail one.. 
              if m_sender not in conf_options["mail_whiteList"] :
                logprint("error mail not in mail list",verbose=9)    
                mailText=mailText+compose_error_mail("white_list")
                continue   


            if conf_options["accept_only_from_white_list"]==1:

              if m_sender not in conf_options["mail_whiteList"] :
                logprint("error mail not in mail list")
                mailText=mailText+compose_error_mail("white_list")
                continue   

            

          else:
            logprint("mail parsing error")
            mailText=mailText+compose_error_mail("parse")
            continue

          if (len(priority)==0):            
            priority=usersDict[onos_usr]["priority"]
          #print "priority set to :",priority

          if compareText(cmd_type,u"so"):  #if the cmd type is set object..

            
            objName=cmd_argument
            if (len(objName)>0)&(len(status)>0):  #the arguments lenghts are ok
              if objName in objectDict:  #the object exist
                obj_previous_status=objectDict[objName].getStatus()
                if (objectDict[objName].validateStatusToSetObj(status)==1 ):  #if the status is ok and type is output  
                  logprint("check priority")
                  if objectDict[objName].checkRequiredPriority(priority)==1:  #check priority 
                    logprint("priority ok")

                    #check permission  
                    if objectDict[objName].checkPermissions(onos_usr,"x",priority):#check if user has execution to obj                   
                      logprint("permission ok ,i write to obj")
                      mailText=mailText+"O.N.O.S. received the mail :"+l+" and is processing it ,"
                      priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status,"write_to_hw":1,"priority":priority,"user":"onos_usr","mail_report_list":[m_sender] })  
                      continue

                    else: #permission error
                      logprint("permission error"+str(objName),verbose=10) 
                      continue
                                                           

 
                  else:
                    logprint("error mail , user priority not sufficent to change the obj:"+objName+" status",verbose=10)
                    mailText=mailText+compose_error_mail("so_priority",objName)
                    continue


              
                else:   
                  logprint("error mail ,object:"+objName+" type not compatible with status passed ",verbose=10)
                  mailText=mailText+compose_error_mail("so_value",objName)
                  continue


              else:
                logprint("error mail, can't found the argument in the dictionary ",verbose=10)
                mailText=mailText+compose_error_mail("so_obj_not_exist",objName)
                continue                                         
            
            else:
              logprint("error mail invalid arg len",verbose=10)
              continue
                      
          else: #not a know cmdtype
            logprint("unknow mail cmd:"+cmd_type,verbose=10)            
            continue                                  

        logprint("send mail.."+mailText)

        mailQueue.put({"mail_address":m_sender,"mailText":mailText,"mailSubject":mailSubject})


    else:#no mail received
      #time.sleep(mail_check_frequency)
      mailCheckThreadIsrunning=0
      return()            
  #time.sleep(mail_check_frequency)
  mailCheckThreadIsrunning=0
  return()


def internetCheckConnection():
  internet_state=0
  try:
    urllib2.urlopen("http://www.google.com")  
    internet_state=1
  except Exception as e: 
    message="no internet connection 0"
    logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
    internet_state=0
  return(internet_state)


def hardwareHandlerThread():  #check the nodes status and update the webobjects values 
  global mailCheckThreadIsrunning
  global last_pin_read_time
  global last_mail_sync_time
  global last_server_sync_time
  global last_error_check_time
  global last_internet_check
  global reconnect_serial_port_enable
  read_pin=1   #banana
  #time.sleep(5)  #wait for webserver to startup 
  logprint("hardwareHandlerThread() executed")
  #if (exit==0):   #if exit ==1  then close the webserver
  #print time.time()
  #print "last_mail_sync_time",last_mail_sync_time
  #print  "last_server_sync_time",last_server_sync_time
  #print "last_pin_read_time",last_pin_read_time
  #print "diff last_mail_sync_time",time.time()-last_mail_sync_time
  #print "diff last_server_sync_time",time.time()-last_server_sync_time
  #print "diff last_pin_read_time",time.time()-last_pin_read_time
  last_node_check=0
  last_internet_check=0
  internetCheckThreshold=10  # how often do onos check for connection (expressed in seconds)




  while (exit==0): 

    time.sleep(1.5)# was 1.5 .. to save cpu load



    if ( (time.time()-last_internet_check) >internetCheckThreshold ):   #was EVERY 5 SECONDS
      last_internet_check=time.time()
      internet_connection=internetCheckConnection()
 




    if ( (time.time()-last_node_check) >2 ):   #EVERY 2 SECONDS   todo: make this function..
      #print "threads:",len(threading.enumerate())
      #print "check nodeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

      if enable_usb_serial_port==1:

        if (hardware.serialCommunicationIsWorking==0)&(reconnect_serial_port_enable==0):
          reconnect_serial_port_enable=time.time()+30   

        if(reconnect_serial_port_enable!=0)&(reconnect_serial_port_enable<time.time()) :  #check if serial port has to be reconnected
          hardware.serialCommunicationIsWorking=0
        #if reconnect_serial_port_enable<time.time():
          layerExchangeDataQueue.put( {"cmd":"reconnectSerialPort"}) 
          reconnect_serial_port_enable=0     

      last_node_check=time.time()
      #banana try...
      for a in nodeDict.keys():
        if a==router_sn:  #skip the router node
          continue

        if nodeDict[a].getNodeTimeout()=="never": #never timeout
          continue
         
        #print "nodecheck:"+a

        #print "last_node_sync:"+str(nodeDict[a].getLastNodeSync()) 
        #print "time_now:"+str(time.time()) 

        #print "difference=:"+str(time.time()-nodeDict[a].getLastNodeSync())

        #message="nodecheck:"+a+" last_sync:"+str(nodeDict[a].getLastNodeSync())+" time_now:"+str(time.time())+"timeout at:"+str(nodeDict[a].getNodeTimeout())+"will timeout in:"+str( nodeDict[a].getNodeTimeout() -(time.time()-nodeDict[a].getLastNodeSync() ) )
        #logprint(message,verbose=1)   


        if  (  (time.time()-nodeDict[a].getLastNodeSync() )>nodeDict[a].getNodeTimeout()  ) : #the node is not connected anymore       

          if nodeDict[a].getNodeActivity()==0 or nodeDict[a].getNodeActivity()==2: #if the node was already inactive or preactive
            nodeDict[a].updateLastNodeSync(time.time()-99999) #set this to prevent the overflow of the variable
            message="the node:"+a+"is disconnected for timeout but was already so.." 
            logprint(message,verbose=2) 
            continue #skip

          node_address=nodeDict[a].getNodeAddress() 
          numeric_address=int(node_address)
          if numeric_address not in next_node_free_address_list: 
            next_node_free_address_list.pop()

          nodeDict[a].setNodeActivity(0)  #set the node as inactive
          message="the node:"+a+" IS NOT CONNECTED ANYMORE,did you disconnect it? difference=:"+str(time.time()-nodeDict[a].getLastNodeSync())
          logprint(message,verbose=6)  

          for b in nodeDict[a].getnodeObjectsDict().values():#for each object in the node 
            priorityCmdQueue.put( {"cmd":"setSts","webObjectName":b,"status_to_set":"inactive","write_to_hw":0,"user":"onos_node","priority":99,"mail_report_list":[]}) 

          #for b in objectDict.keys():
          #  if objectDict[b].getHwNodeSerialNumber()==a :  #if the web object is from the node a then disactive it
              #objectDict[b].setStatus("inactive")
          #    priorityCmdQueue.put( {"cmd":"setSts","webObjectName":b,"status_to_set":"inactive","write_to_hw":0,"user":"onos_node","priority":99,"mail_report_list":[]}) 

        else:#now the node is connected
          if nodeDict[a].getNodeActivity()==0 or nodeDict[a].getNodeActivity()==2: #the node was not connected but now it is
            nodeDict[a].setNodeActivity(1)  #set the node as active
            message="The node:"+a+" IS NOW RECONNECTED "+"at:" +getErrorTimeString()
            logprint(message,verbose=5)
            #for b in objectDict.keys():
            for b in nodeDict[a].getnodeObjectsDict().values():#for each object in the node 
              logprint("objectDict[b].getHwNodeSerialNumber():"+str(objectDict[b].getHwNodeSerialNumber()) )
              #if objectDict[b].getHwNodeSerialNumber()==a :  #if the web object is from the node a then reactive it
              logprint("webobject:"+b+"returned active",verbose=5)
              prev_s=objectDict[b].getPreviousStatus() 
              current_s=objectDict[b].getStatus()
              if ((current_s=="inactive") or (current_s=="onoswait") ): 
              #  prev_s=objectDict[b].getStartStatus()      #if the current status is "inactive" set it to the previous status
                logprint("the new status will be:"+str(prev_s) )
                priorityCmdQueue.put( {"cmd":"setSts","webObjectName":b,"status_to_set":prev_s,"write_to_hw":1,"user":"onos_node","priority":99,"mail_report_list":[]})
                #set the web_object to the status before the disconnection 
          
          #nodeDict[a].updateLastNodeSync(time.time())




    if (conf_options["online_server_enable"]==1)&(internet_connection==1):
      if (onlineServerSyncThreadIsrunning==0)&((time.time()-last_server_sync_time)>online_server_delay):
        last_server_sync_time=time.time()
        logprint("i started the online server sync service")
        try:
          w4 = threading.Thread(target=onlineServerSync)
          w4.daemon = True  #make the thread a daemon thread
          w4.start()
        except Exception as e :
          message="error executing onlineServerSync()"
          logprint(message,verbose=10,error_tuple=(e,sys.exc_info())) 
   # time.sleep(0.3) #don't remove this or else the router became instable

   #the mail check will run only if the onlineServerSync is not running    
    if (conf_options["enable_mail_service"]==1)&(internet_connection==1)&(onlineServerSyncThreadIsrunning==0):   
      if (mailCheckThreadIsrunning==0)&((time.time()-last_mail_sync_time)>mail_check_frequency):
        last_mail_sync_time=time.time()
        try:
          w3 = threading.Thread(target=mailCheckThread)
          w3.daemon = True  #make the thread a daemon thread
          w3.start()
        except Exception as e :
          message="error executing mailCheckThread()"
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
          #continue
         
    #time.sleep(0.2)
    if (read_pin>0)&((time.time()-last_pin_read_time)>router_read_pin_frequency):  #execute every n seconds
      last_pin_read_time=time.time()
      #time.sleep(0.2)

      #try:
      #read local onosCenter pins (the router pin)
      try:
        read_pin=read_pin+hardware.read_router_pins()  # if hardware.read_router_pins() is -1 for two times it will go to <0
      except Exception as e :
        message="error executing hardware.read_router_pins()"
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 




    # remove serial packets not useful

    try: 

      if hardware.serial_communication.uart!=0:

        if hardware.serialCommunicationIsWorking==1:
          #print str(hardware.serial_communication.uart)
          if len (hardware.serial_communication.uart.readed_packets_list)>0:
            logprint("there is an incoming data on serial port buffer"+str(hardware.serial_communication.uart.readed_packets_list))

            if hardware.serial_communication.uart.readed_packets_list[0]=="[S_ertx1_#]":
              hardware.serial_communication.uart.readed_packets_list.pop(0)  

            elif hardware.serial_communication.uart.readed_packets_list[0]=="[S_nocmd0_#]":
              hardware.serial_communication.uart.readed_packets_list.pop(0)  
     
            with lock_serial_input:
              if len (hardware.serial_communication.uart.readed_packets_list)>20: #if the list became long cut the first 4 elements
                hardware.serial_communication.uart.readed_packets_list.pop(0)  
                hardware.serial_communication.uart.readed_packets_list.pop(0) 
                hardware.serial_communication.uart.readed_packets_list.pop(0)  
                hardware.serial_communication.uart.readed_packets_list.pop(0)   

        else:
          hardware.serialCommunicationIsWorking==0
          logprint("serial port not working correctly",verbose=9)  

    except Exception as e:

      if enable_usb_serial_port==1:
        message="serial port not working correctly2"
        logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))
      else:
        pass



    if (mail_error_log_enable==1):

      if (  (  (time.time()-last_error_check_time)>error_log_mail_frequency)  ):
        last_error_check_time=time.time()
        try:
          
          error_text=""
          while not errorQueue.empty():
            error_text =error_text+";;;\n"+str(errorQueue.get())
            #errorQueue.task_done()
          if (len (error_text) > 0):
            mailQueue.put({"mail_address":mail_where_to_send_errors,"mailText":error_text,"mailSubject":"onos_errors_report"})

        except Exception as e:
          message="error in the error mail log of hardwareHandlerThread,error:"+error_text
          logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))











    if ( mailQueue.empty()==0 )&( mailOutputHandler_is_running==0)&(internet_connection==1)&(conf_options["enable_mail_output_service"]==1):  #start the mail output thread if needed
      #print "mailOutputHandler_is_running=",mailOutputHandler_is_running
      #print "i execute mailOutputHandler thread ddddddddddddddddddddDDDDDDDDDDDDDDDDDDDdddddddddddDDDDDDDDDDDDDDDDdd "
      try:
        send_mail = threading.Thread(target=mailOutputHandler)
        send_mail.daemon = True  #make the thread a daemon thread
        send_mail.start()

      except Exception as e:     
        message="error in the mail send of onosBusThread "
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))
   
      #print "mailOutputHandler_is_running=",mailOutputHandler_is_running




def executeQueueFunction(dataExchanged):

  if ((dataExchanged["cmd"])=="setNodePin"):
    try: 
      node_serial_number=dataExchanged["nodeSn"]
      pin_number=dataExchanged["pinNumber"]
      pin_status=dataExchanged["status_to_set"]
      write_hw_enable=dataExchanged["write_to_hw"]
      mail_list_to_report_to=dataExchanged["mail_report_list"]
      setNodePin(node_serial_number,pin_number,pin_status,write_hw_enable)
    except Exception as e :
      message="error in the setNodePin of onosBusThread "
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))

      return(-1)

        

  if (dataExchanged["cmd"]=="setSts"):    

    try:          
      objName=dataExchanged["webObjectName"]
      status_to_set=dataExchanged["status_to_set"]
      write_hw_enable=dataExchanged["write_to_hw"]
      usr=dataExchanged["user"]#"onos_sys"
      priority=0
      mail_list_to_report_to=[]
      if "mail_report_list" in dataExchanged.keys():
        mail_list_to_report_to=dataExchanged["mail_report_list"]
      if "user" in dataExchanged.keys():
        usr=dataExchanged["user"]
      if "priority" in dataExchanged.keys():
        priority=dataExchanged["priority"]

      changeWebObjectStatus(objName,status_to_set,write_hw_enable,usr,priority,mail_list_to_report_to)

    except Exception as e:
      message="error in the setSts of onosBusThread "
      logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))


        
  if (dataExchanged["cmd"]=="scen_check"):
    try:
      scenarioName=dataExchanged["scenarioName"]
      checkwebObjectScenarios(scenarioName) 
    except Exception as e:
      message="error in the scen_check of onosBusThread ,scenario_name:"
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))


  if (dataExchanged["cmd"]=="updateObjFromNode"):

    logprint("updateObjFromNode_in_executeQueueFunction")

#hardwareModelDict["WPlugAvx"]["pin_mode"]["digital_obj_out"]={"plug":[(0)],"plug2":[(1)]}# 

    node_serial_number=dataExchanged["nodeSn"]
    node_address=dataExchanged["nodeAddress"]
    node_fw=dataExchanged["nodeFw"]
    if node_serial_number not in nodeDict.keys():
      message="error node_sn:"+node_serial_number+" not in nodeDict"
      logprint(message,verbose=6)
      priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":node_serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 
      return

    updateNodeAddress(node_serial_number,uart_router_sn,node_address,node_fw)
    node_model_name=node_serial_number[0:-4]#get WPlugAvx from  WPlugAvx0008
    logprint(str(dataExchanged["objects_to_update"].keys())+"end data_exanged")


    try:
      #{obj_number_to_update:obj_value}  
      for a in dataExchanged["objects_to_update"].keys(): # for each obj in the node that is to update.. 
        logprint("object address in the node="+str(a) )
        try:
          objName=nodeDict[node_serial_number].getNodeObjectFromAddress(int(a))
          objectDict[objName].getStatus()  #just to see if the object exist and otherwise to create it in the except...
        except Exception as e: #todo place this somewhere else..
          hwType=node_serial_number[0:-4]  #get Plug6way  from Plug6way0001
          message="warning in the updateObjFromNode,the object doesnt exist yet"
          logprint(message,verbose=7,error_tuple=(e,sys.exc_info()))  
          msg=createNewNode(node_serial_number,node_address,node_fw)+"_#]" 
          createNewWebObjFromNode(hwType,node_serial_number) 

          return()

        logprint("objName to upade the value:"+objName) 
        status_to_set=dataExchanged["objects_to_update"][a]
        write_hw_enable=0
        usr="onos_node"
        priority=0
        mail_list_to_report_to=[]
      #example of objName: socket0_Plug6way0002
        logprint("I call changeWebObjectStatus() to update the obj from node update")
        if status_to_set!=objectDict[objName].getStatus():
          #print(str((objName,status_to_set,write_hw_enable,usr,priority,mail_list_to_report_to)))

          changeWebObjectStatus(objName,status_to_set,write_hw_enable,usr,priority,mail_list_to_report_to) 

    except Exception as e: 
      message="error in the for loop of updateObjFromNode condition :node="+node_serial_number
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))



  if (dataExchanged["cmd"]=="updateNodeAddress"): # called from node_query_handler.py


    try:
      node_serial_number=dataExchanged["nodeSn"]
      node_address=dataExchanged["nodeAddress"]
      node_fw=dataExchanged["nodeFw"]
      if node_serial_number not in nodeDict.keys():
        priorityCmdQueue.put( {"cmd":"createNewNode","nodeSn":node_serial_number,"nodeAddress":node_address,"nodeFw":node_fw }) 
        return

      if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node was inactive
        nodeDict[node_serial_number].setNodeActivity(2)  #set the node as preactive state(not active yet but turned on)

      updateNodeAddress(node_serial_number,uart_router_sn,node_address,node_fw)

    except Exception as e:
      message="error in the updateNodeAddress of onosBusThread ,Node:"+str(node_serial_number)
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))




  if (dataExchanged["cmd"]=="createNewNode"):


    try:
      node_serial_number=dataExchanged["nodeSn"]
      node_address=dataExchanged["nodeAddress"]
      node_fw=dataExchanged["nodeFw"]

      msg=str(createNewNode(node_serial_number,node_address,node_fw) )+"_#]" 

      if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node was inactive
        nodeDict[node_serial_number].setNodeActivity(2)  #set the node as preactive state(not active yet but turned on)



    except Exception as e:
      message="error in the createNewNode of onosBusThread ,NewNode:"+str(node_serial_number)
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))

    
  if (dataExchanged["cmd"]=="NewAddressToNodeRequired"):
  
    old_address="254"
    node_fw="def1"
    try:
      node_serial_number=dataExchanged["nodeSn"]
      node_fw=dataExchanged["nodeFw"]
      #old_address=dataExchanged["nodeAddress"]
      if node_serial_number in nodeDict:
        old_address=nodeDict[node_serial_number].getNodeAddress()  
      else:
        msg=createNewNode(node_serial_number,old_address,node_fw)+"_#]" 

      #   [S_254sa123WLightSS0003_#]
      if old_address=="001":   #the router node will not need another address ..only a confirm for first message sync
        new_address=old_address
      else:
        new_address=getNextFreeAddress(node_serial_number,uart_router_sn,node_fw)

      hardware.setAddressToNode(node_serial_number,old_address,new_address) 
      #if result==1:
      #  print "i save the new address in the config memory"

    except Exception as e:
      message="error in the NewAddressToNodeRequired of onosBusThread ,Node:"+str(node_serial_number)
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
      msg=createNewNode(node_serial_number,old_address,node_fw)+"_#]" 


     
  if (dataExchanged["cmd"]=="set_serialCommunicationIsWorking=0"): #todo check if it works
    try:
      hardware.serialCommunicationIsWorking=0
    except Exception as e  :
      message="error in set_serialCommunicationIsWorking=0"
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
       


  if (dataExchanged["cmd"]=="reconnectSerialPort"): #todo check if it works
    hardware.serialCommunicationIsWorking=0
    logprint("I try to reconnect serial port from webserver.py")
    try:
        tryToReconnect=1
        try:
          if hardware.serial_communication.uart.ser.isOpen() == False:
            logprint("hardware.serial_communication.uart.ser.isOpen() == False ") 
          else:
            logprint("hardware.serial_communication.uart.ser.isOpen() = "+str(hardware.serial_communication.uart.ser.isOpen()))  
            #hardware.serial_communication.uart.ser.close()  
            #tryToReconnect=0

        except:
          logprint("error can't do hardware.serial_communication.uart.ser.isOpen() ",verbose=8) 
          tryToReconnect=1

        if tryToReconnect==1:
          result=hardware.connectSerialPort() 
          if result==1:
            #hardware.serial_communication.working=1
            logprint("serial port successfully reconnected from webserver.py",verbose=8)

          else:
            hardware.serial_communication.working=0
            logprint("error serial port can't be reconnected from webserver.py,serial port is already connected",verbose=8)


    except Exception as e: 

      message="error in serial port reconnection"
      logprint(message,verbose=6,error_tuple=(e,sys.exc_info()) )  


  logprint("dataExchanged = : "+str(dataExchanged) )

  return()

def onosBusThread():

  global internet_connection
  time.sleep(5)  #wait for webserver to startup 
  while (exit==0):   #if exit ==1  then close the webserver
    time.sleep(0.03)    #wait until layerExchangeDataQueue has some element     
    try:



      if not priorityCmdQueue.empty():   #this has priority over the other layer
        executeQueueFunction(priorityCmdQueue.get())
    
      if not layerExchangeDataQueue.empty():
        executeQueueFunction(layerExchangeDataQueue.get())


      if not priorityCmdQueue.empty():   #this has priority over the other layer
        executeQueueFunction(priorityCmdQueue.get())


      if not priorityCmdQueue.empty():   #this has priority over the other layer
        executeQueueFunction(priorityCmdQueue.get())


      if not layerExchangeDataQueue.empty():
        executeQueueFunction(layerExchangeDataQueue.get())



      while not priorityCmdQueue.empty():   #this has priority over the other layer
        executeQueueFunction(priorityCmdQueue.get())
        
      while not layerExchangeDataQueue.empty():
        executeQueueFunction(layerExchangeDataQueue.get())




      

        







    #here starts the less important part ,executed only when there is nothing in layerExchangeDataQueue

         
      try:
        old_minutes=objectDict["minutes"].getStatus()
      except Exception as e:  
        logprint("error in the minutes update of onosBusThread ")
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
        old_minutes=0

    #time_objects_handler
      if (old_minutes!=datetime.datetime.today().minute):  #each minute check
        



        try:
          changeWebObjectStatus("minutes",datetime.datetime.today().minute,0)
          changeWebObjectStatus("dayTime",datetime.datetime.today().minute+(datetime.datetime.today().hour)*60,0)

          old_hours=objectDict["hours"].getStatus()
          old_day=objectDict["day"].getStatus()
          old_month=objectDict["month"].getStatus()
          old_year=objectDict["year"].getStatus()
          old_dayTime=objectDict["dayTime"].getStatus()  #hours of the day expressed in minutes


          if (old_hours!=datetime.datetime.today().hour):
            #os.system('''ntpd -q -p 0.openwrt.pool.ntp.org''') #update from online time
            try:
              with lock_bash_cmd:
                subprocess.check_output('''ntpd -q -p 0.openwrt.pool.ntp.org''', shell=True,close_fds=True)
            except:
              logprint("error executing ntpd, maybe ntpd is not installed..",verbose=8) 


            changeWebObjectStatus("hours",datetime.datetime.today().hour,0)

          if (old_day!=datetime.datetime.today().day):
            changeWebObjectStatus("day",datetime.datetime.today().day,0)

          if (old_month!=datetime.datetime.today().month):
            changeWebObjectStatus("month",datetime.datetime.today().month,0)

          if (old_year!=datetime.datetime.today().year):
            changeWebObjectStatus("year",datetime.datetime.today().year,0)

        except Exception as e: 
          message="error in the time_objects_handler of onosBusThread "
          logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))



        global check_log_len_time
    

        if log_enable==1 :
          if ((old_dayTime-check_log_len_time)>10):  #each 10 minutes make a check,

 #    for u in user_active_time_dict.keys(): #check the user login timout

            check_log_len_time=old_dayTime
            logprint("check_log_len_time ")
            error_phrase="error"

            if os.path.getsize(log_name)>1000000: #if log size > 1 megabyte then save the errors and delete it
              logprint("i clear the onos log") 
              #os.system('''grep -B5 -A5 -P '^'''+error_phrase+'''$' '''+log_name+'''>>'''+error_log_name)  #save the 5 line prev and after the line with an error 
              with lock_bash_cmd:
                subprocess.check_output('''grep -B5 -A5 -P '^'''+error_phrase+'''$' '''+log_name+'''>>'''+error_log_name, shell=True,close_fds=True)
      #grep -B5 -A5 -P '^5$' filename
              #os.system('''echo " " >'''+log_name) #clear the file
              with lock_bash_cmd:
                subprocess.check_output('''echo " " >'''+log_name, shell=True,close_fds=True) 

    except Exception as e: 
      message="main error in onosBusThread() "
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))







def nodeTcpServer():



  while (exit==0):   #if exit ==1  then close the webserver
    #wait_because_node_is_talking=0  
    time.sleep(0.3)# was 0.2

    time.sleep(0.5) #for openwrt node
    try:
      # Create a TCP/IP socket
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  #    sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY, True) #disable_nagle_algorithm'):   #http://pydoc.net/Python/mrs-mapreduce/0.9/mrs.http/  https://aboutsimon.com/index.html%3Fp=85.html

      server_address = (get_ip_address(), service_webserver_port) #stored in globalVar.py
      #print >>sys.stderr, 'starting up on %s port %s' % server_address


      sock.bind(server_address)
      sock.listen(1)

      # Listen for incoming connections

      node_ip=""
      while (exit==0):
        time.sleep(0.1)
        #wait_because_node_is_talking=0  
        # Wait for a connection
        sock.settimeout(480) 
       # print >>sys.stderr, 'waiting for a connection'
        try:
          connection, client_address = sock.accept()  
          node_ip=client_address[0]
          logprint("nodeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"+str(node_ip) )
        except Exception as e  :
          message="error timeout in receiving!!!"
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info()))
          try:
            connection.close()
            logprint("connection  closed")   
          except:
            logprint("connection alredy closed") 
          logprint("error connection, client_address = sock.accept()  in nodeTcpServer()",verbose=7)






      
        else: # if the try was executed without errors
          received_message=""
          try:
            #print >>sys.stderr, 'connection from', client_address

          # Receive the data in small chunks and retransmit it
            #wait_because_node_is_talking=1
            while (exit==0):

              data = connection.recv(1024) #accept data till 1024 bytes


              received_message=received_message+data 


  
             # print >>sys.stderr, 'received "%s"' % data
              if data:
                connection.settimeout(2.0) 
               # print >>sys.stderr, 'sending data back to the client'

                
                msg=received_message
                if ( (data.find("[S_")!=-1)&(data.find("_#]")!=-1))  :   # if the message is completed close the connection
                  logprint("end line received!!!! ----------------------------------------------------")
                  logprint("received_message:"+received_message)
#example:  "pinsetup?node_sn=ProminiA0001&fw=4.85_#]"

                  if received_message.startswith("[S_001sy?") :  
                    cmd_start=msg.find("[S_")
                    cmd_end=msg.find("[S_")
                    cmd=buf[cmd_start:cmd_end+3]     
                    node_sn=cmd[12:24]   
                    node_fw=cmd[8:12]
                    logprint("node_sn"+node_sn+"node_fw"+node_fw+"nodeip"+str(node_ip ))
                    msg=createNewNode(node_sn,node_ip,node_fw)+"_#]"
                    connection.sendall("[S_ok...[S_")  
                    connection.close()   
                    #wait_because_node_is_talking=0        
                    break


                  if received_message.startswith("n_sync?") :                  
                    node_sn=re.search('sn=(.+?)&',received_message).group(1) 
                    node_fw=re.search('&fw=(.+?)_#',received_message).group(1) 
                    logprint("node_sn"+node_sn+"node_fw"+node_fw+"nodeip"+str(node_ip ))
                    connection.sendall('ok')  
                    connection.close()   
                    msg=createNewNode(node_sn,node_ip,node_fw)+"_#]" #i call createNewNode just to update the node ip ...
                    #wait_because_node_is_talking=0
                    break

                  connection.sendall(data) 
                  connection.close()
                  #wait_because_node_is_talking=0
                  break

              else:
                print('no more data from',client_address)
                connection.close()
                #wait_because_node_is_talking=0
                break
    
          
          except Exception as e  :
            message="error tcp connection"
            logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 


          finally:

            try:
              connection.close()
            except:
              logprint("connection not created2")



           
        try:
        # Clean up the connection, close() is always called, even in the event of an error.
          connection.close()
        except:
          logprint("connection not created3") 


    except Exception as e  :
      message="error tcp server thread"
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))

    finally:

      try:
        connection.close()
      except:
        logprint("connection not created 4")


def run_while_true(server_class=BaseHTTPServer.HTTPServer,
                   handler_class=RequestHandler):
    """
    This assumes that keep_running() is a function of no arguments which
    is tested initially and after each request.  If its return value
    is true, the server continues.
    """
    server_address = ('', gui_webserver_port)
    httpd = server_class(server_address, MyHandler)

    while exit==0:   #if exit ==1  then close the webserver

#main loop of the webserver
      #print "main webserver "

      try:
        httpd.handle_request() 
      except Exception as e:
        message="something went wrong on main Webserver handler "   
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))     

def main():
    global exit
    try:
        
        #server = HTTPServer(('', 80), MyHandler)
        logprint('started httpserver...')




        bus = threading.Thread(target=onosBusThread)
        bus.daemon = True  #make the thread a daemon thread
        bus.start()

        #w2 = threading.Thread(target=nodeTcpServer)
        #w2.daemon = True  #make the thread a daemon thread
        #w2.start()




        w1 = threading.Thread(target=hardwareHandlerThread)
        w1.daemon = True  #make the thread a daemon thread
        w1.start()

        run_while_true()



    except KeyboardInterrupt:
         #updateJson()
        logprint('^C received, shutting down server',verbose=7)

        hardware.close()
        exit=1
        server.socket.close()

if __name__ == '__main__':
    main()

