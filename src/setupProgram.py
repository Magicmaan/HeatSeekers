from tkinter import ttk
from tkinter import Tk
from tkinter import END
from tkinter import Text
from tkinter import scrolledtext
from tkinter import Widget
from tkinter import N, S, W, E
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, DND_TEXT, DND_ALL, TkinterDnD

from Util.pingIP import pingIP
import queue
import tkinter as tk
import logging
import threading
import os

class setupProgram(ttk.Frame):
    DATA_PATH:str = f"{os.getenv('APPDATA')}/HeatSeekers"
    
    clientname_blacklist_chars:str = '/\:*?"<>|,;{}[]()!@#$%^&*+`~ -'
    def __init__(self, root: Widget=None):
        if not root:
            root = TkinterDnD.Tk()
            root.title("Setup")
        super().__init__(root,padding=10)
        self.root = root
        
        self.setupGUI()
        self.setupDragDrop()
        
        root.geometry("500x300")
        self.pack()
        self.mainloop()
    
    def setupGUI(self):
        self.root.resizable(False, False)
        self.grid(column=0, row=0, sticky=(N, S, W, E))
        
        ttk.Label(self, text="Hostname:").pack()
        self.hostname = ttk.Entry(self, width=75); self.hostname.pack()
        
        ttk.Label(self, text="Client Name:").pack()
        self.clientname = ttk.Entry(self, width=75); self.clientname.pack()
        
        ttk.Label(self, text="Certificate:").pack()
        self.certPath = ttk.Entry(self, width=75); self.certPath.pack()
        
        ttk.Label(self, text="Private Key:").pack()
        self.keyPath = ttk.Entry(self, width=75); self.keyPath.pack()
        
        ttk.Label(self, text="Root CA:").pack()
        self.caPath = ttk.Entry(self, width=75); self.caPath.pack()
        
        ttk.Button(self, text="Confirm",command=self.on_confirm).pack()
    
    def setupDirectory(self):
        os.mkdir(self.DATA_PATH)
        
        os.mkdir(f'{self.DATA_PATH}/mqtt')
        os.mkdir(f'{self.DATA_PATH}/mqtt/certs')
        
        os.mkdir(f'{self.DATA_PATH}/data')
        os.mkdir(f'{self.DATA_PATH}/data/logs')
    
    def saveData(self, hostname:str, clientname:str, certPath:str, keyPath:str, caPath:str):
        with open(f'{self.DATA_PATH}/mqtt/host.txt', 'w') as f:
            f.write(hostname)
        
        with open(f'{self.DATA_PATH}/mqtt/certs/certificate.pem.crt', 'w') as f:
            f.write(certPath)
        
        with open(f'{self.DATA_PATH}/mqtt/certs/private.pem.key', 'w') as f:
            f.write(keyPath)
        
        with open(f'{self.DATA_PATH}/mqtt/certs/ROOTCA1.pem', 'w') as f:
            f.write(caPath)
        
        with open(f'{self.DATA_PATH}/mqtt/topics.txt', 'w') as f:
            f.write(clientname)
        
        os.mkdir(f'{self.DATA_PATH}/data/{clientname}')  
        os.mkdir(f'{self.DATA_PATH}/data/{clientname}/temperature_data')
        os.mkdir(f'{self.DATA_PATH}/data/{clientname}/humidity_data')
    
    def setupDragDrop(self):
        self.clientname.drop_target_register(DND_FILES)
        self.clientname.dnd_bind('<<Drop>>', self.drop_clientname)
        self.hostname.drop_target_register(DND_FILES)
        self.hostname.dnd_bind('<<Drop>>', self.drop_hostname)
        self.certPath.drop_target_register(DND_FILES)
        self.certPath.dnd_bind('<<Drop>>', self.drop_certPath)
        self.keyPath.drop_target_register(DND_FILES)
        self.keyPath.dnd_bind('<<Drop>>', self.drop_keyPath)
        self.caPath.drop_target_register(DND_FILES)
        self.caPath.dnd_bind('<<Drop>>', self.drop_caPath)
    
    def drop_clientname(self,event):
        f = self.getDropFileContents(event)
        if f:
            self.clientname.delete(0, END)
            self.clientname.insert(0, f)
        self.validate_clientname()
    def drop_hostname(self, event):
        f = self.getDropFileContents(event)
        if f:
            print(f)
            self.hostname.delete(0, END)
            self.hostname.insert(0, f)
        self.validate_hostname()
    def drop_certPath(self, event):
        f = self.getDropFileContents(event)
        if f:
            self.certPath.delete(0, END)
            self.certPath.insert(0, f.read())
    def drop_keyPath(self, event):
        f = self.getDropFileContents(event)
        if f:
            self.keyPath.delete(0, END)
            self.keyPath.insert(0, f.read())
    def drop_caPath(self, event):
        f = self.getDropFileContents(event)
        if f:
            self.caPath.delete(0, END)
            self.caPath.insert(0, f.read())
    def getDropFileContents(self, event) -> str:
        """get text contents of dropped file"""
        filename = event.data
        if not filename:
            return None
        if not os.path.isfile(filename):
            return None
        
        with open(filename, 'r') as f:
            data = f.read()
            return data
        
        return None
    
    def validate_clientname(self) -> bool:
        if not self.clientname.get():
            messagebox.showerror("Error", "Please enter a client name")
            return False
        if any((c in self.clientname_blacklist_chars) for c in self.clientname.get()):
            messagebox.showerror("Error", f"Client name cannot contain any of the following characters:{self.clientname_blacklist_chars}")
            return False
        return True
    def validate_hostname(self) -> bool:
        if not self.hostname.get():
            messagebox.showerror("Error", "Please enter a hostname")
            return False
        #check if hostname is valid
        if not pingIP(self.hostname.get()):
            messagebox.showerror("Error", "Unable to ping: {self.hostname.get()}\n Please be sure the hostname is correct, and are connected.")
            return False
        return True

    def on_confirm(self) -> bool:
        if not self.validate_hostname():
            return
        if not self.validate_clientname():
            return
        
        
        if not self.certPath.get():
            messagebox.showerror("Error", "Please enter a certificate path")
            return
        if not self.keyPath.get():
            messagebox.showerror("Error", "Please enter a private key path")
            return
        if not self.caPath.get():
            messagebox.showerror("Error", "Please enter a Root CA path")
            return
        
        self.setupDirectory()
        self.saveData(self.hostname.get(), self.clientname.get(), self.certPath.get(), self.keyPath.get(), self.caPath.get())
        self.root.destroy()
        
        
m = setupProgram()