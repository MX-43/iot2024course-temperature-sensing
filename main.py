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
readings_per_cycle = 20 # transmitting roughly every X minutes
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

# config ssl connection w Transport Layer Security encryption (cert required)
# context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# context.verify_mode = ssl.CERT_REQUIRED
# context.load_verify_locations('ccertificate.pem') # Load the certificate from path

# mqtt client connect

client = MQTTClient(client_id=b'picow', server=config.MQTT_BROKER, port=config.MQTT_PORT,
                    user=config.MQTT_USER, password=config.MQTT_PWD, ssl=context)

client.connect()


# define I2C connection and BMP
#i2c = machine.I2C(id=1, sda=Pin(14), scl=Pin(15)) # id=channel
#bmp = BMP280(i2c)

i2c = machine.I2C(id=0, scl=machine.Pin("GP21"), sda=machine.Pin("GP20"))
bme = bme280.BME280(i2c=i2c)


def publish(mqtt_client, topic, value):
    mqtt_client.publish(topic, value)
    print("[INFO][PUB] Published {} to {} topic".format(value, topic))







new_reading = 0.0
while True:
    print("alive", bme.values[0])
    new_reading = float((bme.values[0])[:-1]) #temp reading is like "22.38C" so cut the C
    
    #check if newest reading signals a big change from the average
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
            
            #print(temp_avg)
        
            if diff_avg < threshold_to_return_to_averaging:
                print(temp_avg, "avg  VS reading:", new_reading)
                # publish as MQTT payload
                led.on()
                #publish(client, 'picow/temp_avg', str(temp_avg))
                publish(client, 'picow/temp_outlier', str(new_reading))
                led.off()
                #readings_since_transmit = 0
                count_of_alert_readings = 0
                difference_list = []
    #if not a big change, use the reading for averaging
    else:
        count_of_alert_readings = 0
        
        if len(difference_list) > 0:
            difference_list= difference_list[1:]
        
        temp_list.append(new_reading)
        del temp_list[:-readings_per_cycle] #keep list length at max
        #print(temp_list)
        temp_sum = 0.0
        #check that we have enough readings for averaging
        if len(temp_list) > (readings_per_cycle-1):
            #get average temperature over the past N readings
            for reading in temp_list:
                temp_sum += reading
            temp_avg = temp_sum / len(temp_list)
            #print(temp_avg)
    readings_since_transmit += 1
    
    if readings_since_transmit >= readings_per_cycle:
        print("transmitting regular data, no door events. Avg: ", temp_avg, "vs new: ", new_reading)
        #transmitting regular data, no door events (for debugging)
        
        # publish as MQTT payload
        led.on()
        publish(client, 'picow/temp_avg', str(temp_avg))
        led.off()
        readings_since_transmit = 0

    # publish as MQTT payload
    #led.on()
    #publish(client, 'picow/temp', str(bme.values[0]))
    #publish(client, 'picow/pressure', str(bme.values[1]))
    #led.off()

    time.sleep_ms(sleep_between_readings)

