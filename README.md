To run project, setup MicroPython on the Raspberry Pi Pico W and install main.py and other files EXCLUDING flow.json which is for the for Node-RED flow.

Additionally, Get a HiveMQ account and start a cluster for it. Install Node-RED, InfluxDB on local device such as PC.

Connect Pico to the cluster to send MQTT messages to it; messages should be visible in the web client monitoring.

After get this working, Node-RED can be connected to HiveMQ to subscribe to the messages. The file "flow.json" can be used in Node-RED to import the flowchart used in this project. You could also implement some other solution to use the temperature / door opening data.
