
from collections import OrderedDict
from Tkinter import *


class MetadataFrame(Frame):

    def __init__(self, meta, **kwargs):

        Frame.__init__(self, **kwargs)

        d,c,e = Frame(self),Frame(self),Frame(self)

        bg_other = "#E8E8E8"
        bg_name = "#C0C0C0"

        self.meta = meta
        meta = [(str(key), str(meta[key])) for key in meta]
        meta.reverse()

        key_width = max(7, max( len(key) for (key,value) in meta ) )
        value_width = max(7, max( len(value) for (key,value) in meta ) )

        for (key, value) in meta:

            
            key_label = Label(master=d, text=key, bg=bg_name, anchor="w", font="14", width=key_width)
            point_label = Label(master=c, text=' : ', bg=bg_name, font="14")
            value_label = Label(master=e, text=value, bg=bg_name, font="14", width=value_width)

            key_label.pack(fill="x")
            point_label.pack(fill="x")
            value_label.pack(fill="x")
            
            bg_name, bg_other = bg_other, bg_name
        
        d.pack(side="left")
        c.pack(side="left")
        e.pack(side="left")
            

if __name__ == '__main__':

    # Use example:
    root = Tk()
    meta = OrderedDict(Name='Antonio Ribeiro Alves Junior', Age=27, City="Gent")
    app = MetadataFrame(master=root, meta=meta)
    app.pack()
    app.mainloop()
    
    app.destroy()
