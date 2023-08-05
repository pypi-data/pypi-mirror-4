import gtk
import os.path
from conffile import Config
from alsamorse import KochLesson

class PropertyDialog:
    def __init__(self):
        self.__gladefile = os.path.join(os.path.dirname(__file__), "propdialog.glade")
        self.__xml = gtk.glade.XML(self.__gladefile,"propdialog")
        self.__widget = self.__xml.get_widget("propdialog")
        self.__lessontime = self.__xml.get_widget("lessontime")
        self.__countdown  = self.__xml.get_widget("countdown")
        self.__prefer_last = self.__xml.get_widget("prefer_last")
        self.__ign_box = self.__xml.get_widget("ignorechars")
        
        cfg = Config()
        self.__lessontime.set_value(cfg.opt_lessontime)
        self.__countdown.set_value(cfg.opt_countdown)
        self.__prefer_last.set_active(cfg.opt_preferlast)
        self.__ign_box.set_text(cfg.opt_ignorechars)
        
            

    def run(self):
        if self.__widget.run() == gtk.RESPONSE_CANCEL:
            self.__widget.destroy()
            return None

        


        cfg = Config()
        cfg.opt_lessontime  = self.__lessontime.get_value()
        cfg.opt_countdown   = self.__countdown.get_value()
        cfg.opt_preferlast  = self.__prefer_last.get_active()
        cfg.opt_ignorechars = filter(lambda x: x in KochLesson.chars,
                                     self.__ign_box.get_text())
        cfg.save()

        self.__widget.destroy()

                

