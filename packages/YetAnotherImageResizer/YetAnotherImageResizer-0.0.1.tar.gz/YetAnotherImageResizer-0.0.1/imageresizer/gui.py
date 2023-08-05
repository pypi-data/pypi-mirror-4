""" Module gui contains the Tk GUI. """
import Tkinter
import tkFileDialog
import ttk
import logging.config
import imageresizer
import os

class ImageResizerApp:
    """ Class to display a Tk GUI to create the images required by Piwigo. """

    def __init__(self, master):

        pwd = os.path.dirname(__file__)
        print "file", __file__
        print pwd
        logging.config.fileConfig(os.path.join(pwd,'logger.ini'))

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = '~/Images'
        options['mustexist'] = True
        options['parent'] = master
        options['title'] = 'This is a title'

        self.source_dir = None
        self.source_dirvar = Tkinter.StringVar()
        self.source_dirvar.set('...')

        self.destination_dir = None
        self.destination_dirvar = Tkinter.StringVar()
        self.destination_dirvar.set('...')

        frame = Tkinter.Frame(master)
        frame.pack()

        self.choose_source_dir = Tkinter.Button(frame,
                text='Please choose source directory',
                command=self.asksrcdirectory)
        self.choose_source_dir.pack(side=Tkinter.TOP)

        self.label_source_dir = Tkinter.Label(frame,
                textvariable=self.source_dirvar)
        self.label_source_dir.pack(side=Tkinter.TOP)

        self.choose_destination_dir = Tkinter.Button(frame,
                text='Please choose destination directory',
                command=self.askdstdirectory)
        self.choose_destination_dir.pack(side=Tkinter.TOP)

        self.label_destination_dir = Tkinter.Label(frame,
                textvariable=self.destination_dirvar)
        self.label_destination_dir.pack(side=Tkinter.TOP)

        self.progress = ttk.Progressbar(frame, orient="horizontal",
                                        length=300, mode="determinate")
        self.progress.pack(side=Tkinter.TOP)

        self.label_info = Tkinter.Label(frame, textvariable=None)
        self.label_info.pack(side=Tkinter.TOP)

        self.button_quit = Tkinter.Button(frame, text="Quit", fg="red",
                command=frame.quit)
        self.button_quit.pack(side=Tkinter.LEFT)

        self.button_process = Tkinter.Button(frame, text="GO !!",
                command=self.say_hi)
        self.button_process.pack(side=Tkinter.RIGHT)

        self.root = master

    def asksrcdirectory(self):
        """ Display a 'FileDialog' to choose the source directory. """

        self.source_dir = tkFileDialog.askdirectory(**self.dir_opt)
        self.source_dirvar.set("You choose %s" % self.source_dir)

    def askdstdirectory(self):
        """ Display a 'FileDialog' to chosse the destination directory. """

        self.destination_dir = tkFileDialog.askdirectory(**self.dir_opt)
        self.destination_dirvar.set("You choose %s" % self.destination_dir)

    def say_hi(self):
        """ Create the images required by Piwigo and display the progression. 
        """

        my_imageresizer = imageresizer.ImageResizer(
                self.source_dir, self.destination_dir)
        nb_of_steps = my_imageresizer.check()
        self.progress["maximum"] = nb_of_steps
        self.progress["value"] = 0

        def update_progress(current_step, image_file = None):
            """ Display the progression of the process. """
            self.progress["value"] = current_step
            self.root.update()
        my_imageresizer.subscribe(update_progress)
        my_imageresizer.process()
