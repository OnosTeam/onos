# -*- coding: UTF-8 -*-
import codecs
import json
import globalVar
from get_top_menu import *   #works because there is sys.path.append(lib_dir2)  in globalVar.py

logprint("jscmd.py executed")
logprint("current path:"+current_path)
#/gui/jscmd.py?c=gzol&z=zona1&u=marco&p=1234

cmd_type=re.search('c=(.+?)&',current_path).group(1) 
logprint(cmd_type)




if cmd_type=="gzol":  #get zone object list
  logprint("gzol cmd found")
  #'{"msg":{"zoneName":"zona1","list_of_objects":["obj1","obj2","OBJ3"]  } }'
  zone_name=re.search('z=(.+?)&',current_path).group(1) 
  logprint("zone name:"+zone_name)

  if zone_name in list(zoneDict):
    obj_name_list=zoneDict[zone_name]["objects"]  
    html='''{"msg":{"zoneName":"'''+zone_name+'''","list_of_objects":'''+json.dumps(obj_name_list, indent=2,sort_keys=True) 
  else:
    html='{"msg":"z_error"}'

else:
  html='{"msg":"cmd_error"}'



web_page=html





















