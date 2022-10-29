import os
from TypingHelper import *

def get_untitled_filename(name, ext, sep) -> FilePath:
    # list of all filenames with specified extension in the current directory
    ext_names = []
    for item in os.listdir():
        items = item.split(".")
        if len(items) > 1 and items[1] == ext:
            ext_names.append(items[0])

    # if the name already exists, append separator and number
    fname = name
    cnt = 1
    while fname in ext_names:
        fname = name + sep + str(cnt)
        cnt += 1

    # add path and extension, return
    fname = os.getcwd() + os.sep + fname + "." + ext
    return fname
