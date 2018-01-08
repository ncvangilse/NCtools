#class DataAxes(Axes):
#    name = 'interactive'
#    
#    def i
#    
#    def format_coord(self, x, y):
#        normal_part = Axes.format_coord(self, x, y)
#        if self.images:
#            # Most recent image is usually on top
#            im = self.images[-1]
#            j, i = self._coords2index(im, x, y)
#            z = im.get_array()[j, i]
#            return "Value: %f, %s" % (z, normal_part)
#            return normal_part
#            
#            
#            @staticmethod
#            def _coords2index(im, x, y):
#                """
#                Convert data coordinates to index coordinates.
#                Credit: mpldatacursor developers.
#                Copyright (c) 2012. BSD License
#                Modified from original found at:
#                https://github.com/joferkington/mpldatacursor/blob/master/
#                mpldatacursor/pick_info.py
#                """
#                xmin, xmax, ymin, ymax = im.get_extent()
#                if im.origin == 'upper':
#                    ymin, ymax = ymax, ymin
#                    im_shape = im.get_array().shape[:2]
#                    data_extent = mtransforms.Bbox([[ymin, xmin],
#                    [ymax, xmax]])
#                    array_extent = mtransforms.Bbox([[0, 0], im_shape])
#                    trans = (mtransforms.BboxTransformFrom(data_extent) +
#                    mtransforms.BboxTransformTo(array_extent))
#                    j, i = trans.transform_point([y, x]).astype(int)
#                    # Clip the coordinates to the array bounds.
#                    return (min(max(j, 0), im_shape[0] - 1),
#                    min(max(i, 0), im_shape[1] - 1))
#                    # Register DataAxes so that it can be used like any other Axes
#                    # Uses the 'name' attribute, so it will be accessible as 'data'.
#                    mproj.projection_registry.register(DataAxes)

################################################################

#from matplotlib import pyplot as plt
#import numpy as np
#from matplotlib.widgets import Button
#
#x = np.linspace(0,6,100)
#y = np.sin(x)
#fig = plt.figure()
#ax = fig.add_subplot(111)
#ax.plot(x,y)
#
#fig.canvas.mpl_connect('enter_axes_event', onpick)
#
#
import sys

modules = []
for module in sys.modules:
    if module.startswith('matplotlib'):
        modules.append(module)

for module in modules:
    sys.modules.pop(module)

import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
#from matplotlib.patches import Rectangle
#from matplotlib.axis import XAxis
#from matplotlib.axis import YAxis
#from matplotlib.text import Text
import matplotlib.projections as mproj
from matplotlib import cbook
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import combinations
import tkinter as tk
from tkinter import ttk 

import copy
from inspect import signature, Parameter

import shapely
from shapely.ops import cascaded_union
from descartes import PolygonPatch
import inspect
#from Publisher import Publisher
import re
import time


plt.ion()


class InteractiveFigure(object):
    def __init__(self, fig):
        self.fig = fig
        self.wcanvas = self.fig.canvas.get_tk_widget()
#        self._txtrect = TextEditorWidget()
        self._obj = None
        self._selector = Selector(fig)
#        self._e = None
        self.fig.canvas.mpl_connect('figure_enter_event', self.fig_enter_callback)
        self.fig.canvas.mpl_connect('figure_leave_event', self.fig_leave_callback)
        self.fig.canvas.mpl_connect('motion_notify_event', self.motion_callback)
#        self.fig.canvas.mpl_connect('button_press_event', self.button_press_callback)
#        self.fig.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self._tick_artists = self._get_all_tick_artists()
    def fig_enter_callback(self, event):
        pass
    def fig_leave_callback(self, event):
        pass
#        self._clear_selector()

    def _get_best_object(self, objs):
        obj = None
        objtypes = [type(x) for x in objs]
        for i, objtype in enumerate(objtypes):
            if objtype in [matplotlib.axis.XAxis, matplotlib.axis.YAxis]:
                obj = objs[i]
        i = -1
        print(objs)
        while i < len(objs) and not obj:
            i += 1
            #If top element is the Selector itself or the mysterious Line2D((0,0),(1,0)), we are interested in the next element:
            if objs[i]==self._selector._patch or str(objs[i])=='Line2D((0,0),(1,0))' or str(objs[i])=='Rectangle(0,0;1x1)':
                    pass                
            elif isinstance(objs[i], matplotlib.axes._axes.Axes) and (isinstance(objs[i+1], matplotlib.text.Text) or isinstance(objs[i+1], matplotlib.patches.Rectangle)):
                i += 1
            else:
                obj = objs[i]
        for ax in self._tick_artists.keys():
            for axis in self._tick_artists[ax].keys():
                if obj in self._tick_artists[ax][axis]:
#                    obj = axis._get_tick(True)
                    obj = axis
                    break
        print('Picking: ', obj)
        return obj

       
    def motion_callback(self, event):
#        print('------MOTION--------')
        if self._selector.locked():
            return
        objs = sorted(self.fig.findobj(lambda x: x.contains(event)[0]), key=lambda x: x.zorder, reverse=True)
#        print(objs)
        obj = self._get_best_object(objs)
#        i = -1
#        #If top element is the Selector itself or the mysterious Line2D((0,0),(1,0)), we are interested in the next element:
#        while objs[i]==self._selector._patch or str(objs[i])=='Line2D((0,0),(1,0))':
#            i -= 1
#        obj = objs[i]

        if self._obj:
            if self._obj == obj:
                return
            else:
                self._clear_selector()
        self._obj = obj
        self._selector.set_obj(obj)
#        self._draw_selector()

    def _clear_selector(self):
        self._selector.clear()

    def _draw_selector(self):
        if isinstance(self._obj, matplotlib.patches.Rectangle):
            self._selector.set_obj(self._obj)
        elif isinstance(self._obj, matplotlib.text.Text):
            self._selector.set_obj(self._obj)
        elif isinstance(self._obj, matplotlib.axis.XAxis):
            self._selector.set_obj(self._obj)
        elif isinstance(self._obj, matplotlib.axis.YAxis):
            self._selector.set_obj(self._obj)
        elif type(self._obj) in [matplotlib.axis.YTick, matplotlib.axis.XTick]:
            self._selector.set_obj(self._obj)
#        elif isinstance(self._obj, matplotlib.lines.Line2D):
#            pass
        else:
            self._obj.set_color('red')
            print(type(self._obj))

        self.fig.canvas.draw_idle()

    def _get_all_tick_artists(self):
        artists = {}
        for ax in self.fig.axes:
            ax_children = {}
            for axis in [ax.xaxis, ax.yaxis]:
                list_ = []
                for mt in axis.get_major_ticks():
                    list_ += mt.get_children()
                for mt in axis.get_minor_ticks():
                    list_ += mt.get_children()
                ax_children[axis] = list_
            artists[ax] = ax_children
        return artists

