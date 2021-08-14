import time
import paho.mqtt.client as mqtt
import multiprocessing as mp
import json

start=False

with open('config.json') as file:
    
    json_data = json.load(file)
    # Client, user and device details.
    serverUrl = json_data['mqttServerUrl']
    clientId = json_data['clientId']
    device_name = json_data['device_name']
    tenant = json_data['tenant']
    username = json_data['username']
    password = json_data['password']

def on_message(client, userdata, message):
    
    global start
    
    payload = message.payload.decode("utf-8")
    print(" < received message " + payload)
    print(payload[payload.rfind(",")+1:len(payload)])
    
    if payload[payload.rfind(",")+1:len(payload)].strip()=="start":
        start=True
    if payload[payload.rfind(",")+1:len(payload)].strip()=="stop":
        start=False
    if payload[payload.rfind(",")+1:len(payload)].strip()=="reset":
        send_BikeStartSession()
    if payload.startswith("510"):
        task_queue.put(perform_restart)

    if payload.startswith("511"):
        print('Command Message Received')

def perform_restart():
    
    print("Simulating device restart...")
    publish("c8y/s/us", "501,c8y_Restart", wait_for_ack=True);

    print("...restarting...")
    time.sleep(1)

    publish("c8y/s/us", "503,c8y_Restart", wait_for_ack=True);
    print("...restart completed")
    
def send_BikeSpeedMeasurement(data):
    global start
    if start:
        print("Sending bike speed measurement...")
        publish("c8y/s/us", "200,BikeSpeedMeasurement,S,{},m/s".format(data))
    
def send_BikeRevolutions(data):
    global start
    if start:
        print("Sending bike revolutions...")
        publish("c8y/s/us", "200,BikeRevolutions,R,{},rev".format(data))
    
def publish(topic, message, wait_for_ack=False):
    
    QoS = 2 if wait_for_ack else 0
    message_info = client.publish(topic, message, QoS)
    
    if wait_for_ack:
        print(" > awaiting ACK for {}".format(message_info.mid))
        message_info.wait_for_publish()
        print(" < received ACK for {}".format(message_info.mid))
        
def on_publish(client, userdata, mid):
    
    print(" > published message: {}".format(mid))
    
def initiate_measurements():
    
    print("Initiating the measurements...")
    data=0
    publish("c8y/s/us", "200,SessionSpeed,SS,{},m/s".format(data))
    publish("c8y/s/us", "200,SessionAverageSpeed,SAS,{},m/s".format(data))
    publish("c8y/s/us", "200,SessionMaximumSpeed,SMS,{},m/s".format(data))
    publish("c8y/s/us", "200,SessionTotalDistance,STD,{},m".format(data))
    publish("c8y/s/us", "200,SessionTotalCaloriesBurnt,STCB,{},cal".format(data))
    
def send_BikeStartSession():
    
    print("Starting new session on cumulocity...")
    publish("c8y/s/us", "400,BikeStartSession,Starting new bike session...")
    time.sleep(1)
    initiate_measurements()
    
# Connect the client to Cumulocity IoT and register a device.
client = mqtt.Client(clientId)
client.on_message = on_message
client.on_publish = on_publish
client.connect(serverUrl)
client.loop_start()

time.sleep(3)
# The supported operations for this device, in this case it is c8y_Restart and c8y_Command , which allows for the device to be
# restarted and sent for other Commands.
publish("c8y/s/us", "114,c8y_Restart,c8y_Command")

print("Device registered successfully!")
# Subscribe to operations.
client.subscribe("c8y/s/ds")
