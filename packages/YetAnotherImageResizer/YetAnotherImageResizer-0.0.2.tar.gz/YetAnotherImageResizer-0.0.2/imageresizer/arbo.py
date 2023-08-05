""" Module arbo contains the list of function to manage file tree. """
import os

def is_image(filename):
    """ Returns true if filename is a JPG file. """

    return filename[-3:].upper() in ("JPG")

def browse(source_dir, destination_dir):
    """ Enumerates all the tuples (d, f) for all the JPG file 'f' contained in
    source_dir where 'd' in the destination directory. """

    dirnames = list_dir(source_dir)
    for dirname in dirnames:
        current_source_dir = os.path.join(
                    source_dir,
                    dirname)
        current_destination_dir = os.path.join(
                    destination_dir,
                    dirname)
        for filename in (x for x in os.listdir(current_source_dir) \
                    if is_image(x)):
            yield (
                    os.path.join(current_source_dir, filename),
                    current_destination_dir)

def list_dir(dirname):

    """
    list_dir(dirname) returns the list of the sub-directories of dirname which
    contain JPG files.

    For example:

    /tmp/mydir/
    |-- a
    |   |-- b
    |   |   |-- b.jpg
    |   |   `-- c
    |   `-- d
    `-- a.jpg

    list_dir('/tmp/mydir')
    >>> ["", "a/b"]

    """

    dirname = os.path.normpath(dirname)
    my_list_dir = []
    for root, _, filenames in os.walk(dirname):
        image_found = False
        for filename in filenames:
            if (is_image(filename)):
                image_found = True
                break
        if image_found:
            # we extract the relative path
            my_list_dir.append(os.path.join(root[len(dirname) + 1:]))

    return my_list_dir
