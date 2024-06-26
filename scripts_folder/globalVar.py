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
  This module is imported from all the others and it stores the global variables and some global functions.


"""

import Queue
import datetime
import string, cgi
import time
import codecs  # to save and open utf8 files
import socket
from signal import signal, SIGPIPE, SIG_DFL  # to prevent [Errno 32] Broken pipe
import unicodedata
import sys
import subprocess
from os import curdir, sep
import shutil

import BaseHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from time import gmtime, strftime

import json
import os
import commands
import syslog
# import urllib2,urllib
import urllib2
# import httplib
import thread
import threading
import os.path
import random
import binascii  # used by weobject class for the permission
import re  # regular expression
import smtplib   # used by mail_agent to send mail
import platform
import csv # used to write csv

# Add vendor directory to module search path
lib_dir = os.path.join('external_libraries')
sys.path.append(lib_dir)
# Now you can import any library located in the "external_libraries" folder!

lib_dir2 = os.path.join('gui')
sys.path.append(lib_dir2)

import urllib3
from urllib3 import PoolManager ,Timeout
# use example urllib3
# url_request_manager = PoolManager(10)
# url_request_manager=PoolManager(10)
# r = url_request_manager.request('GET', 'http://example.com')
# or
# r=url_request_manager.request_encode_body('POST','url',fields,timeout=Timeout(total=5.0))
# print r.data
#
# r = url_request_manager.request('GET', 'http://example.com:80',timeout=Timeout(total=5.0))

url_request_manager = PoolManager(8)


exit=0
debug=2  # debug mode , if set to 1  the debug mode is on if setted to 2 the debug is medium
objectDict={}  # objectDict  contain all the web_object  and the key of the dictionary for each web_object is the name of the web_object
zoneDict={}  # dict where the key is the name from roomList and the value is a list of all the webobject names present in the room
router_hardware={}
scenarioDict={}


timezone="CET-1CEST,M3.5.0,M10.5.0/3"  #will be overwritten by /scripts_folder/config_files/cf.json
os.environ['TZ']=timezone
try:
    time.tzset()
except Exception as e:
    print("tzset not present , timezone will work anyway")
    pass
# time_gap=120    #minutes of difference between utc and local time
# export TZ="CET-1CEST,M3.5.0,M10.5.0/3"



user_active_time_dict={}
login_required=1  # if setted to 1 enable the webpage login  and allow only logged user to use onos,overwritten by /scripts_folder/config_files/cfg.json
logTimeout=15 # minutes of user inactivity before logout , will be overwritten by /scripts_folder/config_files/cf.json

log_name="file.log"
error_log_name="erros.log"
log_enable=0   # enable the log file size check ,not implemented...
check_log_len_time=datetime.datetime.today().minute
mail_error_log_enable=1  # enable onos to send mail when an error happens
mail_verbose_level=5 # the error must have a greater verbose level than mail_verbose_level to be sent via mail
error_log_mail_frequency=30  # seconds between a error check and another
last_error_check_time=0
mail_where_to_send_errors="electronicflame@gmail.com"

hardwareModelDict={}

# read_onos_sensor_enabled=1
enable_csv_log=1 # enable the csv logging of the objects status(to log a object also the enable_logging of that object must be=1

enable_usb_serial_port=1 # if setted to 0 disable usb serial port also if supported by the hardware in hardwareModelDict[]
enable_onosCenter_hw_pins=0  # enable the use of onosCenter local hw pins
reconnect_serial_port_enable=0  # this will be equal to time.time() when the serial port has to be reconnected
router_sn="RouterOP0000"
uart_router_sn=""  # the sn of the node connected to the usb of the pc where onos is run..
router_hardware_type="RouterOP" # select the type of hardware
router_hardware_fw_version="5.32"
gui_webserver_port=80
service_webserver_port=81
onos_center_internal_ip='192.168.101.1'  # the ip of the lan , the one where all nodes are attached
service_webserver_delay=1 # seconds of delay between each answer
node_webserver_port=9000   # the web server port used on remote nodes
router_read_pin_frequency=20  #seconds between a pin read in the router hardware
last_pin_read_time=0


platform=platform.node()
base_cfg_path=""

# if (os.path.exists("/sys/class/gpio")==1) : #if the directory exist ,then the hardware has embedded IO pins
if (platform.find("Orange")!=-1)or(platform.find("orange")!=-1)or(platform.find("RouterOP")!=-1): #found uname with orange pi name or RouterOP
    router_sn=platform[0:12]  # get the serial number from /etc/hostname  
    router_hardware_type="RouterOP"
    enable_usb_serial_port=1
    base_cfg_path="/bin/onos/scripts_folder/"
    baseRoomPath="/bin/onos/scripts_folder/zones/"
    
elif (platform.find("raspberry")!=-1)or(platform.find("raspberry")!=-1)or(platform.find("RouterOP")!=-1): #found uname with orange pi name or RouterOP
    router_sn=platform[0:12]  # get the serial number from /etc/hostname  
    router_hardware_type="RouterOP"
    enable_usb_serial_port=1
    base_cfg_path="/bin/onos/scripts_folder/"
    baseRoomPath="/bin/onos/scripts_folder/zones/"

else: # disable serial port
    router_sn=platform[0:12]  # get the serial number from /etc/hostname  
    router_hardware_type="RouterPC"
    enable_usb_serial_port=0
    base_cfg_path=""
    baseRoomPath=os.getcwd()+"/zones/"    # you musn't have spaces on the path..






csv_folder=base_cfg_path+'csv/'

accept_only_from_white_list=0  # if set to 1 the onos cmd will be accepted only from mail in white list
# will be overwritten by /scripts_folder/config_files/cf.json

mail_whiteList=[]  # will be overwritten by /scripts_folder/config_files/cf.json
mail_whiteList.append("elettronicaopensource@gmail.com")
mail_whiteList.append("electronicflame@gmail.com")

enable_mail_service=1  # active mailCheckThread   will be overwritten by /scripts_folder/config_files/cf.json
enable_mail_output_service=1 #activate the sending of mails from onos  will be overwritten by /scripts_folder/config_files/cf.json
last_mail_sync_time=0  
mailCheckThreadIsrunning=0 # tell onos if the mail thread is alredy running
mail_service=0
mail_check_frequency=10  # seconds between 2 checks
mailOutputHandler_is_running=0  # tell onos if the thread is already running
mail_retry_timeout=120  # seconds between retry after error in sending mail




last_internet_check=0  # the last time the internet connection was checked
enable_onos_auto_update="yes" # possible value: "yes","no","ask_me"  # banana ask_me not implemented yet
scenarios_enable=1  # tell onos if it have to check the scenarios or not. warning overwritten by scenarios_enable in cfg.json
online_server_enable=0  # enable the remote online server to controll onos from internet without opening the router ports
# will be overwritten by /scripts_folder/config_files/cf.json
enable_mqtt = 0 #tell onos to enable mqtt or not, warning overwritten by scenarios_enable in cfg.json


last_server_sync_time=0
onlineServerSyncThreadIsrunning=0 #tell onos if the thread is running
online_server_delay=3  # 3  #seconds between each online server query
online_object_dict=[]   # online object dict ,used to know if an update of the dict is needed
online_zone_dict=[]   # online zone dict ,used to know if an update of the dict is needed
if online_server_enable==1 :
    force_online_sync_users=1    # used to know if an update of the dict is required
else:
    force_online_sync_users=0    # used to know if an update of the dict is required
online_usersDict={}
online_first_contact=1  # tell if is the first contact between this router and the online server
onos_online_key=router_sn  # unique key used by the router to login on the online server 
onos_online_password="qwerty"  # password used by the router to login on the online server 
onos_online_site_url="https://myonos.com/onos/"  # remote online server url (where the php onos scripts are located)

internet_connection=0  # tell onos if there is internet connection, do not change it..onos will change it if there is internet

serial_answer_readyQueue=Queue.Queue()  # used in arduinoserial

queryToNetworkNodeQueue=Queue.Queue()

queryToRadioNodeQueue=Queue.PriorityQueue()

node_query_network_threads_executing=0

node_query_radio_threads_executing=0

max_number_of_node_query_network_threads_executing=1 # tells onos the maximun number of thread it can executes to handle network node queries

layerExchangeDataQueue = Queue.Queue()  # this queue will contain all the dictionaries to pass data from the hardware layer to the webserver layer   router_handler.py will pass trought this queue all the change of hardware status to the webserver.py


priorityCmdQueue=Queue.Queue()  # this queue will contain all the command received from the web gui...those will have priority over the one contained in layerExchangeDataQueue 


mailQueue=Queue.Queue()  # this queue will contain all the mail to send , onos will send them as soon as possible

errorQueue=Queue.Queue()  # this queue will contain all the error happened

lock_bash_cmd= threading.Lock()

lock_serial_input=threading.Lock()




lock1_current_node_handler_dict= threading.Lock()  # lock to access current_node_handler_list
# lock2_query_threads = threading.Lock()  #lock to access query_to_nodeDict{}
# wait_because_node_is_talking=0

current_node_handler_dict={}   # dictionary containing all the node_serial_number of the nodes that are being queried
query_to_node_dict={} # this dictionary will  have the node_serial_number as key and will contain a list of dictionaries 
# example :   query_to_node_dict={'Plug6way0001':[{"address":address,"query":query,"objName":objName,"status_to_set":status_to_set,"user":user,"priority":priority,"mail_report_list":mail_report_list]}
# to access it:  query_to_node_dict['Plug6way0001'][0]["address"]  to get the  first address  



if (enable_mail_service==1)or(enable_mail_output_service==1): 
    import imaplib   # used by mail_agent 
    import email     # used by mail_agent 
    # imaplib.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # see https://aboutsimon.com/index.html%3Fp=85.html  


recoverycfg_json='''
{
  "conf_options_dictionary": {
    "accept_only_from_white_list": 0, 
    "enable_mail_output_service": 1, 
    "enable_mail_service": 0, 
    "enable_onos_auto_update": "yes", 
    "logTimeout": 15, 
    "login_required": 0, 
    "mail_whiteList": [], 
    "node_password_dict": {
      "Sonoff1P0000": "onosBestHome9999", 
      "Sonoff1P0001": "onosBestHome9999", 
      "Sonoff1P0002": "onosBestHome9999"
    }, 
    "online_server_enable": 0, 
    "online_usersDict": {
      "'''+router_sn+'''": {
        "mail_control_password": "'''+onos_online_password+'''", 
        "priority": 0, 
        "pw": "'''+onos_online_password+'''", 
        "user_mail": "elettronicaopensource@gmail.com"
      }
    }, 
    "scenarios_enable": 0, 
    "timezone": "CET-1CEST,M3.5.0,M10.5.0/3"
  }
}

'''






#banana to make a default json without all this data
recoverydata_json=''' 
{
  "dictionaries": {
    "nodeDictionary": {
      "RouterOP0000": {
        "hwModelName": "RouterOP", 
        "nodeAddress": "0", 
        "nodeObjectsDict": {}, 
        "node_serial_number": "RouterOP0000"
      }
    }, 
    "objectDictionary": {
      "day": {
        "cmdDict": {
          "0": "", 
          "1": "", 
          "s_cmd": ""
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "day=0", 
          "1": "day=1", 
          "onoswait": "dayWAIT"
        }, 
        "mail_l": [], 
        "node_sn": 9999, 
        "notes": " ", 
        "objname": "day", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [
          9999
        ], 
        "priority": 0, 
        "scenarios": [], 
        "status": 22, 
        "styleDict": {
          "0": "background-color:green;", 
          "1": "background-color:red;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "b"
      }, 
      "dayTime": {
        "cmdDict": {
          "0": "", 
          "1": "", 
          "s_cmd": ""
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "dayTime=0", 
          "1": "dayTime=1", 
          "onoswait": "dayTimeWAIT"
        }, 
        "mail_l": [], 
        "node_sn": 9999, 
        "notes": " ", 
        "objname": "dayTime", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [
          9999
        ], 
        "priority": 0, 
        "scenarios": [], 
        "status": 882, 
        "styleDict": {
          "0": "background-color:green;", 
          "1": "background-color:red;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "b"
      }, 
      "hours": {
        "cmdDict": {
          "0": "", 
          "1": "", 
          "s_cmd": ""
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "hours=0", 
          "1": "hours=1", 
          "onoswait": "hoursWAIT"
        }, 
        "mail_l": [], 
        "node_sn": 9999, 
        "notes": " ", 
        "objname": "hours", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [
          9999
        ], 
        "priority": 0, 
        "scenarios": [], 
        "status": 14, 
        "styleDict": {
          "0": "background-color:green;", 
          "1": "background-color:red;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "b"
      }, 
      "minutes": {
        "cmdDict": {
          "0": "", 
          "1": "", 
          "s_cmd": ""
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "minutes=0", 
          "1": "minutes=1", 
          "onoswait": "minutesWAIT"
        }, 
        "mail_l": [], 
        "node_sn": 9999, 
        "notes": " ", 
        "objname": "minutes", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [
          9999
        ], 
        "priority": 0, 
        "scenarios": [], 
        "status": 42, 
        "styleDict": {
          "0": "background-color:green;", 
          "1": "background-color:red;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "b"
      }, 
      "month": {
        "cmdDict": {
          "0": "", 
          "1": "", 
          "s_cmd": ""
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "month=0", 
          "1": "month=1", 
          "onoswait": "monthWAIT"
        }, 
        "mail_l": [], 
        "node_sn": 9999, 
        "notes": " ", 
        "objname": "month", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [
          9999
        ], 
        "priority": 0, 
        "scenarios": [], 
        "status": 10, 
        "styleDict": {
          "0": "background-color:green;", 
          "1": "background-color:red;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "b"
      }, 
      "onosCenterWifi": {
        "cmdDict": {
          "0": "systemctl stop create_ap", 
          "1": "systemctl start create_ap", 
          "s_cmd": "systemctl start create_ap"
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "onosCenterWifi=0", 
          "1": "onosCenterWifi=1", 
          "onoswait": "onosCenterWifiWAIT"
        }, 
        "mail_l": [], 
        "node_sn": "RouterOP0000", 
        "notes": " ", 
        "objname": "onosCenterWifi", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [], 
        "priority": 0, 
        "scenarios": [], 
        "status": "0", 
        "styleDict": {
          "0": "background-color:#A9E2F3;", 
          "1": "background-color:#8181F7;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "digital_obj_out"
      }, 
      "year": {
        "cmdDict": {
          "0": "", 
          "1": "", 
          "s_cmd": ""
        }, 
        "enable_logging": 0, 
        "grp": [
          "web_interface", 
          "onos_mail_guest"
        ], 
        "htmlDict": {
          "0": "year=0", 
          "1": "year=1", 
          "onoswait": "yearWAIT"
        }, 
        "mail_l": [], 
        "node_sn": 9999, 
        "notes": " ", 
        "objname": "year", 
        "own": "onos_admin", 
        "perm": "111111111", 
        "pins": [
          9999
        ], 
        "priority": 0, 
        "scenarios": [], 
        "status": 2017, 
        "styleDict": {
          "0": "background-color:green;", 
          "1": "background-color:red;", 
          "default_s": "background-color:red ;color black", 
          "onoswait": "background-color:grey ;color black"
        }, 
        "type": "b"
      }
    }, 
    "scenarioDictionary": {}, 
    "zoneDictionary": {
      "RouterOP0000": {
        "group": [], 
        "hidden": 0, 
        "objects": [
          "onosCenterWifi"
        ], 
        "order": 0, 
        "owner": "onos_sys", 
        "permissions": "777"
      }
    }
  }
}
'''



#scenarioDict["scenario1"]={"enabled":1,"one_time_shot":1,"autodelete":0,"actType":"delay","conditions":"#_dayTime_#>0","functionsToRun":["socket0_RouterGL0001=1"],"afterDelayFunctionsToRun":["button0_RouterGL0001=1"],"delayTime":1,"priority":0}


#scenarioDict["scenario2"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"#_dayTime_#>0","functionsToRun":["onosCenterWifi=0],"priority":0}

#scenarioDict["scenario3"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==12)&(#_minutes_#==0)","functionsToRun":["onosCenterWifi=1"],"priority":0}



#banana to remove
#scenarioDict["scenario2"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==8)&(#_minutes_#==0)","functionsToRun":["button0_RouterGL0000=1","Wifi_netgear==1","Caldaia=0"],"priority":0}

#scenarioDict["scenario3"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==8)&(#_minutes_#==25)","functionsToRun":["button0_RouterGL0000=0","Wifi_netgear==0"],"priority":0}



#scenarioDict["scenario4"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==12)&(#_minutes_#==30)","functionsToRun":["button0_RouterGL0000=1","Wifi_netgear==1"],"priority":0}



#scenarioDict["scenario5"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==14)&(#_minutes_#==0)","functionsToRun":["button0_RouterGL0000=0","Wifi_netgear==0"],"priority":0}



#scenarioDict["scenario6"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==18)&(#_minutes_#==0)","functionsToRun":["button0_RouterGL0000=1","Wifi_netgear==1"],"priority":0}


#scenarioDict["scenario7"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==0)&(#_minutes_#==0)","functionsToRun":["button0_RouterGL0000=0","Wifi_netgear==0","counter1=0"],"priority":0}


#scenarioDict["scenario8"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_minutes_#>-1)","functionsToRun":["wifi0_Plug6way0001=!#_wifi0_Plug6way0001_#","button1_RouterGL0000==!#_wifi0_Plug6way0001_#"],"priority":0}

#scenarioDict["scenario9"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"1","functionsToRun":["counter1=#_counter1_#+1"],"priority":0}


#scenarioDict["scenario10"]={"enabled":1,"one_time_shot":0,"autodelete":0,"actType":"nodelay","conditions":"(#_hours_#==23)&(#_minutes_#==0)","functionsToRun":["Caldaia=0"],"priority":0}











nodeDict={}

node_used_addresses_list=[0, 1, 2]   #list of free node addresses from 2 to 254
usersDict={}
usersDict["onos_mail_guest"]={"pw":"onos", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com"}
usersDict["web_interface"]={"pw":"onos", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com"}
usersDict["scenario"]={"pw":"onos", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com"}
usersDict["onos_node"]={"pw":"onos", "mail_control_password":"onosm", "priority":99, "user_mail":"elettronicaopensource@gmail.com"}
usersDict["onos_node_reconnect"]={"pw":"onos", "mail_control_password":"onosm", "priority":99, "user_mail":"elettronicaopensource@gmail.com"}
usersDict["marco"]={"pw":"1234", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com", "advanced_settings":1}
usersDict["casa"]={"pw":"1234", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com", "advanced_settings":1}
#usersDict["mauro"]={"pw":"12345678","mail_control_password":"onosm","priority":0,"user_mail":"elettronicaopensource@gmail.com"}





online_usersDict["marco"]={"pw":"1234", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com"}

online_usersDict["casa"]={"pw":"1234", "mail_control_password":"onosm", "priority":0, "user_mail":"elettronicaopensource@gmail.com"}


usersDict.update(online_usersDict) #insert the online users in the local dictionary

node_password_dict={} # dictionary where the key is the node_serial_number and the value is the node password

onos_mail_conf={"mail_account":"onos.beta@gmail.com","pw":"gmailbeta1234","smtp_port":"587","smtp_server":"smtp.gmail.com","mail_imap":"imap.gmail.com"}

#onos_mail_conf={"mail_account":"onos.beta@yahoo.com", "pw":"mailbeta1234", "smtp_port":"587", "smtp_server":"smtp.mail.yahoo.com", "mail_imap":"imap.mail.yahoo.com"}


#gmail problem solving:


#This worked for me.

#1) Login to your gmail account.

#2) Go to https://www.google.com/settings/security/lesssecureapps and Turn On this feature.

#3) Go to https://accounts.google.com/DisplayUnlockCaptcha and click Continue.

#Then you can authenticate your Additional Email Address from your Gmail Account.





conf_options={u"online_server_enable":online_server_enable, u"enable_mail_output_service":enable_mail_output_service, u"enable_mail_service":enable_mail_service, u"accept_only_from_white_list":accept_only_from_white_list, u"mail_whiteList":mail_whiteList, u"timezone":timezone, u"login_required":login_required, u"logTimeout":logTimeout, "node_password_dict":node_password_dict, "online_usersDict":online_usersDict, "enable_onos_auto_update":enable_onos_auto_update, "scenarios_enable":scenarios_enable, "enable_mqtt":enable_mqtt}

#localhost/setup/node_manager/RouterGL0001


hardwareModelDict["RouterOP"]={"hwName":"RouterOP", "max_pin":5, "hardware_type":"gl.inet_only","hw_communication_type":"rfm69", "pin_mode":{}, "parameters":{}, "timeout":"never"}
hardwareModelDict["RouterOP"]["pin_mode"]["digital_input"]={}
hardwareModelDict["RouterOP"]["parameters"]["bash_pin_enable"]=1
hardwareModelDict["RouterOP"]["parameters"]["serial_port_enable"]=1  #not yet implemented
hardwareModelDict["RouterOP"]["object_list"]= {}
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]={}
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]={}
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]["object_numbers"]=[0]   #
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]["bash_cmd"]={}
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]["bash_cmd"]["0"]="ifdown wlan1"
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]["bash_cmd"]["1"]="ifup wlan1"
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]["bash_cmd"]["s_cmd"]="ifup wlan1"
hardwareModelDict["RouterOP"]["object_list"]["digital_obj_out"]["onosCenterWifi"]["options"]=["no_write_to_hw"]

hardwareModelDict["RouterPC"]={"hwName":"RouterPC", "max_pin":0, "hardware_type":"pc","hw_communication_type":"rfm69", "pin_mode":{}, "parameters":{}, "timeout":"never"}
hardwareModelDict["RouterPC"]["parameters"]["bash_pin_enable"]=1
hardwareModelDict["RouterPC"]["parameters"]["serial_port_enable"]=1   #not yet implemented

hardwareModelDict["ProminiS"]={"hwName":"ProminiS", "max_pin":13, "hardware_type":"arduino2009_serial","hw_communication_type":"rfm69", "pin_mode":{}, "timeout":360}
hardwareModelDict["ProminiS"]["pin_mode"]["sr_relay"]={"socket":[(20, 19)]}
hardwareModelDict["ProminiS"]["pin_mode"]["digital_input"]={"d_sensor":[(21)]}
hardwareModelDict["ProminiS"]["pin_mode"]["digital_output"]={"button":[(5), (6)]}


hardwareModelDict["ProminiA"]={"hwName":"ProminiA", "max_pin":18, "hardware_type":"arduino_promini","hw_communication_type":"rfm69", "pin_mode":{}, "parameters":{}, "timeout":"never"}
hardwareModelDict["ProminiA"]["pin_mode"]["digital_input"]={"d_sensor":[(2), (3), (4)]}
hardwareModelDict["ProminiA"]["pin_mode"]["digital_output"]={"button":[(6), (7), (8)]}
hardwareModelDict["ProminiA"]["pin_mode"]["analog_input"]={"a_sensor":[(14), (15), (16), (17), (18), (19)]}
hardwareModelDict["ProminiA"]["pin_mode"]["servo_output"]={"servo":[(5)]}
#hardwareModelDict["ProminiA"]["pin_mode"]["analog_output"]={"a_out":[(9)]}

hardwareModelDict["Plug6way"]={"hwName":"Plug6way", "max_pin":18, "hardware_type":"arduino_promini","hw_communication_type":"rfm69", "pin_mode":{}, "parameters":{}, "timeout":90}
hardwareModelDict["Plug6way"]["pin_mode"]["sr_relay"]={"socket":[(2, 3), (4, 5), (6, 7), (8, 9), (14, 15)], "wifi":[(16, 17)]}

hardwareModelDict["WLightSS"]={"hwName":"WLightSS", "max_pin":13, "hardware_type":"arduino2009_serial","hw_communication_type":"rfm69", "pin_mode":{}, "parameters":{}, "timeout":360}
hardwareModelDict["WLightSS"]["pin_mode"]["sr_relay"]={"socket":[(7, 8)]}
hardwareModelDict["WLightSS"]["pin_mode"]["digital_output"]={"button":[(5), (6)]}


#hardwareModelDict["WLightSA"]={"hwName":"WLightSA", "max_pin":13, "hardware_type":"arduino2009_serial", "pin_mode":{}, "parameters":{}, "query":{}, "timeout":360}
#hardwareModelDict["WLightSA"]["pin_mode"]["digital_obj_out"]={"lamp":[(5, 6)]}
#hardwareModelDict["WLightSA"]["pin_mode"]["analog_input"]={"luminosity":[(14)], "temperature":[(15)]}
#hardwareModelDict["WLightSA"]["pin_mode"]["cfg_obj"]={"lux_threshold":[(-1)], "timeout_to_turn_off":[(-1)]}#this have no pins..
#hardwareModelDict["WLightSA"]["query"]["digital_obj_out"]={"lamp":"wl#_objnumber_##_valuelen:1_#"}  #define the base query for this
#hardwareModelDict["WLightSA"]["query"]["cfg_obj"]={"lux_threshold":"lt#_valuelen:3_#", "timeout_to_turn_off":"to#_valuelen:4_#" }  #define the base query for this
                   
hardwareModelDict["WPlug1vx"]={"hwName":"WPlug1vx", "max_pin":13, "hardware_type":"arduino_promini","hw_communication_type":"rfm69", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":360}
hardwareModelDict["WPlug1vx"]["object_list"]["digital_obj_out"]={}
hardwareModelDict["WPlug1vx"]["object_list"]["digital_obj_out"]["presa"]={}
hardwareModelDict["WPlug1vx"]["object_list"]["digital_obj_out"]["presa"]["object_numbers"]=[0]   #
hardwareModelDict["WPlug1vx"]["object_list"]["digital_obj_out"]["presa"]["query"]="d#_objnumber_##_valuelen:1_#"


#deprecated ..
#hardwareModelDict["WPlugAvx"]["query"]["digital_obj_out"]={"plug":"wb#_objnumber_##_valuelen:1_#","plug2":"wb#_objnumber_##_valuelen:1_#"}  #define the base query for this node digital_obj_out..so onos will write for example: [S_001wp01x_#] , valuelen:1  means that this part will be replaced with a single character('0' or '1' since is digital_obj_out)  , the starting [S_001  and the ending _#]  will be added in router_handler.py at the end of the message a '\n' will be added anyway , all this is handled in router_hadler.py composeChangeNodeOutputPinStatusQuery()



hardwareModelDict["Wrelay4x"]={"hwName":"Wrelay4x", "max_pin":13, "hardware_type":"arduino_promini","hw_communication_type":"rfm69", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":360}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["caldaia"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["caldaia"]["object_numbers"]=[0]   #
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["caldaia"]["query"]="d#_objnumber_##_valuelen:1_#"
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["router"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["router"]["object_numbers"]=[1]   #
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["router"]["query"]="d#_objnumber_##_valuelen:1_#"
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["object_numbers"]=[2]#see arduino code at :"define object numbers to use in the pin configuration"
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["query"]="d#_objnumber_##_valuelen:1_#"
#hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay"]["mqtt_topic"]="Wrelay4x/relay#_objnumber_##_valuelen:1_#/status"
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay2"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay2"]["object_numbers"]=[3]   #
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["relay2"]["query"]="d#_objnumber_##_valuelen:1_#"

hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["led"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["led"]["object_numbers"]=[5]   #
hardwareModelDict["Wrelay4x"]["object_list"]["digital_obj_out"]["led"]["query"]="d#_objnumber_##_valuelen:1_#"


hardwareModelDict["Wrelay4x"]["object_list"]["cfg_obj"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["cfg_obj"]["syncTime"]={}
hardwareModelDict["Wrelay4x"]["object_list"]["cfg_obj"]["syncTime"]["object_numbers"]=[6]
hardwareModelDict["Wrelay4x"]["object_list"]["cfg_obj"]["syncTime"]["query"]="C#_objnumber_##_valuelen:3_#"


 #define the base query for this node digital_obj..so onos will write for example: [S_01d001x_#] , valuelen:1  means that this part will be replaced with a single character('0' or '1' since is digital_obj)  , the starting [S_01  and the ending _#]  will be added in router_handler.py at the end of the message a '\n' will be added anyway , all this is handled in router_hadler.py composeChangeNodeOutputPinStatusQuery()


hardwareModelDict["WreedSaa"]={"hwName":"WreedSaa", "max_pin":13, "hardware_type":"arduino_promini","hw_communication_type":"rfm69", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":360}
hardwareModelDict["WreedSaa"]["parameters"]={}
hardwareModelDict["WreedSaa"]["parameters"]["battery_node"]=1
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_in"]={}
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_in"]["reed1"]={}
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_in"]["reed1"]["object_numbers"]=[0]

# object 1 is hardware button but I don't have to show it on html
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]={}
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]["led"]={}
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]["led"]["object_numbers"]=[2] 
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]["led"]["query"]="d#_objnumber_##_valuelen:1_#"

hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]={}
hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]["tempSensor"]={}
hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]["tempSensor"]["object_numbers"]=[3]

hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]["luminosity_sensor"]={}
hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]["luminosity_sensor"]["object_numbers"]=[10] 

hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]["battery_state"]={}
hardwareModelDict["WreedSaa"]["object_list"]["analog_obj_in"]["battery_state"]["object_numbers"]=[9] 
# "analog_input" don't need the query part because is only a input and not an output..

hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]["digOut"]={}
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]["digOut"]["object_numbers"]=[4]
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_out"]["digOut"]["query"]="d#_objnumber_##_valuelen:1_#"

hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_in"]["reed2"]={}
hardwareModelDict["WreedSaa"]["object_list"]["digital_obj_in"]["reed2"]["object_numbers"]=[5]

hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]={}
hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["syncTime"]={}
hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["syncTime"]["object_numbers"]=[6]  

hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["reed1Logic"]={}
hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["reed1Logic"]["object_numbers"]=[7] 
hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["reed1Logic"]["query"]="c#_objnumber_##_valuelen:1_#"

hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["reed2Logic"]={}
hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["reed2Logic"]["object_numbers"]=[8] 
hardwareModelDict["WreedSaa"]["object_list"]["cfg_obj"]["reed2Logic"]["query"]="c#_objnumber_##_valuelen:1_#"



hardwareModelDict["Sonoff1P"]={"hwName":"Sonoff1P", "max_pin":13, "hardware_type":"sonoff_single_plug","hw_communication_type":"wifi_tasmota", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":360} #  360 seconds of timeout
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]={}
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]={}
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["object_numbers"]=[0] # see arduino code at :"define object numbers to use in the pin configuration"
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["begin_connection_query"]="""http://#_node_address_#/cm?cmnd=LedState%201""" # todo to implement it..this query will be sent the first time a this object is connected..
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["query"]="http://#_node_address_#/cm?user=admin&password=#_node_password_#&cmnd=Power%20#_objnumber_##_valuelen:1_#"  # http://192.168.1.6/cm?cmnd=Power%2000   and http://192.168.1.6/cm?cmnd=Power%2001
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["query_expected_answer"]={}
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["query_expected_answer"][0]="""RESULT = {"POWER":"OFF"}"""
hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["query_expected_answer"][1]="""RESULT = {"POWER":"ON"}"""
hardwareModelDict["Sonoff1P"]["object_list"]["cfg_obj"]={}
hardwareModelDict["Sonoff1P"]["parameters"]["password"]="onosBestHome9999"
#hardwareModelDict["Sonoff1P"]["object_list"]["digital_obj_out"]["relay"]["mqtt_topic"]="Wrelay4x/relay#_objnumber_##_valuelen:1_#/status"



