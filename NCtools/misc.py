import re
import os

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

    
def file_get_basename(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def grouped(iterable, n=2):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)
    
def coords_to_extent(coords):
    raise NotImplementedError

def extent_to_coords(extent):
    return grouped([x for i in range(2) for x in extent[i::2]])    
 

def getpattern(pattern, txt):
    print('This function (NCs_tools.misc.gettpattern) is redundant to re.findall - use that instead!')
    try:
        result = re.search(pattern, txt).groups()
        if len(result)==1:
            return result[0]
        else:
            return result
    except AttributeError:
        # AAA, ZZZ not found in the original string
        return '' # apply your error handling    
        

class FileTemplate(object):
    def __init__(self, specs=None, template=None, file_basename=None, file_ext=None):
        if not os.path.exists(template):
            raise ValueError(f'File: {template} doesnt exist!')
        self.specs=specs
        self.file_basename = file_basename
        self.file_ext = file_ext
        self.file_template = template
        with open(self.file_template,'r') as f:
            self.template_str = f.read()
        self.string = self.template_str
        if specs:
            self.check_specs()
            params0= self.get_template_parameters()
            substitutions={}
            for p,default in params0.items():
                subname = '{'+p+','+default+'}'
                if p in self.specs.keys():
                    substitutions.update({subname:self.specs[p]})
                else:
                    substitutions.update({subname:params0[p]})
            self.substitutions = substitutions
            for subname,val in self.substitutions.items():
                self.string = self.string.replace(subname,str(val))
            #Should work? But throws a key error probably due to the float in the end of the keynames:
            #self.string = self.template_str.format(**substitutions)

    def to_file(self):
        with open(self.get_filename(), 'w') as f:
            f.write(self.string)
        print(f'File written: {self.get_filename()}')
        return self.get_filename()
            
    def get_filename(self):
        if not self.file_ext:
            self.file_ext = os.path.splitext(self.file_template)[1]
        if not self.file_basename:
            self.file_basename = os.path.splitext(self.file_template)[0]
        suffix = ''
        for p in sorted(self.specs.keys()):
            suffix += '_'+p.capitalize()+'_'+str(self.specs[p])
        return self.file_basename + suffix + self.file_ext

    def check_specs(self):
        if not isinstance(self.specs, dict):
            raise ValueError('Input specs type must be a dict')
            for p in self.specs.keys():
                if p not in self.get_template_parameters().keys():
                    raise ValueError(f'Could not find parameter: "{p})" from the specs in the template. Please check for consistency')
    def get_template_parameters(self):
        M = re.findall('{(\S+)}', self.template_str)
        params = {}
        for m in M:
            p,default = tuple(m.split(','))
            params.update({p:default})
        return params
    
class SimplePublisher(object):
    def __init__(self, events=None):
        # maps event names to subscribers
        # str -> dict
        self.events=dict()

        if events:
            self.add_event(events)

    def add_event(self, events):
        if isinstance(events, str):
            events = [events]
        self.events.update({ event : dict()
                          for event in events })
    def remove_event(self, events):
        if isinstance(events, str):
            events = [events]
        for event in events:
            if event in self.events:
                self.events.pop(event, None)

    def get_subscribers(self, event):
        return self.events[event]
    def register(self, event, who, callback=None):
        if callback == None:
            callback = getattr(who, 'update')
        self.get_subscribers(event)[who] = callback
    def unregister(self, event, who):
        del self.get_subscribers(event)[who]
    def dispatch(self, event, *message):
        for subscriber, callback in self.get_subscribers(event).items():
            callback(*message)    
    
    
if __name__ == '__main__':
    x = FileTemplate(template=r'.\data\template.txt', specs={'R':5000, 'soil_density':3})
        
