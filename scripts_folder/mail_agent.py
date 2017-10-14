
#import chardet

"""
| This module handles the onos email system.
| It handles the incoming mails and the outbound email.\n
|

.. warning::

  | You musn't have the fowarding from the mail you use as onos income mail. 
  | You musn't use a mail programm to automaticly download the mail. 
  |   Because otherwise the mail will be donwloaded elsewhere and onos will not be able to read it since it reads only the unreaded mails.
"""

from globalVar import logprint
import sys

#onos_mail_account="electronicflame@gmail.com"
#onos_mail_pw='password'
#mail_imap='imap.gmail.com'
#receiver_user_mail=onos_mail_account  #JUST FOR TEST	
#smtp_port="587"
#smtp_server='smtp.gmail.com'

#onos_mail_conf={"mail_account":"electronicflame@gmail.com","pw":"password","smtp_port":"587","smtp_server":"smtp.gmail.com","mail_imap":"imap.gmail.com"}

def sendMail(receiver_user_mail,mailtext,mailSubject,mail_conf,smtplib,string):
  """
  This function send a mail from the onos system.

  .. warning::

   If you want to send a mail, is better to add it to the mailQueue using:     
   mailQueue.put({"mail_address":m_sender,"mailText":mailText,"mailSubject":mailSubject})
   In this way the mail will be sent after the previous ones are sent. 

  :param receiver_user_mail: 
    The mail receiver

  :param mailtext: 
    The mail text content

  :param mailSubject: 
    The mail subject
  
  :param mail_conf: 
    The dictionary containing the mail credential,server address and smtp_port. (for now i tried only with gmail). 

  :param imaplib: 
    The imaplib library imported in globalVar.py

  :param string: 
    The string library imported in globalVar.py


  """

  logprint("sendMail executed ")
  onos_mail_pw=mail_conf["pw"]
  smtp_port=mail_conf["smtp_port"]
  smtp_server=mail_conf["smtp_server"]
  onos_mail_account=mail_conf["mail_account"]
  SUBJECT =mailSubject
  TO = receiver_user_mail
  FROM = onos_mail_account
  text = mailtext
  BODY = string.join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Subject: %s" % SUBJECT ,
        "",
        mailtext
        ), "\r\n")  


#Next, log in to the server

  # the try must be on where the function is called

  sent=1
  try:
    server = smtplib.SMTP(smtp_server+':'+smtp_port)  

    server.starttls()

    server.login(onos_mail_account, onos_mail_pw)

    msg = BODY

    server.sendmail(onos_mail_account, receiver_user_mail, msg)
    

  except Exception as e :
    message="error in mail sending mail_agend"
    logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
    sent=e.args
  return(sent)
  


