from tkinter import ttk
from tkinter import Tk
from tkinter import END
from tkinter import Text
from tkinter import scrolledtext
from tkinter import Widget
from tkinter import N, S, W, E
from tkinter import messagebox

import queue
import py_hot_reload
import tkinter as tk
import logging
import threading



# https://beenje.github.io/blog/posts/logging-to-a-tkinter-scrolledtext-widget/
# https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt



#TODO:
# create it lol

# access anywhere (singleton or global)
# log levels


logger = logging.getLogger("Logger")


class QueueHandler(logging.Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        print(f'adding record to queue: {record}')
        self.log_queue.put(record)
 
class LoggerUI():
    def __init__(self, root: Widget):
        self.root = root
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid()
        
        self.setupWindow()
        self.setupLogger()
        
        self.start()
    
    def start(self):
        print("Started logger")
        self.root.mainloop()
    
    def display(self, record):
        #take in string and display to window
        msg = self.queue_handler.format(record)
        self.scrollPane.configure(state='normal')
        self.scrollPane.insert(END, msg + '\n', record.levelname)
        self.scrollPane.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrollPane.yview(END)
        
    def setupLogger(self):
        # Create a custom logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        
        # Create a handler for the logger
        formatter = logging.Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        self.logger.addHandler(self.queue_handler)
        
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)
        
        # Log some messages
        self.log()
    
    def showFileName(self,bool:bool):
        if bool:
            self.queue_handler.setFormatter(logging.Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s'))
        else:
            self.queue_handler.setFormatter(logging.Formatter(datefmt='%H:M:S', fmt='%(name)s - %(levelname)s - %(message)s'))
    
    def setupWindow(self):
        ttk.Label(self.frame, text="Hello World!").grid(column=0, row=0)
        ttk.Button(self.frame, text="Quit", command=self.root.destroy).grid(column=1, row=1)
        ttk.Button(self.frame, text="Log", command=self.log).grid(column=1, row=0)
        
        
       #scrollPane
        self.scrollPane = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=100, height=16)
        self.scrollPane.grid(column=0, row=1, columnspan=1, sticky=(N, S, W, E))
        self.scrollPane.tag_config('INFO', foreground='black')
        self.scrollPane.tag_config('DEBUG', foreground='gray')
        self.scrollPane.tag_config('WARNING', foreground='orange')
        self.scrollPane.tag_config('ERROR', foreground='red')
        self.scrollPane.tag_config('CRITICAL', foreground='red', underline=1)
        
        buttonsFrame = ttk.Frame(self.frame, height=1, relief=tk.SUNKEN).grid(column=0, row=0, columnspan=1)
        ttk.Checkbutton(buttonsFrame, text="Show File Name", command=lambda: self.showFileName(True)).grid(column=0, row=0)
        ttk.Checkbutton(buttonsFrame, text="Debug", command=lambda: self.logger.setLevel(logging.DEBUG)).grid(column=1, row=0)
        ttk.Checkbutton(buttonsFrame, text="Info", command=lambda: self.logger.setLevel(logging.INFO)).grid(column=2, row=0)
        ttk.Checkbutton(buttonsFrame, text="Warning", command=lambda: self.logger.setLevel(logging.WARNING)).grid(column=3, row=0)
        ttk.Checkbutton(buttonsFrame, text="Error", command=lambda: self.logger.setLevel(logging.ERROR)).grid(column=4, row=0)
        ttk.Checkbutton(buttonsFrame, text="Critical", command=lambda: self.logger.setLevel(logging.CRITICAL)).grid(column=5, row=0)
        
        
        
        
        

        
    
    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            
            except queue.Empty:
                break
            else:
                #send to display
                self.display(record)
        
        self.frame.after(100, self.poll_log_queue)
        
    

    def log(self):
        self.logger.debug('debug message')
        self.logger.info('info message')
        self.logger.warning('warning message')
        self.logger.error('error message')
        self.logger.critical('critical message')

        

def main():
    root = Tk()

    log = LoggerUI(root)
    log.start()
    logger.info("Hello World")
    
    

    

    
if __name__ == "__main__":
    t = threading.Thread(target=main)
    t.start()
    logger.info("Hello World")
    print("done")