"""
  This module is imported from all the others and it stores the global variables and some global functions.


"""

import Queue
import datetime
import string,cgi,time
import codecs #to save and open utf8 files
import socket  

from signal import signal, SIGPIPE, SIG_DFL  # to prevent [Errno 32] Broken pipe
import unicodedata
import os,sys,datetime,subprocess
from os import curdir, sep
import shutil 

import BaseHTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from time import gmtime, strftime

import json
import unicodedata
import os
import codecs
#import urllib2,urllib 
import urllib2
#import httplib
import thread,threading,time
import os.path
import random
import binascii  #used by weobject class for the permission 
import re  #regular expression
import smtplib   #used by mail_agent to send mail



# Add vendor directory to module search path
lib_dir = os.path.join('external_libraries')
sys.path.append(lib_dir)
# Now you can import any library located in the "external_libraries" folder!

lib_dir2 = os.path.join('gui')
sys.path.append(lib_dir2)

import urllib3
from urllib3 import PoolManager ,Timeout
#use example urllib3
#url_request_manager = PoolManager(10)
#url_request_manager=PoolManager(10)
#r = url_request_manager.request('GET', 'http://example.com')
#or
#r=url_request_manager.request_encode_body('POST','url',fields,timeout=Timeout(total=5.0))
#print r.data
#
# r = url_request_manager.request('GET', 'http://example.com:80',timeout=Timeout(total=5.0))

url_request_manager = PoolManager(8)


exit=0
debug=1  #debug mode , if set to 1  the debug mode is on 
object_dict={} #object_dict  contain all the web_object  and the key of the dictionary for each web_object is the name of the web_object
zoneDict={}#dict where the key is the name from roomList and the value is a list of all the webobject names present in the room  
router_hardware={}
scenarioDict={}


timezone="CET-1CEST,M3.5.0,M10.5.0/3"  #will be overwritten by /scripts_folder/config_files/cf.json
os.environ['TZ']=timezone 
try:
  time.tzset()
except:
  print "tzset not present , timezone will work anyway"
#time_gap=120    #minutes of difference between utc and local time 
#export TZ="CET-1CEST,M3.5.0,M10.5.0/3"



user_active_time_dict={}
login_required=1  #if setted to 1 enable the webpage login  and allow only logged user to use onos,overwritten by /scripts_folder/config_files/cfg.json
logTimeout=15 #minutes of user inactivity before logout , will be overwritten by /scripts_folder/config_files/cf.json

log_name="file.log"
error_log_name="erros.log"
log_enable=0   #enable the log file size check
check_log_len_time=datetime.datetime.today().minute
mail_error_log_enable=1  #enable onos to send mail when an error happens
error_log_mail_frequency=30  #seconds between a error check and another
last_error_check_time=0
mail_where_to_send_errors="electronicflame@gmail.com"

baseRoomPath="zones/"
hardwareModelDict={}

#read_onos_sensor_enabled=1
enable_usb_serial_port=1 #if setted to 0 disable usb serial port also if supported by the hardware in hardwareModelDict[]
router_sn="RouterGA0000"
uart_router_sn="" #the sn of the node connected to the usb of the pc where onos is run..
router_hardware_type="RouterGA" #select the type of hardware
router_hardware_fw_version="5.14"
gui_webserver_port=80
service_webserver_port=81
onos_center_internal_ip='192.168.101.1'  # the ip of the lan , the one where all nodes are attached
service_webserver_delay=1 #seconds of delay between each answer
node_webserver_port=9000   # the web server port used on remote nodes
router_read_pin_frequency=20  #seconds between a pin read in the router hardware
last_pin_read_time=0


if (os.path.exists("/sys/class/gpio")==1)&(router_hardware_type=="RouterGL") : #if the directory exist ,then the hardware has embedded IO pins
  discovered_running_hardware=router_hardware_type
  base_cfg_path="/bin/onos/scripts_folder/"
else:
  discovered_running_hardware="pc"  #the hardware has not IO pins
  base_cfg_path=""




accept_only_from_white_list=0  #if set to 1 the onos cmd will be accepted only from mail in white list
#will be overwritten by /scripts_folder/config_files/cf.json

