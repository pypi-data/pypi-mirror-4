import os

def list_dir(dirname):
    l = []
    for root, dirnames, filenames in os.walk(dirname):
        ok = False
        for filename in filenames:
            if (filename[-3:] == "jpg" or filename[-3:] == "JPG"):
                ok = True
                break
        if ok:
            l.append(os.path.join(root[len(dirname) + 1:]))
    return l