class Publisher(object):
    #Subclass the Publisher class to enable the subclass to publish events on changes.
    #Subscribers can subscribe by
    #publisher_instance.subscribe('event_name', 'subscriber_id', [a reference to a receiving function])
    
    #The publisher can then publish by
    #self.dispatch('event_name', 'some value')
    def __init__(self, events=None):
        # maps event names to subscribers
        # str -> dict
        self.events = dict()

    def add_event(self, events):
        if isinstance(events, str):
            events = [events]
        self.events.update({ event : dict()
                          for event in events })
    def remove_event(self, events):
        if isinstance(events, str):
            events = [events]
        for event in events:
            if event in self.events.keys():
                self.events.pop(event, None)

    def get_subscribers(self, event):
        return self.events[event]
    def subscribe(self, event, who, callback=None):
        if callback == None:
            callback = getattr(who, 'update')
        if event not in self.events.keys():
            self.add_event(event)
        self.get_subscribers(event)[who] = callback
    def unsubscribe(self, event, who):
        del self.get_subscribers(event)[who]
    def dispatch(self, event, message):
        for subscriber, callback in self.get_subscribers(event).items():
            callback(message)

            
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
        print(mg, sg)
        if anchor == 'ne':
            self.moveto((mg[2] + mg[0] + b , mg[3]))
        elif anchor == 'nw':
            self.moveto((mg[2] - sg[0] - b, mg[3]))
        elif anchor == 'se':
            self.moveto((mg[2] + mg[0] + b, mg[3] + mg[1] + b))
        elif anchor == 'sw':
            self.moveto((mg[2], mg[3] + mg[1] + b))
    
        
class Selector(object):
    def __init__(self, fig, obj=None):
#        Publisher.__init__(self)
        self.fig = fig
        self.editor = None
        self._patch = None
        self._geometry = self.fig.canvas.get_tk_widget().master.geometry()
#        self._ignore_findobj = True
        self.unlock()
        if obj:
            self.set_obj(obj)
    
    def set_obj(self, obj):
        self._obj = obj
        self.draw()

    def draw(self):
        if isinstance(self._obj, matplotlib.lines.Line2D):
            if self._obj.axes:
                xydata = self._obj.get_xydata()
                #get the data to display coordinates, add the buffer and then plot it:
                xydisp = self._obj._axes.transData.transform(xydata)
                if self._obj.get_linestyle() == 'None':
                    points = shapely.geometry.MultiPoint(xydisp).buffer(self._obj.get_markersize())
                    points = cascaded_union(points)
                    patches = [PolygonPatch(p, fc='none', ec='#6699cc', alpha=0.5, figure = self.fig, transform = self._obj.axes.transData.inverted()) for p in points]
                    self._patch = matplotlib.collections.PatchCollection(patches, match_original=True)
                    self._obj.axes.add_collection(self._patch)
                    self._remove_patch_func = self._patch.axes.collections.remove
                else:
                    patchdata = shapely.geometry.LineString(xydisp).buffer(10)
                    self._patch = PolygonPatch(patchdata, fc='none', ec='#6699cc', alpha=0.5, figure=self.fig)
                    self._obj.axes.patches.extend([self._patch])
                    self._remove_patch_func = self._obj.axes.patches.remove
            else:
#                print 'self.tmp: {} has no axes!'.format(str(self._obj))
                self.tmp = self._obj
        elif isinstance(self._obj, matplotlib.patches.Rectangle):
            print('SELECTOR FROM RECTANGLE')
#            self._obj.set_color('black')
        else:
            print('Unknown _obj: ', type(self._obj), self._obj)
            try:
                if type(self._obj) in [matplotlib.axis.XAxis, matplotlib.axis.YAxis]:
                    tb = self._obj.get_tightbbox(self.fig.canvas.renderer)
                    b = tb.padded(10).transformed(self.fig.transFigure.inverted())
#                    print(b)
#                if type(self._obj) in [matplotlib.axis.XTick, matplotlib.axis.YTick]:
#                    b = self._obj.get_tightbbox(self.fig.canvas.renderer)
##                    b = tb.padded(10).transformed(self.fig.transFigure.inverted())
                else:
                    b = self._obj.get_window_extent().padded(5).transformed(self.fig.transFigure.inverted())
                self._patch = matplotlib.patches.Rectangle((b.x0, b.y0), b.width, b.height, facecolor = 'none', transform = self.fig.transFigure, edgecolor='#6699cc')
                self.fig.patches.extend([self._patch])
                self._remove_patch_func = self.fig.patches.remove
            except Exception as ex:
#                print("Unexpected error:", sys.exc_info()[0])
#                print(ex)
#                print('self.tmp: {} doesnt work!'.format(str(self._obj)))
                self.tmp = self._obj
                
#        print type(self._patch)
#        print type(self._tmp)

        self.fig.canvas.draw_idle()
        self.fig.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.fig.canvas.mpl_connect('button_release_event', self.button_release_callback)
        
        
    def contains(self, event=None, misc=None):
        #The PatchCollection does not report True when it should, so return the self._obj.contains instead:
        if isinstance(self._patch, matplotlib.collections.PatchCollection):
            return self._obj.contains(event)
        else:
            return self._patch.contains(event)

        
    def clear(self):
#        self._patch.remove()
        try:
            self._remove_patch_func(self._patch)
        except:
            pass
#        if self._patch in self.fig.patches:
#            self._remove_patch_func(self._patch)
##            self.fig.patches.remove(self._patch)
        self.fig.canvas.draw_idle()

    def button_press_callback(self, event):
        if event.button==3:
            self.unlock()
        elif event.button==1:
            if self.contains(event)[0]:
                self.lock()
                self.editor = PropsEditor(self._obj)
#                print self.fig.canvas.get_tk_widget().master.geometry()
#                self.fig.canvas.get_tk_widget().master.bind('<Configure>', self.configure_callback)
#                self.add_event('geometry_change')
#                self.subscribe('geometry_change', 'editor', self.editor.update_geometry)
#                self.editor
                
                self.editor.mainloop()
            else:
                self.unlock()
#        print '1'
#        if self.editor:
#            print '2'
#            if not self.editor.contains(event)[0]:
#                print '3'
#                self.editor.clear()
#                self.editor = None
#        if self.contains(event)[0]:
#            print '4'
#            if hasattr(self._obj, 'set_text'):
#                self.editor = TextEditor(self._obj)
#            elif hasattr(self._obj, 'set_facecolor'):
#                self.editor = ColorEditor(self._obj)
##        self._txtrect._update_status(event)

            
    
        
    def button_release_callback(self, event):
        pass
    
    def locked(self):
        return self._locked
    
    def lock(self):
        self._locked = True
    
    def unlock(self):
        self.clear()
        self._locked = False

        
