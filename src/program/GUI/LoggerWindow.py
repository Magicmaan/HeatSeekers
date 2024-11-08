from os import path
import string
from tkinter import ttk, Tk, END, scrolledtext, Widget, N, S, W, E, Toplevel, StringVar
from program import DIRECTORIES, START_TIME, INSTANCE_FILES
import queue
import logging
from logging import Handler, LogRecord
import tkinter as tk

from program.Logger import getLogger, logFormatter


_logger = getLogger()



class QueueHandler(Handler):
    """Class to send logging records to a queue

    It can be used from different threads
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: LogRecord):
        self.log_queue.put(record)



class LoggerWindow(ttk.Frame):
    """
    A GUI window for displaying log messages using Tkinter.

    Attributes:
        root (Widget): The root widget for the window.
        frame (ttk.Frame): The main frame of the window.
        logQueue (queue.Queue): The queue for log messages.
        queueHandler (QueueHandler): The handler for the log queue.
        scrollPane (scrolledtext.ScrolledText): The text widget for displaying logs.
    Methods:
        init(root: Widget=None, logger: logging.Logger=None):
            Initializes the LoggerWindow with the given root widget and logger.
        setupWindow():
            Configures the window layout and widgets.
        isTopLevel():
            Checks if the root widget is a Toplevel widget.
    """
    def __init__(self, root: Widget=None, loggerName:str = None, blacklist:list=None, format:str = None):
        if not root:
            root = Tk()
        super().__init__(root)
        self.root = root
        self.title = loggerName if loggerName else "Debug Logger"
        self.root.title(self.title)
        self.logger = getLogger(loggerName) if loggerName else _logger
        
        self.logLevel:StringVar = StringVar()
        self.logLevel.set("DEBUG")
        self._setLogLevel()
        
        self.frame = ttk.Frame(self.root, padding=10, name='loggerFrame')
        self.frame.grid(column=0, row=0, sticky=(N, S, W, E))
        
        self.loggerBlacklist = blacklist if blacklist else [""]
        #bool whether to log to terminal
        self._logToTerminal = False
        self.setupGUI()
        #add Handler to redirect logger to a Queue
        #This can be read by tkinter
        self.logQueue = queue.Queue()
        self.queueHandler = QueueHandler(self.logQueue)
        self.logger.addHandler(self.queueHandler)

        formatString = format if format else '%(asctime)s %(name)s - %(levelname)s - %(message)s'
        #set a formatter
        self.formatter = logging.Formatter(datefmt='%H:%M:%S', fmt=formatString)
        
        self.queueHandler.setFormatter(self.formatter)
        

        
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)
    
    def setupGUI(self):
        # Configure the grid to expand and contract with the window size
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Configure the grid in the frame to expand and contract with the window size
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Create a frame for the top bar
        bar = ttk.Frame(self.frame, height=20)
        bar.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=(N, S, W, E))
        
        #buttons for the top bar
        ttk.Button(bar, text="Quit", command=self.root.destroy).grid(column=1, row=0)
        ttk.Button(bar, text="Log", command=self.log).grid(column=2, row=0)
        ttk.Checkbutton(bar, text="Log to terminal", command=self.toggleLogToTerminal).grid(column=3, row=0)
        ttk.Checkbutton(bar, text="Log to file", command=self.toggleLogToFile).grid(column=4, row=0)
        ttk.Radiobutton(bar, text="Debug", variable=self.logLevel, value="DEBUG", command=self._setLogLevel).grid(column=5, row=0)
        ttk.Radiobutton(bar, text="Info", variable=self.logLevel, value="INFO", command=self._setLogLevel).grid(column=6, row=0)
        ttk.Radiobutton(bar, text="Warning", variable=self.logLevel, value="WARNING", command=self._setLogLevel).grid(column=7, row=0)
        ttk.Radiobutton(bar, text="Error", variable=self.logLevel, value="ERROR", command=self._setLogLevel).grid(column=8, row=0)
        
        
        # Create a scrolled text widget for displaying logs
        self.scrollPane = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, width=100)
        self.scrollPane.grid(column=0, row=1, columnspan=1, sticky=(N, S, W, E))
        
        # Configure the grid in the frame to expand and contract with the window size
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
        # Configure tags for different log levels
        self.scrollPane.tag_config('INFO', foreground='black')
        self.scrollPane.tag_config('DEBUG', foreground='gray')
        self.scrollPane.tag_config('WARNING', foreground='orange')
        self.scrollPane.tag_config('ERROR', foreground='red')
        self.scrollPane.tag_config('CRITICAL', foreground='red', underline=1)
    
    #toggle functions for buttons
    def toggleLogToTerminal(self):
        self._logToTerminal = not self._logToTerminal
    def toggleLogToFile(self):
        self._logToFile = not self._logToFile
    def _setLogLevel(self):
        self.logger.setLevel(self.logLevel.get())
    
        
    def display(self, record: LogRecord):
        if record.name in self.loggerBlacklist:
            return
        
        #take in string and display to window
        msg = self.formatter.format(record)
        if self._logToTerminal:
            print(msg)
        
        self.scrollPane.configure(state='normal')
        self.scrollPane.insert(END, msg + '\n', record.levelname)
        self.scrollPane.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrollPane.yview(END)
    
    def poll_log_queue(self):
        assert self.logQueue is not None, "logQueue is None"
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record: LogRecord = self.logQueue.get(block=False)
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
    
    def isTopLevel(self):
        return isinstance(self.root, Toplevel)

class DebugLoggerWindow(LoggerWindow):
    def __init__(self):
        super().__init__()

class SensorLoggerWindow(LoggerWindow):
    def __init__(self):
        super().__init__(None, "SENSOR_DATA",format='%(message)s')
        
