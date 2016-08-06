"""| This module will set the right timezone to the openwrt system calling:
   | 'ntpd -q -p 0.openwrt.pool.ntp.org' 
   | And executing  'echo "export TZ='+timezone+'">> /etc/profile'
   |
 

"""


from conf import *           # import parameter from conf.py  which will read the data from the  json 

os.system('''ntpd -q -p 0.openwrt.pool.ntp.org''') 
#if os.path.isfile("/etc/profile"):
try:
  
  prof = open('/etc/profile', 'r')
  profile=prof.read()
  prof.close()
   #print profile
  if (string.find(profile,timezone)== -1) :
    os.system('echo "export TZ='+timezone+'">> /etc/profile') ##export TZ="CET-1CEST,M3.5.0,M10.5.0/3"
    print " onos set the timezone to:"+timezone
    os.system("source /etc/profile") #reload the profile to update time
  else:
    print "timezone ok"
  #banana to add the change of the line to change the timezone
except:
  print "error onos can't set the timezone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  errorQueue.put( "error onos can't set the timezone!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