class PropEditor(object):
    def __init__(self, master, obj, prop, row, eval_value=True):
        self.master = master
        self.row = row
        self._obj = obj
        self.prop = prop
        self.val0 = eval('self._obj.get_{}()'.format(self.prop))
        self.type = type(self.val0)
        self.eval_value = eval_value
        self.positional_args = [x for x, p in signature(eval('self._obj.set_{}'.format(self.prop))).parameters.items() if p.default == Parameter.empty and p.kind not in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]]

        
    def draw(self):
        self.l = ttk.Label(self.master, text=self.prop, justify = tk.RIGHT).grid(column = 1, row = self.row, sticky = tk.W)
        self.f = ttk.Frame(self.master)
        self.l_help = ttk.Label(self.master, text=', '.join(self.positional_args), justify = tk.LEFT).grid(column = 3, row = self.row, sticky = tk.W)
        self.f.grid(column = 2, row = self.row, sticky = tk.EW)
        self.master.columnconfigure(2, weight = 1)
        self.f.columnconfigure(1, weight = 1)
        self.insert_e(self.f)

    def insert_e(self):
        #Should be overwritten by subclasses:
        pass

    def update_value(self, value):
#        print('type should be: {}'.format(self.type))
#        value = "'{}'".format(value)
        unpack = ''
#        if self.type != str and value[0]!='#':
        if self.eval_value:
            value = eval(value)
#            value = "'{}'".format(value)
#        else:
#            value = eval(value)
        if len(self.positional_args) > 1:
            unpack = '*'
        s = 'self._obj.set_{}({})'.format(self.prop, unpack+'value')
        try:
            eval(s)
            self._obj.figure.canvas.draw_idle()
        except Exception as ex:
            print("Unexpected error:", sys.exc_info()[0])
            print(ex)
            print('{} is not valid for {}'.format(value, self.prop))
    
            
class PropEntry(PropEditor):
    def __init__(self, master, obj, prop, row, eval_value=True):
        super().__init__(master, obj, prop, row, eval_value=eval_value)
        self.draw()
    
    def insert_e(self, master):
        self.e = ttk.Entry(master)
        self.e.grid(column = 1, row = 1, sticky = tk.EW)
        self.e.insert(0, str(self.val0))
        self.e.bind('<Return>', self._e_return_callback)

    def _e_return_callback(self, tkevent):
        self.update_value(self.e.get())

        
class PropCombobox(PropEditor):
    def __init__(self, master, obj, prop, row, validlist, eval_value=True):
        super(self.__class__, self).__init__(master, obj, prop, row, eval_value=eval_value)
        self._validlist = validlist
        self.draw()
    
    def insert_e(self, master):
        self.e = ttk.Combobox(master, values = self._validlist)
        self.e.grid(column = 1, row = 1, sticky = tk.EW)
        self.e.config(postcommand = self.postcommand)
        self.e.set(str(self.val0))
        self.e.bind('<Return>', self._e_return_callback)

    def _e_return_callback(self, tkevent):
        self.update_value(self.e.get())

    def postcommand(self):
        self.update_value(self.e.get())
        
class PropButton(PropEditor):
    #The cmd is given a reference to the entry object self.e, so it must be able to handle this:
    def __init__(self, master, obj, prop, row, cmd, eval_value=True):
        super(self.__class__, self).__init__(master, obj, prop, row, eval_value=eval_value)
        self.cmd = cmd
        self.master = master
        self.draw()
    
    def insert_e(self, master):
        self.e = ttk.Entry(master)
        self.e.insert(0, str(self.val0))
        self.e.grid(column = 1, row = 1, sticky = tk.EW)
        self.e.bind('<Return>', self._e_return_callback)

        b = ttk.Button(master, command = self.button_command)
        b.grid(column = 2, row = 1, sticky = tk.EW)
        b.config(text = '*', width = 2)

    def receive_color(self,hextext):
        self.e.delete(0, 'end')
        self.e.insert(0, hextext)
        self.update_value(self.e.get())
        
        
    def button_command(self):
        self.cmd('color_entry', self.receive_color, self.master)
#        pass
        
    def _e_return_callback(self, tkevent):
        self.update_value(self.e.get())
        
        
class PropsEditor(object):
    def __init__(self, obj):
        plt.ioff()
        self._obj = obj
#        self._geom0 = geom0
#        self.fig = matplotlib.figure.Figure()
        self.root = tk.Tk()
        self.attachable_window = WindowAttacher(root = self.root, master = self._obj.figure.canvas.get_tk_widget().master, anchor = 'ne', name = 'PropsEditor')
        ttk.Label(self.root, text=str(self._obj)).grid(column = 1, row = 1, columnspan = 10)
        allmtds = [i[0] for i in inspect.getmembers(self._obj, predicate=inspect.ismethod)]
        getters = [k[4:] for k in allmtds if 'get_' ==k[0:4]]
        setters = [k[4:] for k in allmtds if 'set_' ==k[0:4]]
        getsetters = set(getters).intersection(setters)
        textillegalmethods = set(['agg_filter', 'animated', 'axes', 'contains','figure', 'font_properties','fontproperties', 'gid', 'ha', 'name', 'path_effects', 'sketch_params', 'stretch', 'style', 'url', 'usetex', 'va', 'variant', 'weight'])
        rectillegalmethods = set(['aa', 'ec', 'fc', 'ls', 'lw', 'x', 'y', 'xy', 'clip_path'])
        lineillegalmethods = set(['c', 'data', 'mec', 'mew', 'mfc', 'mfcalt', 'ms', 'xdata', 'ydata'])
#        axesillegalmethods = set(['_view'])
        axisillegalmethods = set(['ticklabels'])
        mtds = getsetters - textillegalmethods
        mtds -= rectillegalmethods
        mtds -= lineillegalmethods
#        mtds -= axesillegalmethods
        mtds -= axisillegalmethods
        row = 1
        self.editors = {}
        for prop in sorted(mtds):
            row += 1
            if 'color' in prop:
#            if 'color' in prop in ['facecolor', 'color', 'backgroundcolor', 'edgecolor, mar']:
                self.editors[prop] = PropButton(self.root, self._obj, prop, row, ColorEditor, eval_value=False)
            #TEXT Specific cases:
            elif prop == 'horizontalalignment':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['center', 'right', 'left'])
            elif prop == 'verticalalignment':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['center', 'top', 'bottom', 'baseline'])
            elif prop == 'family':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['serif' ,'sans-serif' ,'cursive' ,'fantasy' ,'monospace' ])
            elif prop == 'multialignment':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['center', 'right', 'left'])
            elif prop == 'fontstyle':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['normal' , 'italic' , 'oblique'])
            elif prop == 'variant':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['normal' , 'small-caps'])
            elif prop == 'fontweight':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['normal' , 'ultrabold' , 'bold' , 'heavy' , 'light' ,  'ultralight'])
            elif prop == 'fontname':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
            #RECT specific cases:
            elif prop == 'joinstyle':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['miter' , 'round' , 'bevel'])
            elif prop == 'hatch':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['/' , '\\' , '|' , '-' , '+' , 'x' , 'o' , 'O' , '.' , '*'], eval_value=False)
            elif prop == 'linestyle':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['solid' , 'dashed', 'dashdot', 'dotted' , '(offset, on-off-dash-seq)' , '-' , '--' , '-.' , ':' , 'None' , ' ' , ''], eval_value=False)
            elif prop == 'rasterized':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row,  ['True', 'False', 'None'])
            #Line2d specific cases:
            elif prop == 'marker':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, [0, 1, 2, 3, 4, u'D', 6, 7, u's', u'|', u'', u'None', u'x', 5, u'_', u'^', u' ', u'd', u'h', u'+', u'*', u',', u'o', u'.', u'1', u'p', u'3', u'2', u'4', u'H', u'v', u'8', u'<', u'>'], eval_value=False)
            #axis specific cases:
            elif prop == 'label_position':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['top', 'bottom', 'left', 'right'], eval_value=False)
            elif prop == 'ticks_position':
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['top', 'bottom', 'left', 'right','both','default', 'none'], eval_value=False)
            elif prop == 'major_formatter':
                PropCombobox(self.root, self._obj, prop, row, [f'{cls.__module__}.{cls.__name__}({get_all_args(cls.__init__)})' for cls in get_subclasses(matplotlib.ticker.Formatter)])
            elif prop == 'minor_formatter':
                PropCombobox(self.root, self._obj, prop, row, [f'{cls.__module__}.{cls.__name__}({get_all_args(cls.__init__)})' for cls in get_subclasses(matplotlib.ticker.Formatter)])
            elif prop == 'major_locator':
                PropCombobox(self.root, self._obj, prop, row, [f'{cls.__module__}.{cls.__name__}({get_all_args(cls.__init__)})' for cls in get_subclasses(matplotlib.ticker.Locator)])
            elif prop == 'minor_locator':
                PropCombobox(self.root, self._obj, prop, row, [f'{cls.__module__}.{cls.__name__}({get_all_args(cls.__init__)})' for cls in get_subclasses(matplotlib.ticker.Locator)])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#            elif prop == 'fontname':
#                PropCombobox(self.root, self._obj, prop, row, ['Sans' , 'Courier' , 'Helvetica'])
#                
                
                
            elif str(eval('self._obj.get_{}()'.format(prop))) in ['True', 'False']:
                self.editors[prop] = PropCombobox(self.root, self._obj, prop, row, ['True', 'False'])
            else:
                if 'text' in prop:
                    eval_value = False
                else:
                    eval_value = True
                self.editors[prop] = PropEntry(self.root, self._obj, prop, row, eval_value=eval_value)
#        a = self.fig.add_subplot(111)
#        self.img = a.imshow(RGB, origin="lower", extent=[0, 360, 0, 1], aspect = 'auto')
#        a.set_xlabel("Hue")
#        a.set_ylabel("Brightness")
#        a.set_position([0.08,0.15,0.8,0.8])
#        #        plt.show()
#        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
#        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
##        plot_widget = canvas.get_tk_widget()
##        plot_widget.grid(row=0, column=0)
##        tk.Button(root,text="Update",command=update).grid(row=1, column=0)
#        canvas.mpl_connect('button_press_event', self.button_press_callback)
#        canvas.mpl_connect('button_release_event', self.button_release_callback)
#        canvas.mpl_connect('motion_notify_event', self.motion_notify_event_callback)
#        canvas.mpl_connect('scroll_event',self.scroll_event_callback)
#        button = tk.Button(master=self.root, text='Quit', command=self._quit)
#        button.pack(side=tk.BOTTOM)
#        canvas.show()
        self.root.update()
#        self.root.mainloop()

#    def update_geometry(self, geom):
#        g = self.root.geometry()
#        m = re.match("(\d+)x(\d+)([-+]\d+)([-+]\d+)", g)
#        g = np.asarray(map(int, m.groups()))
#        self.root.geometry('+%d+%d' % (g[2] + geom[2], g[3] + geom[3]))
#        self.root.lift()
    
    def mainloop(self):
        self.root.mainloop()
        
        
class ColorEditor(Publisher):
    #Subscribe to color_changes by
    #coloreditor.subscribe('subscriber_id', [receiver function of hex colors])
    def __init__(self, subscriber_id, func, master):
        self._publisher = Publisher()
        self.subscribe(subscriber_id, func)
#        self.e = e
        self.button1_is_pressed = False
        self.sat = 1.0
#        self._obj = obj
        V, H = np.mgrid[0:1:100j, 0:1:300j]
        S = np.ones_like(V) * self.sat
        HSV = np.dstack((H,S,V))
        RGB = matplotlib.colors.hsv_to_rgb(HSV)
        plt.ioff()
        self.fig = matplotlib.figure.Figure()
#        self.root = tk.Tk()
        self.root = tk.Toplevel()
        a = self.fig.add_subplot(111)
        self.img = a.imshow(RGB, origin="lower", extent=[0, 360, 0, 1], aspect = 'auto')
        a.set_xlabel("Hue")
        a.set_ylabel("Brightness")
        a.set_position([0.08,0.15,0.8,0.8])
        #        plt.show()
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.attachable_window = WindowAttacher(root = self.root, master = master, anchor = 'ne', name = 'ColorEditor')
#        plot_widget = canvas.get_tk_widget()
#        plot_widget.grid(row=0, column=0)
#        tk.Button(root,text="Update",command=update).grid(row=1, column=0)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_event_callback)
        canvas.mpl_connect('scroll_event',self.scroll_event_callback)
        button = tk.Button(master=self.root, text='Quit', command=self._quit)
        button.pack(side=tk.BOTTOM)
        canvas.show()
#        self.root.mainloop()

    def subscribe(self, subscriber_id, func):
        self._publisher.subscribe('color_change', subscriber_id, func)

    def draw_colors(self):
        V, H = np.mgrid[0:1:100j, 0:1:300j]
        S = np.ones_like(V) * self.sat
        HSV = np.dstack((H,S,V))
        RGB = matplotlib.colors.hsv_to_rgb(HSV)
        self.img.set_data(RGB)
        self.fig.canvas.draw_idle()
        
    def scroll_event_callback(self, event):
        self.sat += event.step/10
        self.sat = np.clip(self.sat, 0, 1)
        self.draw_colors()
        if self.button1_is_pressed:
            self._dispatch(event)
        
    def button_release_callback(self, event):
        self.button1_is_pressed = False

    def button_press_callback(self, event):
        self.button1_is_pressed = True
        self._dispatch(event)

    def motion_notify_event_callback(self, event):
        if self.button1_is_pressed:
            self._dispatch(event)

    def _dispatch(self, event):
        if event.xdata and event.ydata:
#            self.e.set_facecolor(matplotlib.colors.hsv_to_rgb([event.xdata/360, self.sat, event.ydata]))
#            self.e.delete(0, 'end')
#            self.e.insert(0, matplotlib.colors.rgb2hex(matplotlib.colors.hsv_to_rgb([event.xdata/360, self.sat, event.ydata])))
            self._publisher.dispatch('color_change', matplotlib.colors.rgb2hex(matplotlib.colors.hsv_to_rgb([event.xdata/360, self.sat, event.ydata])))
#            self._obj.figure.canvas.draw_idle()
        
        
    def _quit(self):
#        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
#                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
#        exit()
                        
    def clear(self):
        self._quit()
        self = None
                        
    def contains(self, event=None):
        return (None, None)
        
    