#hardwareModelDict["WPlugAvx"]={"hwName":"WPlugAvx","max_pin":13,"hardware_type":"arduino_promini","pin_mode":{},"parameters":{},"query":{},"timeout":360}
#hardwareModelDict["WPlugAvx"]["pin_mode"]["digital_obj_out"]={"plug":[(0)],"plug2":[(1)]}#  one object with a double set reset relay, is the obj0
#hardwareModelDict["WPlugAvx"]["pin_mode"]["digital_output"]={"button":[(5),(6)]}
#hardwareModelDict["WPlugAvx"]["query"]["digital_obj_out"]={"plug":"wb#_objnumber_##_valuelen:1_#","plug2":"wb#_objnumber_##_valuelen:1_#"}  #define the base query for this node digital_obj..so onos will write for example: [S_001wp01x_#] , valuelen:1  means that this part will be replaced with a single character('0' or '1' since is digital_obj)  , the starting [S_001  and the ending _#]  will be added in router_handler.py at the end of the message a '\n' will be added anyway.







# note that in the format ["analog_output"]={"a_out":[(11),(10)]}  
# "a_out" is only the the html name that onos will add to the webobject name
# so the final webobject name will be for example a_out0_ProminiA0001  
# the web object type will be "analog_output"

# if the type of "pin_mode" is digital_obj then the structure must be :{"plug":[(0)],"plug2":[(1)]}   with a custom name for each object,  if you have to do more than one object of the same type write progressive names..like: {"plug01":[(0)],"plug02":[(1)]}
# in the digital_obj case the number zero here [(0)] indicates the number of the object in the arduino node software make sure to don't repeat numbers there.



