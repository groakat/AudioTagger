    import os

def HyphenReplaceUnder(directory):
    """
    Function to batch replace the hyphen (-) in filenames with an underscore (_).
    
    Directory where files are located must be specified in format 'C:/...Folder name/'
    
    """
    
    TARGET_DIR = directory
    
    for FILE_OLD in os.listdir(TARGET_DIR):

        FILE_NEW = FILE_OLD.replace('-', '_')
        
        print FILE_NEW
        FILE_OLD = TARGET_DIR + FILE_OLD
        FILE_NEW = TARGET_DIR + FILE_NEW
    
        print 'Renaming', FILE_OLD, 'to', FILE_NEW
        os.rename(FILE_OLD, FILE_NEW)

def NumberFilename(directory):
    """
    Function to batch add a number to the front of filenames in a folder.
    
    Directory where files are located must be specified in format 'C:/...Folder name/'
    
    Numbering starts from 1.
    
    """
    
    TARGET_DIR = directory
    files = os.listdir(TARGET_DIR)
    index = 1
    for FILE_OLD in files:
        FILE_NEW = str(index) + FILE_OLD
        FILE_OLD = TARGET_DIR + FILE_OLD
        FILE_NEW = TARGET_DIR + FILE_NEW
        
        print 'Renaming', FILE_OLD, 'to', FILE_NEW
        os.rename(FILE_OLD, FILE_NEW)
        index += 1

def FileRename(directory):
    """
    Function batch renames all files in a folder from format 
    "_SITE-DETECTOR_DATE_HHM000AutomaticallyGeneratedNumber.wav" 
    to 
    "NUMBER_SITE-DETECTOR_DATE_HHMM.wav"
    
    Directory where files are located must be specified in format 'C:/...Folder name/'
    
    """

    TARGET_DIR = directory
    files = os.listdir(TARGET_DIR)
    
    #Split filename list into two lists at index position -10. Removes file extension.
    EndingList = []
    for i in files:
        End = i[-10:-4]
        
        EndingList.append(End)
        
    StartingList = []
    for i in files:
        Start = i[:-10]
        
        StartingList.append(Start)
        
    #Convert EndingList from string to integers
    
    EndingList = [int(i) for i in EndingList]
    
    #Alter value of time numbers.
    EndingAdjust = []
    for i in EndingList:
        if i > 30:
            i = i - 299971
        else:
            i = i - 1
        EndingAdjust.append(i)
        
    # Convert EndingAdjust from integers to string and padding single integers (1-9) witha zero
    EndingAdjust = [str(i).zfill(2) for i in EndingAdjust]
    
    # Join StartingList and EndingAdjust to create new filename list (using list comprehension)
    filenameList = [a + b for a, b in zip(StartingList, EndingAdjust)]
    
    # Rename files with new filenames.
    index = 0
    for FILE_OLD in os.listdir(TARGET_DIR):
            FILE_NEW = filenameList[index]
            FILE_OLD = TARGET_DIR + FILE_OLD
            FILE_NEW = TARGET_DIR + FILE_NEW
            
            os.rename(FILE_OLD, FILE_NEW + '.wav')
            index += 1