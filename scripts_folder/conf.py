
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
This module is used to import all the configurations from the saved files at the onos startup

"""



from globalVar import*
from web_object import *
import router_handler
import hw_node




global exit   #if exit ==1 all the program stop and exit
global object_dict
global zoneDict
global nodeDict
global hardwareModelDict
global scenarioDict


router_hardware=hardwareModelDict[router_hardware_type]   #router_hardware_type is in globalVar.py


hardware_labels=hardwareModelDict.keys()
#hardware_labels=["onosPlug6way","onosPlug2way","onosTsensorA","onosTsensorB","onosIRcmdAAA","onosProminiA"]

#router_sn is in globalVar.py


try:
  hardware=router_handler.RouterHandler(router_hardware,router_sn)
except Exception, e  :               
  print "error in the init of class router_handler  e:"+str(e.args)  
  errorQueue.put("error in the init of class router_handler  e:"+str(e.args) )


print "router hardware selected is"+router_hardware_type


def newDefaultWebObj(name):
  """
  Return a new web_object given only its name, used to create new web_objects for exemple when a new zone is created 
  """

  return(WebObject(name,"b",0,{u"0":"background-color:green;",u"1":"background-color:red;"},{u"0":name+u"=0",u"1":name+u"=1"},{}," ",[9999],9999,{}))


def newDefaultWebObjBody(name):
  """
  Return a new web_object given only its name, used to create the zone html body object  
  """

  return(WebObject(name,"b",0,{u"0":"background-color:#A9E2F3;",u"1":"background-color:#8181F7;"},{u"0":name+u"=0",u"1":name+u"=1"},{}," ",[9999],9999,{}))


def newNodeWebObj(name,objType,node_sn,pinList):
  """
  Return a new web_object given its name,objType,node_sn,pinList used to create new web_objects for exemple when a new node is added 
  """

  return(WebObject(name,objType,0,{u"0":"background-color:#A9E2F3;",u"1":"background-color:#8181F7;"},{u"0":name+u"=0",u"1":name+u"=1"},{}," ",pinList,node_sn,{}))



object_dict={} #object_dict  contain all the web_object  and the key of the dictionary for each web_object is the name of the web_object

objectList=[]
roomList=[]
zoneDict={}#dict where the key is the name from roomList and the value is a list of all the webobject names present in the room  


object_dict["minutes"]=newDefaultWebObj("minutes")
object_dict["hours"]=newDefaultWebObj("hours")
object_dict["day"]=newDefaultWebObj("day")
object_dict["month"]=newDefaultWebObj("month")
object_dict["year"]=newDefaultWebObj("year")
object_dict["dayTime"]=newDefaultWebObj("dayTime")  #hours of the day expressed in minutes








#base_cfg_path is in globalVar.py

def readDictionaryFromSavedFile(key):
  """
  Given a key it reads the value in the json dictionary from a file config_files/data.json saved on the storage memory 

 
  """
  print "readDictionaryFromSavedFile() executed to read: "+str(key)
  try:
    json_file = codecs.open(base_cfg_path+"config_files/data.json",'r',"utf8")
    readed_data = json_file.read()
    json_file.close() 
    readed_dict=json.loads(readed_data)
    value=readed_dict[key]
  except Exception, e: 
    print "error in readDictionaryFromSavedFile with key: "+str(key)+" e:"+str(e.args)
    errorQueue.put( "error in readDictionaryFromSavedFile with key: "+str(key)+" e:"+str(e.args)) 
    print "can't import data.json file , i will load the recovery one "
    readed_data=recoverydata_json  # is in globalVar.py
    readed_dict=json.loads(readed_data)
    value=readed_dict[key]

  return(value)






def readConfigurationsFromSavedFile(key):
  """
  Given a key it reads the value in the json dictionary from a file config_files/cfg.json saved on the storage memory 
 
  """

  print "readConfigurationsFromSavedFile() executed to read: "+str(key)
  try:
    cfg_json_file = codecs.open(base_cfg_path+"config_files/cfg.json",'r',"utf8")
    cfg_readed_data = cfg_json_file.read()
    cfg_json_file.close() 
    data=json.loads(cfg_readed_data)
    value=data[key] 
  except Exception, e: 
    print "error in readConfigurationsFromSavedFile with key: "+str(key)+" e:"+str(e.args)
    errorQueue.put( "error in readConfigurationsFromSavedFile with key: "+str(key)+" e:"+str(e.args))  
    print "can't import cfg.json file , i will load the recovery one "
    cfg_readed_data=recoverycfg_json # is in globalVar.py
    data=json.loads(cfg_readed_data)
    value=data[key]
  return(value)



def importConfig():

  """

  This function imports all the data and configurations from the files saved on storage memory.|br|
  The file are located in the config_files directory


  """

  global zoneDict
  global nodeDict
  global scenarioDict
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

  accept_only_from_white_list=readConfigurationsFromSavedFile(u"accept_only_from_white_list")  
  enable_mail_service=readConfigurationsFromSavedFile(u"enable_mail_service")  
  enable_mail_output_service=readConfigurationsFromSavedFile(u"enable_mail_output_service")
  logTimeout=readConfigurationsFromSavedFile(u"logTimeout")  
  login_required=readConfigurationsFromSavedFile(u"login_required")  
  mail_whiteList=readConfigurationsFromSavedFile(u"mail_whiteList")  
  online_server_enable=readConfigurationsFromSavedFile(u"online_server_enable")  
  online_usersDict.update(readConfigurationsFromSavedFile(u"online_usersDict"))  
  usersDict.update(online_usersDict)
  timezone=readConfigurationsFromSavedFile(u"timezone")  
  enable_onos_auto_update=readConfigurationsFromSavedFile(u"enable_onos_auto_update")  
  scenarios_enable=readConfigurationsFromSavedFile(u"scenarios_enable") 

  zoneDict.update(readDictionaryFromSavedFile(u"zoneDictionary"))
  scenarioDict.update(readDictionaryFromSavedFile(u"scenarioDictionary"))
  tmp_obj_dict=readDictionaryFromSavedFile(u"objectDictionary")

  conf_options={u"online_server_enable":online_server_enable,u"enable_mail_output_service":enable_mail_output_service,u"enable_mail_service":enable_mail_service,u"accept_only_from_white_list":accept_only_from_white_list,u"mail_whiteList":mail_whiteList,u"timezone":timezone,u"login_required":login_required,u"logTimeout":logTimeout,"online_usersDict":online_usersDict,"enable_onos_auto_update":enable_onos_auto_update,"scenarios_enable":scenarios_enable}

  for a in tmp_obj_dict.keys():  #for each object in the file
    object_html_name=a
    object_type=tmp_obj_dict[a][u"type"]
    object_start_status=tmp_obj_dict[a][u"status"]
    object_styleDict=tmp_obj_dict[a][u"styleDict"]
    object_style0=object_styleDict[u"0"]
    object_style1=object_styleDict[u"1"]
    object_htmlDict=tmp_obj_dict[a][u"htmlDict"]
    object_html0=object_htmlDict[u"0"]
    object_html1=object_htmlDict[u"1"]
    object_cmdDict= tmp_obj_dict[a][u"cmdDict"]
    object_command0=object_cmdDict[u"0"]
    object_command1=object_cmdDict[u"1"]
    object_init_command=object_cmdDict[u"s_cmd"]
    object_notes=tmp_obj_dict[a][u"notes"]
    object_hardware_pins=tmp_obj_dict[a][u"pins"]
    object_node_serial_number=tmp_obj_dict[a][u"node_sn"]
    object_scenarios=tmp_obj_dict[a][u"scenarios"]
    object_priority=tmp_obj_dict[a][u"priority"]
    object_permission=tmp_obj_dict[a][u"perm"]
    object_owner=tmp_obj_dict[a][u"own"]
    object_group=tmp_obj_dict[a][u"grp"]
    object_mail_report_list=tmp_obj_dict[a][u"mail_l"]


    if (object_start_status=="inactive"):  #prevent the node to been setted as inactive
      object_start_status=0       

    objectList.append(WebObject(object_html_name,object_type,object_start_status,object_styleDict,object_htmlDict,object_cmdDict,object_notes,object_hardware_pins,object_node_serial_number,{u"scenarios":object_scenarios,u"priority":object_priority,u"perm":object_permission,u"own":object_owner,u"grp":object_group,u"mail_l":object_mail_report_list}))
    #create a new webobject with the data collected from the file and append it to objectList



  tmp_node_dict=readDictionaryFromSavedFile(u"nodeDictionary")
  for a in tmp_node_dict.keys():  #for each node in the file
    node_serial_number=tmp_node_dict[a][u"node_serial_number"]
    node_type=tmp_node_dict[a][u"hwModelName"]
    #node_sn=tmp_node_dict[a]["node_serial_number"]
    node_address=tmp_node_dict[a][u"nodeAddress"]   
    hardware_node_type=hardwareModelDict[node_type]
    nodeDict[node_serial_number]=hw_node.HwNode(node_serial_number,hardware_node_type,node_address,router_hardware_fw_version) 
    if nodeDict[node_serial_number].getNodeTimeout()!="never":
      nodeDict[node_serial_number].setNodeActivity(0)  #set the node as inactive at startup if there is a getNodeTimeout for the node


  #ricreate the nodeDict from the json backup
  #note that the io config will be done in webserver.py where i add the objectList elements to object_dict






importConfig()

object_dict["onosCenterWifi"]=newDefaultWebObj("onosCenterWifi")  #turn on or off wifi
#object_dict["wifi0_Plug6way0001"]=newDefaultWebObj("wifi0_Plug6way0001")  #turn on or off wifi
object_dict["onosCenterWifi"].setCommand0("uci set wireless.radio0.disabled=1&uci commit wireless && wifi")
object_dict["onosCenterWifi"].setCommand1("uci set wireless.radio0.disabled=0&uci commit wireless && wifi")

object_dict["counter1"]=newDefaultWebObj("counter1")  #count

#zoneDict[router_sn]["objects"].append("OnosCenterWifi")