#class ColorEditor(object):
#    def __init__(self, obj):
#        self._obj = obj
#        self.fig = obj.figure
#        self._obj.set_facecolor = askcolor()
#        self.fig.canvas.draw_idle()
#
#    def contains(self, event):
#        return self._obj.contains(event)
#    
#    def clear(self):
#        self = None
#            
class TextEditor(object):
    def __init__(self, obj):
        self._obj = obj
        self.fig = obj.figure
        self.wcanvas = self.fig.canvas.get_tk_widget()
        self._e = None
        self.draw_entry()
        
    def draw_entry(self):
        b = self._obj.get_window_extent()
        self.bbox = b
        cx = b.x0 + b.width/2
        cy = b.y0 + b.height/2
        font = (self._obj.get_fontfamily()[0], int(self._obj.get_fontsize()), self._obj.get_fontstyle())
        self._e = ttk.Entry(master = self.wcanvas, font = font, justify = self._obj.get_horizontalalignment())
        self._e.insert(0, self._obj.get_text())
        self._e.focus_set()
        self._e.selection_range(0, tk.END)
        figwidth, figheight = self.fig.canvas.get_width_height()
        self.wcanvas.create_window([cx, figheight - cy], window = self._e, anchor = tk.CENTER)
        self._e.bind('<Return>', self._text_entry_return_callback)
        self._e.bind('<Escape>', self.clear)

    def _text_entry_return_callback(self, tkevent):
        self._obj.set_text(self._e.get())
        self.clear()
#        self._e.destroy()
        self.fig.canvas.draw_idle()

    def clear(self, event=None):
        self._e.destroy()
        self = None

    def contains(self, event):
        return self._obj.contains(event)

def get_positional_args(func):
    args = [x for x, p in signature(func).parameters.items() if p.default == Parameter.empty and p.kind not in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD] and p.name != 'self']
    if len(args)== 1:
        args = args[0]
    elif len(args)==0:
        args = ''
    else:
        args = ', '.join(args)
    return args
        

def get_all_args(func):
    posargs = []
    kwargs = []
    star_kwargs=False
    star_args=False
    starred = []
    for x,p in signature(func).parameters.items():
        if p.name != 'self':
            if p.kind not in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                if p.default == Parameter.empty:
                    posargs += [x]
                else:
                    kwargs += [x]
            elif p.kind ==Parameter.VAR_POSITIONAL:
                star_args = True
            elif p.kind ==Parameter.VAR_KEYWORD:
                star_kwargs = True
    if star_args:
        starred += ['*args']
    if star_args:
        starred += ['**kwargs']
    str_out = ', '.join(posargs + kwargs + starred) 
    return str_out
    
    
def get_subclasses(super_cls):
    return [cls for cls in super_cls.__subclasses__()]


        
class FigureEditor(object):
    #Perhaps the text-edit related stuff should ported to another class or functiont to keep the FigureEditor general in its definitions
    def __init__(self, obj = None):
        self._obj = obj
        if obj:
            self.set_obj(obj)

    def _update_status(self, event):
        if event.button == 1:
            self._entry_handler(event)
        elif event.button == 3:
            self._context_menu_handler(event)
            
    def set_obj(self, obj):
        self._obj = obj
        self.fig = obj.figure
        self.wcanvas = self.fig.canvas.get_tk_widget()
        self.reset()
        if isinstance(self._obj, Text):
            self._draw_selector('rect')
#        elif isinstance(self._obj, Line2D):
            

    def _draw_selector(self, selectortype):
        if selectortype == 'rect':
            b = self._obj.get_window_extent().padded(4).transformed(self.fig.transFigure.inverted())
            self._selector = matplotlib.patches.Rectangle((b.x0, b.y0), b.width, b.height, facecolor = 'none', transform = self.fig.transFigure)
            self.fig.patches.extend([self._selector])
            self.fig.canvas.draw_idle()
    
    def contains(self, event):
        return self._selector.contains(event)        

    def reset(self):
        try:
            if isinstance(self._selector, matplotlib.patches.Rectangle):
                self.fig.patches.remove(self._rect)
        except:
            pass
        self.fig.canvas.draw_idle()
 
    def _update_status(self, event):
        if event.button == 1:
            if isinstance(self._obj, Text):
                self.draw_entry()
        elif event.button == 3:
            self._context_menu_handler(event)

    def draw_entry(self):
        b = self._obj.get_window_extent()
        cx = b.x0 + b.width/2
        cy = b.y0 + b.height/2
        font = (self._obj.get_fontfamily()[0], int(self._obj.get_fontsize()), self._obj.get_fontstyle())
        self._e = ttk.Entry(master = self.wcanvas, font = font, justify = self._obj.get_horizontalalignment())
        self._e.insert(0, self._obj.get_text())
        self._e.focus_set()
        self._e.selection_range(0, tk.END)
        figwidth, figheight = self.fig.canvas.get_width_height()
        self.wcanvas.create_window([cx, figheight - cy], window = self._e, anchor = tk.CENTER)
        self._e.bind('<Return>', self._text_entry_return_callback)
        self._e.bind('<Escape>', self.remove_entry)

    def _text_entry_return_callback(self, tkevent):
        self._obj.set_text(self._e.get())
        self._e.destroy()
        self.fig.canvas.draw_idle()
        self.draw_rect()               

    def remove_entry(self, event=None):
        if self._e:
            self._e.destroy()
            self._e = None        


