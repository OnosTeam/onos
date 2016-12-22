# -*- coding: UTF-8 -*-

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



def make_query_to_radio_node(serialCom,node_serial_number,query,number_of_retry_already_done=0):
  """
  | This function make a query to a radio/serial node and wait the answer from the serial gateway.
  | If the answer is positive 
  |   it will add to the priorityCmdQueue the command to change the web_object status
  |   from pending to succesfully changed .
  | If the answer from the node is an error or the node is not responding
  |   the query will be repeated x times before giving up.


  """

  max_retry=2 
  for m in range(0,max_retry):   #retry n times to get the answer from node   #retry n times to get the answer from node
    
    # [S_001dw06001_#]

 
    node_address=nodeDict[node_serial_number].getNodeAddress()

    query=query[0:3]+node_address+query[6:] #change the address query if the node get a new one

    data=""

    end_of_query=query.find("_#]")

    # [S_ok003sr070811_#]
    expected_confirm="[S_ok"+query[3:end_of_query+3]
     #if data.find("ok"+query[3:end_of_query+3])!=-1:    

    if number_of_retry_already_done!=0:  #look if the node has already answer the previous query..

      for a in serialCom.uart.readed_packets_list:
        if a.find(expected_confirm)!=-1 :  #found the answer
          serialCom.uart.readed_packets_list.remove(a) 
          return (a)

    time.sleep(0.2)  


    if serialCom.uart.ser.isOpen() == False :
      print "serial port is not open in make_query_to_radio_node()"
      priorityCmdQueue.put( {"cmd":"reconnectSerialPort"}) 
    # time.sleep(1)  
      return(-1)


    try:  
      data=serialCom.uart.write(str(query))

      #data=pyserial_port.writeToSerial(query)
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(exc_type, fname, exc_tb.tb_lineno)   
      print str(e.args)
     # time.sleep(2)  


    if data.find(expected_confirm)!=-1:
      return(data)

    if data=="error_reception":
      continue
  
    
    
  
     # return(1) 
    print "expected confirm:"+expected_confirm
    print "uart rx list:"
    print serialCom.uart.readed_packets_list




   # with lock_serial_input:

    #for a in serialCom.uart.readed_packets_list.:

    for i in xrange(len(serialCom.uart.readed_packets_list) - 1, -1, -1):  #iterate the list from the last element to the first
      a=serialCom.uart.readed_packets_list[i]

      if a.find(expected_confirm)!=-1 :  #found the answer
        serialCom.uart.readed_packets_list.pop(i)
        return (a)

      if a=="[S_ertx1_#]":
        serialCom.uart.readed_packets_list.pop(i)
        continue 


    #print "uart rx list after:"
    #print serialCom.uart.readed_packets_list
 


    #print "answer received from serial port is wrong:'"+data+"'end_data, trying query the serial node the expected answer was:"+expected_confirm+",the number of try is "+str(m) 
    errorQueue.put("answer received from serial port is wrong:'"+data+"', trying query the serial node the expected answer was:'"+expected_confirm+"'the number of try is "+str(m)+" at:" +getErrorTimeString() )    
    time.sleep(0.2*m) 


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
        except Exception as e  :
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

    except Exception as e  :
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






def handle_new_query_to_radio_node_thread(serialCom): 
  """
  | This is a thread function that will run until every request in the queryToRadioNodeQueue is done.
  | It will get each query from queryToRadioNodeQueue and call make_query_to_radio_node() 
  | While the query is running the current_node_handler_list will contain the node serialnumber being queried
  | In this way onos will avoid to make multiple simultaneos query to the same node.
  
 

  """


  print "executed handle_new_query_to_radio_node_thread() "

  global node_query_radio_threads_executing
  global next_node_free_address_list
  global nodeDict
  node_query_radio_threads_executing=1

  time_of_write=time.time()  #after n query sent wait a moment to let the remote nodes starts the tranmissions
  old_time_of_write=time.time() 
  time_waiting_for_incoming_msg=time.time()
  threshold_of_time_query=0.1
 
  while not queryToRadioNodeQueue.empty():
    #query_sent_before_delay=query_sent_before_delay+1
    time_of_write=time.time() 
    old_time_of_write=time_of_write 
    time_waiting_for_incoming_msg=time.time() 


    if (time.time()-time_waiting_for_incoming_msg-threshold_of_time_query)>(time_of_write-old_time_of_write):
      time.sleep(0.01)   #need this to allow the serial node to pick up the messages from the radio nodes..
      old_time_of_write=time.time() 
      time_waiting_for_incoming_msg=time.time() 
      time_of_write=time.time() 
      print("wait to allow rx from radio nodes")
      query_sent_before_delay=0
      continue 


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

    node_address=nodeDict[node_serial_number].getNodeAddress()

    query=query[0:3]+node_address+query[6:] #change the address query if the node get a new one

    #if number_of_retry_done>0:
      
    #else:
    #  query_order=query_time-currentRadioQueryPacket[0]  # i used time_when_the_query_was_created - priority..

    print ("current query_order:"+str(query_order)+"for query:"+query)


    node_address=nodeDict[node_serial_number].getNodeAddress()


    query_answer=make_query_to_radio_node(serialCom,node_serial_number,query)
    if query_answer==-1 : #invalid answer received

      if priority==99: #if the priority is 99 then the query will be always retrayed infinites times.
        query_order=time.time()+1 #make the query less important..to allow other queries to run
      else:
        number_of_retry_done=number_of_retry_done+1
        if number_of_retry_done>15:  #if greater that n don't repeat the query.
          print ("i retried the query:"+query+"more than 15 times , I giveup")
          errorQueue.put("i retried the query:"+query+"more than 15 times , I giveup")
          continue

        if (time.time()-query_time )>100:
          #if more than n seconds has passed since the query was made the first time..don't repeat the query.
          print ("i retried the query "+query+"more than 100 seconds , I giveup")
          errorQueue.put("i retried the query:"+query+"more than 100 seconds  , I giveup")
          continue
        query_order=time.time()+queryToRadioNodeQueue.qsize() #make the query less important..to allow other queries to run   



     
      queryToRadioNodeQueue.put((query_order,query,node_serial_number,number_of_retry_done,query_time,objName,status_to_set,user,priority,mail_report_list,cmd))

    else:##if the query was accepted from the radio/serial node
      #since onos was able to talk to the node I update the LastNodeSync
      layerExchangeDataQueue.put( {"cmd":"updateNodeAddress","nodeSn":node_serial_number,"nodeAddress":node_address}) 

      if cmd=="set_address":
        new_address=status_to_set
        int_address=int(new_address)
        if int_address not in next_node_free_address_list:
          next_node_free_address_list.append(int_address) 
        continue  #this cmd don't need to change webobject..so i continue      

      priorityCmdQueue.put( {"cmd":"setSts","webObjectName":objName,"status_to_set":status_to_set,"write_to_hw":0,"user":user,"priority":priority,"mail_report_list":mail_report_list })
      




  
  node_query_radio_threads_executing=0
  print "handle_new_query_to_radio_node_thread closed"
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




  except Exception as e :
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








