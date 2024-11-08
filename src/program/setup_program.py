from tkinter import ttk
from tkinter import Tk
from tkinter import END
from tkinter import Widget
from tkinter import N, S, W, E
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from System import Environment
from mqtt import pingIP
from dataclasses import astuple
from . import DIRECTORIES, FILES
import os
from program.Logger import getLogger


logger = getLogger("SETUP")

class SETUP_STATE:
    SETUP = 0
    VERIFY = 1
    COMPLETE = 2

class SetupProgram(ttk.Frame):
    clientname_blacklist_chars:str = '/\:*?"<>|,;{}[]()!@#$%^&*+`~ -'
    directories = astuple(DIRECTORIES())
    files = astuple(FILES())
    
    
    def __init__(self, root: Widget=None):
        if not root:
            root = TkinterDnD.Tk()
            root.title("Setup")
        super().__init__(root,padding=10)
        self.root = root
        
        
        self.setupState = SETUP_STATE.VERIFY
        appDataState, missingDirectories, missingFiles = self.verifyAppData()
        
        if appDataState:
            self.setupState = SETUP_STATE.COMPLETE
        else:
            self.setupState = SETUP_STATE.SETUP
            
        if self.setupState == SETUP_STATE.COMPLETE:
            root.destroy()
            logger.info("App data verified")
            return
        
        if self.setupState == SETUP_STATE.SETUP:
            logger.info("App data not verified")
            logger.debug(f"Missing directories: {missingDirectories}")
            logger.debug(f"Missing files: {missingFiles}")
            
            self.setupGUI()
            self.setupDragDrop()
            root.geometry("500x300")
            self.pack()
            self.mainloop()
    
    def verifyAppData(self) -> tuple[bool, list[str], list[str]]:
        """Verify that all directories and files exist\n
        Returns a tuple of (isVerified, missingDirectories, missingFiles)"""
        isVerified = True
        missingDirectories = []
        missingFiles = []
        
        verifiedDirectory, missingDirectories = self.verifyDirectories()
        if not verifiedDirectory:
            isVerified = False
        
        verifiedFiles, missingFiles = self.verifyFiles()
        if not verifiedFiles:
            isVerified = False
        
        return isVerified, missingDirectories, missingFiles

    def verifyDirectories(self) -> tuple[bool, list[str]]:
        """Verify that all directories exist\n
        Returns a tuple of (isVerified, missingDirectories)"""
        missingDirectories = []
        for d in self.directories:
            if not os.path.exists(d):
                missingDirectories.append(d)
                
        return (len(missingDirectories) == 0, missingDirectories)

    def verifyFiles(self) -> tuple[bool, list[str]]:
        """Verify that all files exist\n
        Returns a tuple of (isVerified, missingFiles)"""
        missingFiles = []
        for f in self.files:
            if not os.path.exists(f):
                missingFiles.append(f)
                
        return (len(missingFiles) == 0, missingFiles)
    
    def setupGUI(self):
        self.root.resizable(False, False)
        self.grid(column=0, row=0, sticky=(N, S, W, E))
        
        ttk.Label(self, text="Hostname:").pack()
        self.hostname = ttk.Entry(self, width=75); self.hostname.pack()
        test = ttk.Label(self.hostname, text="Drag and drop files here")
        
        ttk.Label(self, text="Device Name: (leave empty to use device name)").pack()
        self.clientname = ttk.Entry(self, width=75); self.clientname.pack()
        
        ttk.Label(self, text="Certificate:").pack()
        self.certPath = ttk.Entry(self, width=75); self.certPath.pack()
        
        ttk.Label(self, text="Private Key:").pack()
        self.keyPath = ttk.Entry(self, width=75); self.keyPath.pack()
        
        ttk.Label(self, text="Root CA:").pack()
        self.caPath = ttk.Entry(self, width=75); self.caPath.pack()
        
        ttk.Button(self, text="Confirm",command=self.on_confirm).pack()
    
    def setupDirectory(self):
        """Create directories if they do not exist"""
        for d in self.directories:
            if not os.path.exists(d):
                logger.debug(f"Creating directory: {d}")
                os.makedirs(d,exist_ok=True)
    
    def saveData(self, hostname:str, clientname:str, certPath:str, keyPath:str, caPath:str):
        """write hostname, clientname, certPath, keyPath, caPath to files"""
        with open(FILES.HOST, 'w') as f:
            f.write(hostname)
        with open(FILES.CERTIFICATE, 'w') as f:
            f.write(certPath)
        with open(FILES.PRIVATE_KEY, 'w') as f:
            f.write(keyPath)
        with open(FILES.ROOT_CA, 'w') as f:
            f.write(caPath)
        with open(FILES.TOPICS, 'w') as f:
            f.write(clientname)

    
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
            self.hostname.delete(0, END)
            self.hostname.insert(0, f)
        self.validate_hostname()
    def drop_certPath(self, event):
        f = self.getDropFileContents(event)
        if f:
            self.certPath.delete(0, END)
            self.certPath.insert(0, f)
    def drop_keyPath(self, event):
        f = self.getDropFileContents(event)
        if f:
            self.keyPath.delete(0, END)
            self.keyPath.insert(0, f)
    def drop_caPath(self, event):
        f = self.getDropFileContents(event)
        if f:
            self.caPath.delete(0, END)
            self.caPath.insert(0, f)
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
            self.clientname.insert(0, Environment.DEVICE_NAME)

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
            logger.error(f"Unable to ping: {self.hostname.get()}")
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
        
if __name__ == "__main__":
    SetupProgram()