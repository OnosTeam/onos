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

"""| This module will set the right timezone to the openwrt system calling:
   | 'ntpd -q -p 0.openwrt.pool.ntp.org' 
   | And executing  'echo "export TZ='+timezone+'">> /etc/profile'
   |
 

"""


from conf import *           # import parameter from conf.py  which will read the data from the  json 
import platform

os.system('''ntpd -q -p 0.openwrt.pool.ntp.org''') 
#if os.path.isfile("/etc/profile"):
try:
  
  prof = open('/etc/profile', 'r')
  profile=prof.read()
  prof.close()
   #print profile
  if (string.find(profile,conf_options["timezone"])== -1) :
    platform=platform.node()
    if platform.find("Orange")!=-1: #found uname with orange pi name
      router_hardware_type="RouterOP"
      os.system("mount -o remount,rw /")  #remount the  filesystem as rw
      os.system('echo "export TZ='+conf_options["timezone"]+'">> /etc/profile') ##export TZ="CET-1CEST,M3.5.0,M10.5.0/3"
      os.system("mount -o remount,ro /")  #remount the  filesystem as ro
    else:
      os.system('echo "export TZ='+conf_options["timezone"]+'">> /etc/profile') ##export TZ="CET-1CEST,M3.5.0,M10.5.0/3"
    logprint(" onos set the timezone to:"+conf_options["timezone"])
    os.system("source /etc/profile") #reload the profile to update time
  else:
    logprint("timezone ok")
  #banana to add the change of the line to change the timezone
except:
  logprint("error, onos can't set the timezone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

