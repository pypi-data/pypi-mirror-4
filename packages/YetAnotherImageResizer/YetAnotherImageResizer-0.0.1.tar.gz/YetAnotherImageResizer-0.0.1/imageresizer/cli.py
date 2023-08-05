""" Module cli contains the CLI version. """
import imageresizer
import sys
import argparse

def parse():
    """ Parses the command line. """

    parser = argparse.ArgumentParser(
            description='Create all the images required by Piwigo')
    parser.add_argument('--cli',
            metavar=('source_dir', 'destination_dir'),
            type=str, nargs=2,
            help='CLI version')
    args = parser.parse_args()
    return args

def display_progress(current_step, image_file, nb_of_steps):
    """ Display the progression of the creation. """

    i = (float(current_step) / nb_of_steps) *100
    sys.stdout.write("\r%d%%\t %s" %(i, image_file))    # or print >> sys.stdout, "\r%d%%" %i,
    sys.stdout.flush()

def process(source_dir, destination_dir):
    """ Creates the images required by Piwigo and display the progression.
    """

    my_imageresizer = imageresizer.ImageResizer(
        source_dir, destination_dir)
    nb_of_steps = my_imageresizer.check()

    if nb_of_steps == 0:
        print "Nothing to do ..."""
        return

    def update_progress(current_step, image_file = None):
            """ Display the progression of the process. """
            display_progress(current_step, image_file, nb_of_steps)
    my_imageresizer.subscribe(update_progress)
    my_imageresizer.process()
