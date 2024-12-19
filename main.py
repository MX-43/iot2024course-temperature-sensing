from machine import Pin, I2C
import network
import time
import bme280
from umqtt.simple import MQTTClient
import ssl
import config
import usocket as socket
import ustruct as struct
from ubinascii import hexlify

led = Pin("LED", Pin.OUT)

# Variables for calculating temp averages
temp_list = []
temp_avg = 0.0
temp_sum = 0.0
min_change_that_triggers_alert = 0.5
difference_list = []
diff_avg = 0.0
diff_sum = 0.0
threshold_to_return_to_averaging=0.6

# Variables for determining when to transmit the next message
readings_per_cycle = 20 # transmitting roughly every 100 seconds
readings_since_transmit = 0
count_of_alert_readings = 0
min_count_of_alert_readings_before_alert_is_sent = 3
sleep_between_readings = 5000 # 5000 = every 5s /// 120 000 = 2min


# setup wifi
ssid = config.ssid
password = config.pwd

# connect to wifi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() == 3: # connected
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# check if connection successful
if wlan.status() != 3: 
    raise RuntimeError('[ERROR] Failed to establish a network connection')
else: 
    print('[INFO] CONNECTED!')
    network_info = wlan.ifconfig()
    print('[INFO] IP address:', network_info[0])
    
# config ssl connection w Transport Layer Security encryption (no cert)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) # TLS_CLIENT = connect as client not server/broker
context.verify_mode = ssl.CERT_NONE # CERT_NONE = not verify server/broker cert - CERT_REQUIRED: verify

# mqtt client connect
client = MQTTClient(client_id=b'picow', server=config.MQTT_BROKER, port=config.MQTT_PORT,
                    user=config.MQTT_USER, password=config.MQTT_PWD, ssl=context)

client.connect()


# define device, pin connections
i2c = machine.I2C(id=0, scl=machine.Pin("GP21"), sda=machine.Pin("GP20"))
bme = bme280.BME280(i2c=i2c)

def publish(mqtt_client, topic, value):
    mqtt_client.publish(topic, value)
    print("[INFO][PUB] Published {} to {} topic".format(value, topic))


new_reading = 0.0
while True:
    print("alive", bme.values[0])
    new_reading = float((bme.values[0])[:-1]) #temp reading is like "22.38C" so cut the C from the end
    
    # check if newest reading signals a big change from the average
    # temp_avg is 0.0 until enough readings (determined by readings_per_cycle) have been collected
    # we only want to use "normal" readings for averaging, and normal is determined as being within range (min_change_that_triggers_alert) of the temp average.
    # if the reading differs from the average too much, we process it as an outlier here:
    if temp_avg != 0.0 and abs(temp_avg - new_reading) > min_change_that_triggers_alert:
        count_of_alert_readings += 1
        
        #check that we have enough proof of door opening event
        difference_list.append(abs(temp_avg - new_reading))
        del difference_list[:-min_count_of_alert_readings_before_alert_is_sent] #keep list length at max
        if len(difference_list) >= (min_count_of_alert_readings_before_alert_is_sent):
            #get average temperature over the past N readings
            diff_sum = 0
            for reading in difference_list:
                diff_sum += reading
            diff_avg = diff_sum / len(difference_list)

            # we allow the system to start averaging based on threshold_to_return_to_averaging
            # to make it possible to return to averaging even if the "normal" temperature has changed while outlier temperatures were recorded
            # for example it may be that someone was cooking before, but now that it's stopped the temperature will only return to regular indoor levels instead of cooking levels
            if diff_avg < threshold_to_return_to_averaging:
                print(temp_avg, "avg  VS reading:", new_reading)
                # publish as MQTT payload
                led.on()
                publish(client, 'picow/temp_outlier', str(new_reading))
                led.off()
                count_of_alert_readings = 0
                difference_list = []
    #The reading wasn't deemed an outlier, so we use it for averaging:
    else:
        count_of_alert_readings = 0
        
        if len(difference_list) > 0:
            difference_list= difference_list[1:]
        
        temp_list.append(new_reading)
        del temp_list[:-readings_per_cycle] #keep list length at max
        temp_sum = 0.0
        #check that we have enough readings for averaging
        if len(temp_list) > (readings_per_cycle-1):
            # get average temperature over the past N readings
            # we use averaging to try avoid sensor errors causing rapid fluctuation which could cause lots of unndecessary messages
            for reading in temp_list:
                temp_sum += reading
            temp_avg = temp_sum / len(temp_list)

    # we transmit the average temperature regularly, to provide data for possible future analysis and to help with testing
    readings_since_transmit += 1
    if readings_since_transmit >= readings_per_cycle:
        print("transmitting regular data, no door events. Avg: ", temp_avg, "vs new: ", new_reading)
        
        # publish as MQTT payload
        led.on()
        publish(client, 'picow/temp_avg', str(temp_avg))
        led.off()
        readings_since_transmit = 0

    time.sleep_ms(sleep_between_readings)