#Wpcountx is a node with: 2 current sensors 2 relay and a led
hardwareModelDict["Wpcountx"]={"hwName":"Wpcountx", "max_pin":13, "hardware_type":"arduino_promini","hw_communication_type":"rfm69", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":360}
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]={}
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay0"]={}
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay0"]["object_numbers"]=[0]
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay0"]["query"]="d#_objnumber_##_valuelen:1_#"
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay1"]={}
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay1"]["object_numbers"]=[1]
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay1"]["query"]="d#_objnumber_##_valuelen:1_#"
#hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["relay"]["mqtt_topic"]="Wrelay4x/relay#_objnumber_##_valuelen:1_#/status"
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["led"]={}
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["led"]["object_numbers"]=[2]
hardwareModelDict["Wpcountx"]["object_list"]["digital_obj_out"]["led"]["query"]="d#_objnumber_##_valuelen:1_#"

hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]={}
hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours0_live"]={}
hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours0_live"]["object_numbers"]=[3]

hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours1_live"]={}
hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours1_live"]["object_numbers"]=[4]

hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]={}
hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]["Whours0_total"]={}
hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]["Whours0_total"]["object_numbers"]=[5]
hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]["Whours0_total"]["query"]="d#_objnumber_##_valuelen:1_#"

hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]["Whours1_total"]={}
hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]["Whours1_total"]["object_numbers"]=[6]
hardwareModelDict["Wpcountx"]["object_list"]["incremental_numeric_var"]["Whours1_total"]["query"]="d#_objnumber_##_valuelen:1_#"

hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours_live_diff"]={} #the difference between the 2 live values
hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours_live_diff"]["object_numbers"]=[7]

hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours_total_diff"]={} #the difference between the 2 total values
hardwareModelDict["Wpcountx"]["object_list"]["numeric_var"]["Whours_total_diff"]["object_numbers"]=[8]

hardwareModelDict["Wpcountx"]["object_list"]["cfg_obj"]={}
hardwareModelDict["Wpcountx"]["object_list"]["cfg_obj"]["syncTime"]={}
hardwareModelDict["Wpcountx"]["object_list"]["cfg_obj"]["syncTime"]["object_numbers"]=[9]
hardwareModelDict["Wpcountx"]["object_list"]["cfg_obj"]["syncTime"]["query"]="C#_objnumber_##_valuelen:3_#"




hardwareModelDict["ZigXiaomiReed"]={"hwName":"ZigXiaomiReed", "max_pin":4, "hardware_type":"xiaomi_zigbee_mqtt_reed_ZigXiaomiReed_MCCGQ11LM","hw_communication_type":"zigbee", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":3120}
#topic example: zigbee2mqtt/0x00158d00040aaf3e {"battery":100,"voltage":3075,"contact":false,"linkquality":28}
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]={} # Objectname
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["object_type"]="digital_obj_in" # Type of object
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["object_position"]=0 #this is the first object in the hardware
#hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" #this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["json_payload"]="contact"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["values_options_dict"]={"False":{"value":"0","text":"Open"},"True":{"value":"1","text":"Close"}} #if the topic has value false, the onos_object will have value 0 and text Open...
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["suffix"]="" # text part to add on the right of the value
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["bash_cmd"]={}
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["bash_cmd"]["0"]=""
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["bash_cmd"]["1"]=""
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Reed_state"]["bash_cmd"]["s_cmd"]=""


hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]={} # Objectname
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["object_type"]="numeric_var_display"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["object_position"]=1 #this is the position of object in the hardware
#hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["json_payload"]="battery"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Battery"]["suffix"]=" %" # text part to add on the right of the value

hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]={} # Objectname
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["object_type"]="numeric_var_display"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["object_position"]=2 # this is the position of object in the hardware
#hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" # this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["json_payload"]="voltage"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Voltage"]["suffix"]=" V" # text part to add on the right of the value

hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]={} # Objectname
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["object_type"]="numeric_var_display"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["object_position"]=3 # this is the position of object in the hardware
#hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" # this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["json_payload"]="linkquality"
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiReed"]["object_list"]["Linkquality"]["suffix"]=" %" # text part to add on the right of the value









                   
hardwareModelDict["ZigXiaomiWeat"]={"hwName":"ZigXiaomiReed", "max_pin":4, "hardware_type":"xiaomi_zigbee_mqtt_temperature_humidity_pressure_sensor_WSDCGQ11LM","hw_communication_type":"zigbee", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":3120}
#zigbee2mqtt/0x00158d000444618a {"battery":100,"voltage":3015,"temperature":22.08,"humidity":69.49,"pressure":998,"linkquality":70}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]={} # Objectname
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["object_type"]="numeric_var_display" # Type of object
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["object_position"]=0 #this is the first object in the hardware
#hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" #this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["json_payload"]="temperature"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["suffix"]="" # text part to add on the right of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["bash_cmd"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["bash_cmd"]["0"]=""
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["bash_cmd"]["1"]=""
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Temperature"]["bash_cmd"]["s_cmd"]=""

hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]={} # Objectname
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["object_type"]="numeric_var_display" # Type of object
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["object_position"]=1 #this is the first object in the hardware
#hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" #this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["json_payload"]="humidity"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Humidity"]["suffix"]="" # text part to add on the right of the value

hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]={} # Objectname
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["object_type"]="numeric_var_display" # Type of object
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["object_position"]=2 #this is the first object in the hardware
#hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" #this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["json_payload"]="pressure"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Pressure"]["suffix"]="" # text part to add on the right of the value

hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]={} # Objectname
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["object_type"]="numeric_var_display"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["object_position"]=3 #this is the position of object in the hardware
#hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["json_payload"]="battery"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Battery"]["suffix"]=" %" # text part to add on the right of the value

hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]={} # Objectname
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["object_type"]="numeric_var_display"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["object_position"]=4 # this is the position of object in the hardware
#hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" # this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["json_payload"]="voltage"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Voltage"]["suffix"]=" V" # text part to add on the right of the value

hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]={} # Objectname
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["object_type"]="numeric_var_display"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["object_position"]=5 # this is the position of object in the hardware
#hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["mqtt_topic"]="zigbee2mqtt/0x00serial_number" # this is the base mqtt topic,serial_number will be replaced with the hw serialnumber
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["json_payload"]="linkquality"
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["values_options_dict"]={}
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["ZigXiaomiWeat"]["object_list"]["Linkquality"]["suffix"]=" %" # text part to add on the right of the value





hardwareModelDict["MqttPzWhMeter"]={"hwName":"MqttPzWhMeter", "max_pin":4, "hardware_type":"Pzem0004T_v30_watt_meter","hw_communication_type":"mqtt", "pin_mode":{}, "object_list":{}, "parameters":{}, "query":{}, "timeout":3120}

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]["object_position"]=1 #this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]["json_payload"]="W1"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Power_Absorption"]["suffix"]=" W" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]["object_position"]=2 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]["json_payload"]="A1"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Current_Absorption"]["suffix"]=" A" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]["object_position"]=3 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]["json_payload"]="Wh1"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Energy_used"]["suffix"]=" Wh" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]["object_position"]=4 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]["json_payload"]="V1"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Voltage"]["suffix"]=" V" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]["object_position"]=5 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]["json_payload"]="Pf1"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Power_Factor"]["suffix"]=" " # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]["object_position"]=6 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]["json_payload"]="Hz1"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Grid_Frequency"]["suffix"]=" Hz" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]["object_position"]=7 #this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]["json_payload"]="W2"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Prod"]["suffix"]=" W" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]["object_position"]=8 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]["json_payload"]="A2"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Current_Prod"]["suffix"]=" A" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]["object_position"]=9 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]["json_payload"]="Wh2"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Energy_Prod"]["suffix"]=" Wh" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]["object_position"]=10 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]["json_payload"]="V2"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Voltage"]["suffix"]=" V" # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]["object_position"]=11 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]["json_payload"]="Pf2"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Power_Factor"]["suffix"]=" " # text part to add on the right of the value

hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]={} # Objectname
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]["object_type"]="numeric_var_display"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]["object_position"]=12 # this is the position of object in the hardware
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]["json_payload"]="Hz2"
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]["values_options_dict"]={}
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]["prefix"]="" # text part to add on the left of the value
hardwareModelDict["MqttPzWhMeter"]["object_list"]["Solar_Frequency"]["suffix"]=" Hz" # text part to add on the right of the value


hardwareModelDict["RouterRB"]={"hwName":"RouterRB", "max_pin":15, "hardware_type":"rasberry_b_rev2_only", "pin_mode":{}, "parameters":{}, "timeout":180}
hardwareModelDict["RouterRB"]["pin_mode"]["digital_output"]={"button":[(2), (3), (4), (7), (8), (9), (10), (23), (24), (25), (27)]}
hardwareModelDict["RouterRB"]["pin_mode"]["digital_in"]={"d_sensor":[(0), (1), (2), (3), (4), (5), (6)]}
hardwareModelDict["RouterRB"]["pin_mode"]["sr_relay"]={"socket":[(11, 17), (18, 22)]}


# to see how to setup an arduino you can read
# /usr/share/arduino/hardware/arduino/variants/standard/pins_arduino.h

# hardwareModelDict contain the hardware model for each hardware , each new hardware can be created modding 
# the hardware_model.json file  todo..

# option for obj_type :

#old
# sr_relay:  latch relay where the first pi in the tuple is set and the second is reset
# digital_output: output digital pins 
# digital_input : input  digital pins
# analog_input  : analog input
# servo_output  : servomotor control pin
# analog_output    : pwm output pin
# time  : containing a int with a time
# serial_output    : serial output , allow to write to a serial port 
# serial_input     : serial input  , allow to read  a serial port
#end old

# numeric_var:   containing a numeric float variable,not used inside arduino nodes because onos will not send query for this type..
# string_var :   containing a utf8 string variable,not used inside arduino nodes because onos will not send query for this type..


# special_pin      : handled on the node arduino firmware side
# digital_obj_out  : handled on the node arduino firmware side
# digital_obj_in   : handled on the node arduino firmware side
# analog_obj_in    : handled on the node arduino firmware side 
# analog_obj_out   : handled on the node arduino firmware side 
# cfg_obj          : handled on the node arduino firmware side, will be hidden in the created zone not avaible in the config...




