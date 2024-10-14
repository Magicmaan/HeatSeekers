def getAverageData(self,dataSet:list) -> float:
    """Get the average from a 1D data set"""
    assert len(dataSet) > 2, "Data set must have at least 2 data points"
    sum = 0
    for data in dataSet:
        sum += data[1]
    
    return sum / len(dataSet)

def calculateGradient(dataCache: list) -> float:
    """Calculate the gradient of the temperature data in the data cache"""
    #wait for enough data
    if len(dataCache) < 2:
        return 0
    
    # Calculate the gradient using the first and last data points in the cache
    DTemperature = dataCache[-1][1] - dataCache[0][1]
    DTime = dataCache[-1][0] - dataCache[0][0]

    return DTemperature / DTime if DTime != 0 else 0

def predictFutureValue(dataCache: list, timestep: int) -> float:
    """Predict the future value based on the gradient and a timestep ahead in seconds"""
    if len(dataCache) < 2:
        return 0
    gradient = calculateGradient(dataCache)
    if not gradient:
        return dataCache[-1][1]
    # Predict future temperature
    futureValue = dataCache[-1][1] + gradient * timestep

    return futureValue
