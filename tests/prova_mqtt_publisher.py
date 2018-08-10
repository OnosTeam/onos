import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
  print("Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
  client.subscribe("$SYS/#")



client = mqtt.Client()
client.on_connect = on_connect





client.connect("192.168.1.2", 1883, 60) # connect(host, port=1883, keepalive=60, bind_address="")

topic="prova"

client.publish(topic, payload="value=1", qos=0, retain=False)

topic="sonoff/channel-0"
client.publish(topic, payload="toggle", qos=0, retain=False)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
