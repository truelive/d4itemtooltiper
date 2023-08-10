import tkinter
from tkinter import ttk
import threading, time
from datetime import datetime
from functools import reduce

class TimerWidget:
    def __init__(self, config):
        display_cfg = config['display']
        self.windowcheck_millis = int(display_cfg['lifetime'])
        
        self.item_width = int(display_cfg['item_width'])
        self.item_heigh = int(display_cfg['item_heigh'])
        self.item_power_hit_color = display_cfg['item_power_hit_color']
        self.item_power_hit = int(display_cfg['item_power_hit'])
        self.affix_miss_color = display_cfg['affix_miss_color']
        self.affix_hit_color = display_cfg['affix_hit_color']
        self.font = display_cfg['font']

    def create_widget(self, d4_items, position):
        self.root = tkinter.Tk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.start_x = position[0]
        self.start_y = position[1]
        self.root.overrideredirect(1)
        item_width = self.item_width
        item_heigh = self.item_heigh
        width = len(d4_items)*item_width
        
        height = (reduce(max, map(lambda x: len(x.affx), d4_items))+1)*item_heigh
        self.root.geometry(f"{width}x{height}+{self.start_x-width}+{self.start_y-height}")
        self.root.attributes('-topmost', True)
        self.root.config(bg='gray')
        self.root.wm_attributes("-transparentcolor", 'gray')
        # root.update()
        self.wcnv = tkinter.Canvas(self.root, bg='gray')
        wcnv = self.wcnv
        for x in range(len(d4_items)):
            column = x*item_width
            wcnv.create_rectangle(column, 0, column + item_width, item_heigh, fill=self.item_power_hit_color if int(d4_items[x].item_power) > self.item_power_hit else self.affix_miss_color)
            wcnv.create_text(column, item_heigh/2, text=d4_items[x].item_power, anchor=tkinter.W, font=self.font)
            for y in range(1, len(d4_items[x].affx)+1):
                row = y*item_heigh
                color = self.affix_miss_color
                af = d4_items[x].affx[y-1]
                if af[0] == True:
                    color = self.affix_hit_color
                wcnv.create_rectangle(column, row, column + item_width, row + item_heigh, fill=color)
                wcnv.create_text(column, row+item_heigh/2, text=af[1], anchor=tkinter.W, font=self.font)
            row = len(d4_items[x].affx)
            
            
        wcnv.bind('<Double-Button-1>', self.stop)
        wcnv.bind('<Motion>', self.stop)
        wcnv.pack()
        
    def start(self):
        self.root.after(self.windowcheck_millis, self.stop)
        self.root.mainloop()
        
    
    def stop(self, event=None):
        print("CLOSING " + str(event))
        self.root.destroy()

    def renderItems(self, d4_items, position):
        print("creating a window")
        self.create_widget(d4_items, position)
        print("starting a window")
        self.start()


    