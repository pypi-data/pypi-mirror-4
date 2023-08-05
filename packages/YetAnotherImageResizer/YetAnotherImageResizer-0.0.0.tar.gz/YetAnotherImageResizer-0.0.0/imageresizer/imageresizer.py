import image
import arbo
import logging
import os
from observable import Observable

class ImageResizer(Observable):

    logger = logging.getLogger("imageresizer")

    def __init__(self, source_dir, destination_dir):

        Observable.__init__(self)
        self.source_dir = source_dir
        self.destination_dir = destination_dir

    def browse(self):
        dirnames = arbo.list_dir(self.source_dir)
        for dirname in dirnames:
            current_source_dir = os.path.join(self.source_dir, dirname)
            current_destination_dir = os.path.join(self.destination_dir, dirname)
            for x in (x for x in os.listdir(current_source_dir) if x[-3:].lower() == "jpg"):
                yield (current_destination_dir,
                       os.path.join(current_source_dir, x))

    def check(self):
        return len(list(self.browse()))


    def process(self):
        self.logger.debug("source_dir='%s' destination_dir='%s'" %
                         (self.source_dir,
                          self.destination_dir))
        nb = 0
        for c in self.browse():
            d, f = c
            nb += 1
            self.logger.debug("Process source_file '%s' destination_dir '%s'" % (f,d))
            i = image.MyImageButMieux(f,d)
            i.process()
            self.emit(nb, f)
        return nb
