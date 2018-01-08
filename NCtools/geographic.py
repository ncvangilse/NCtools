# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 16:39:02 2017

@author: fbx182
"""

import geotiler
import utm
#import redis
#import functools
#from geotiler.cache import redis_downloader
from mpl_toolkits.basemap import Basemap
import numpy as np
#import copy
import matplotlib.pyplot as plt


class CoordinateHelper(object):
    def __init__(self, x=None,y=None, zone=None, zone_number=None,  zone_letter=None, mm=None, bbox_expand=0.05, projection='merc', **kwargs):
        self.expand = bbox_expand
        if zone and not (zone_number and zone_letter):
            self._zone_number = int(zone[0:2])
            self._zone_letter = zone[2:3]
        else:
            self._zone_number=zone_number
            self._zone_letter = zone_letter
        self.zone_numbers = None
        self.zone_letters = None
        self.set_xy(x,y)
        if not x is None:
            if not mm:
                self.mm = self.get_basemap(projection=projection, **kwargs)
            elif isinstance(mm, Basemap):
                self.mm = mm
            else:
                raise ValueError('bmap must be a mpl_toolkits.basemap.Basemap but is a {type(mm)}')
        
        
    def set_xy(self,x,y, ctype=None):
        self.x = np.array(x)
        self.y = np.array(y)
        if self.x.shape != self.y.shape:
            raise ValueError(f'x and y must have same shape! ({self.x.shape} != {self.y.shape})')
        if ctype in ['latlon', 'img', 'utm']:
            self.type = ctype
        else:
            self._detect_type()
#        try:

        if not self._zone_number is None:
            self.zone_numbers = np.tile(self._zone_number, self.x.shape)
            if not self._zone_letter is None:
                self.zone_letters = np.tile(self._zone_letter, self.x.shape)
                return

        self.zone_numbers, self.zone_letters = self._get_zones()
#        self.zone_numbers = zone_numbers
#        print(zone_numbers, zone_letters )
#                self.zone_letter = zone_letter
#                and not self.zone_letter is None:
#            if (self.zone_number, self.zone_letter) != (zone_number, zone_letter):
#                Warning('The zone for the new data ((zone_number, zone_letter)} does not correspond to the zone already initialized ({self.zone_number, self.zone_letter}).')
#        except Exception as ex:
#            print(ex)
        
            
    def _detect_type(self):
#        print(self.y, type(self.y))
        if all([np.all((-180<=c) & (c<=180)) for c in (self.x,self.y)]):
            self.type = 'latlon'
            y = self.y
            self.y = self.x
            self.x = y
        elif all([np.all((0<c) & (c<1e5)) for c in (self.x,self.y)]):
            self.type = 'img'
        elif all([np.all((0<c) & (c<1e7)) for c in (self.x,self.y)]):
            self.type = 'utm'
        else:
            raise ValueError('Could not detect coord type (latlon/utm/img) based on data ranges')
        print(f'{self.type} detected')

    def get_bbox_latlon(self, format='latlon'):
        lat,lon = self.to_latlon()
        lonm = lon.min()
        lonM = lon.max()
        latm = lat.min()
        latM = lat.max()
        lonex = (lonM-lonm)*self.expand/2
        latex = (latM-latm)*self.expand/2
        if format=='basemap':
            return {
                'llcrnrlon':lonm - lonex,
                'llcrnrlat':latm - latex,
                'urcrnrlon':lonM + lonex,
                'urcrnrlat':latM + latex
            }
        elif format[0:6]=='lonlat':
            bbox = (
                lonm - lonex,
                latm - latex,
                lonM + lonex,
                latM + latex
            )
        else:
            bbox = (
                latm - latex,
                lonm - lonex,
                latM + latex,
                lonM + lonex
            )
        if format[-1]==',':
            return (bbox[0:2], bbox[2:4])
        else:
            return bbox
    
    def get_bbox_utm(self):
        bbox = self.get_bbox_latlon(format='latlon')
        return tuple([utm.from_latlon(lat, lon)[0:2] for lat,lon in  zip(bbox[::2], bbox[1::2])])

    def get_basemap(self, **kwargs):
        self.mm = Basemap(**self.get_bbox_latlon(format='basemap'), **kwargs)
        return self.mm

    def get_osm_zoom_level(self, bbox):
        m0 = 156412
        bbox = self.get_bbox_latlon(format='latlon,')
        dlat = bbox[1][0]-bbox[0][0]
        dlon = bbox[1][1] - bbox[0][1]
        level_diff =np.abs(np.array([360/2**x for x in range(20)])-max(dlat, dlon))
        level = level_diff.argmin()+2
        print(f'OSM level {level} selected to display minimum {max(dlat, dlon)} degrees')
        return level
        
    def get_osm(self, *args, provider='osm', **kwargs):
        #geotiler cannot handle the bbox to be of type numpy, so convert to native floats:
        bbox = [x.item() for x in self.get_bbox_latlon(format='lonlat')]
        gm = geotiler.Map(extent=bbox, zoom=self.get_osm_zoom_level(bbox), provider=provider)
        self.img = geotiler.render_map(gm)
        return self.mm.imshow(self.img, *args, interpolation='lanczos', origin='upper', **kwargs)

    def to_img(self):
        if self.type=='img':
            return (self.x, self.y)
        else:
            if isinstance(self.mm, Basemap):
                if self.type=='latlon':
                    return self.mm(self.x,self.y, latlon=True)
                elif self.type=='utm':
                    f = np.vectorize(utm.to_latlon)
                    return self.mm(f(self.x,self.y, zone_number=self.zone_numbers, zone_letter=self.zone_letters), latlon=True)
            else:
                raise AttributeError('Cannot convert image coordinates to latlon as no basemap is defined!')

    def to_utm(self):
        f = np.vectorize(utm.from_latlon)
        if self.type=='latlon':
            return f(self.x,self.y)[0:2]
        elif self.type=='utm':
            return (self.x, self.y)
        elif self.type=='img':
            if isinstance(self.mm, Basemap):
                return f(self.mm(self.x, self.y))[0:2]
            else:
                raise AttributeError('Cannot convert image coordinates to UTM as no basemap is defined!')

    def to_lonlat(self):
        lat, lon = self.to_latlon()
        return (lon, lat)

    def to_latlon(self):
        if self.type=='latlon':
            return (self.x, self.y)
        elif self.type=='utm':
            f = np.vectorize(utm.to_latlon)
            return f(self.x,self.y, zone_number=self.zone_numbers, zone_letter=self.zone_letters)
        elif self.type=='img':
            if isinstance(self.mm, Basemap):
                return self.mm(self.x, self.y)
            else:
                raise AttributeError('Cannot convert image coordinates to latlon as no basemap is defined!')

    def _get_zones(self):
        f_letter = np.vectorize(utm.latitude_to_zone_letter)
        f_number = np.vectorize(utm.latlon_to_zone_number)
        lat, lon = self.to_latlon()
        zone_numbers = f_number(lat,lon)
        zone_letters = f_letter(lat)
        if len(set(zip(zone_numbers.ravel(), zone_letters.ravel()))) !=1:
            print(f'Coordinates are spread across several UTM zones {[str(n) + l for n,l in set(zip(zone_numbers.ravel(), zone_letters.ravel()))]}')
        return zone_numbers, zone_letters

def poly_area2D(poly):
    '''
    From https://gist.github.com/rob-murray/11245628
    An implementation of Green's theorem, an algorithm to calculate area of 
    a closed polgon. This works for convex and concave polygons that do not
    intersect oneself whose vertices are described by ordered pairs.
    Args:
        poly: The polygon expressed as a list of vertices, or 2D vector points
    '''

    # ensure we have a list; best to assert that it isnt a string as in python several types can
    # act as a list
    assert not isinstance(poly, str) 

    total = 0.0
    N = len(poly)
    for i in range(N):
        v1 = poly[i]
        v2 = poly[(i+1) % N]
        total += v1[0]*v2[1] - v1[1]*v2[0]
    return abs(total/2)


if __name__ == '__main__':
#    c = Coord(np.random.normal(5e5,1e4,100), np.random.normal(5e5,1e4,100))
#    c = CoordinateHelper(np.random.normal(12.568337,0.1,100), np.random.normal(55.676097,0.05,100))
    X,Y = np.meshgrid(np.linspace(12,13,100), np.linspace(55,56,100))
    c = CoordinateHelper(X,Y)
    
#    c.get_osm(provider='stamen-toner')
#    c.get_osm()
           