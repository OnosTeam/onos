import socket,time



# Connect as client to a selected server
# on a specified port

retry_times=10
timeout=1
i=0
received_answer=""
message_to_send="onos_a07v100s0001_#]"
while i<retry_times:
  i=i+1
  # Set up a TCP/IP socket

  
  try:
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(("192.168.0.107",9000))
    #s.settimeout(5)


    # Protocol exchange - sends and receives
    s.settimeout(5) #timeout of 5 second
    s.send(message_to_send)
    
    while True:
      try:  
        resp = s.recv(1024)

      except:
        print "error reception" 
        break

      received_answer=received_answer+resp 
      if resp.endswith("_#]"):
        break
      print resp,


      if received_answer.find("_#]")==-1:
        print "message sent correctly but error reception" 
        i=1000
        break


    # Close the connection when completed
    s.close()
    print "\ndone"

  except Exception, e  :
    print "error_i retry",e
    s.close()
    time.sleep(timeout)
    continue


  else:  # the connection was succesfull

    
    if received_answer==message_to_send:
      print "message sent correctly"
      break
    else:
      print "answer received is wrong"
      continue




