from tkinter import ttk
from tkinter import Tk
from tkinter import END
from tkinter import Text
from tkinter import scrolledtext
from tkinter import Widget
from tkinter import N, S, W, E
from tkinter import messagebox
from program import DIRECTORIES
from . import QueueHandler
import queue
from logging import LogRecord
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


logger = logging.getLogger()

class LoggerUI():
    LOG_PATH:str = DIRECTORIES.LOGS_PATH
    #TODO: SPLIT THE LOGGER AND THE UI
    def __init__(self, root: Widget=None, parentLogger=None):
        if not root:
            root = Tk()
        self.root = root
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(column=0, row=0, sticky=(N, S, W, E))
        
        self.parentLogger = parentLogger
        
        self.setupWindow()
        
        #self.start()
    
    def start(self):
        self.root.mainloop()
    
    def display(self, record):
        #take in string and display to window
        msg = self.parentLogger.queueHandler.format(record)
        
        self.scrollPane.configure(state='normal')
        self.scrollPane.insert(END, msg + '\n', record.levelname)
        self.scrollPane.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrollPane.yview(END)
        
    def setupLogger(self):
        # Create a custom logger
        self.logger = logging.getLogger()
        
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        logger.addHandler(self.queue_handler)
        
        # Create a handler for the logger
        formatter = logging.Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        
        
        
        
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)
        
        # Log some messages
        self.log()
    
    def showFileName(self,bool:bool):
        if bool:
            self.logger.queue_handler.setFormatter(logging.Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s'))
        else:
            self.logger.queue_handler.setFormatter(logging.Formatter(datefmt='%H:M:S', fmt='%(name)s - %(levelname)s - %(message)s'))
    
    def setupWindow(self):
        # Create a frame for the top bar
        bar = ttk.Frame(self.frame, height=20)
        bar.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=(N, S, W, E))
        

        ttk.Button(bar, text="Quit", command=self.root.destroy).grid(column=1, row=0)
        ttk.Button(bar, text="Log", command=self.log).grid(column=2, row=0)
        
        # Create a scrolled text widget for displaying logs
        self.scrollPane = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=100)
        self.scrollPane.grid(column=0, row=1, columnspan=1, sticky=(N, S, W, E))
        
        # Configure tags for different log levels
        self.scrollPane.tag_config('INFO', foreground='black')
        self.scrollPane.tag_config('DEBUG', foreground='gray')
        self.scrollPane.tag_config('WARNING', foreground='orange')
        self.scrollPane.tag_config('ERROR', foreground='red')
        self.scrollPane.tag_config('CRITICAL', foreground='red', underline=1)
        
        # Initialize the file name display toggle
        fileNameb = True
        
        # Create checkbuttons for log level filters and file name display
        buttonsFrame = bar
        self.bool_FileName = ttk.Checkbutton(bar, text="Show File Name", state="ACTIVE", variable=fileNameb, command=lambda: self.showFileName(True)).grid(column=0, row=0)
        ttk.Checkbutton(buttonsFrame, text="Debug", variable=tk.BooleanVar(value=True), command=lambda: fileNameb).grid(column=3, row=0)
        ttk.Checkbutton(buttonsFrame, text="Info", variable=tk.BooleanVar(value=True), command=lambda: self.logger.setLevel(logging.INFO)).grid(column=4, row=0)
        ttk.Checkbutton(buttonsFrame, text="Warning", variable=tk.BooleanVar(value=True), command=lambda: self.logger.setLevel(logging.WARNING)).grid(column=5, row=0)
        ttk.Checkbutton(buttonsFrame, text="Error", variable=tk.BooleanVar(value=True), command=lambda: self.logger.setLevel(logging.ERROR)).grid(column=6, row=0)
        ttk.Checkbutton(buttonsFrame, text="Critical", variable=tk.BooleanVar(value=True), command=lambda: self.logger.setLevel(logging.CRITICAL)).grid(column=7, row=0)
        
        # Configure column and row weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=0)
        self.frame.rowconfigure(0, weight=0)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.logger.logQueue.get(block=False)
            except queue.Empty:
                break
            else:
                #send to display
                self.display(record)
        self.frame.after(100, self.poll_log_queue)
        
    def log(self):
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warning message')
        logger.error('error message')
        logger.critical('critical message')

class CustomLogger():
    def __init__(self, logPath:str=None, showGUI:bool=True):
        self.root = Tk()
        self.showGUI = True
        
        self.logQueue = queue.Queue()
        self.queueHandler = QueueHandler(self.logQueue)
        
        self.setFormatter(logging.Formatter(datefmt='%H:%M:%S', fmt='%(asctime)s %(name)s - %(levelname)s - %(message)s'))
        self.addHandler(self.queueHandler)
        
        
        self.GUI = LoggerUI(self.root, self)
        #calls self.start()
        print("Started logger")  

    def setFormatter(self, formatter:logging.Formatter):
        assert isinstance(formatter, logging.Formatter), f"formatter is not a logging.Formatter, it is a {type(formatter)}"
        assert self.queueHandler is not None
        self.queueHandler.setFormatter(formatter)
    
    def addHandler(self, handler:logging.Handler):
        assert isinstance(handler, logging.Handler), f"handler is not a logging.Handler, it is a {type(handler)}"
        logger.addHandler(handler)
    
    def testLog(self):
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warning message')
        logger.error('error message')
        logger.critical('critical message')

def main():
    root = Tk()

    log = LoggerUI(root)
    log.start()
    logger.info("Hello World")
    
#if __name__ == "__main__":
#    t = threading.Thread(target=main)
#    t.start()
#    logger.info("Hello World")
#    print("done")