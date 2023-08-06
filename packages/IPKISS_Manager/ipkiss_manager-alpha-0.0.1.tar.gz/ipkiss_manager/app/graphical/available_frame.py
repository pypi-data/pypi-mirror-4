
from Tkinter import *


class TopFrame(Frame):
    """
        Frame that will contains 
    """
    def __init__(self, **kwargs):
        Frame.__init__(self, **kwargs)


class BotomFrame(Frame):
    """
        frame to place my metadata frame
    """

class AvailableFrame(Frame):
    " Frame to show all available distributions "

    def __init__(self, **kwargs):
        Frame.__init__(self, **kwargs)

        self.bf = Frame(master=self)
        self.tf = TopFrame(master=self)

        self.tf.pack()
        self.bf.pack(width=100)

    def update_metadata(self, metadata):

        if self.botom_frame:
            self.botom_frame.detach


if __name__ == '__main__':
    # Use example:
    root = Tk()
    app = AvailableFrame(master=root, width=768, height=576)
    app.pack()
    app.mainloop()
    
    app.destroy()