mail_whiteList=[]  #will be overwritten by /scripts_folder/config_files/cf.json
mail_whiteList.append("elettronicaopensource@gmail.com")
mail_whiteList.append("electronicflame@gmail.com")
mail_whiteList.append("marco_righe@yahoo.it")
enable_mail_service=1  #active mailCheckThread   will be overwritten by /scripts_folder/config_files/cf.json
enable_mail_output_service=1 #activate the sending of mails from onos  will be overwritten by /scripts_folder/config_files/cf.json
last_mail_sync_time=0  
mailCheckThreadIsrunning=0 # tell onos if the mail thread is alredy running
mail_service=0
mail_check_frequency=10  #seconds between 2 checks
mailOutputHandler_is_running=0  #tell onos if the thread is already running
mail_retry_timeout=120  #seconds between retry after error in sending mail





enable_onos_auto_update="yes" # possible value: "yes","no","ask_me"  # banana ask_me not implemented yet
scenarios_enable=0  # tell onos if it have to check the scenarios or not. warning overwrite by scenarios_enable in cfg.json
online_server_enable=0  #enable the remote online server to controll onos from internet without opening the router ports
#will be overwritten by /scripts_folder/config_files/cf.json

last_server_sync_time=0
onlineServerSyncThreadIsrunning=0 #tell onos if the thread is running
online_server_delay=3  #3  #seconds between each online server query
online_object_dict=[]   #online object dict ,used to know if an update of the dict is needed
online_zone_dict=[]   #online zone dict ,used to know if an update of the dict is needed
if online_server_enable==1 :
  force_online_sync_users=1    #used to know if an update of the dict is required
else:
  force_online_sync_users=0    #used to know if an update of the dict is required
online_usersDict={}
online_first_contact=1  #tell if is the first contact between this router and the online server
onos_online_key=router_sn  #unique key used by the router to login on the online server 
onos_online_password="1234"  #password used by the router to login on the online server 
onos_online_site_url="http://www.myonos.com/onos/"  #remote online server url (where the php onos scripts are located)

internet_connection=0  #tell onos if there is internet connection, do not change it..onos will change it if there is internet


queryToNetworkNodeQueue=Queue.Queue()

queryToRadioNodeQueue=Queue.PriorityQueue()


node_query_threads_executing=0# 

node_query_radio_threads_executing=0

max_number_of_node_query_threads_executing=2 #tells onos the maximun number of thread it can executes to handle network node queries

layerExchangeDataQueue = Queue.Queue()  # this queue will contain all the dictionaries to pass data from the hardware layer to the webserver layer   router_handler.py will pass trought this queue all the change of hardware status to the webserver.py


priorityCmdQueue=Queue.Queue()  #this queue will contain all the command received from the web gui...those will have priority over the one contained in layerExchangeDataQueue 


mailQueue=Queue.Queue()  # this queue will contain all the mail to send , onos will send them as soon as possible

errorQueue=Queue.Queue()  # this queue will contain all the error happened

lock_bash_cmd= threading.Lock()

lock_serial_input=threading.Lock()
waitToReceiveUntilIRead=0  #stop the incoming uart reading until the data has been readed
waitTowriteUntilIReceive=0 


lock1_current_node_handler_list= threading.Lock()  #lock to access current_node_handler_list
#lock2_query_threads = threading.Lock()  #lock to access query_to_nodeDict{}
wait_because_node_is_talking=0

current_node_handler_list=[]   #list containing all the node_serial_number of the nodes that are being queried
query_to_node_dict={} # this dictionary will  have the node_serial_number as key and will contain a list of dictionaries 
#example :   query_to_node_dict={'Plug6way0001':[{"address":address,"query":query,"objName":objName,"status_to_set":status_to_set,"user":user,"priority":priority,"mail_report_list":mail_report_list]}
#to access it:  query_to_node_dict['Plug6way0001'][0]["address"]  to get the  first address  


last_received_packet="" # used in arduinoSerial.py  
data_to_write="" # used in arduinoSerial.py 
write_to_serial_packet_ready=0 # used in arduinoSerial.py 






if (enable_mail_service==1)or(enable_mail_output_service==1): 
  import imaplib   #used by mail_agent 
  import email     #used by mail_agent 
  #imaplib.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # see https://aboutsimon.com/index.html%3Fp=85.html  




