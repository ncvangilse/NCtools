import collections
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms

class MarkerSize(object):
    def __init__(self, series, minsize=20, maxsize=100):
        import matplotlib
        self.series = series
        self.min = series.min()
        self.max = series.max()
        self.minsize=minsize
        self.maxsize=maxsize
        self.name = series.name
        self.norm = matplotlib.colors.Normalize(series.min(), series.max())

    def select(self, df):
        return self.get_sizes(self.series.loc[df.index])

    def get_sizes(self, values):
        return self.minsize + self.norm(values) * (self.maxsize-self.minsize)        

    def legend(self, nsizes=5, ax=None, roundoff=True, **kwargs):
        size =collections.OrderedDict() 
        for s in np.linspace(self.min, self.max, nsizes):
            if roundoff:
                s=round(s)
            size[s] = plt.scatter([],[], s=self.get_sizes(s), facecolor='none', edgecolors='k')
        self.leg = secondary_legend(ax, size.values(), size.keys(), title=self.name, **kwargs)


def secondary_legend(ax=None, *args, rel_loc = 'left', **kwargs):
    if not ax:
        ax = plt.gca()
    old_legend = ax.get_legend()
    leg = ax.legend(*args, **kwargs)
    if old_legend:
        ax.add_artist(old_legend)
        ax.figure.canvas.draw()
        bb0 = old_legend.get_window_extent()
        bb1 = leg.get_window_extent().transformed(ax.transAxes.inverted())
        if rel_loc in ['left', 'right'] :
            bb1.y1 += 0.015
            dx = (bb0.x1 - bb0.x0)/72
            dy = 0
            if rel_loc == 'left':
                dx = -dx
        if rel_loc in ['over', 'under'] :
            bb1.x1 += 0.015
            dy = (bb0.y1 - bb0.y0)/72
            dx = 0
            if rel_loc == 'under':
                dy = -dy
        offset = transforms.ScaledTranslation(dx, dy, ax.figure.dpi_scale_trans)
        shadow_transform = ax.transAxes + offset
        leg.set_bbox_to_anchor(bb1, transform =shadow_transform)
    return leg
    
    