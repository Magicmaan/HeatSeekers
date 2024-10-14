import matplotlib.pyplot as plt
import numpy as np


class Graph:
    def __init__(self, data:list[float,float]):
        
        self.xaxis, self.yaxis = zip(*data)
        
        
        plt.plot(self.xaxis, self.yaxis)
        plt.show()
        


if __name__ == "__main__":
    x = np.logspace(0.1, 1, 20)
    y = np.linspace(1, 20, 20)
    data = list(zip(x, y))
    g = Graph(data)
    print("Done")