#THIS TextEditorWidget class should work as is:
#class TextEditorWidget(object):
#    def __init__(self, txtobj = None):
#        self._txtobj = txtobj
#        self._visible = False
#        if txtobj:
#            self.set_txtobj(txtobj)
#
#    def set_txtobj(self, txtobj):
#        self._txtobj = txtobj
#        self.fig = txtobj.figure
#        self.wcanvas = self.fig.canvas.get_tk_widget()
#        self._e = None
#        self.draw_rect()
#
#    def draw_rect(self):
#        self.reset()
#        b = self.obj.get_window_extent().padded(4).transformed(self.fig.transFigure.inverted())
#        self._rect = matplotlib.patches.Rectangle((b.x0, b.y0), b.width, b.height, facecolor = 'none', transform = self.fig.transFigure)
#        self.fig.patches.extend([self._rect])
#        self.fig.canvas.draw_idle()
#
#        
#    def _update_status(self, event):
#        if event.button == 1:
#            self._entry_handler(event)
#        elif event.button == 3:
#            self._context_menu_handler(event)
#
#    def _entry_handler(self, event):
#        if self.contains(event)[0]:
#            self.draw_entry()
#        else:
#            self.remove_entry()
#
#    def _context_menu_handler(self, event):
#        func = self._txtobj.set_color
#        m = tk.Menu(None, tearoff=0, takefocus=0)
#        m.add_command(label='test', command=self.remove_entry)
#        m.add_cascade(label='color', menu=self.menu_colors(m, func, selected_color = self._txtobj.get_color()))
#        root_coords = fig.canvas._master.winfo_geometry().split('+')
#        figwidth, figheight = self.fig.canvas.get_width_height()
#        m.tk_popup(int(root_coords[1]) + int(event.x), int(root_coords[2]) + figheight - int(event.y))
#        
#                
#    def contains(self, event):
#        return self._rect.contains(event)
#        
#    def draw_entry(self):
#        b = self._txtobj.get_window_extent()
#        cx = b.x0 + b.width/2
#        cy = b.y0 + b.height/2
#        font = (self._txtobj.get_fontfamily()[0], int(self._txtobj.get_fontsize()), self._txtobj.get_fontstyle())
#        self._e = ttk.Entry(master = self.wcanvas, font = font, justify = self._txtobj.get_horizontalalignment())
#        self._e.insert(0, self._txtobj.get_text())
#        self._e.focus_set()
#        self._e.selection_range(0, tk.END)
#        figwidth, figheight = self.fig.canvas.get_width_height()
#        self.wcanvas.create_window([cx, figheight - cy], window = self._e, anchor = tk.CENTER)
#        self._e.bind('<Return>', self.return_callback)
#        self._e.bind('<Escape>', self.remove_entry)
#
#    def remove_entry(self, event=None):
#        if self._e:
#            self._e.destroy()
#            self._e = None
#        
#    def return_callback(self, tkevent):
#        self._txtobj.set_text(self._e.get())
#        self._e.destroy()
#        self.fig.canvas.draw_idle()
#        self.draw_rect()
#    
#    def draw_rect(self):
#        self.reset()
#        b = self._txtobj.get_window_extent().padded(4).transformed(self.fig.transFigure.inverted())
#        self._rect = matplotlib.patches.Rectangle((b.x0, b.y0), b.width, b.height, facecolor = 'none', transform = self.fig.transFigure)
#        self.fig.patches.extend([self._rect])
#        self._visible = True
#        self.fig.canvas.draw_idle()
#        
#    def reset(self):
#        try:
#            self.fig.patches.remove(self._rect)
#        except:
#            pass
#        self._visible = False
#        self.fig.canvas.draw_idle()
#        
#        
#    def menu_colors(self, master, func, selected_color = None):
#        def give_color():
#            func(selectedColor.get())
#            self.fig.canvas.draw_idle()
#
#        m = tk.Menu(master, tearoff=0)
#        selectedColor = tk.StringVar()
#        colors = [ "Black", "White", "Blue", "Yellow", "Red", "Pink", "Gray", "Purple"]
#        if selected_color:
#            if selected_color not in colors:
#                colors.append(selected_color)
#                selectedColor.set( colors[-1] )
#            else:
#                selectedColor.set( colors.index(selected_color) )
#        else:
#            selectedColor.set( colors[ 0 ] )
#          
#        for item in colors:
#            m.add_radiobutton( label = item,
#            variable = selectedColor,
#            command = give_color )
#        return m

        
        
class InteractiveAxes(object):
    
    def __init__(self, ax):
        self.ax = ax
        self.fig = self.ax.figure
        self.scale_buttons = []
        self.scale_button_axes = []
        self.scale_button_ax_coords = []
        self.scaletypes = ['Linear', 'Logarithmic']
        self
        self.button_w = 0.03
        self.button_h = 0.2
#        self.register_xscale_buttons()
        self.register_scale_buttons()
        self.fig.canvas.mpl_connect('axes_enter_event', self.enter_callback)
        self.fig.canvas.mpl_connect('axes_leave_event', self.leave_callback)
        plt.sca(self.ax)
#        self.figure.canvas.mpl_disconnect('button_press_event')

    def register_xscale_buttons(self):
        pass
        
    def register_scale_buttons(self):
        axpos = self.ax.get_position()
        for scaletype in self.scaletypes:
            n = len(self.scale_button_axes)/2
            for axdim in ['x', 'y']:
                if axdim  is 'y':
                    ax = self.fig.add_axes([axpos.x0, axpos.ymax - self.button_h*(n+1),  self.button_w, self.button_h])
                else:
#                    ax = self.fig.add_axes([axpos.xmax - self.button_h * (n+1), axpos.y0 + 0.1,  self.button_h, self.button_w])
                    ax = self.fig.add_axes([axpos.xmax - self.button_h * (n+1), axpos.y0,  self.button_h, self.button_w])
                ax.set_zorder(10)
                b = Button(ax, scaletype, color='1', hovercolor='#FFFF88')
                if axdim  is 'y':
                    b.label.set_rotation(90)
                self.scale_button_axes += [ax]
                self.scale_buttons += [b]
                self.scale_button_ax_coords += [ax.bbox.get_points()]
                b.on_clicked(self.scale_callback)
        
    def xscale_callback(self, event):
        event
        
    def scale_callback(self, event):
        #Create a list that contains 'Logarithmic' and 'Linear' in the right order:
        sc = [item for sublist in  zip(self.scaletypes, self.scaletypes) for item in sublist]
        x, y = event.x, event.y
        for i, coords in enumerate(self.scale_button_ax_coords):
            if self._iswithin([x,y], coords):
                if sc[i] is 'Linear':
                    if self._box_alignment(coords) is 'horizontal':
                        self.ax.set_xscale('linear')
                    else:
                        self.ax.set_yscale('linear')
                elif sc[i] is 'Logarithmic':
                    if self._box_alignment(coords) is 'horizontal':
                        self.ax.set_xscale('log')
                    else:
                        self.ax.set_yscale('log')
                break
        
    def enter_callback(self, event):
        for scalebuttonax in self.scale_button_axes:
            scalebuttonax.set_visible(True)
            self.fig.canvas.draw_idle()

    def leave_callback(self, event):
        for scalebuttonax in self.scale_button_axes:
            scalebuttonax.set_visible(False)
            self.fig.canvas.draw_idle()
    
    def _iswithin(self, p, c):
#        print p,c
        result = c[0][0] <= p[0] <= c[1][0] and c[0][1] <= p[1] <= c[1][1]
#        print result
        return result

    def _box_alignment(self, c):
        if c[1][0] - c[0][0] > c[1][1] - c[0][1]:
            return 'horizontal'
        else:
            return 'vertical'
           
#mproj.projection_registry.register(InteractiveAxes)      

class AxesBinder(object):
    def __init__(self, ax):
        self.ax = ax
        self.fig = self.ax.get_figure()
        self._clickx = None
        self._clicky = None
        self._key = None
        self._button = None
        self._dragx = None
        self._dragy = None
        self._dragxy = None
        self._key = None
        self._binds = dict()
        self._lastx = None
        self._lasty = None
        self.cid_key_press = self.fig.canvas.mpl_connect('key_press_event', self._eventprocessor)
        self.cid_key_release = self.fig.canvas.mpl_connect('key_release_event', self._eventprocessor)
        self.cid_button_press = self.fig.canvas.mpl_connect('button_press_event', self._eventprocessor)
        self.cid_button_release = self.fig.canvas.mpl_connect('button_release_event', self._eventprocessor)
        self.cid_scroll = self.fig.canvas.mpl_connect('scroll_event',self._eventprocessor)
        self.cid_motion = self.fig.canvas.mpl_connect('motion_notify_event', self._eventprocessor)

    def bind(self, eventstr, func, factor = 1.0, axis='both'):
        eventtriggerstr = eventstr.replace('dragx', 'drag').replace('dragy', 'drag').replace('dragxy', 'drag')
        self._binds[eventtriggerstr] = [func, factor, axis, eventstr]
