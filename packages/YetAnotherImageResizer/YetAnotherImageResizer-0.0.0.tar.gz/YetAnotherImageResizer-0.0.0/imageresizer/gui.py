from Tkinter import *
import tkFileDialog
import ttk
import logging.config
import imageresizer
import os

class ImageResizerApp:

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

        self.source_dirvar = StringVar()
        self.source_dirvar.set('...')

        self.destination_dirvar = StringVar()
        self.destination_dirvar.set('...')

        frame = Frame(master)
        frame.pack()

        self.choose_source_dir = Button(frame, text='Please choose source directory',
                                        command=self.asksrcdirectory)
        self.choose_source_dir.pack(side=TOP)

        self.label_source_dir = Label(frame, textvariable=self.source_dirvar)
        self.label_source_dir.pack(side=TOP)

        self.choose_destination_dir = Button(frame, text='Please choose destination directory',
                                        command=self.askdstdirectory)
        self.choose_destination_dir.pack(side=TOP)

        self.label_destination_dir = Label(frame, textvariable=self.destination_dirvar)
        self.label_destination_dir.pack(side=TOP)

        self.progress = ttk.Progressbar(frame, orient="horizontal",
                                        length=300, mode="determinate")
        self.progress.pack(side=TOP)

        self.label_info = Label(frame, textvariable=None)
        self.label_info.pack(side=TOP)

        self.button_quit = Button(frame, text="Quit", fg="red", command=frame.quit)
        self.button_quit.pack(side=LEFT)

        self.button_process = Button(frame, text="GO !!", command=self.say_hi)
        self.button_process.pack(side=RIGHT)

        self.root = master

    def asksrcdirectory(self):
        self.source_dir = tkFileDialog.askdirectory(**self.dir_opt)
        self.source_dirvar.set("You choose %s" % self.source_dir)

    def askdstdirectory(self):
        self.destination_dir = tkFileDialog.askdirectory(**self.dir_opt)
        self.destination_dirvar.set("You choose %s" % self.destination_dir)

    def say_hi(self):
        pi = imageresizer.ImageResizer(self.source_dir, self.destination_dir)
        nb = pi.check()
        self.progress["maximum"] = nb
        self.progress["value"] = 0

        def f(x,y = None):
            self.progress["value"] = x
            self.root.update()
        pi.subscribe(f)
        pi.process()
