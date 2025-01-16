from typing import List
from System import DIRECTORIES
import glob
import json
import numpy as np

from program.Logger import getLogger
import time

logger = getLogger("LOG_UTIL")

def getSensorLogs():
    folder = DIRECTORIES.SENSOR_DATA_PATH
    files = glob.glob(folder + "/*.json")
    return files



def getSensorLogsDate(date:str):
    """
        Retrieve sensor logs for a specific date.
        Args:
            date (str): The date for which to retrieve the sensor logs in the format 'YYYYMMDD'.
        Returns:
            None: This function currently does not return anything.
    """
    # get filepaths
    folder = DIRECTORIES.SENSOR_DATA_PATH
    files = glob.glob(folder + f"/{date}*.json")
    if len(files) == 0:
        logger.error(f"No files found for date: {date}")
        return None
    
    logger.debug(f"Files found for date {date}: {len(files)}")
    
    return files

def averageEntries(entries: list[dict]) -> dict:
    start_time = time.time()
    if not entries:
        return {
            "timestamp": None, 
            "temperature": 0, 
            "humidity": 0, 
            "units": {"temperature": "C", "humidity": "%"}, 
            "predicted_temperature": 0
        }
    
    
    # use numpy since entries could be very big
    temperatures = np.array([entry["temperature"] for entry in entries])
    humidities = np.array([entry["humidity"] for entry in entries])
    averageTemp = np.mean(temperatures)
    averageHumidity = np.mean(humidities)
    
   
    return {
        "timestamp": entries[-1]["timestamp"], 
        # convert back from np.float64 to float
        "temperature": float(averageTemp), 
        "humidity": float(averageHumidity), 
        "units": {"temperature": "C", "humidity": "%"}, 
    }

    
    
def concatenateSensorLogs(files: List[str], round: str="hour") -> List[dict]:
    """
        Concatenate sensor logs into a single list.
        Args:
            files (List[str]): A list of filepaths to the sensor logs.
            round ("10","hour", "day"): used to average out data so that it is not too granular
        Returns:
            List[dict]: A list of dictionaries containing the sensor log data.
    """
    data = []
    for file in files:
        print(file)
        with open(file, 'r') as f:
            roundedEntries = []
            currentMinute = -1
            currentHour = -1
            currentDay = -1
            
            for line in f: 
                jsonObj = json.loads(line)
                ts = jsonObj["timestamp"]
                hour, minute, second = ts.split(":")
                minute = minute[0] + "0"
                # append objects to list
                roundedEntries.append(jsonObj)
                
                # when the minute changes by 10 -> 0, 10, 20, 30, 40, 50...
                # average out the data for that 10 minute period
                # then insert into the data list
                
                # issue with this is that across files it could create several entries for same / similar time
                # i.e. 10:03, 10:36 if they're in different files this will create duplicates
                if round == "10":
                    # on hour change, reset minute
                    if ( hour != currentHour ):
                        currentHour = hour
                        currentMinute = 00
                    # Skip lines where the minute value is not a multiple of 10
                    if (minute != currentMinute):
                        currentMinute = minute
                        
                        roundedEntries = averageEntries(roundedEntries)
                        data.append(roundedEntries)
                        roundedEntries = []
                # when the hour changes, average out the data for that hour
                elif round == "hour":
                    if (hour != currentHour):
                        currentHour = hour
                        roundedEntries = averageEntries(roundedEntries)
                        data.append(roundedEntries)
                        roundedEntries = []

        # append last entries that may've escaped the loop
        if roundedEntries:
            roundedEntries = averageEntries(roundedEntries)
            data.append(roundedEntries)
                
        print(data)
    
    return data
