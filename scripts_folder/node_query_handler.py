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
| This Modules handles all the query to the nodes.
| it will receive the data from the router_handler and it will send the query to the nodes.
| It will also retry sending the message if the node doesn't answer right or if doesn't answer at all.
| If the nodes confirm the command was received then this module will tell onos to set the web object status 
| to reflect the new node status after the command was received.
|
"""


from conf import *

#import pyserial_port

def check_answer_to_radio_query(expected_confirm,serialCom):
  copy_of_readed_packets_list=serialCom.uart.readed_packets_list
  i=len(serialCom.uart.readed_packets_list)-1 
  while i>0:  #iterate the list from the last element to the first
    try:
      a=copy_of_readed_packets_list[i]          
      logprint("check of all received answers0 current one was:"+str(a))
      if a.find(expected_confirm)!=-1 :  #found the answer
        logprint("I have found the answer I was looking for")
        while a in serialCom.uart.readed_packets_list:  # remove all the occurences of the answer 
          serialCom.uart.readed_packets_list.remove(a)  
        return (a)

      while "[S_er" in a and a in serialCom.uart.readed_packets_list :
        serialCom.uart.readed_packets_list.remove(a)
      while "[S_nocmd" in a and a in serialCom.uart.readed_packets_list:
        serialCom.uart.readed_packets_list.remove(a)
   
      i=i-1 

    except Exception as e  :
      message="error in check_answer_to_radio_query()  "
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 
      return(-1)

  return(-1)




def make_query_to_radio_node(serialCom,node_serial_number,query,number_of_retry_already_done):
  """
  | This function make a query to a radio/serial node and wait the answer from the serial gateway.
  | If the answer is positive 
  |   it will add to the priorityCmdQueue the command to change the web_object status
  |   from pending to succesfully changed .
  | If the answer from the node is an error or the node is not responding
  |   the query will be repeated x times before giving up.


  """
  logprint("make_query_to_radio_node executed with number_of_retry_already_done:"+str(number_of_retry_already_done))
  max_retry=1 
  answer_received=""
  for m in range(0,max_retry):   #retry n times to get the answer from node  
    
    # [S_001dw06001_#]

    if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node is inactive
      logprint("error01_radio_query,the node"+node_serial_number+"is inactive ,so I delete its query",verbose=8)
      return()

 
    node_address=nodeDict[node_serial_number].getNodeAddress()

    query=query[0:3]+node_address+query[6:] #change the address query if the node get a new one

    data=""

    end_of_query=query.find("_#]")

    # [S_ok003sr070811_#]
    expected_confirm="[S_ok"+query[3:end_of_query+3]
     #if data.find("ok"+query[3:end_of_query+3])!=-1:    
    logprint("expected_confirm:"+expected_confirm+"__")

    
    if number_of_retry_already_done!=0:  #look if the node has already answer the previous query..
      
      logprint("current serialCom.uart.readed_packets_list:"+str(serialCom.uart.readed_packets_list))
      answer_received=check_answer_to_radio_query(expected_confirm,serialCom)
      try:  #need this because sometimes it is an int..and some time is null..
        if answer_received.find(expected_confirm)!=-1 :  #found the answer
          return(answer_received)
      except:
        pass


    try:  
      data=serialCom.uart.write(query)
    except Exception as e:
      message="error writing to serial port, data to send:"+query+", at:"+getErrorTimeString()
      logprint(message,verbose=8,error_tuple=(e,sys.exc_info()))  

    if data.find(expected_confirm)!=-1 :  #found the answer
      while data in serialCom.uart.readed_packets_list:  # remove all the occurences of the answer 
        serialCom.uart.readed_packets_list.remove(data)  

      return(data)

    answer_received=check_answer_to_radio_query(expected_confirm,serialCom)
    try:  #need this because sometimes it is an int..and some time is null..
      if answer_received.find(expected_confirm)!=-1 :  #found the answer
        return(answer_received)
    except:
      pass
#    time.sleep(0.4)   #wait a bit between the retry..

  logprint("Great serial error,answer received from serial port was wrong:"+data+"end_data, trying query the serial,node the query was"+query+"the number of try was "+str(max_retry)+" at:" +getErrorTimeString() )


  return(-1) 







def make_query_to_http_node(node_serial_number,query,query_expected_answer,objName,status_to_set,user,priority,mail_report_list):
  """
  | This function make a http query to a ethernet/wifi/powerline node and wait the answer from the node.
  | If the answer is positive 
  |   it will add to the priorityCmdQueue the command to change the web_object status
  |   from pending to succesfully changed .
  | If the answer from the node is an error or the node is not responding
  |   the query will be repeated x times before giving up.
  |

  """

    #time.sleep(0.1) 

  logprint("make_query_to_http_node() thread executed")
  logprint( "i try this query:"+query)
  timeout=0.1
  html_response="local_error_in_router_handler_cant_connect_to_node"    
  
  #wait_timeout=1000

  for m in range(0,12):   #retry n times to get the answer from node
 

    if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node is inactive
      logprint("error01_http_query,the node"+node_serial_number+"is inactive ,so I delete its query",verbose=8)
      return()

   
    node_address=nodeDict[node_serial_number].getNodeAddress()  #update the node address ..maybe has changed..
    logprint("connection try number:"+str(m)+"to ip number"+str(node_address) )
    html_response="local_error_in_router_handler_cant_connect_to_node"  
    received_answer=""
    flag=0
    #while (wait_because_node_is_talking==1):  #the node is talking to onos...wait ...banana to make it for each node..
    #  logprint("i wait_because_node_is_talking ..............") 
    #  time.sleep(0.1) 

 
    try:
      if m<5:
            
        response = url_request_manager.request('GET',query,timeout=Timeout(total=2.0))

            #response=urllib2.urlopen(req, timeout=10) 
      else:
            #response=urllib2.urlopen(req, timeout=1)
        response = url_request_manager.request('GET',query,timeout=Timeout(total=5.0))

      http_response = response.data
      message="node http_response:"+http_response+"end response"
      logprint(message,verbose=3) 
      if (http_response.find(query_expected_answer)!=-1):   #if the server response is ok  then break the loop
        message="answer is the expected one:("+query_expected_answer+"), I will change html"
        logprint(message,verbose=3)    
        priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })
        return()
      else:
        message="error the node answer with:"+http_response+"i will retry,try number:"+str(m)+"the query was"+query+"the expected_answer was"+query_expected_answer
        logprint(message,verbose=4) 

        m=m+1       




      if m>5:

        timeout=2
        time.sleep(timeout)
        continue




    except Exception as e  :
      message="error2 in make_query_to_http_node() trying to query a node the query was"+query+"the number of try is "+str(m)+"at:"+getErrorTimeString() 
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
      continue 


  message="error3 in make_query_to_http_node()  the query was"+query+"the number of try is "+str(m)+"at:"+getErrorTimeString()+"the answer from node was:"+http_response+",too many retry I give up" 
  logprint(message,verbose=9) 



  return()









def make_query_to_tcp_node(node_serial_number,query,query_expected_answer,objName,status_to_set,user,priority,mail_report_list):
  """
  | This function make a query to a powerline/ethernet node and wait the answer from the node.
  | If the answer is positive 
  |   it will add to the priorityCmdQueue the command to change the web_object status
  |   from pending to succesfully changed .
  | If the answer from the node is an error or the node is not responding
  |   the query will be repeated x times before giving up.


  """

    #time.sleep(0.1) 

  logprint("make_query_to_tcp_node() thread executed")
  logprint( "i try this query:"+query)
  timeout=0.1
  html_response="local_error_in_router_handler_cant_connect_to_node"    
  
  #wait_timeout=1000

  for m in range(0,8):   #retry n times to get the answer from node
   
    if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node is inactive
      logprint("error01_tcp_query_the node"+node_serial_number+"is inactive ,so I delete its query",verbose=8)
      return()
    node_address=nodeDict[node_serial_number].getNodeAddress()  #update the node address ..maybe has changed..
    logprint("connection try number:"+str(m)+"to ip number"+str(node_address) )
    html_response="local_error_in_router_handler_cant_connect_to_node"  
    received_answer=""
    flag=0
    #while (wait_because_node_is_talking==1):  #the node is talking to onos...wait ...banana to make it for each node..
    #  logprint("i wait_because_node_is_talking ..............") 
    #  time.sleep(0.1) 
    #  flag=1
    #if flag==1:
    #  time.sleep(0.2)
 
    try:
      s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to reuse the same address...prevent address already in use error
      s.connect((node_address,node_webserver_port))
    # Protocol exchange - sends and receives
      time_start=time.time()
      s.settimeout(4) #timeout of 2 second ,don't change this!
      s.sendall(query)

      while (exit==0):
        logprint("s.recv(1024aaaa)")
        resp=""
        try:
          resp = s.recv(1024) 
        except Exception as e  :
          message="error0 in make_query_to_network_node() router_handler class trying to query a node the query was"+query+"the number of try is "+str(m)
          logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 
          break

        logprint("after s.recv(1024)")
        received_answer=received_answer+resp 
        #if (time.time()> (time_start+wait_timeout) ):
        #  print "timeout waiting for answer from node....................................................................."
        #  break

        if received_answer.find("_#]")!=-1:
          break
          logprint(resp)


        if received_answer.find("ok")!=-1:
         # print "message sent"
          m=1000
          break


      # Close the connection when completed
      s.close()
      logprint("\ndone")

    except Exception as e  :
      message="error2 in make_query_to_network_node() router_handler class trying to query a node the query was"+query+"the number of try is "+str(m)+"at:"+getErrorTimeString() 
      logprint(message,verbose=9,error_tuple=(e,sys.exc_info())) 

      s.close()


      if m>5:

        timeout=2
      time.sleep(timeout)
      continue


    else:  # the connection was succesfull

    
      if received_answer.find("ok_#]")!=-1:
        logprint("msg sent correctly")
        html_response=received_answer
        priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })
        return()
        #break
      else:
        html_response=received_answer
        logprint("answer received is wrong:"+received_answer)
        time.sleep(timeout)
        continue


  logprint("great error the node did not answer also if tried :"+str(m)+"times, the node will not be setted anymore(probably is not connected)")   

  return()






def handle_new_query_to_radio_node_thread(serialCom): 
  """
  | This is a thread function that will run until every request in the queryToRadioNodeQueue is done.
  | It will get each query from queryToRadioNodeQueue and call make_query_to_radio_node() 

  
 

  """


  logprint("executed handle_new_query_to_radio_node_thread() ")

  global node_query_radio_threads_executing
  global node_used_addresses_list
  global nodeDict
  node_query_radio_threads_executing=1

  time_of_write=time.time()  #after n query sent wait a moment to let the remote nodes starts the tranmissions
  old_time_of_write=time.time() 
  time_waiting_for_incoming_msg=time.time()
  threshold_of_time_query=0.1
 
  while not queryToRadioNodeQueue.empty():
    time.sleep(0.3)   #need this to allow the serial node to pick up the messages from the radio nodes..




    #query_sent_before_delay=query_sent_before_delay+1
    time_of_write=time.time() 
    old_time_of_write=time_of_write 
    #time_waiting_for_incoming_msg=time.time() 


    if (time.time()-time_waiting_for_incoming_msg-threshold_of_time_query)>(time_of_write-old_time_of_write):
      logprint("wait to allow rx from radio nodes")
      time.sleep(0.7)   #need this to allow the serial node to pick up the messages from the radio nodes..
      old_time_of_write=time.time() 
      time_waiting_for_incoming_msg=time.time() 
      time_of_write=time.time() 
      query_sent_before_delay=0



    currentRadioQueryPacket=queryToRadioNodeQueue.get() #get the tuple:                                                 

#((query_order,query,node_serial_number,number_of_retry_done,query_time,objName,status_to_set,user,priority,mail_report_list,cmd))
    query_order=currentRadioQueryPacket[0]
    query=currentRadioQueryPacket[1]   
    node_serial_number=currentRadioQueryPacket[2]
    number_of_retry_done=currentRadioQueryPacket[3]
    query_time=currentRadioQueryPacket[4]
    objName=currentRadioQueryPacket[5]
    status_to_set=currentRadioQueryPacket[6]
    user=currentRadioQueryPacket[7]
    priority=currentRadioQueryPacket[8]
    mail_report_list=currentRadioQueryPacket[9]
    cmd=currentRadioQueryPacket[10]

    if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node is inactive
      logprint("error00_radio_handler, the node"+node_serial_number+"is inactive ,so I delete its query",verbose=8)
      continue         ##skip to the next query ..


    node_address=nodeDict[node_serial_number].getNodeAddress()

    query=query[0:3]+node_address+query[6:] #change the address query if the node get a new one

    #if number_of_retry_done>0:
      
    #else:
    #  query_order=query_time-currentRadioQueryPacket[0]  # i used time_when_the_query_was_created - priority..

    logprint("current query_order:"+str(query_order)+"for query:"+query)


    query_answer=make_query_to_radio_node(serialCom,node_serial_number,query,number_of_retry_done)
    if query_answer==-1 : #invalid answer received
      logprint("error query_answer wrong UUUUUUUUuuuuuuuuuuuuuuUUUUUUUUUUUUuuuuuuuuuuu",verbose=4)
      number_of_retry_done=number_of_retry_done+1
      if priority==99: #if the priority is 99 then the query will be always retrayed infinites times.
        query_order=time.time()+1 #make the query less important..to allow other queries to run
        if number_of_retry_done>35:  #if greater that n wait a bit
          logprint("sleep a bit because number_of_retry_done>35")
          time.sleep(0.5)   #need this to allow the serial node to pick up the messages from the radio nodes..
      else:
        query_order=time.time()+queryToRadioNodeQueue.qsize() #make the query less important..to allow other queries to run   
        if number_of_retry_done>20:  #if greater that n don't repeat the query.
          logprint("i retried the query:"+query+"more than 20 times , I giveup",verbose=10)
          continue

        if (time.time()-query_time )>500:
          #if more than n seconds has passed since the query was made the first time..don't repeat the query.
          logprint("i retried the query "+query+"more than 500 seconds ago , I giveup",verbose=10)

          continue

      queryToRadioNodeQueue.put((query_order,query,node_serial_number,number_of_retry_done,query_time,objName,status_to_set,user,priority,mail_report_list,cmd))

    else:##if the query was accepted from the radio/serial node
      node_fw=nodeDict[node_serial_number].getNodeFwVersion()
      #since onos was able to talk to the node I update the LastNodeSync
      nodeDict[node_serial_number].updateLastNodeSync(time.time())

      #layerExchangeDataQueue.put( {"cmd":"updateNodeAddress","nodeSn":node_serial_number,"nodeAddress":node_address,"nodeFw":node_fw}) 

      if cmd=="set_address":
        new_address=status_to_set
        int_address=int(new_address)
        if int_address not in node_used_addresses_list:
          node_used_addresses_list.append(int_address) 
        continue  #this cmd don't need to change webobject..so i continue      

      priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })
      

  node_query_radio_threads_executing=0
  logprint("handle_new_query_to_radio_node_thread closed")
  return()



def handle_new_query_to_network_node_thread(): 
  """
  | This is a thread function that will run until every request in the queryToNetworkNodeQueue is done.
  | It will get each query from queryToNetworkNodeQueue and call make_query_to_network_node() 
  | While the query is running the current_node_handler_dict will contain the node serialnumber 
  | being queried as key and the query as value
  | Todo: implement the same safe strategy to queue the not successful query to retry them later...like done in handle_new_query_to_radio_node_thread

 

  """


  logprint("executed handle_new_query_to_network_node_thread() ")
  query_type="http"   #if query_type== tcp it will send a tcp 

  global node_query_network_threads_executing
  try:
    #with lock2_query_threads:
    node_query_network_threads_executing=node_query_network_threads_executing+1

    while not queryToNetworkNodeQueue.empty():   #banana maybe to implement Queue.PriorityQueue() to give priority to certain queries
      current_query=queryToNetworkNodeQueue.get()
      #queryToNetworkNodeQueue.task_done() #banana maybe to remove because not usefull
      node_serial_number=current_query["node_serial_number"]

      logprint("node_query_network_threads_executing:"+str(node_query_network_threads_executing))

      if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node is inactive
        logprint("error00_network_handler, the node"+node_serial_number+"is inactive ,so I delete its query",verbose=8)
        continue ##skip to the next query ..



      #address=current_query["address"]
      query=current_query["query"]
      query_expected_answer=current_query["query_expected_answer"]
      objName=current_query["objName"]
      status_to_set=current_query["status_to_set"]
      user=current_query["user"]
      priority=current_query["priority"]
      mail_report_list=current_query["mail_report_list"]
      #while (wait_because_node_is_talking==1):  #the node is talking to onos...wait ...todo to make it for each node..
      #  logprint("the node is talking to onos...wait iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiit")
      #  time.sleep(0.1)  
        #print "wait!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"  

      with lock1_current_node_handler_dict:
        if ((node_serial_number not in current_node_handler_dict)): #or (node_query_network_threads_executing==1)):
          current_node_handler_dict[node_serial_number]=query
          logprint("handle_new_query_to_network_node_thread excuted with "+node_serial_number)
        else:
          logprint("node is already being contacted:q->"+current_query["query"] )
          if current_node_handler_dict[node_serial_number] in current_node_handler_dict.values(): 
            #there is already this query pending...I will not add another 
            continue
          else:
            queryToNetworkNodeQueue.put(current_query) 



      if query_type=="http":  
        make_query_to_http_node(node_serial_number,query,query_expected_answer,objName,status_to_set,user,priority,mail_report_list)
      else:
        make_query_to_tcp_node(node_serial_number,query,query_expected_answer,objName,status_to_set,user,priority,mail_report_list)
    
      with lock1_current_node_handler_dict:
        logprint("lock2b from handle_new_query_to_network_node_thread_remove,query_to_node_dict[node_serial_number]"+node_serial_number)
        del current_node_handler_dict[node_serial_number]
         


      time.sleep(0.1)  #delay to not block the node , now the thread will get the next query to execute
 





#here there is no more queries to make




  except Exception as e :
    message="main error in handle_new_query_to_network_node_thread, current query:"+str(current_query)
    logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 



    with lock1_current_node_handler_dict:
      try:
        logprint("lock2c from handle_new_query_to_network_node_thread_remove,query_to_node_dict)[node_serial_number]"+node_serial_number)
        del current_node_handler_dict[node_serial_number]
        if node_query_network_threads_executing>0:
          node_query_network_threads_executing=node_query_network_threads_executing-1
      except Exception as e :
        message="error in current_node_handler_dict remove after main error"
        logprint(message,verbose=8,error_tuple=(e,sys.exc_info())) 

  if node_query_network_threads_executing>0:
    node_query_network_threads_executing=node_query_network_threads_executing-1
  return()








