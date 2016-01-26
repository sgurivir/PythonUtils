
import os, glob

scanned_files =[]
def scandirs(path, extension):
    for currentFile in glob.glob( os.path.join(path, '*') ):
        if not os.path.isdir(currentFile):
            if currentFile.endswith(extension):
            	scanned_files.append(currentFile)
        else:
	    scandirs(currentFile, extension)

scandirs("/tmp/", ".config")
print scanned_files
