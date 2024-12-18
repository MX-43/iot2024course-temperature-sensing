# Dog Activity Monitoring with Door Opening Detection

This project is designed to monitor a dog's outdoor activity by tracking door opening events. Using a **temperature sensor** positioned near the door, the device detects when the door is opened, allowing the system to automatically track when the dog is let outside. This data can help remind the user to let the dog outside and also monitor any behavioral changes over time, which could be useful for tracking the dog’s health.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
- [Code Explanation](#code-explanation)
- [Acknowledgments](#acknowledgments)
- [Troubleshooting](#troubleshooting)

---

## 1. Project Overview

In households with dogs, it can often be difficult to remember exactly when and how many times the dog has been let outside. To solve this problem, this project uses a **device** equipped with a **temperature sensor** positioned near the front door. By detecting temperature changes caused by the door being opened, the device automatically tracks when the door is opened, which indicates that the dog has been let outside.

The data collected by the device is stored and analyzed to track the frequency of door opening events. This information can be used to remind the user to let the dog outside after a set amount of time. Furthermore, by continuously monitoring the door's activity, it’s possible to detect patterns in the dog’s behavior, which could provide valuable insights into its health. For instance, some dogs may request to be let outside when they need to go, and tracking these behaviors over time can help identify potential health concerns.

While the primary focus of this project is on demonstrating the **data collection process** and detecting **door opening events**, the system also includes the capability to forward **alerts** to the user’s preferred mobile device, ensuring they are reminded when the dog needs to be let outside.

---

## Features:
- **Real-time Door Monitoring**: Tracks door opening events using a **temperature sensor** placed near the door.
- **Data Collection & Alerting**: Sends alerts when the door is opened, helping users track when the dog is let outside.
- **Behavioral Monitoring**: Provides insights into the dog’s behavior by tracking the frequency of door opening events over time.
- **User Reminders**: Reminds users to let the dog outside after a predefined time interval.
- **Mobile Notifications**: Alerts can be forwarded to the user’s mobile device for convenience.
- **MQTT Communication**: Sends data to a cloud-based MQTT broker for monitoring and analysis.

---

## 2. Getting Started

### Prerequisites

Before starting, ensure you have the following:

1. **Hardware**:
   - **Raspberry Pi Pico W** (or another suitable microcontroller).
   - **Temperature Sensor** (e.g., **BME280** sensor for detecting door temperature changes).
   - **LED** (for status indication).
   - Access to an **MQTT Broker** (e.g., **Mosquitto**, **AWS IoT**, **CloudMQTT**).
  
2. **Software**:
   - **MicroPython** installed on the microcontroller.
   - A method for uploading and running scripts, such as **Thonny IDE** or **ampy**.
   - A **Wi-Fi** network for internet connectivity.

### Setup Instructions

1. **Clone the Repository**:
   Clone this repository to your local machine.

   ```bash
   git clone https://github.com/MX-43/iot2024course-temperature-sensing.git
   cd iot2024course-temperature-sensing
   ```

2. **Install Dependencies**:
   Ensure the necessary libraries are available on your device. These include:
   - `umqtt.simple` (for MQTT communication).
   - `bme280` (for interacting with the BME280 sensor).

   Upload these libraries to your device using **Thonny IDE** or another compatible upload method.

3. **Configure the Network and MQTT Settings**:
   Edit the **`config.py`** file to include your Wi-Fi and MQTT broker details.

   ```python
   ssid = "your_wifi_ssid"
   pwd = "your_wifi_password"
   MQTT_BROKER = "your_mqtt_broker_address"
   MQTT_PORT = 1883  # or use a secure port like 8883
   MQTT_USER = "your_mqtt_user"
   MQTT_PWD = "your_mqtt_password"
   ```

4. **Upload the Code**:
   Use **Thonny IDE** or any other suitable method to upload the script to your microcontroller.

5. **Run the Script**:
   Once uploaded, run the script. The device will start reading temperature data from the sensor, track door opening events, and send alerts to the MQTT broker. The **LED** will indicate when an outlier temperature (indicative of the door being opened) is detected.

---

## 3. Code Explanation

### 1. **Wi-Fi Connection**
   The script connects to the specified Wi-Fi network and prints the device’s IP address once successfully connected.

### 2. **Sensor Data Collection**
   The **BME280** sensor collects temperature data over **I2C**. When a significant change in temperature is detected (indicating that the door was opened), the system records this event.

### 3. **Temperature Averaging and Alert System**
   - The temperature is averaged over a set number of readings.
   - If the temperature deviates significantly from the average (suggesting the door has opened), the system checks if this event should trigger an alert.

### 4. **MQTT Communication**
   The device connects to an MQTT broker and securely sends temperature data and alerts via the **umqtt.simple** library. The system uses **SSL** encryption for secure communication.

### 5. **LED Indicators**
   The **LED** stays on during normal operation. When a significant temperature change is detected (indicating that the door has been opened), the **LED** blinks briefly to indicate an outlier reading.

---

## 4. Acknowledgments

- The **starting code** for this project was provided by the **Teaching Assistant (TA)**. This code was adapted to include features like temperature averaging, door opening detection, and MQTT communication.
- Libraries used:
  - **`umqtt.simple`**: For MQTT communication.
  - **`bme280`**: For reading temperature, pressure, and humidity data from the BME280 sensor.
  - **`machine`**, **`time`**, **`network`**: For device control and network operations.

---

## 5. Troubleshooting

If you encounter issues, check the following:

1. **Wi-Fi Connection**: Ensure the **SSID** and **password** in the `config.py` file are correct.
2. **Sensor Not Working**: Check the wiring and ensure that the **BME280** sensor is properly connected to the microcontroller.
3. **MQTT Connection**: Double-check your MQTT broker details and verify that the broker is up and running. If using **SSL**, ensure the broker supports secure connections.