recoverycfg_json='''

{
  "accept_only_from_white_list": 0, 
  "enable_mail_service": 1, 
  "enable_mail_output_service": 1,
  "enable_onos_auto_update": "yes", 
  "logTimeout": 15, 
  "login_required": 0, 
  "mail_whiteList": [], 
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


'''


#banana to make a default json without all this data
recoverydata_json=''' {
  "nodeDictionary": {
    "Plug6way0001": {
      "hwModelName": "Plug6way", 
      "nodeAddress": "192.168.101.108", 
      "node_serial_number": "Plug6way0001"
    }, 
    "Plug6way0002": {
      "hwModelName": "Plug6way", 
      "nodeAddress": "192.168.101.104", 
      "node_serial_number": "Plug6way0002"
    }, 
    "RouterGL0000": {
      "hwModelName": "RouterGL", 
      "nodeAddress": "0", 
      "node_serial_number": "RouterGL0000"
    }
  }, 
  "objectDictionary": {
    "Caldaia": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "Caldaia=0", 
        "1": "Caldaia=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "Caldaia", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        4, 
        5
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "Casa_body": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "Casa_body=0", 
        "1": "Casa_body=1"
      }, 
      "mail_l": [], 
      "node_sn": 9999, 
      "notes": " ", 
      "objname": "Casa_body", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        9999
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:#A9E2F3;", 
        "1": "background-color:#8181F7;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "Wifi_netgear": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "Wifi_netgear=0", 
        "1": "Wifi_netgear=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "Wifi_netgear", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        2, 
        3
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "aaaaaaaaaaaaaaaaaaaaaaaaa": {
      "cmdDict": {
        "0": "", 
        "1": "", 
        "s_cmd": ""
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "aaaaaaaaaaaaaaaaaaaaaaaaa=0", 
        "1": "aaaaaaaaaaaaaaaaaaaaaaaaa=1"
      }, 
      "mail_l": [], 
      "node_sn": 9999, 
      "notes": " ", 
      "objname": "aaaaaaaaaaaaaaaaaaaaaaaaa", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        9999
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": "1", 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "button0_RouterGL0000": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "button0_RouterGL0000=0", 
        "1": "button0_RouterGL0000=1"
      }, 
      "mail_l": [
        "electronicflame@gmail.com"
      ], 
      "node_sn": "RouterGL0000", 
      "notes": " ", 
      "objname": "button0_RouterGL0000", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        18
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "digital_output"
    }, 
    "button1_RouterGL0000": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "button1_RouterGL0000=0", 
        "1": "button1_RouterGL0000=1"
      }, 
      "mail_l": [], 
      "node_sn": "RouterGL0000", 
      "notes": " ", 
      "objname": "button1_RouterGL0000", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        22
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": "onoswait", 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "digital_output"
    }, 
    "counter1": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "counter1=0", 
        "1": "counter1=1"
      }, 
      "mail_l": [], 
      "node_sn": 9999, 
      "notes": " ", 
      "objname": "counter1", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        9999
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 741, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "d_sensor0_RouterGL0000": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "d_sensor0_RouterGL0000=0", 
        "1": "d_sensor0_RouterGL0000=1"
      }, 
      "mail_l": [], 
      "node_sn": "RouterGL0000", 
      "notes": " ", 
      "objname": "d_sensor0_RouterGL0000", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        21
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "digital_input"
    }, 
    "day": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "day=0", 
        "1": "day=1"
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
      "status": 2, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "dayTime": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "dayTime=0", 
        "1": "dayTime=1"
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
      "status": 1301, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "hours": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "hours=0", 
        "1": "hours=1"
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
      "scenarios": [
        "scenario2", 
        "scenario3", 
        "scenario4", 
        "scenario5", 
        "scenario6", 
        "scenario7", 
        "scenario10"
      ], 
      "status": 21, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "minutes": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "minutes=0", 
        "1": "minutes=1"
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
      "scenarios": [
        "scenario2", 
        "scenario3", 
        "scenario4", 
        "scenario5", 
        "scenario6", 
        "scenario7", 
        "scenario8"
      ], 
      "status": 41, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "month": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "month=0", 
        "1": "month=1"
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
      "status": 1, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "onosCenterWifi": {
      "cmdDict": {
        "0": "uci set wireless.radio0.disabled=1&uci commit wireless && wifi", 
        "1": "uci set wireless.radio0.disabled=0&uci commit wireless && wifi", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "onosCenterWifi=0", 
        "1": "onosCenterWifi=1"
      }, 
      "mail_l": [], 
      "node_sn": 9999, 
      "notes": " ", 
      "objname": "onosCenterWifi", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        9999
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "rergswgeg": {
      "cmdDict": {
        "0": "", 
        "1": "", 
        "s_cmd": ""
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "rergswgeg=0", 
        "1": "rergswgeg=1"
      }, 
      "mail_l": [], 
      "node_sn": 9999, 
      "notes": " ", 
      "objname": "rergswgeg", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        9999
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "socket0_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket0_Plug6way0001=0", 
        "1": "socket0_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "socket0_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        2, 
        3
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket0_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket0_Plug6way0002=0", 
        "1": "socket0_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "socket0_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        2, 
        3
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket0_RouterGL0000": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket0_RouterGL0000=0", 
        "1": "socket0_RouterGL0000=1"
      }, 
      "mail_l": [], 
      "node_sn": "RouterGL0000", 
      "notes": " ", 
      "objname": "socket0_RouterGL0000", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        20, 
        19
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 1, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket1_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket1_Plug6way0001=0", 
        "1": "socket1_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "socket1_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        4, 
        5
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket1_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket1_Plug6way0002=0", 
        "1": "socket1_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "socket1_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        4, 
        5
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket2_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket2_Plug6way0001=0", 
        "1": "socket2_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "socket2_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        6, 
        7
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket2_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket2_Plug6way0002=0", 
        "1": "socket2_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "socket2_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        6, 
        7
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket3_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket3_Plug6way0001=0", 
        "1": "socket3_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "socket3_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        8, 
        9
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket3_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket3_Plug6way0002=0", 
        "1": "socket3_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "socket3_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        8, 
        9
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket4_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket4_Plug6way0001=0", 
        "1": "socket4_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "socket4_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        14, 
        15
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket4_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket4_Plug6way0002=0", 
        "1": "socket4_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "socket4_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        14, 
        15
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket5_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket5_Plug6way0001=0", 
        "1": "socket5_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "socket5_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        16, 
        17
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "socket5_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "socket5_Plug6way0002=0", 
        "1": "socket5_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "socket5_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        16, 
        17
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "wifi0_Plug6way0001": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "wifi0_Plug6way0001=0", 
        "1": "wifi0_Plug6way0001=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0001", 
      "notes": " ", 
      "objname": "wifi0_Plug6way0001", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        16, 
        17
      ], 
      "priority": 0, 
      "scenarios": [
        "scenario9"
      ], 
      "status": "onoswait", 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "wifi0_Plug6way0002": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "wifi0_Plug6way0002=0", 
        "1": "wifi0_Plug6way0002=1"
      }, 
      "mail_l": [], 
      "node_sn": "Plug6way0002", 
      "notes": " ", 
      "objname": "wifi0_Plug6way0002", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        16, 
        17
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;color:black;", 
        "1": "background-color:red;color: black;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "sr_relay"
    }, 
    "wwwwwwwwwww": {
      "cmdDict": {
        "0": "", 
        "1": "", 
        "s_cmd": ""
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "wwwwwwwwwww=0", 
        "1": "wwwwwwwwwww=1"
      }, 
      "mail_l": [], 
      "node_sn": 9999, 
      "notes": " ", 
      "objname": "wwwwwwwwwww", 
      "own": "onos_admin", 
      "perm": "111111111", 
      "pins": [
        9999
      ], 
      "priority": 0, 
      "scenarios": [], 
      "status": 0, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }, 
    "year": {
      "cmdDict": {
        "0": " ", 
        "1": " ", 
        "s_cmd": " "
      }, 
      "grp": [
        "web_interface", 
        "onos_mail_guest"
      ], 
      "htmlDict": {
        "0": "year=0", 
        "1": "year=1"
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
      "status": 2016, 
      "styleDict": {
        "0": "background-color:green;", 
        "1": "background-color:red;", 
        "default_s": "background-color:red ;color black", 
        "wait": "background-color:grey ;color black"
      }, 
      "type": "b"
    }
  }, 
  "zoneDictionary": {
    "Casa": {
      "group": [], 
      "hidden": 0, 
      "objects": [
        "Caldaia", 
        "Wifi_netgear", 
        "aaaaaaaaaaaaaaaaaaaaaaaaa"
      ], 
      "order": 0, 
      "owner": "onos_sys", 
      "permissions": "777"
    }, 
    "Plug6way0001": {
      "group": [], 
      "hidden": 0, 
      "objects": [
        "wifi0_Plug6way0001", 
        "socket0_Plug6way0001", 
        "socket1_Plug6way0001", 
        "socket2_Plug6way0001", 
        "socket3_Plug6way0001", 
        "socket4_Plug6way0001", 
        "socket5_Plug6way0001"
      ], 
      "order": 2, 
      "owner": "onos_sys", 
      "permissions": "777"
    }, 
    "Plug6way0002": {
      "group": [], 
      "hidden": 0, 
      "objects": [
        "wifi0_Plug6way0002", 
        "socket0_Plug6way0002", 
        "socket1_Plug6way0002", 
        "socket2_Plug6way0002", 
        "socket3_Plug6way0002", 
        "socket4_Plug6way0002", 
        "socket5_Plug6way0002"
      ], 
      "order": 3, 
      "owner": "onos_sys", 
      "permissions": "777"
    }, 
    "RouterGL0000": {
      "group": [], 
      "hidden": 0, 
      "objects": [
        "button0_RouterGL0000", 
        "button1_RouterGL0000", 
        "d_sensor0_RouterGL0000", 
        "onosCenterWifi", 
        "socket0_RouterGL0000"
      ], 
      "order": 1, 
      "owner": "onos_sys", 
      "permissions": "777"
    }
  }, 
  "scenarioDictionary": {
    "scenario10": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==23)&(#_minutes_#==30)", 
      "enabled": 1, 
      "functionsToRun": [
        "Caldaia=0"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario2": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==8)&(#_minutes_#==0)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=1", 
        "Wifi_netgear==1", 
        "Caldaia=0"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario21": {
      "type_after_run":"0", 
      "conditions": "(#_minutes_#>-1)", 
      "enabled": 1, 
      "functionsToRun": [
        "socket0_WLightSS0004=!#_socket0_WLightSS0004_#", 
        "button1_RouterGL0000==!#_wifi0_Plug6way0001_#"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario3": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==8)&(#_minutes_#==25)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=0", 
        "Wifi_netgear==0"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario4": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==12)&(#_minutes_#==30)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=1", 
        "Wifi_netgear==1"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario5": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==14)&(#_minutes_#==0)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=0", 
        "Wifi_netgear==0"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario6": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==18)&(#_minutes_#==0)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=1", 
        "Wifi_netgear==1"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario7": {
      "type_after_run":"0", 
      "conditions": "(#_hours_#==0)&(#_minutes_#==0)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=0", 
        "Wifi_netgear==0", 
        "counter1=0"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario8": {
      "type_after_run":"0", 
      "conditions": "(#_minutes_#>-1)", 
      "enabled": 1, 
      "functionsToRun": [
        "wifi0_Plug6way0001=!#_wifi0_Plug6way0001_#", 
        "button1_RouterGL0000==!#_wifi0_Plug6way0001_#"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenario9": {
      "type_after_run":"0", 
      "conditions": "1", 
      "enabled": 1, 
      "functionsToRun": [
        "counter1=#_counter1_#+1"
      ], 
      "one_time_shot": 0, 
      "priority": 0
    }, 
    "scenarioA": {
      "type_after_run":"0", 
      "conditions": "(#_year_#==2016)", 
      "enabled": 1, 
      "functionsToRun": [
        "button0_RouterGL0000=1", 
        "aaaaaaaaaaaaaaaaaaaaaaaaa=2016", 
        "counter1=1", 
        "socket3_Plug6way0001=1"
      ], 
      "one_time_shot": 0, 
      "priority": 0
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

next_node_free_address_list=[1,2]   #list of free node addresses from 2 to 254
usersDict={}
usersDict["onos_mail_guest"]={"pw":"onos","mail_control_password":"onosm","priority":0,"user_mail":"elettronicaopensource@gmail.com"}
usersDict["web_interface"]={"pw":"onos","mail_control_password":"onosm","priority":0,"user_mail":"elettronicaopensource@gmail.com"}
usersDict["scenario"]={"pw":"onos","mail_control_password":"onosm","priority":0,"user_mail":"elettronicaopensource@gmail.com"}
usersDict["onos_node"]={"pw":"onos","mail_control_password":"onosm","priority":99,"user_mail":"elettronicaopensource@gmail.com"}
usersDict["marco"]={"pw":"1234","mail_control_password":"onosm","priority":0,"user_mail":"elettronicaopensource@gmail.com"}




online_usersDict["marco"]={"pw":"1234","mail_control_password":"onosm","priority":0,"user_mail":"elettronicaopensource@gmail.com"}


usersDict.update(online_usersDict) #insert the online users in the local dictionary



onos_mail_conf={"mail_account":"onos.beta@gmail.com","pw":"gmailbeta","smtp_port":"587","smtp_server":"smtp.gmail.com","mail_imap":"imap.gmail.com"}


conf_options={u"online_server_enable":online_server_enable,u"enable_mail_output_service":enable_mail_output_service,u"enable_mail_service":enable_mail_service,u"accept_only_from_white_list":accept_only_from_white_list,u"mail_whiteList":mail_whiteList,u"timezone":timezone,u"login_required":login_required,u"logTimeout":logTimeout,"online_usersDict":online_usersDict,"enable_onos_auto_update":enable_onos_auto_update,"scenarios_enable":scenarios_enable}

#localhost/setup/node_manager/RouterGL0001
hardwareModelDict["RouterGL"]={"hwName":"RouterGL","max_pin":5,"hardware_type":"gl.inet_only","pin_mode":{},"parameters":{},"timeout":"never"}
hardwareModelDict["RouterGL"]["pin_mode"]["sr_relay"]={"socket":[(20,19)]}
hardwareModelDict["RouterGL"]["pin_mode"]["digital_input"]={"d_sensor":[(21)]}
hardwareModelDict["RouterGL"]["pin_mode"]["digital_output"]={"button":[(18),(22)]}
hardwareModelDict["RouterGL"]["parameters"]["bash_pin_enable"]=1
hardwareModelDict["RouterGL"]["parameters"]["serial_port_enable"]=0


hardwareModelDict["RouterGA"]={"hwName":"RouterGA","max_pin":5,"hardware_type":"gl.inet_with_arduino2009","pin_mode":{},"parameters":{},"timeout":"never"}
hardwareModelDict["RouterGA"]["pin_mode"]["sr_relay"]={"socket":[(20,19)]}
hardwareModelDict["RouterGA"]["pin_mode"]["digital_input"]={"d_sensor":[(21)]}
hardwareModelDict["RouterGA"]["pin_mode"]["digital_output"]={"button":[(18),(22)]}
hardwareModelDict["RouterGL"]["parameters"]["bash_pin_enable"]=1
hardwareModelDict["RouterGL"]["parameters"]["serial_port_enable"]=1

hardwareModelDict["ProminiS"]={"hwName":"ProminiS","max_pin":13,"hardware_type":"arduino2009_serial","pin_mode":{},"timeout":360}
hardwareModelDict["ProminiS"]["pin_mode"]["sr_relay"]={"socket":[(20,19)]}
hardwareModelDict["ProminiS"]["pin_mode"]["digital_input"]={"d_sensor":[(21)]}
hardwareModelDict["ProminiS"]["pin_mode"]["digital_output"]={"button":[(5),(6)]}


hardwareModelDict["ProminiA"]={"hwName":"ProminiA","max_pin":18,"hardware_type":"arduino_promini","pin_mode":{},"parameters":{},"timeout":"never"}
hardwareModelDict["ProminiA"]["pin_mode"]["digital_input"]={"d_sensor":[(2),(3),(4)]}
hardwareModelDict["ProminiA"]["pin_mode"]["digital_output"]={"button":[(6),(7),(8)]}
hardwareModelDict["ProminiA"]["pin_mode"]["analog_input"]={"a_sensor":[(14),(15),(16),(17),(18),(19)]}
hardwareModelDict["ProminiA"]["pin_mode"]["servo_output"]={"servo":[(5)]}
#hardwareModelDict["ProminiA"]["pin_mode"]["analog_output"]={"a_out":[(9)]}

hardwareModelDict["Plug6way"]={"hwName":"Plug6way","max_pin":18,"hardware_type":"arduino_promini","pin_mode":{},"parameters":{},"timeout":90}
hardwareModelDict["Plug6way"]["pin_mode"]["sr_relay"]={"socket":[(2,3),(4,5),(6,7),(8,9),(14,15)],"wifi":[(16,17)]}

hardwareModelDict["WLightSS"]={"hwName":"WLightSS","max_pin":13,"hardware_type":"arduino2009_serial","pin_mode":{},"parameters":{},"timeout":360}
hardwareModelDict["WLightSS"]["pin_mode"]["sr_relay"]={"socket":[(7,8)]}
hardwareModelDict["WLightSS"]["pin_mode"]["digital_output"]={"button":[(5),(6)]}


hardwareModelDict["WLightSA"]={"hwName":"WLightSA","max_pin":13,"hardware_type":"arduino2009_serial","pin_mode":{},"parameters":{},"query":{},"timeout":360}
hardwareModelDict["WLightSA"]["pin_mode"]["digital_obj"]={"lamp":[(5,6)]}
hardwareModelDict["WLightSA"]["pin_mode"]["analog_input"]={"luminosity":[(14)],"temperature":[(15)]}
hardwareModelDict["WLightSA"]["pin_mode"]["cfg_obj"]={"lux_threshold":[(-1)],"timeout_to_turn_off":[(-1)]}#this have no pins..
hardwareModelDict["WLightSA"]["query"]["digital_obj"]={"lamp":"wl#_objnumber_##_valuelen:1_#"}  #define the base query for this
hardwareModelDict["WLightSA"]["query"]["cfg_obj"]={"lux_threshold":"lt#_valuelen:3_#" ,"timeout_to_turn_off":"to#_valuelen:4_#" }  #define the base query for this
                   



hardwareModelDict["WPlugAvx"]={"hwName":"WPlugAvx","max_pin":13,"hardware_type":"arduino_promini","pin_mode":{},"parameters":{},"query":{},"timeout":360}
hardwareModelDict["WPlugAvx"]["pin_mode"]["digital_obj"]={"plug":[(0)],"plug2":[(1)]}#  one object with a double set reset relay, is the obj0
hardwareModelDict["WPlugAvx"]["pin_mode"]["digital_output"]={"button":[(5),(6)]}
hardwareModelDict["WPlugAvx"]["query"]["digital_obj"]={"plug":"wb#_objnumber_##_valuelen:1_#","plug2":"wb#_objnumber_##_valuelen:1_#"}  #define the base query for this node digital_obj..so onos will write for example: [S_001wp01x_#] , valuelen:1  means that this part will be replaced with a single character('0' or '1' since is digital_obj)  , the starting [S_001  and the ending _#]  will be added in router_handler.py at the end of the message a '\n' will be added anyway.







# note that in the format ["analog_output"]={"a_out":[(11),(10)]}  
# "a_out" is only the the html name that onos will add to the webobject name
#so the final webobject name will be for example a_out0_ProminiA0001  
#the web object type will be "analog_output"

# if the type of "pin_mode" is digital_obj then the structure must be :{"plug":[(0)],"plug2":[(1)]}   with a custom name for each object,  if you have to do more than one object of the same type write progressive names..like: {"plug01":[(0)],"plug02":[(1)]}
#in the digital_obj case the number zero here [(0)] indicates the number of the object in the arduino node software make sure to don't repeat numbers there.


hardwareModelDict["RouterRB"]={"hwName":"RouterRB","max_pin":15,"hardware_type":"rasberry_b_rev2_only","pin_mode":{},"parameters":{},"timeout":180}
hardwareModelDict["RouterRB"]["pin_mode"]["digital_output"]={"button":[(2),(3),(4),(7),(8),(9),(10),(23),(24),(25),(27)]}
hardwareModelDict["RouterRB"]["pin_mode"]["digital_input"]={"d_sensor":[(0),(1),(2),(3),(4),(5),(6)]}
hardwareModelDict["RouterRB"]["pin_mode"]["sr_relay"]={"socket":[(11,17),(18,22)]}


#to see how to setup an arduino you can read
#/usr/share/arduino/hardware/arduino/variants/standard/pins_arduino.h

#hardwareModelDict contain the hardware model for each hardware , each new hardware can be created modding 
#the hardware_model.json file  todo..

#option for obj_type :
# sr_relay:  latch relay where the first pi in the tuple is set and the second is reset
# digital_output: output digital pins 
# digital_input : input  digital pins
# analog_input  : analog input
# servo_output  : servomotor control pin
# analog_output    : pwm output pin
# time  : containing a int with a time
# numeric_var:   containing a numeric float varaible 
# string_var :   containing a utf8 string varaible 
# serial_output : serial output , allow to write to a serial port 
# serial_input  : serial input  , allow to read  a serial port
# special_pin   : handled on the node arduino firmware side
# digital_obj    : handled on the node arduino firmware side
# analog_obj     : handled on the node arduino firmware side     
# cfg_obj        : handled on the node arduino firmware side, will be hidden in the created zone not avaible in the config...




#option for hardware_type
#arduino_2009
#arduino_promini
#arduino_uno
#arduino_mega1280
#arduino_mega2560
#gl.inet
#rasberry_b_rev2_only


#timeout:    is the time (in seconds) onos will let pass without contact with the node after which the node will be setted as inactive 


#to get the list of varius type used in a harware configuration:
#print hardwareModelDict["ProminiA"]["pin_mode"].keys()
#print hardwareModelDict["onosPlug6way"]["pin_mode"].keys()
#to get the pin used in a specific mode:
#print hardwareModelDict["onosProminiA"]["pin_mode"]["digital_input"]


# To  get the max pin used for the  onosPlug6way  hardware you have to write:
#  print hardwareModelDict["onosPlug6way"]["max_pin"]
# 
# To get the hardware type for a hardware:
#  print hardwareModelDict["onosPlug6way"]["hardware_type"]
#
#
















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
  print "executed getListUsedPinsByHardwareModel"

  if hwName not in hardwareModelDict.keys(): #if the hardware model doesn't exist
    print "the hardware model "+hwName+" doesn't exist"
    errorQueue.put("the hardware model "+hwName+" doesn't exist" )
    return(-1)
  pin_list=[]
  for a in hardwareModelDict[hwName]["pin_mode"].keys():
    #an example of a value is  "digital_output"
    for b in hardwareModelDict[hwName]["pin_mode"][a]:
      #an example of b value is d_sensor
      for c in hardwareModelDict[hwName]["pin_mode"][a][b]:
        #an example of c value is 13  but if the hwtype is sr_relay then an example is (2,3)
        if type(c) in (tuple, list):  #check if is a list or not
          for d in c:  # for every pin of the list 
            #print d
            pin_list.append(d)
        else:  #is not a list  
          pin_list.append(c)


  print "pin used:"
  print pin_list
  return (pin_list)



def getListPinsConfigByHardwareModel(hwName,pin_mode):
  """
  Given hardware name and a pin mode , return a list containing the pin numbers that are configurated with that pin_mode

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




  print "executed getListPinsConfigByHardwareModel ()"
  if hwName not in hardwareModelDict.keys(): #if the hardware model doesn't exist
    print "the hardware model "+hwName+" doesn't exist"
    errorQueue.put( "the hardware model "+hwName+" doesn't exist" )
    return([])
  if pin_mode not in hardwareModelDict[hwName]["pin_mode"].keys(): #if the type  doesn't exist in the hardware model 
    print "the hardware type "+pin_mode+" doesn't exist in this hardware model"+hwName
    #errorQueue.put("the hardware type "+pin_mode+" doesn't exist in this hardware model"+hwName )
    return([])
 # else:
 #   print ( "the hardware type "+pin_mode+" Exist in this hardware model")
 


  pin_list=[]
  for a in hardwareModelDict[hwName]["pin_mode"][pin_mode]:  #extract a list of all the pin to use as pin_mode
    for b in hardwareModelDict[hwName]["pin_mode"][pin_mode][a]:
      if type(b) in (tuple, list):
        for c in b:
        #an example of b value is d_sensor
          print c
          pin_list.append(c)
      else:
        pin_list.append(b)

 
  return(pin_list) 


error_count=0

def getErrorTimeString():
  """
  Called when an error occours ,return the current time and a progressive number of the error, incrementing the error_count.
  Used to send the error time and error_count to debug the software.
 
"""

  global error_count
  error_count=error_count+1 
  return(str(datetime.datetime.today().hour)+":"+str(datetime.datetime.today().minute)+"n:"+str(error_count) )

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