#        print self._binds

    def unbind(self, eventstr):
        eventtriggerstr = eventstr.replace('dragx', 'drag').replace('dragy', 'drag').replace('dragxy', 'drag')
        if eventtriggerstr in self._binds.keys():
            del self._binds[eventtriggerstr]

    def _eventprocessor(self, event):
        if event.inaxes == self.ax:
            self._event = event
            eventstr = []
            amount = dict(zip(['x','y','xy', 'dx','dy'], [0] * 5))
            if event.name=='key_press_event':
                if event.key == 'control':
                    self._key = 'ctrl'
                else:
                    self._key = event.key
                    
            elif event.name=='key_release_event':
                self._key = None
            
            if event.name=='button_press_event':
                self._button = event.button
                self._clickx = event.x
                self._clicky = event.y
                self._clickevent = event
                self._pan_start = cbook.Bunch(
                    lim=self.ax.viewLim.frozen(),
                    trans=self.ax.transData.frozen(),
                    trans_inverse=self.ax.transData.inverted().frozen(),
                    bbox=self.ax.bbox.frozen())
            elif event.name=='button_release_event':
                self._clickx = None
                self._clicky = None
                self._button = None
                self._dragx = None
                self._dragy = None
                self._dragxy = None
            if self._key:
                eventstr += [self._key]
            if event.name=='scroll_event':
               self._clickevent = event
               eventstr += ['scroll']
               amount = dict(zip(['x','y','xy', 'dx', 'dy'], [event.step] * 5))
            elif event.name=='motion_notify_event':
                if self._button is not None:
                    eventstr += ['drag']
                    amountx = event.x - self._clickx
                    amounty = event.y - self._clicky
                    dx = event.x - self._lastx
                    dy = event.y - self._lasty
                    amountxy = (amountx + amounty) /(2 ** 0.5)
                    amount = dict(x=amountx, y = amounty, xy = amountxy, dx = dx, dy = dy)
            elif self._button and self._button not in ('up', 'down'):
                eventstr += [str(self._button)]
            eventstr = '+'.join(eventstr)
            self._eventhandler(eventstr, amount)
            self._lastx = event.x
            self._lasty = event.y


    def _eventhandler(self, eventstr, amount):
        total_amount = 1
#        print(eventstr)
        if eventstr in self._binds.keys():
            func, factor, axis, eventstr0 = self._binds[eventstr]
            e = eventstr.split('+')
            if 'scroll' in e:
                amount['scalar'] = amount['dx']
            elif 'dragx' in e:
                amount['scalar'] = amount['dx']
            elif 'dragy' in e:
                amount['scalar'] = amount['dy']
            elif 'dragxy' in e:
                amount['scalar'] = amount['xy']
            elif 'drag' in e:
                amount['scalar'] = amount['xy']

#            print(e)

            func(amount, factor, axis)
#            print '{}({},{})'.format(func, factor,axis)
#            eval('{}({},{})'.format(func, factor,axis))

    def zoom(self, amount, factor = 0.1, axis='both', base_scale = 2.0):
#        print self._event.inaxes
        assert axis in ('both', 'x', 'y')        
        workonx = False
        workony = False
        if axis=='both':
            workonx = True
            workony = True
        elif axis =='x':
            workonx = True
        elif axis=='y':
            workony = True
        if self._event.name=='scroll_event':
            zoomfactor = 0.3
        else:
            zoomfactor = 0.01
        scale_factor = base_scale ** (amount['scalar'] * factor * zoomfactor)
        print(amount['scalar'])
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xdata = self._clickevent.xdata # get event x location
        ydata = self._clickevent.ydata # get event y location
        xa = xdata - cur_xlim[0]
        xb = cur_xlim[1] - xdata
        ya = ydata - cur_ylim[0]
        yb = cur_ylim[1] - ydata            
        if workonx:
            self.ax.set_xlim([xdata - xa*scale_factor,
                         xdata + xb*scale_factor])
        if workony:
            self.ax.set_ylim([ydata - ya*scale_factor,
                         ydata + yb*scale_factor])
        self._event.canvas.draw_idle() # force re-draw
            
            
    def pan(self, amount, factor=1.0, axis='both'):
#        print self._event.inaxes
        assert axis in ('both', 'x', 'y')        
        workonx = False
        workony = False
        if axis=='both':
            workonx = True
            workony = True
        elif axis =='x':
            workonx = True
        elif axis=='y':
            workony = True
                
        dx = amount['x']
        dy = amount['y']
#        print dx,dy

        if dx == 0 and dy == 0:
            return
        p = self._pan_start
        result = p.bbox.translated(-dx, -dy) \
            .transformed(p.trans_inverse)
        
        if dx != 0 and workonx:
            self.ax.set_xlim(*result.intervalx)

        if dy != 0 and workony:
            self.ax.set_ylim(*result.intervaly)
        self._event.canvas.draw_idle() # force re-draw
                        
def raise_window(figname=None):
    """
    Raise the plot window for Figure figname to the foreground.  If no argument
    is given, raise the current figure.

    This function will only work with a Tk graphics backend.  It assumes you
    have already executed the command 'import matplotlib.pyplot as plt'.
    """

    if figname: 
        plt.figure(figname)
    cfm = plt.get_current_fig_manager()
    cfm.window.attributes('-topmost', True)
    cfm.window.attributes('-topmost', False)
    cfm.window.focus()
    return cfm


def pick_callback(event):
    print(event.ind)
            




