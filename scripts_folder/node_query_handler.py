# -*- coding: UTF-8 -*-

"""
| This Modules handles all the query to the nodes.
| it will receive the data from the router_handler and it will send the query to the nodes.
| It will also retry sending the message if the node doesn't answer right or if doesn't answer at all.
| If the nodes confirm the command was received then this module will tell onos to set the web object status 
| to reflect the new node status after the command was received.
|
"""


from globalVar import *



def make_query_to_radio_node(serialCom,node_serial_number,node_address,query):
  """
  | This function make a query to a radio/serial node and wait the answer from the serial gateway.
  | If the answer is positive 
  |   it will add to the priorityCmdQueue the command to change the web_object status
  |   from pending to succesfully changed .
  | If the answer from the node is an error or the node is not responding
  |   the query will be repeated x times before giving up.


  """

  max_retry=20
  for m in range(0,max_retry):   #retry n times to get the answer from node   #retry n times to get the answer from node
    
    # [S_001dw06001_#]
    query=query[0:3]+nodeDict[node_serial_number].getNodeAddress()+query[6:] #change the address query if the node get a new one

    data=serialCom.status.write(query)
    time.sleep(0.01) 
    if data.find("ok"+query[3:])!=-1:      
      return(1) 
    print "answer received from serial port is wrong:"+data+"end_data, trying query the serial,node the query was:"+query[3:]+"end,the number of try is "+str(m) 
    errorQueue.put("answer received from serial port is wrong:"+data+"end_data, trying query the serial,node the query was"+query+"the number of try is "+str(m)+" at:" +getErrorTimeString() )    
    time.sleep(0.1*m) 


  print("Great serial error,answer received from serial port was wrong:"+data+"end_data, trying query the serial,node the query was"+query+"the number of try was "+str(max_retry)+" at:" +getErrorTimeString() )  
             
  errorQueue.put("Great serial error,answer received from serial port was wrong:"+data+"end_data, trying query the serial,node the query was"+query+"the number of try was "+str(max_retry)+" at:" +getErrorTimeString() )  
  return(-1) 





def make_query_to_network_node(node_serial_number,query,objName,status_to_set,user,priority,mail_report_list):
  """
  | This function make a query to a powerline/ethernet node and wait the answer from the node.
  | If the answer is positive 
  |   it will add to the priorityCmdQueue the command to change the web_object status
  |   from pending to succesfully changed .
  | If the answer from the node is an error or the node is not responding
  |   the query will be repeated x times before giving up.


  """

    #time.sleep(0.1) 
  print "make_query_to_network_node() thread executed"
  print "i try this query:"+query
  timeout=0.1
  html_response="local_error_in_router_handler_cant_connect_to_node"    
  
  #wait_timeout=1000

  for m in range(0,8):   #retry n times to get the answer from node
   
    node_address=nodeDict[node_serial_number].getNodeAddress()  #update the node address ..maybe has changed..
    print "connection try number:"+str(m)+"to ip number"+str(node_address)
    html_response="local_error_in_router_handler_cant_connect_to_node"  
    received_answer=""
    flag=0
    while (wait_because_node_is_talking==1):  #the node is talking to onos...wait ...banana to make it for each node..
      print "i rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr" 
      time.sleep(0.1) 
      flag=1
    if flag==1:
      time.sleep(0.2)
 
    try:
      s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to reuse the same address...prevent address already in use error
      s.connect((node_address,node_webserver_port))
    # Protocol exchange - sends and receives
      time_start=time.time()
      s.settimeout(4) #timeout of 2 second ,don't change this!
      s.sendall(query)

      while (exit==0):
        print "s.recv(1024aaaa)"
        resp=""
        try:
          resp = s.recv(1024) 
        except Exception, e  :
          print "error_qqqq retry",e
          errorQueue.put("error0 in make_query_to_network_node() router_handler class trying to query a node the query was"+query+"the number of try is "+str(m)+"error:"+str(e.args)+"at:" +getErrorTimeString() )
          break

        print "after s.recv(1024)"
        received_answer=received_answer+resp 
        #if (time.time()> (time_start+wait_timeout) ):
        #  print "timeout waiting for answer from node....................................................................."
        #  errorQueue.put("timeout waiting for answer from node, the query was:"+query)  
        #  break

        if received_answer.find("_#]")!=-1:
          break
          print resp


        if received_answer.find("ok")!=-1:
         # print "message sent"
          m=1000
          break


      # Close the connection when completed
      s.close()
      print "\ndone"

    except Exception, e  :
      print "error_i retry",e
      errorQueue.put("error2 in make_query_to_network_node() router_handler class trying to query a node the query was"+query+"the number of try is "+str(m) +str(e.args)+"at:" +getErrorTimeString() )    
      print"the query was"+query+"number of try  "+str(m)  

      s.close()


      if m>5:

        timeout=2
      time.sleep(timeout)
      continue


    else:  # the connection was succesfull

    
      if received_answer.find("ok_#]")!=-1:
        print "msg sent correctly"
        html_response=received_answer
        priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })
        return()
        #break
      else:
        html_response=received_answer
        print "answer received is wrong:"+received_answer
        time.sleep(timeout)
        continue


  print "great error the node did not answer also if tried :"+str(m)+"times, the node will not be setted anymore(probably is not connected)"   
  errorQueue.put("great error the node did not answer also if tried :"+str(m)+"times, the node will not be setted anymore(probably is not connected)"    ) 
  return()





