#from ttkthemes.themed_tk import ThemedToplevel
import tkinter as tk
from tkinter import ttk
#import tkinter as tk
#from ttkthemes.themed_tk import ThemedTk
#from tkinter import ttk 
import PIL
import PIL.ImageTk
#from PIL import Image, ImageTk
import matplotlib
import numpy as np
import re

class ScrolledWindow(tk.Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected 
    to canvas scrollregion.

    2. self.scrollwindow is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>.scrollwindow
    to get them inserted into canvas

    __init__(self, parent, canv_w = 400, canv_h = 400, *args, **kwargs)
    docstring:
    Parent = master of scrolled window
    canv_w - width of canvas
    canv_h - height of canvas

    """


    def __init__(self, parent, canv_w = 400, canv_h = 400, *args, **kwargs):
        """Parent = master of scrolled window
        canv_w - width of canvas
        canv_h - height of canvas

       """
        super().__init__(parent, *args, **kwargs)

        self.parent = parent

        # creating a scrollbars
        self.xscrlbr = ttk.Scrollbar(self.parent, orient = 'horizontal')
        self.xscrlbr.grid(column = 0, row = 1, sticky = 'ew', columnspan = 2)         
        self.yscrlbr = ttk.Scrollbar(self.parent)
        self.yscrlbr.grid(column = 1, row = 0, sticky = 'ns')         
        # creating a canvas
        self.canv = tk.Canvas(self.parent)
        self.canv.config(relief = 'flat',
                         width = 10,
                         heigh = 10, bd = 2)
        # placing a canvas into frame
        self.canv.grid(column = 0, row = 0, sticky = 'nsew')
        # accociating scrollbar comands to canvas scroling
        self.xscrlbr.config(command = self.canv.xview)
        self.yscrlbr.config(command = self.canv.yview)

        # creating a frame to inserto to canvas
        self.scrollwindow = ttk.Frame(self.parent)

        self.canv.create_window(0, 0, window = self.scrollwindow, anchor = 'nw')

        self.canv.config(xscrollcommand = self.xscrlbr.set,
                         yscrollcommand = self.yscrlbr.set,
                         scrollregion = (0, 0, 100, 100))

        self.yscrlbr.lift(self.scrollwindow)        
        self.xscrlbr.lift(self.scrollwindow)
        self.scrollwindow.bind('<Configure>', self._configure_window)  
        self.scrollwindow.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollwindow.bind('<Leave>', self._unbound_to_mousewheel)

        return

    def _bound_to_mousewheel(self, event):
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1*(event.delta/120)), "units")  

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight())
        self.canv.config(scrollregion='0 0 %s %s' % size)
        if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canv.config(width = self.scrollwindow.winfo_reqwidth())
        if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
            # update the canvas's width to fit the inner frame
            self.canv.config(height = self.scrollwindow.winfo_reqheight())


class WindowAttacher(object):
    def __init__(self, root, master, anchor = 'ne', name=None):
        self.root = root
        self.name = name
        self.master = master.winfo_toplevel()
        self.master._child_window_destroyer = self._destroyer
#        self.master._destroyer = self.master_is_destroyed_callback
        self.root._destroyer = self._destroyer
        self.master_geometry = self._get_geometry(self.master)
        self.root_geometry = self._get_geometry(self.root)
        self.master.wm_protocol("WM_DELETE_WINDOW", self.master_is_destroyed_callback)
        self.root.wm_protocol("WM_DELETE_WINDOW", self.root_is_destroyed_callback)
        self.attach(anchor)
        self._update_relative_anchor_point()
        self._masterbindid = self.master.bind('<Configure>', self.master_configure_callback, '+')
        self._rootbindid = self.root.bind('<Configure>', self.root_configure_callback, '+')

    def _update_relative_anchor_point(self):
        root_corner_xy = self.get_window_nw(self.root)
        self._update_master_corner_xy()
        self._relative_anchor_point = root_corner_xy - self._master_corner_xy

    def _update_master_corner_xy(self):
        self._update_relative_direction()
        if self._relative_direction == 'ne':
            self._master_corner_xy = self.get_window_ne(self.master)
        elif self._relative_direction == 'se':
            self._master_corner_xy = self.get_window_se(self.master)
        elif self._relative_direction == 'sw':
            self._master_corner_xy = self.get_window_sw(self.master)
        elif self._relative_direction == 'nw':
            self._master_corner_xy = self.get_window_nw(self.master)

    def _update_relative_direction(self):
        cm = self.get_window_center(self.master)
        sm = self.get_window_nw(self.root)
        out = ''
        if sm[1] <= cm[1]:
            out += 'n'
        else:
            out += 's'
        if sm[0] >= cm[0]:
            out += 'e'
        else:
            out += 'w'
        self._relative_direction = out            
            
    def master_configure_callback(self, tkEvent):
        new_master_geometry = self._get_geometry(self.master)
        if set(self.master_geometry) != set(new_master_geometry):
            self._update_master_corner_xy()
            self.master_geometry = new_master_geometry
            self.update_root_position()  

    def root_configure_callback(self, tkEvent):
        new_root_geometry = self._get_geometry(self.root)
        if set(self.root_geometry) != set(new_root_geometry):
            self.root_geometry = new_root_geometry
            self._update_relative_anchor_point()  

            
    def _destroyer(self):
        self._release_from_parent()
        if hasattr(self.root, '_child_window_destroyer'):
           self.root._child_window_destroyer()
#        print self.name + ': ROOT IS DESTROYED'
        self.root.destroy()
           
    def _release_from_parent(self):
#        print self.name + ': RELEASED FROM PARENT'
        self.master.unbind('<Configure>', self._masterbindid)
        if hasattr(self.master, '_destroyer'):
            self.master.wm_protocol("WM_DELETE_WINDOW", self.master._destroyer)
        else:
            self.master.wm_protocol("WM_DELETE_WINDOW", self.master.destroy)
            
        del self.master._child_window_destroyer
        #If the master has a _destroyer, it means that itself is an attachable window
        
            
    def master_is_destroyed_callback(self):
#        print self.name + ': MASTER IS DESTROYED'
        if hasattr(self.master, '_destroyer'):
            self.master._destroyer()
        else: 
           self.master._child_window_destroyer()
           self.master.destroy()

    def root_is_destroyed_callback(self):
        self._destroyer()
        
    def get_window_center(self, toplevel):
        g = self._get_geometry(toplevel)
        return np.array([g[2]+g[0]/2, g[3]+g[1]/2])
        
    def get_window_nw(self, toplevel):
        g = self._get_geometry(toplevel)
        return np.array([g[2], g[3]])

    def get_window_sw(self, toplevel):
        g = self._get_geometry(toplevel)
        return np.array([g[2], g[1] + g[3]])

    def get_window_se(self, toplevel):
        g = self._get_geometry(toplevel)
        return np.array([g[0] + g[2], g[1] + g[3]])

    def get_window_ne(self, toplevel):
        g = self._get_geometry(toplevel)
        return np.array([g[0] + g[2], g[3]])
        
    def update_root_position(self):
        self.root.geometry('+%d+%d' % tuple(self._master_corner_xy + self._relative_anchor_point))
        self.root.update()
        self.root.lift()

    def _get_geometry(self, toplevel):
        geom_str = toplevel.geometry()
        m = re.match("(\d+)x(\d+)\+?(\-?\d+)\+?(\-?\d+)", geom_str)
#        import pdb; pdb.set_trace()
        return np.array(list(map(int, m.groups())))
        
    def moveto(self, xy):
        self.root.geometry('+%d+%d' % (xy[0], xy[1]))
        self.root.lift()
#        self.root.event_generate('<Configure>', when = 'tail')

    def attach(self, anchor='ne'):
        self.anchor = anchor
        #mg = Master Geometry, sg = Self Geometry
        self.mg = mg = self._get_geometry(self.master)
        self.sg = sg = self._get_geometry(self.root)
        b = 8
#        print(mg, sg)
        if anchor == 'ne':
            self.moveto((mg[2] + mg[0] + b , mg[3]))
        elif anchor == 'nw':
            self.moveto((mg[2] - sg[0] - b, mg[3]))
        elif anchor == 'se':
            self.moveto((mg[2] + mg[0] + b, mg[3] + mg[1] + b))
        elif anchor == 'sw':
            self.moveto((mg[2], mg[3] + mg[1] + b))
    

# Adapted from here: http://effbot.org/zone/tkinter-autoscrollbar.htm

class AutoScrollbar(ttk.Scrollbar):
    '''
    A scrollbar that hides itself if it's not needed. 
    Only works if you use the grid geometry manager.
    '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)

    def pack(self, *args, **kwargs):
        raise TclError('Cannot use pack with this widget.')

    def place(self, *args, **kwargs):
        raise TclError('Cannot use pack with this widget.')


#https://stackoverflow.com/questions/30018148/python-tkinter-scrollable-frame-class
class ScrolledFrame(ttk.Frame):
    def __init__(self, top, *args, **kwargs):

        def frame_changed(_):
            self.frame.update_idletasks()
            self.canvas.config(scrollregion = self.canvas.bbox('all'))
            self.fit_width()

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")  

        def _bound_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)   
    
        def _unbound_to_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>") 


        ttk.Frame.__init__(self, top, *args, **kwargs)

        hscrollbar = AutoScrollbar(self, orient = tk.HORIZONTAL)
        hscrollbar.grid(row = 1, column = 0, sticky = 'ew')

        vscrollbar = AutoScrollbar(self, orient = tk.VERTICAL)
        vscrollbar.grid(row = 0, column = 1, sticky = 'ns')

        self.canvas = tk.Canvas(self, xscrollcommand = hscrollbar.set,
                              yscrollcommand = vscrollbar.set)
        self.canvas.config(relief = 'flat',
                         width = 104,
                         heigh = 200, bd = 2)        
        self.canvas.grid(row = 0, column = 0, sticky = 'nsew')

        hscrollbar.config(command = self.canvas.xview)
        vscrollbar.config(command = self.canvas.yview)

        # Make the self.canvas expandable
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create the self.canvas contents
        self.frame = ttk.Frame(self.canvas)
        self.frame.rowconfigure(1, weight = 1)
        self.frame.columnconfigure(1, weight = 1)

        self.canvas.create_window(0, 0, window = self.frame, anchor = 'nw')
        self.canvas.config(scrollregion = self.canvas.bbox('all'))
        self.frame.bind('<Configure>', frame_changed)
        self.frame.bind('<Enter>', _bound_to_mousewheel)
        self.frame.bind('<Leave>', _unbound_to_mousewheel)

    def fit_width(self):
        self.canvas['width'] = self.frame.winfo_reqwidth()



    
#    
## This is an example of using my new class I defined above.
## It's how I know my class isn't working quite right.
#root = tk.Tk()
#scrolled = ScrolledFrame(root)
#scrolled.grid(row = 0, column = 0, sticky = 'news')
#root.rowconfigure(0, weight = 1)
#root.columnconfigure(0, weight = 1)
#
#for i in range(10):
#    for j in range(10):
#        button = tk.Button(scrolled.frame, text = '%d, %d' % (i, j))
#        button.grid(row = i, column = j, sticky = 'news')

#autoScrollable.frame.update_idletasks()
#autoScrollable.canvas.config(scrollregion = autoScrollable.canvas.bbox('all'))

#root.mainloop()


class ImageCombobox(ttk.Frame):
    def __init__(self, master, raw_items, preview=True, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.preview = preview
        self.make_listbox(raw_items)
        self.items=self.listbox.items
        self.curselection = next(i for i,img in enumerate(self.listbox.items) if img[0]) 
#        self.cmap = cmap
        self.l = ImageListboxItem(self, self.listbox.items[self.curselection], index=0)
        self.l.grid(row=1, column=1)
        self.l.bind('<<item_selected>>', self.show_listbox)
        self.master.bind('<Escape>', self.close_listbox)
        
    def make_listbox(self, items):
        self.listbox = ImageListbox(items, dock_widget=self)
        self.listbox.bind('<<selection_change>>', self.on_selection)
        if self.preview:
            self.listbox.bind('<<active_item_change>>', self.on_active_item_change)
            
    def show_listbox(self, event):
        try: 
            self.listbox.wm_state()
        except:
#            print('ImageCombobox.show_listbox.except')
            self.make_listbox(self.items)
        self.listbox.deiconify()

    def on_selection(self, event):
        if self.items[self.curselection][0]:
            self.event_generate('<<selection_change>>', when='tail')
            self.l.update_item(self.items[self.curselection])
        self.listbox.close_listbox(event)

    def on_active_item_change(self, event):
        if self.items[self.listbox.curselection][0]:
            self.curselection = self.listbox.curselection
            self.event_generate('<<selection_change>>', when='tail')
            self.l.update_item(self.items[self.curselection])

    def close_listbox(self, event):
        if self.listbox:
            self.listbox.close_listbox(event)

    def get_name(self):
        return self.items[self.curselection][1]
        
#    def set(self, name):
#        print('setting ', name)
#        print(sorted(self.names))
#        if self.names:
#            self.listbox.curselection = self.names.index(name)
#            self.on_active_item_change('none_event')
            
#    def insert(self, index=-1, items=None):
#        if isinstance(items, dict):
#            if all([isinstance(v, dict) for v in items.values()]):
#                pass
                
            

class ImageListboxItem(ttk.Frame):
    def __init__(self, master, item, index, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        def on_enter(event):
            event.widget['background'] = 'black'
            self.event_generate('<<item_active>>', when='tail')
        def on_leave(event):
            event.widget['background'] = ''
        def on_click(event):
#            print('ImageListboxItem.on_click')
            self.event_generate('<<item_selected>>', when='tail')
            
#            if display_name:
#                l_name = ttk.Label(self, text=name, width=12)
#                l_name.grid(row=1, column=1, sticky='nes')
        self.l_name = ttk.Label(self, width=12)
        self.l_name.grid(row=1, column=1, sticky='nes')
        self.index = index
        self.l = ttk.Label(self)
        self.l.grid(row=1, column=2, sticky='nes')
        self.l.bind('<Enter>', on_enter)
        self.l.bind('<Leave>', on_leave)
        self.l.bind('<Button-1>', on_click)
        self.update_item(item)

    def update_item(self, item):
        if isinstance(item, tuple):
            self.image = item[0]
            self.name = item[1]
        else:
            self.image = item
            self.name=None
        if not self.image:
            self.l_name.configure(width=0)
        self.l.configure(image=self.image)
        self.l_name.configure(text=self.name)

class ImageListbox(tk.Toplevel):
    def __init__(self, raw_items, dock_widget=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.withdraw()
        def _leave(event):
#                event.widget['background'] = ''
            self.quit()
#        self.images = []
#        self.names = []
        self.curselection = 0
#        self.root = tk.Toplevel()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
    #    root.set_theme('aquativo')
        if dock_widget:
            self.window_attacher = WindowAttacher(root = self, master = dock_widget, anchor = 'sw', name = 'ImageListbox')
#            self.master = master
            self.geometry(f'+{dock_widget.winfo_rootx()}+{dock_widget.winfo_rooty() + dock_widget.winfo_height()}')
        self.scrolled = ScrolledFrame(self)
        self.scrolled.grid(row=0, column=0, sticky='news')
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1) 
        self.rows = []
        self.items = []
        self.insert(items=raw_items)

    def close_listbox(self, _):
        self.destroy()
            
    def insert(self, index='end', items=None):
        len0 = len(self.items)
        def _insert_single_item(index, image, name=None):
#            if isinstance(image, PIL.ImageTk.PhotoImage):
            if index=='end':
                self.items.append((image,name))
#                self.images.append(image)
#                self.names.append(name)
            else:
                self.items.insert(index, (image,name))
#                self.images.insert(index, image)
#                self.names.insert(index, name)
        def process_items(index, items):
            if isinstance(items, tuple):
                _insert_single_item(index, items[0], items[1])
            elif isinstance(items, dict):
                for key, v in items.items():
                    if isinstance(key, str):
                        if isinstance(v, dict):
                            #the dict is interpreted to have the key as a seperator string and then contents below:
#                            print((index, None, key))
                            _insert_single_item(index, image=None, name=key)
                            process_items(index, items=v)
                        elif isinstance(v, PIL.ImageTk.PhotoImage):
                            _insert_single_item(index, v, key)
                        
    #           if all([isinstance(v, dict) for v in items.values()]):
            elif isinstance(items, PIL.ImageTk.PhotoImage):
                _insert_single_item(index, items)
            elif isinstance(items, list):
                if all([isinstance(item, PIL.ImageTk.PhotoImage) for item in items]):
                    if index == 'end':
                        self.items.extend(zip(items, [None]*len(items)))
                    else:
                        self.items[index:index] = zip(items, [None]*len(items))
#                elif all([isinstance(item[0], PIL.ImageTk.PhotoImage) for item in items]):
#                    if index == 'end':
#                        self.items.extend(items)
#                    else:
#                        self.items[index:index] = items
                else:
#                    print(items)
                    for item in items:
                        process_items(index, item)
        process_items(index, items)
        if len(self.items) > len0:
            self.redraw()
        
    def redraw(self):
        def image_select(event):
#            print('ImageListbox.redraw.image_select')
            self.curselection = event.widget.index
            self.event_generate('<<selection_change>>', when='tail')
        def image_activate(event):
            self.curselection = event.widget.index
            self.event_generate('<<active_item_change>>', when='tail')
        for l in self.rows:
            l.destroy()
        self.rows = []
        for i in range(len(self.items)):
                l = ImageListboxItem(self.scrolled.frame, self.items[i], index=i)
                l.grid(row=i, column =1)
                if isinstance(self.items[i][0], PIL.ImageTk.PhotoImage):
                    l.bind('<<item_selected>>', image_select)
                    l.bind('<<item_active>>', image_activate)
                self.rows += [l]
        
    
def colormap_to_imagetk(cmap, w=100, h=20):
    colors = cmap(np.linspace(0,1,w))[:,:3]
    colors = colors * 255
    colors = colors.astype(np.uint8)
    colors = colors.reshape((1,w,3))
    colors = np.repeat(colors, h, axis=0)
    img=PIL.Image.fromarray(colors)
    return PIL.ImageTk.PhotoImage(img)    

            
if __name__ == '__main__':

    cmap_names = [('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma']),
         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]    
    cmap_dict = {kind:{name:colormap_to_imagetk(matplotlib.cm.get_cmap(name)) for name in names if name in matplotlib.cm.cmap_d} for kind, names in cmap_names}
    
    root = tk.Toplevel()
#    cmap_names = [name for name in plt.cm.datad.keys() if name[-2:] != '_r']
#    cmap_images = [colormap_to_imagetk(plt.cm.get_cmap(name)) for name in cmap_names]
    x = ImageCombobox(root, dct)
    x.grid()
#    scrolled.canvas.configure
##    