# option for hardware_type
# arduino_2009
# arduino_promini
# arduino_uno
# arduino_mega1280
# arduino_mega2560
# gl.inet
# rasberry_b_rev2_only


# timeout:    is the time (in seconds) onos will let pass without contact with the node after which the node will be setted as inactive 


# to get the list of varius type used in a harware configuration:
# print hardwareModelDict["ProminiA"]["pin_mode"].keys()
# print hardwareModelDict["onosPlug6way"]["pin_mode"].keys()
# to get the pin used in a specific mode:
# print hardwareModelDict["onosProminiA"]["pin_mode"]["digital_input"]


# To  get the max pin used for the  onosPlug6way  hardware you have to write:
#  print hardwareModelDict["onosPlug6way"]["max_pin"]
# 
# To get the hardware type for a hardware:
#  print hardwareModelDict["onosPlug6way"]["hardware_type"]
#
#



error_count=0

def getErrorTimeString():
    """
    Called when an error occours, return the current time and a progressive number of the error, incrementing the error_count.
    Used to send the error time and error_count to debug the software.
   
    """

    global error_count
    error_count=error_count+1 
    return(str(datetime.datetime.today().hour)+":"+str(datetime.datetime.today().minute)+"n:"+str(error_count) )



def logprint(message, verbose=1, error_tuple=None):
    
    """
    |Print the message passed  and if the system is in debug mode or if the error is important send a mail
    |Remember, to clear syslog you could use :  > /var/log/syslog
    |To read system log in openwrt type:logread 

    """
    # used like this: 
    #   except Exception as e: 
    #    message="""error in dataExchanged["cmd"]=="updateObjFromNode" """
    #    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

    global debug

    message=str(message)

    #if "error" in message:  #the message is an error...

    if error_tuple!=None: 
 
        e=error_tuple[0]
        exc_type, exc_obj, exc_tb=error_tuple[1]
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        # to print the message in the system log (to read system log in openwrt type:logread )
        message=message+", e:"+str(e.args)+str(exc_type)+str(fname)+" at line:"+str(exc_tb.tb_lineno)



    debug=1
    debug_level=0
  
    if verbose>debug_level or verbose>8:
        syslog.syslog(message)  
        print (message)
        if debug==1 or verbose>1:
            errorQueue.put({"msg":message, "verbose":verbose})  
      #os.system('echo "'+message+'" >> log.txt')






def getListUsedPinsByHardwareModel(hwName):
  """
  Given an hardware name  return a list with all the pins used by a hardware model

  :param hwName:

    The type of the harware node for examples: 

      - ProminiA
      - Plug6way
      - RouterGL
      - RouterGA 
      - RouterRB 
      - Any other hardware type added as hardwareModelDict key in globalVar.py 

  """
  logprint("executed getListUsedPinsByHardwareModel")

  if hwName not in hardwareModelDict.keys(): # if the hardware model doesn't exist
    logprint("error the hardware model "+hwName+" doesn't exist",verbose=8)
    return(-1)
  pin_list=[]
  for a in hardwareModelDict[hwName]["pin_mode"].keys():
    # an example of a value is  "digital_output"
    for b in hardwareModelDict[hwName]["pin_mode"][a]:
      # an example of b value is d_sensor
      for c in hardwareModelDict[hwName]["pin_mode"][a][b]:
        # an example of c value is 13  but if the hwtype is sr_relay then an example is (2,3)
        if type(c) in (tuple, list):  #check if is a list or not
          for d in c:  # for every pin of the list 
            # print d
            pin_list.append(d)
        else:  # is not a list  
          pin_list.append(c)


  logprint("pin used:"+str(pin_list) )

  return (pin_list)



def getListPinsConfigByHardwareModel(hwName, pin_mode):
  """
  Given hardware name and a pin mode, return a list containing the pin numbers that are configurated with that pin_mode

  :param hwName:

    The type of the hardware node for examples: 

      - ProminiA
      - Plug6way
      - RouterGL
      - RouterGA
      - RouterRB 
      - Any other hardware type added as hardwareModelDict key in globalVar.py


  :param pin_mode:
    The pin mode you are searching for:

     - sr_relay:  
         Latch relay where the first pin in the tuple is set and the second is reset
     - digital_output: 
         Output digital pins 
     - digital_input :
         Input  digital pins
     - analog_input  : 
         Analog input
     - servo_output  :
         Servomotor control pin
     - analog_output    : 
         Pwm output pin


  """




  logprint("executed getListPinsConfigByHardwareModel ()")
  if hwName not in hardwareModelDict.keys(): # if the hardware model doesn't exist
    logprint("error the hardware model "+hwName+" doesn't exist")

    return([])
  if pin_mode not in hardwareModelDict[hwName]["pin_mode"].keys(): #if the type  doesn't exist in the hardware model 
    #print "the hardware type "+pin_mode+" doesn't exist in this hardware model"+hwName

    return([])
 # else:
 #   print ( "the hardware type "+pin_mode+" Exist in this hardware model")
 


  pin_list = []
  for a in hardwareModelDict[hwName]["pin_mode"][pin_mode]:  #extract a list of all the pin to use as pin_mode
    for b in hardwareModelDict[hwName]["pin_mode"][pin_mode][a]:
      if type(b) in (tuple, list):
        for c in b:
        #an example of b value is d_sensor
          logprint(c)
          pin_list.append(c)
      else:
        pin_list.append(b)

  return(pin_list)



# https://unix.stackexchange.com/questions/22465/script-to-check-for-read-only-filesystem
def make_fs_ready_to_write():
  """
  |
  | Enable the linux filesystem to write to disk ,if onos is running on orangePi
  |

  """
  if 0: # router_hardware_type=="RouterOP":
    subprocess.call('mount -o remount,rw /', shell=True, close_fds=True)


def make_fs_readonly():  # change the linux filesystem to readOnly ,if onos is running on orangePi
  """
  |
  | Change the linux filesystem to readOnly ,if onos is running on orangePi
  |

  """
  if 0: # router_hardware_type=="RouterOP":
    subprocess.call('mount -o remount,ro /', shell=True, close_fds=True)



def get_ip_address():
  """
  |
  | Return Current machine ip address as a string, for example "192.168.1.2"
  | See https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

  """
  # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  # s.connect(("8.8.8.8", 80))
  # return s.getsockname()[0]
  return((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])
