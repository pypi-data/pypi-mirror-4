"""
    IPKISS Manager GUI - Graphical User Interface
    This module provides a graphical user interface to IPKISS Manager
"""

from Tkinter import *

class GraphicalManager(Frame):
    pass

class ManagerTabs(Tabs):
    pass

class InstalledFrame(Frame):
    pass

class ManageFrame(Frame):
    pass

def main():
    root = Tk()
    app = GraphicalManager(master=root)
    app.mainloop()
    
    app.destroy()


if __name__ == '__main__':
    main()