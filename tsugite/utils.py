import os

def get_untitled_filename(name,ext,sep):
    # list of all filenames with specified extension in the current directory
    extnames = []
    for item in os.listdir():
        items = item.split(".")
        if len(items)>1 and items[1]==ext:
            extnames.append(items[0])
    # if the name already exists, append separator and number
    fname = name
    cnt = 1
    while fname in extnames:
        fname = name+sep+str(cnt)
        cnt+=1
    # add path and extension, return
    fname = os.getcwd()+os.sep+fname+"."+ext
    return fname