def handle_new_query_to_network_node_thread(): 
  """
  | This is a thread function that will run until every request in the queryToNetworkNodeQueue is done.
  | It will get each query from queryToNetworkNodeQueue and call make_query_to_network_node() 
  | While the query is running the current_node_handler_list will contain the node serialnumber being queried
  | In this way onos will avoid to make multiple simultaneos query to the same node.
  
 

  """


  print "executed handle_new_query_to_network_node_thread() "


  global node_query_threads_executing
  try:
    #with lock2_query_threads:
    node_query_threads_executing=node_query_threads_executing+1

    while not queryToNetworkNodeQueue.empty():   #banana maybe to implement Queue.PriorityQueue() to give priority to certain queries
      current_query=queryToNetworkNodeQueue.get()
      #queryToNetworkNodeQueue.task_done() #banana maybe to remove because not usefull
      node_serial_number=current_query["node_serial_number"]
      if (nodeDict[node_serial_number].getNodeActivity()==0):  # the node is inactive
        print "the node"+node_serial_number+"is inactive ,so I delete its query"
        errorQueue.put("the node"+node_serial_number+"is inactive ,so I delete its query")
        continue ##skip to the next query ..

      with lock1_current_node_handler_list:
        if ((node_serial_number not in current_node_handler_list)): #or (node_query_threads_executing==1)):
          current_node_handler_list.append(node_serial_number)
          print "handle_new_query_to_network_node_thread excuted with "+node_serial_number
        else:
          print "node is already being contacted:q->",current_query
          queryToNetworkNodeQueue.put(current_query)
          continue
      print "node_query_threads_executing:",node_query_threads_executing
      #address=current_query["address"]
      query=current_query["query"]
      objName=current_query["objName"]
      status_to_set=current_query["status_to_set"]
      user=current_query["user"]
      priority=current_query["priority"]
      mail_report_list=current_query["mail_report_list"]
      while (wait_because_node_is_talking==1):  #the node is talking to onos...wait ...todo to make it for each node..
        print "i waiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiit"
        time.sleep(0.1)  
        #print "wait!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"  

      make_query_to_network_node(node_serial_number,query,objName,status_to_set,user,priority,mail_report_list)

    
      with lock1_current_node_handler_list:
        print "lock2b from handle_new_query_to_network_node_thread_remove,query_to_node_dict[node_serial_number]"+node_serial_number
        current_node_handler_list.remove(node_serial_number)


      time.sleep(0.1)  #delay to not block the node , now the thread will get the next query to execute
 





#here there is no more queries to make




  except Exception, e :
    print ("main error in handle_new_query_to_network_node_thread"+str(e.args)+"current query:"+str(current_query)) 
    errorQueue.put("main error in handle_new_query_to_network_node_thread:"+str(e.args)+"current query:"+str(current_query)) 



    with lock1_current_node_handler_list:
      try:
        print "lock2c from handle_new_query_to_network_node_thread_remove,query_to_node_dict[node_serial_number]"+node_serial_number
        current_node_handler_list.remove(node_serial_number)
        query_threads_number=query_threads_number-1
      except:
        print "error in current_node_handler_list.remove after main error" 

  if node_query_threads_executing>0:
    node_query_threads_executing=node_query_threads_executing-1
  return()








