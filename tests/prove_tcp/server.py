import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the socket to the port
server_address = ('192.168.0.102', 82)
print >>sys.stderr, 'starting up on %s port %s' % server_address


sock.bind(server_address)
sock.listen(1)

# Listen for incoming connections


while True:



    # Wait for a connection
    sock.settimeout(60) 
    print >>sys.stderr, 'waiting for a connection'
    try:
      connection, client_address = sock.accept()  
    except socket.timeout:
      print "timeout in receiving!!!"
      try:
        connection.close()
        print "connection  closed"    
      except:
        print "connection alredy closed"   




      
    else: # if the try was executed without errors
      received_message=""
      try:
          print >>sys.stderr, 'connection from', client_address

          # Receive the data in small chunks and retransmit it

          while True:

              data = connection.recv(1024) #accept data till 1024 bytes


              received_message=received_message+data 


  
              print >>sys.stderr, 'received "%s"' % data
              if data:
                  connection.settimeout(2.0) 
                  print >>sys.stderr, 'sending data back to the client'
                   
                  #connection.sendall(data) 

                  if data.endswith("_#]"):   # if the message is completed close the connection
                    print "end line received!!!! "
                    connection.close()
                    break

              else:
                print >>sys.stderr, 'no more data from', client_address
                connection.close()
                break
    

      except Exception, e  :
        print "error tcp connection",e
    
      print "received_message",received_message   

           
    try:
        # Clean up the connection, close() is always called, even in the event of an error.
      connection.close()
    except:
      print "connection not created" 




