import string
status_to_set="0"

def call_mifunction_vers_1():

  for i in range(10):
       
    address_bar="http://192.168.0.100/RouterGL0000/index.html?socket0_RouterGL0000=99&socket0_RouterGL0020=22&socket0_ttgg0000=69"

    equal_position=string.find(address_bar,"=")
    next_point_position=string.find(address_bar,"&",equal_position)
    webobjName=address_bar[0: equal_position]

    if (next_point_position!=-1):
      status_to_set=(  address_bar[(equal_position+1):(next_point_position)]  )
      print "value="+(status_to_set)
    else:                     
      status_to_set=(address_bar[(equal_position):])
      print "value="+(status_to_set)

    address_bar=address_bar[next_point_position-1:]
    while ( ( string.find(address_bar,"&")!=-1)&(len(address_bar)>1 )):
                
      equal_position=string.find(address_bar,"=")
      next_point_position=string.find(address_bar,"&",equal_position)
      webobjName=address_bar[0: equal_position]
                
                #print "cmd:"+cmd
                #print "a:"+address_bar[(equal_position):]
                 
      print "path="+address_bar

      if (next_point_position!=-1):
        status_to_set=(  address_bar[(equal_position+1):(next_point_position)]  )
        print "value="+(status_to_set)
      else:                     
        status_to_set=(address_bar[(equal_position+1):])
        print "value="+(status_to_set)

      address_bar=address_bar[(equal_position+2):] #remove the first '?'

      print "value="+(status_to_set)



def call_mifunction_vers_2a():

  address_bar="http://192.168.0.100/RouterGL0000/index.html?socket0_RouterGL0000=1&socket0_RouterGL0001=0&socket0_RouterGL0001=0 "
  print "fffffffffffffffffffffffffffffffffffffff2"
  for i in range(10):
    path=address_bar[string.find(address_bar,"?"):]  #start from the first "?"  
    path=path.split("&")  
    #path.split("&")
    status_to_set="-1"          
    for a in path:
      try:
        webobjName=a.split("=")[0]
        status_to_set=a.split("=")[1]
      except:
        print "end"
      print "path="+address_bar


      print "value="+(status_to_set)

def call_mifunction_vers_2():

  address_bar="http://192.168.0.100/RouterGL0000/index.html?socket0_RouterGL0000=1&socket0_RouterGL0001=99&socket0_RouterGL0001=770 "
  print "fffffffffffffffffffffffffffffffffffffff2"
  for i in range(10):
    path=address_bar[string.find(address_bar,"?"):]  #start from the first "?"  
    path=path.split("&")  
    #path.split("&")
    status_to_set="-1"          
    for a in path:
      webobjName=re.search('(.+?)=',a).group(1)
      status_to_set=re.search('=(.+?)',a).group(1)
      print "path="+address_bar


      print "value="+(status_to_set)





from time import time
import re
t0 = time()
call_mifunction_vers_1()
t1 = time()
call_mifunction_vers_2()
t2 = time()

print 'function vers1 takes %f' %(t1-t0)
print 'function vers2 takes %f' %(t2-t1)





