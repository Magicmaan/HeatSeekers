# HeatSeekers

### Temperature & Humidity System

HeatSeekers is a Python program designed to monitor temperature and humidity using a DHT22 sensor. The system utilizes MQTT to send messages with the collected data. Additionally, it includes a Node-RED component for visualizing and managing the data.

## Prerequisites

1. Ensure you have Node-RED installed with the dashboard 2.0 package.
2. Set up an MQTT broker, either locally or using AWS IoT. This project uses the mosquitto local broker

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/HeatSeekers.git
   cd HeatSeekers
   ```

2. Create a virtual environment:

   ```sh
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:
     ```sh
     .\venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

4. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

5. Run initialization:

   - The program automatically runs in MQTT mode through a local broker. If you want to use AWS, change `mqttMode` from `"mqtt"` to `"aws"` in `main.py`.
   - When using MQTT, simply enter the broker's hostname (e.g., `localhost` for Mosquitto).
   - If using AWS, either paste in or drag and drop the required files.

6. Run the program:

   You can either use the `run.bat` script or run the components individually:

   - Using `run.bat` script:

     ```sh
     .\run.bat
     ```

   - Individually:
     ```sh
     python main.py
     node-red path/.node-red/flows.json
     ```

7. Run NodeRed.bat

Raspberry pi
DHT22 sensor
4.7k ohm resistor
