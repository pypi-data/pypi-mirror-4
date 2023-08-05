import ConfigParser
import os.path
import re


class Singleton(type):
    """ This class implement the singleton pattern for other classes. """
    def __init__(mcs, *args):
        type.__init__(mcs, *args)
        mcs._instance = None

    def __call__(mcs, *args):
        if mcs._instance is None:
            mcs._instance = type.__call__(mcs, *args)
        return mcs._instance



class Config:
    
      
    __metaclass__ = Singleton
    def __init__(self):
        self._options = {'lessontime': 5,
                         'countdown': 5,
                         'speed': 25,
                         'effspeed': 12,
                         'frequency': 750,
                         'volume': 0,
                         'lesson': 2,
                         'preferlast': False,
                         'ignorechars': ''}

        self._bool_opts  = ['preferlast']
        self._int_opts   = ['lessontime', 'countdown', 'speed', 'effspeed', 'frequency',
                            'lesson']
        self._float_opts = ['volume']
        self._str_opts   = ['ignorechars']
        self.__filename = os.path.expanduser("~/.kochmorse")

        if os.path.exists(self.__filename):
            self.load()
        else:
            self.save()


    def load(self):
        cfg = ConfigParser.SafeConfigParser()
        cfg.read([self.__filename])
        
        if not cfg.has_section('basic'):
            return

        for option in self._options.keys():
            if not cfg.has_option('basic',option):
                continue
            if option in self._float_opts:
                self._options[option] = cfg.getfloat('basic', option)
            elif option in self._bool_opts:
                self._options[option] = cfg.getboolean('basic', option)
            elif option in self._int_opts:
                self._options[option] = cfg.getint('basic', option)
            else:
                self._options[option] = cfg.get('basic', option)
                    

    def save(self):
        cfg = ConfigParser.SafeConfigParser()
        cfg.read([self.__filename])
        
        if not cfg.has_section('basic'):
            cfg.add_section('basic')
        
        for (key, value) in self._options.items():
            if key in self._float_opts:
                value = str(float(value))
            elif key in self._bool_opts:
                value = str(bool(value))
            elif key in self._int_opts:
                value = str(int(value))
            elif key in self._str_opts:
                value = str(value)
                    
            cfg.set('basic', key, value)

        cfg.write(open(self.__filename, "w"))
    

    def __getattr__(self, name):
        m = re.match("^opt_(.+)$", name)
        if not m: 
            return object.__getattribute__(self, name)
      
        return self._options[m.group(1)]


    def __setattr__(self, name, value):
        m = re.match("^opt_(.+)$", name)

        if not m:
            self.__dict__[name] = value
        else: 
            self._options[m.group(1)] = value
