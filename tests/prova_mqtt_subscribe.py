import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
  print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
  client.subscribe("$SYS/#")





# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  if msg.topic=="prova":
    print ("received"+str(msg.payload)+"from topic:"+msg.topic)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message




client.connect("192.168.1.2", 1883, 60)# connect(host, port=1883, keepalive=60, bind_address="")

topic="prova"

#client.publish(topic, payload=None, qos=0, retain=False)

client.subscribe("#", qos=0)  # subscrive to all topics except for topics that start with a $ (these are normally control topics anyway). 
client.subscribe("spk-socket/channel-0", qos=0)

client.on_message = on_message



# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
