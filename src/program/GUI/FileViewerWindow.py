from os import path
import os
from tkinter import ttk, Tk, END, scrolledtext, Widget, N, S, W, E, Toplevel, StringVar
import queue
import logging
from logging import Handler
import tkinter as tk

class FileViewerWindow(ttk.Frame):
    def __init__(self, file_path:str, root: Widget=None):
        if not root:
            root = Tk()
        super().__init__(root)
        self.root = root
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(column=0, row=0, sticky=(N, S, W, E))
        
        self.scrollPane = scrolledtext.ScrolledText(self.frame)
        self.scrollPane.grid(column=0, row=0, sticky=(N, S, W, E))
        
        if not os.path.exists(file_path):
            return
        
        self.file = file_path
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                self.scrollPane.insert(END, line)
                self.previousLine = line
        # Start polling messages from the queue
        self.frame.after(100, self.poll_file)
        

        self.mainloop()
    
    def poll_file(self):
        # Check every 100ms if there is a new message in the queue to display
        assert os.path.exists(self.file)
        with open(self.file, 'r') as f:
            lines = f.readlines()
            if not lines:
                return
            last_line = lines[-1]
            
            if last_line != self.previousLine:
                self.scrollPane.insert(END, last_line)
                self.previousLine = last_line
        
        # Check again in 100ms
        self.frame.after(1000, self.poll_file)

if __name__ == '__main__':
    FileViewerWindow("C:\\Users\\theob\\AppData\\Roaming\\HeatSeekers\\data\\logs\\1728928963.1811082_log.txt")