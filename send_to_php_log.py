
import os,sys,urllib,urllib2,syslog
def send_to_php_log(router_sn,current_hw,current_local_fw,msg,s_mail):


  #http://myonos.com/onos/updates/mail_update.php?sn=RouterOP0000&fw=5.23&msg=check
  try:
    #call http://myonos.com/onos/updates/mail_update.php to send a message
    url = 'http://myonos.com/onos/updates/mail_update.php'
    data = urllib.urlencode({'sn' : router_sn,'hw':current_hw,'fw':current_local_fw,'msg':msg,'pw':'abcdefghi4321','s_mail':s_mail})
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    #urllib2.urlopen("http://myonos.com/onos/updates/mail_update.php?sn="+router_sn+"&fw="+current_local_fw+"&msg="+msg)
  except Exception as e:     
    message="error sending message to php script "
    print(str((e,sys.exc_info()) ) )
    print e.args 



def logprint(message,verbose=1,error_tuple=None):
    
  """
  |Print the message passed  and if the system is in debug mode or if the error is important send a mail
  |Remember, to clear syslog you could use :  > /var/log/syslog
  |To read system log in openwrt type:logread 

  """
# used like this:
#   except Exception as e:
#    message="""error in dataExchanged["cmd"]=="updateObjFromNode" """
#    logprint(message,verbose=10,error_tuple=(e,sys.exc_info()))

  message=str(message)

  if error_tuple!=None: 
    e=error_tuple[0]
    exc_type, exc_obj, exc_tb=error_tuple[1]
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #to print the message in the system log (to read system log in openwrt type:logread )
    message=message+", e:"+str(e.args)+str(exc_type)+str(fname)+" at line:"+str(exc_tb.tb_lineno)

  debug=1
  debug_level=0
  
  if verbose>debug_level or verbose>8:
    syslog.syslog(message) 
    print(message)

 

