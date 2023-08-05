""" Module imageresizer contains the class to create all the images required
by Piwigo. """
import image
import arbo
import logging
from observable import Observable

class ImageResizer(Observable):
    """ Class to create all the images required by Piwigo.
    Gets all the images from a source directory and creates the full file tree
    required by Piwigo into a destination directory.
    """

    logger = logging.getLogger("imageresizer")

    def __init__(self, source_dir, destination_dir):
        Observable.__init__(self)
        self.source_dir = source_dir
        self.destination_dir = destination_dir

    def browse(self):
        """ Enumerates the images to process. """

        return arbo.browse(self.source_dir, self.destination_dir)

    def check(self):
        """ Returns the number of images to process. """

        return len(list(self.browse()))

    def process(self):
        """ Create all the images required by Piwigo. """

        self.logger.debug("source_dir='%s' destination_dir='%s'" %
                         (self.source_dir,
                          self.destination_dir))
        current_step = 0
        for (image_file, destination_dir) in self.browse():
            current_step += 1
            self.logger.debug("Process source_file '%s' destination_dir '%s'" \
                    % (image_file,destination_dir))
            i = image.MyImageButMieux(image_file, destination_dir)
            #i.process()
            self.emit(current_step, image_file)
        return current_step