class PanZoom(object):
    def __init__(self, ax,base_scale = 1.5, whichaxes = 'both', persist = None):
        assert persist in (None, 'zoom', 'pan')
        assert whichaxes in ('both', 'x', 'y')        
        self.workonx = False
        self.workony = False
        if whichaxes=='both':
            self.workonx = True
            self.workony = True
        elif whichaxes=='x':
            self.workonx = True
        elif whichaxes=='y':
            self.workony = True
        
        self.ax = ax
        self.base_scale = base_scale
        self.ctrl_is_held = False
        self.space_is_held = False
        self._event = None
        self.persist = persist

        self.fig = self.ax.get_figure() # get the figure of interest
        # attach the call back
        self.fig.canvas.mpl_connect('scroll_event',self._zoom_fun)
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
        self.fig.canvas.mpl_connect('key_release_event', self._on_key_release)
        self.fig.canvas.mpl_connect('button_press_event', self._zoom_fun)
        self.fig.canvas.mpl_connect('button_release_event', self._zoom_fun)
        self.fig.canvas.mpl_connect('motion_notify_event', self._zoom_fun)
        
        
    def _on_key_press(self,event):
        if event.key == 'control':
            self.ctrl_is_held = True
        if event.key == ' ':
            self.space_is_held = True          
    
    def _on_key_release(self, event):
       if event.key == 'control':
           self.ctrl_is_held = False    
       if event.key == ' ':
           self.space_is_held = False    

    def _zoom_fun(self, event):
        if event.inaxes==self.ax:
            # get the current x and y limits
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.name == 'scroll_event' and (self.ctrl_is_held or self.persist == 'zoom'):
                #|---------X----------------------|
                #    xa               xb
                
                xa = xdata - cur_xlim[0]
                xb = cur_xlim[1] - xdata
                ya = ydata - cur_ylim[0]
                yb = cur_ylim[1] - ydata
                if event.button == 'up':
                    # deal with zoom in
                    scale_factor = 1/self.base_scale
        
                elif event.button == 'down':
                    # deal with zoom out
                    scale_factor = self.base_scale
                else:
                    # deal with something that should never happen
                    scale_factor = 1
                    print(event.button)
                # set new limits
                if self.workonx:
                    self.ax.set_xlim([xdata - xa*scale_factor,
                                 xdata + xb*scale_factor])
                if self.workony:
                    self.ax.set_ylim([ydata - ya*scale_factor,
                                 ydata + yb*scale_factor])

            elif (self.space_is_held or self.persist == 'pan'):
                if event.name == 'button_press_event':  # begin pan
                    self._event = event
                elif event.name == 'button_release_event':  # end pan
                    self._event = None
        
                elif event.name == 'motion_notify_event':  # pan
                    if self._event is None:
                        return

                    dx = xdata - self._event.xdata
                    dy = ydata - self._event.ydata
                    if dx != 0 and self.workonx:
                        self.ax.set_xlim(cur_xlim - dx)
    
                    if dy != 0 and self.workony:
                        self.ax.set_ylim(cur_ylim - dy)
                        
            event.canvas.draw_idle() # force re-draw



#class InteractiveAxes(plt.Axes):
#    name = 'interactive'
#    
#    def __init__(self, *args, **kwargs):
#        plt.Axes.__init__(self, *args, **kwargs)
#        self.scale_buttons = []
#        self.scale_button_axes = []
#        self.scale_button_ax_coords = []
#        self.scaletypes = ['Linear', 'Logarithmic']
#        self
#        self.button_w = 0.03
#        self.button_h = 0.2
##        self.register_xscale_buttons()
#        self.register_scale_buttons()
#        self.figure.canvas.mpl_connect('axes_enter_event', self.enter_callback)
#        self.figure.canvas.mpl_connect('axes_leave_event', self.leave_callback)
##        self.figure.canvas.mpl_disconnect('button_press_event')
#
#
#
#    def register_xscale_buttons(self):
#        pass
#        
#    def register_scale_buttons(self):
#        axpos = self.get_position()
#        for scaletype in self.scaletypes:
#            n = len(self.scale_button_axes)/2
#            for axdim in ['x', 'y']:
#                if axdim  is 'y':
#                    ax = self.figure.add_axes([axpos.x0, axpos.ymax - self.button_h*(n+1),  self.button_w, self.button_h])
#                else:
#                    ax = self.figure.add_axes([axpos.xmax - self.button_h * (n+1), axpos.y0 + 0.1,  self.button_h, self.button_w])
#                ax.set_zorder(10)
#                b = Button(ax, scaletype, color='1', hovercolor='#FFFF88')
#                if axdim  is 'y':
#                    b.label.set_rotation(90)
#                self.scale_button_axes += [ax]
#                self.scale_buttons += [b]
#                self.scale_button_ax_coords += [ax.bbox.get_points()]
#                b.on_clicked(self.scale_callback)
#        
#    def xscale_callback(self, event):
#        event
#        
#    def scale_callback(self, event):
#        #Create a list that contains 'Logarithmic' and 'Linear' in the right order:
#        sc = [item for sublist in  zip(self.scaletypes, self.scaletypes) for item in sublist]
#        x, y = event.x, event.y
#        for i, coords in enumerate(self.scale_button_ax_coords):
#            if self._iswithin([x,y], coords):
#                if sc[i] is 'Linear':
#                    if self._box_alignment(coords) is 'horizontal':
#                        self.set_xscale('linear')
#                    else:
#                        self.set_yscale('linear')
#                elif sc[i] is 'Logarithmic':
#                    if self._box_alignment(coords) is 'horizontal':
#                        self.set_xscale('log')
#                    else:
#                        self.set_yscale('log')
##                switcher = {
##                    'Linear': self.set_yscale('linear'),
##                    'Logarithmic': self.set_yscale('log'),
##                }
##                switcher.get(self.scaletypes[i])
##                plt.draw()
#                break
#        
#    def enter_callback(self, event):
#        for scalebuttonax in self.scale_button_axes:
#            scalebuttonax.set_visible(True)
#            self.get_figure().canvas.draw_idle()
#
#    def leave_callback(self, event):
#        for scalebuttonax in self.scale_button_axes:
#            scalebuttonax.set_visible(False)
#            self.get_figure().canvas.draw_idle()
#    
#    def _iswithin(self, p, c):
##        print p,c
#        result = c[0][0] <= p[0] <= c[1][0] and c[0][1] <= p[1] <= c[1][1]
##        print result
#        return result
#
#    def _box_alignment(self, c):
#        if c[1][0] - c[0][0] > c[1][1] - c[0][1]:
#            return 'horizontal'
#        else:
#            return 'vertical'
#           
#mproj.projection_registry.register(InteractiveAxes)      
    

#f = PanZoom(ax, persist = None, whichaxes = 'both')
 

if __name__ == '__main__':

    freqs = np.arange(2, 20, 3)
    fig, ax = plt.subplots()
    ax.plot(freqs, '.', label='testlabel')
    import pandas as pd
    df = pd.DataFrame(np.random.randn(6,4),columns=list('ABCD'))
#    ax.scatter(df['A'], df['B'])
#    fig, ax = plt.subplots()
#    ax.plot(df['A'], df['B'])
    #ax = fig.add_subplot(111)
#    iax = InteractiveAxes(ax)
    ifig = InteractiveFigure(fig)
    
#    plt.show()
    ##ax = fig.add_subplot(111)
    #plt.subplots_adjust(bottom=0.2)
    #t = np.arange(0.0, 1.0, 0.001)
    #s = np.sin(2*np.pi*freqs[0]*t)
    #tpts = np.arange(0.0, 1.0, 0.1)
    #spts = np.sin(2*np.pi*freqs[0]*tpts)
    #l, = plt.plot(t, s, lw=2)
    #pts, = plt.plot(tpts, spts, 'b*', markersize=10)
    #fig.canvas.mpl_connect('pick_event',pick_callback)
    #
    #
    #
    f = AxesBinder(ax)
    #f.bind('drag', f.pan, factor = 1.0)
    f.bind('ctrl+drag', f.pan)
    f.bind('ctrl+scroll', f.zoom)
    #to = fig.suptitle('tstst')
    #
    ##import matplotlib
    ##matplotlib.get_backend()
    #raise_window()
    #
    #plt.show()