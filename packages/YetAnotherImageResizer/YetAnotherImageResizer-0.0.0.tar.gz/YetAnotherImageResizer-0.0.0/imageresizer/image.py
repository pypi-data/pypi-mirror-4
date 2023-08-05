import os
import shutil
import Image
import logging

class ProcessImage:
    
    logger = logging.getLogger(__name__)
    
    def __init__(self, file, destination_directory):
        self.destination_directory = destination_directory
        self.filename = os.path.basename(file)
        self.file = file
        
    def destination_filename(self, format_filename="%s"):
        ext = self.filename[-3:]
        filename = self.filename[:-4]
        return "%s.%s" % ((format_filename % filename) , ext)
    
    def destination_dirname(self, subdirectory = None):
        if subdirectory:
            return os.path.join(self.destination_directory, subdirectory)
        else:
            return self.destination_directory
    
    def process(self):
        self.logger.info("Process %s %s => %s ..." % (self.__class__.__name__, self.file, os.path.join(self.destination_dirname(),self.destination_filename())))
        if not os.path.exists(self.destination_dirname()):
            os.makedirs(self.destination_dirname())
    
    def resize(self, img, box, fit, out, resize = False):
        '''Downsample the image.
       @param img: Image -  an Image-object
       @param box: tuple(x, y) - the bounding box of the result image
       @param fix: boolean - crop the image to fill the box
       @param out: file-like-object - save the image into the output stream
       '''
        img = Image.open(img)
        
        #preresize image with factor 2, 4, 8 and fast algorithm
        factor = 1
        while img.size[0]/factor > 2*box[0] and img.size[1]*2/factor > 2*box[1]:
            factor *=2
        if factor > 1:
            img.thumbnail((img.size[0]/factor, img.size[1]/factor), Image.NEAREST)
     
        #calculate the cropping box and get the cropped part
        if fit:
            x1 = y1 = 0
            x2, y2 = img.size
            wRatio = 1.0 * x2/box[0]
            hRatio = 1.0 * y2/box[1]
            if hRatio > wRatio:
                y1 = int(y2/2-box[1]*wRatio/2)
                y2 = int(y2/2+box[1]*wRatio/2)
            else:
                x1 = int(x2/2-box[0]*hRatio/2)
                x2 = int(x2/2+box[0]*hRatio/2)
            img = img.crop((x1,y1,x2,y2))
     
        #Resize the image with best quality algorithm ANTI-ALIAS
        if resize:
            img = img.resize(box, Image.ANTIALIAS)
        else:
            img.thumbnail(box, Image.ANTIALIAS)
     
        #save it into a file-like object
        img.save(out, "JPEG", quality=100)
    #resize


class ProcessHighQuality(ProcessImage):
    
    def destination_filename(self, format_filename="%s"):
        return ProcessImage.destination_filename(self, format_filename=format_filename)
    
    def destination_dirname(self, subdirectory="pwg_high"):
        return ProcessImage.destination_dirname(self, subdirectory=subdirectory)
 
    def process(self):
        ProcessImage.process(self)
        shutil.copy(self.file, os.path.join(self.destination_dirname(),self.destination_filename()))

class ProcessThumbnail(ProcessImage):
    
    def destination_filename(self, format_filename="TN-%s"):
        return ProcessImage.destination_filename(self, format_filename=format_filename)
    
    def destination_dirname(self, subdirectory="thumbnail"):
        return ProcessImage.destination_dirname(self, subdirectory=subdirectory)
    
    def process(self):
        ProcessImage.process(self)
        ProcessImage.resize(self,self.file, (128,128), False, os.path.join(self.destination_dirname(),self.destination_filename()))
        
class ProcessMediumQuality(ProcessImage):
    
    def destination_filename(self, format_filename="%s"):
        return ProcessImage.destination_filename(self, format_filename=format_filename)
    
    def destination_dirname(self, subdirectory=""):
        return ProcessImage.destination_dirname(self, subdirectory=subdirectory)
    
    def process(self):
        ProcessImage.process(self)
        ProcessImage.resize(self,self.file, (9999,512), False, os.path.join(self.destination_dirname(),self.destination_filename()))
   
class ProcessCustom(ProcessImage):
    
    def __init__(self, file, destination_directory, format_filename, size, square = False):
        ProcessImage.__init__(self, file, destination_directory)
        self.format_filename = format_filename
        self.square = square
        self.size = size
    
    def destination_filename(self, format_filename= None):
        if not format_filename:
            format_filename = self.format_filename
        return ProcessImage.destination_filename(self, format_filename=format_filename)
    
    def destination_dirname(self, subdirectory=""):
        return ProcessImage.destination_dirname(self, subdirectory=subdirectory)
    
    def process(self):
        ProcessImage.process(self)
        ProcessImage.resize(self,self.file, self.size, False, os.path.join(self.destination_dirname(),self.destination_filename()), self.square)

class MyImage:

    def __init__(self, image_src, destination_dir):
        self.image_src = image_src
        self.destination_dir = destination_dir

    def process(self):
        pt = ProcessThumbnail(self.image_src,self.destination_dir)
        pt.process()
        pq = ProcessHighQuality(self.image_src, self.destination_dir)
        pq.process()
        pm = ProcessMediumQuality(self.image_src, self.destination_dir)
        pm.process()

class MyImageButMieux:

    def __init__(self, image_src, destination_dir):
        self.image_src = image_src
        self.destination_dir = destination_dir

    def process(self):

        sizes = {
      'IMG_SQUARE': ('%s-sq', (120,120) ),
      'IMG_THUMB': ('%s-th', (120,96) ),
      'IMG_XXSMALL': ( '%s-2s' , (240,240) ),
      'IMG_XSMALL': ( '%s-xs' , (432,324) ),
      'IMG_SMALL': ( '%s-sm' , (576,432) ),
      'IMG_MEDIUM': ( '%s-me' , (800,600) ),
      'IMG_LARGE': ( '%s-la' , (1008,756) ),
      'IMG_XLARGE': ( '%s-xl' , (1224,918) ),
      'IMG_XXLARGE': ( '%s-xx', (1656,1242) )}

        for k,v in sizes.items():
            format_filename, size = v
            print k
            print "format_filename ", format_filename
            print "size ", size
            if k == 'IMG_SQUARE':
                i = ProcessCustom(self.image_src,self.destination_dir, format_filename, size, True)
            else:
                i = ProcessCustom(self.image_src,self.destination_dir, format_filename, size)
            i.process()
