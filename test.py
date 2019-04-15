import os
import fnmatch
import sys

'''
For the given path, get the List of all files in the directory tree 
'''
def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    
    # Iterate over all the entries
    for entry in listOfFile:
        
        # Create full path
        fullPath = os.path.join(dirName, entry)
        
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    
    return allFiles        


def main():
    # print(sys.argv[1:][0])
    folder_name = sys.argv[1:][0]
    pattern = '*_Approved*'
    # dirName = '/home/ubuntu/win-share/bookingdoc/Suchada'
    # dirName = '/home/ubuntu/win-share/bookingdoc/Sasima'
    # dirName = '/home/ubuntu/win-share/bookingdoc/Janpen'
    # dirName = '/home/ubuntu/win-share/bookingdoc/Napapan'
    # dirName = '/home/ubuntu/win-share/bookingdoc/Poramin'
    dirName = '/home/ubuntu/win-share/bookingdoc/{}'.format(folder_name)
    
    # Get the list of all files in directory tree at given path
    listOfFiles = getListOfFiles(dirName)
    
    # Print the files
    # for elem in listOfFiles:
     #   print(elem)
    
    # print ("****************")
        
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(dirName):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames] 
    
    # Print the files    
    for elem in listOfFiles:
        # print('Filename: %-25s %s' % (elem, fnmatch.fnmatch(elem, pattern)))
        if not fnmatch.fnmatch(elem, pattern):
            if not fnmatch.fnmatch(elem, "*.db"):
                # print('%-25s|%s' % (elem, fnmatch.fnmatch(elem, pattern)))
                print("{}".format(elem))


if __name__ == '__main__':
    main()
