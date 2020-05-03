import paho.mqtt.client as mqtt
#pip3 install paho-mqtt
#or
#pip install paho-mqtt  #for python2


# The callback for when the client receives a CONNACK response from the server.
def mqtt_on_connect_method(client, userdata, rc):
  print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
  client.subscribe("$SYS/#")





# The callback for when a PUBLISH message is received from the server.
def mqtt_on_message_method(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  if msg.topic=="prova":
    print ("received"+str(msg.payload)+"from topic:"+msg.topic)


mqtt_client = mqtt.Client()
mqtt_client.username_pw_set("mqtt-onos", password="onosmqtt1234")
mqtt_client.on_connect = mqtt_on_connect_method
mqtt_client.on_message = mqtt_on_message_method
mqtt_client.connect("192.168.1.110", 1883, 60)# connect(host, port=1883, keepalive=60, bind_address="")

topic="prova"

#mqtt_client.publish(topic, payload=None, qos=0, retain=False)

mqtt_client.subscribe("#", qos=0)  # subscrive to all topics except for topics that start with a $ (these are normally control topics anyway). 
mqtt_client.subscribe("spk-socket/channel-0", qos=0)
mqtt_client.on_message = mqtt_on_message_method



# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()



#zigbee2mqtt/0x00158d000444618a {"battery":100,"voltage":3015,"temperature":22.08,"humidity":69.49,"pressure":998,"linkquality":70}
#zigbee2mqtt/0x00158d000444618a {"battery":100,"voltage":3015,"temperature":22.08,"humidity":63.39,"pressure":998,"linkquality":70}
#zigbee2mqtt/0x00158d00040aaf3e {"battery":100,"voltage":3075,"contact":false,"linkquality":28}
#zigbee2mqtt/0x00158d00040aaf3e {"battery":100,"voltage":3075,"contact":true,"linkquality":23}
#zigbee2mqtt/0x00158d00040aaf3e {"battery":100,"voltage":3075,"contact":false,"linkquality":15}