def get_text(msg):
    """ | Given the python mail object, parses email message text and return the mail text content.
        | This doesn't support infinite recursive parts, but mail is usually not so naughty.
    """
    text = ""
    if msg.is_multipart():
        html = None
        for part in msg.get_payload():
            if part.get_content_charset() is None:
                charset ='ascii'# chardet.detect(str(part))['encoding']
                logprint("error charset forced to ashii")
            else:
                charset = part.get_content_charset()
            if part.get_content_type() == 'text/plain':
                text = unicode(part.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
            if part.get_content_type() == 'text/html':
                html = unicode(part.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
            if part.get_content_type() == 'multipart/alternative':
                for subpart in part.get_payload():
                    if subpart.get_content_charset() is None:
                        charset ='ascii'# chardet.detect(str(subpart))['encoding']
                        logprint("error charset forced to ashii")
                    else:
                        charset = subpart.get_content_charset()
                    if subpart.get_content_type() == 'text/plain':
                        text = unicode(subpart.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')
                    if subpart.get_content_type() == 'text/html':
                        html = unicode(subpart.get_payload(decode=True),str(charset),"ignore").encode('utf8','replace')

        if html is None:
            return text.strip()
        else:
            return html.strip()
    else: 
        if (msg.get_content_charset())is not None:
          text = unicode(msg.get_payload(decode=True),msg.get_content_charset(),'ignore').encode('utf8','replace')
        else: 
          text = unicode(msg.get_payload(decode=True)).encode('utf8','replace')
        return text.strip()


def receiveMail(mail_conf,imaplib,email):
  """
  | This function connect to the mail server and download all the unread mails.
  | Then if a mail contain the "onos=" string, the mail is added to a list which  will be returned. 
  | Otherwise the mail is setted as unreaded in the mail server since is not a mail command for onos.
  | To connect to the mail server the credential contained in mail_conf[] dictionary will be used.

  :param mail_conf: 
    The dictionary containing the mail credential,server address and smtp_port. (for now i tried only with gmail). 

  :param imaplib: 
    The imaplib library imported in globalVar.py

  :param email: 
    The email library imported in globalVar.py 

  """
  logprint("receiveMail() executed")
  onos_received_mails=[]  #a list of list where the data are (msg_sender,msg_subject,msg_text)
  mail_imap=mail_conf["mail_imap"]
  onos_mail_account=mail_conf["mail_account"]
  onos_mail_pw=mail_conf["pw"]
  mail = imaplib.IMAP4_SSL(mail_imap)
  try:
    
    (retcode, capabilities) = mail.login(onos_mail_account,onos_mail_pw)
  except:
    #print "error mailagent ,  wrong username/password or no internet connection"
    return(-1)

  mail.list()
  mail.select('inbox')

  n=0
  (retcode, messages) = mail.search(None, '(UNSEEN)')
  if retcode == 'OK':

     for num in messages[0].split() :
        #print 'Processing '
        #print "msg number:",n
        n=n+1
        typ, data = mail.fetch(num,'(RFC822)')
        #i=0
        for response_part in data:

           if isinstance(response_part, tuple):
               msg = email.message_from_string(response_part[1])
             #print original.keys()
             #print original
               msg_content_text=get_text(msg).decode('UTF-8')  #convert to utf8
               #example of msg_sender: clive cusslar <clive_cusslar@gmail.com>
               msg_sender=msg['From'].strip(">").strip().lower().split("<") #get lower case without start space,split by <

               if len(msg_sender)>1:
                 msg_sender=msg_sender[1]  # remove the name from  "clive cusslar <clive_cusslar@gmail.com>"  
               else:
                 msg_sender=msg_sender[0]  # and 
               #removes name  ...get only the mail
               msg_sender= msg_sender.decode('UTF-8')  #convert to utf8
               msg_subject= msg['Subject'].decode('UTF-8')  #convert to utf8
               cmd_indicator=u'onos='
               cmd_indicator=cmd_indicator.decode('UTF-8')  #convert to utf8              
               # example : onos=cmd:so,arg:button1_RouterGL0000,st:1,      note the end ","  must be used
               
               start=msg_content_text.find(u"onos=")
               start2=msg_content_text.find("onos=")
               if (start!=-1)|(start2!=-1):
                 logprint("sender:"+msg['From']+",msg_text="+str(msg_content_text)+"onos= found in the mail" )
                 msg_content_text=msg_content_text[start:]
                 typ, data = mail.store(num,'+FLAGS','\\Seen')  #cmd received...set as mail readed
                 #mailtext="onoscmd received i set the webobject to"
                 onos_received_mails.append((msg_sender,msg_subject,msg_content_text))
               else:
                 typ, data = mail.store(num,'-FLAGS','\\Seen')  #not a mail containing onos cmd .. set it as not readed
                 logprint("mail without onos cmd")
                #the -FLAGS set it as unreaded ---the +FLAGS set it as readed

         #print "i=",i
         #i=i+1       

  logprint("received mails:"+str(len(onos_received_mails)) ) 
  return (onos_received_mails) # return a list of received mail that have "onos=" inside the text




#for a in mail_to_send:
#  sendMail(a[0],a[1])




