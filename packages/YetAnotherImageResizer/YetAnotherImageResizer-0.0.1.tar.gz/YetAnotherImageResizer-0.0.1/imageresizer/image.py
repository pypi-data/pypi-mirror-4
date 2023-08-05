""" Module image contains the list of function to manage image. """
import os
import shutil
import Image
import logging

class ProcessImage:
    """ Class to proces somes operations on an image. """

    logger = logging.getLogger(__name__)

    def __init__(self, image_file, destination_directory):
        self.destination_directory = destination_directory
        self.filename = os.path.basename(image_file)
        self.image_file = image_file

    def destination_filename(self, format_filename="%s"):
        """ Returns the destination filename of the image after process on the
        image. """

        ext = self.filename[-3:]
        filename = self.filename[:-4]
        return "%s.%s" % ((format_filename % filename) , ext)

    def destination_dirname(self, subdirectory = None):
        """ Returns the destination directory of the image after process on the
        image. """

        if subdirectory:
            return os.path.join(self.destination_directory, subdirectory)
        else:
            return self.destination_directory

    def process(self):
        """ Performs the process on the image.
        This method must be overidden.
        Actually, it's creating the destination folder. """

        self.logger.info("Process %s %s => %s ..." % (
            self.__class__.__name__,
            self.image_file,
            os.path.join(
                self.destination_dirname(),
                self.destination_filename())))
        if not os.path.exists(self.destination_dirname()):
            os.makedirs(self.destination_dirname())

    @staticmethod
    def resize(img, box, fit, out, resize = False):
        """ Downsample the image.
        @param img: Image -  an Image-object
        @param box: tuple(x, y) - the bounding box of the result image
        @param fix: boolean - crop the image to fill the box
        @param out: file-like-object - save the image into the output stream
        """

        img = Image.open(img)

        #preresize image with factor 2, 4, 8 and fast algorithm
        factor = 1
        while img.size[0]/factor > 2*box[0] and img.size[1]*2/factor > 2*box[1]:
            factor *= 2
        if factor > 1:
            img.thumbnail((img.size[0]/factor, img.size[1]/factor),
                    Image.NEAREST)

        #calculate the cropping box and get the cropped part
        if fit:
            x_1 = y_1 = 0
            x_2, y_2 = img.size
            w_ratio = 1.0 * x_2/box[0]
            h_ratio = 1.0 * y_2/box[1]
            if h_ratio > w_ratio:
                y_1 = int(y_2/2-box[1]*w_ratio/2)
                y_2 = int(y_2/2+box[1]*w_ratio/2)
            else:
                x_1 = int(x_2/2-box[0]*h_ratio/2)
                x_2 = int(x_2/2+box[0]*h_ratio/2)
            img = img.crop((x_1, y_1, x_2, y_2))

        #Resize the image with best quality algorithm ANTI-ALIAS
        if resize:
            img = img.resize(box, Image.ANTIALIAS)
        else:
            img.thumbnail(box, Image.ANTIALIAS)

        #save it into a file-like object
        img.save(out, "JPEG", quality=100)

class ProcessHighQuality(ProcessImage):
    """ Class to copy the image (used for the high quality image)"""

    def destination_filename(self, format_filename="%s"):
        return ProcessImage.destination_filename(self,
                format_filename=format_filename)

    def destination_dirname(self, subdirectory="pwg_high"):
        return ProcessImage.destination_dirname(self, subdirectory=subdirectory)

    def process(self):
        ProcessImage.process(self)
        shutil.copy(self.image_file, os.path.join(self.destination_dirname(),
            self.destination_filename()))

class ProcessThumbnail(ProcessImage):
    """ Class to resize the image to the specified size (128, 128) """

    def destination_filename(self, format_filename="TN-%s"):
        return ProcessImage.destination_filename(self,
                format_filename=format_filename)

    def destination_dirname(self, subdirectory="thumbnail"):
        return ProcessImage.destination_dirname(self,
                subdirectory=subdirectory)

    def process(self):
        ProcessImage.process(self)
        ProcessImage.resize(
                self.image_file,
                (128, 128),
                False,
                os.path.join(
                    self.destination_dirname(),
                    self.destination_filename()))

class ProcessMediumQuality(ProcessImage):
    """ Class to resize the image to the specified size (9999, 512) """

    def destination_filename(self, format_filename="%s"):
        return ProcessImage.destination_filename(self,
                format_filename=format_filename)

    def destination_dirname(self, subdirectory=""):
        return ProcessImage.destination_dirname(self,
                subdirectory=subdirectory)

    def process(self):
        ProcessImage.process(self)
        ProcessImage.resize(
                self.image_file,
                (9999, 512),
                False,
                os.path.join(
                    self.destination_dirname(),
                    self.destination_filename()))

class ProcessCustom(ProcessImage):
    """ Class to resize the image to a specified size """

    def __init__(self, image_file, destination_directory, format_filename,
            size, square = False):
        ProcessImage.__init__(self, image_file, destination_directory)
        self.format_filename = format_filename
        self.square = square
        self.size = size

    def destination_filename(self, format_filename= None):
        if not format_filename:
            format_filename = self.format_filename
        return ProcessImage.destination_filename(self,
                format_filename=format_filename)

    def destination_dirname(self, subdirectory=""):
        return ProcessImage.destination_dirname(self, subdirectory=subdirectory)

    def process(self):
        ProcessImage.process(self)
        ProcessImage.resize(
                self.image_file,
                self.size,
                False,
                os.path.join(
                    self.destination_dirname(),
                    self.destination_filename()),
                self.square)

class MyImage:
    """ Class to create all the images required by Piwigo (before 2.4) """

    def __init__(self, image_src, destination_dir):
        self.image_src = image_src
        self.destination_dir = destination_dir

    def process(self):
        """ Creates all the images required by Piwigo (before 2.4) """

        ProcessThumbnail(self.image_src, self.destination_dir).process()
        ProcessHighQuality(self.image_src, self.destination_dir).process()
        ProcessMediumQuality(self.image_src, self.destination_dir).process()

class MyImageButMieux:
    """ Class to create all the images required by Piwigo (after 2.4) """

    def __init__(self, image_src, destination_dir):
        self.image_src = image_src
        self.destination_dir = destination_dir

    def process(self):
        """ Creates all the images required by Piwigo (after 2.4) """

        sizes = {
      'IMG_SQUARE': ('%s-sq', (120, 120) ),
      'IMG_THUMB': ('%s-th', (120, 96) ),
      'IMG_XXSMALL': ( '%s-2s' , (240, 240) ),
      'IMG_XSMALL': ( '%s-xs' , (432, 324) ),
      'IMG_SMALL': ( '%s-sm' , (576, 432) ),
      'IMG_MEDIUM': ( '%s-me' , (800, 600) ),
      'IMG_LARGE': ( '%s-la' , (1008, 756) ),
      'IMG_XLARGE': ( '%s-xl' , (1224, 918) ),
      'IMG_XXLARGE': ( '%s-xx', (1656, 1242) )}

        for key, value in sizes.items():
            format_filename, size = value
            if key == 'IMG_SQUARE':
                i = ProcessCustom(self.image_src, self.destination_dir,
                        format_filename, size, True)
            else:
                i = ProcessCustom(self.image_src, self.destination_dir,
                        format_filename, size)
            i.process()
