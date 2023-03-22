'''@file transfer_image_SD.py

 @brief Defines the transfer_image_SD task.

 @section description_transfer_image_SD Description
 Defines the transfer_image_SD task that is run after the end of a pass to transfer all the images save on the BBB emmc to the SD card
 - main (transfer_image_SD)

 @section libraries_transfer_image_SD Libraries/Modules
 - python shutil library
 - python os library
 - python sys library


 @section todo_transfer_image_SD TODO
 - None.

 @section author_transfer_image_SD Author(s)
 - Created by Vilius Stonkus on 02/08/2021.
 - Modified by Louis Timperley on 02/08/2021.
'''

import shutil
import os
import sys
sys.path.append('/home/debian')
from shared.config import Config
from shared.logging import create_logger

def check_free_storage(path,config,logger):
    """
        checks there is enough free space (more than 700 MB) on the SD card (and later other external drives) and
        deletes the oldest files first if not enough space

        Parameters:
            config (object): Object containing configuration information
            logger (object): Object containing information on how to write logs
        Returns:
             void
    """
    # check SD free space
    total, used, free = shutil.disk_usage(path)
    deletions = 0
    logger.info(f'free space on SD: {free}Bytes')
    # will remove upto three directories before giving up
    while free < 700000000 & deletions < 3: # 700MB
        # scan SD directory for the last pass' images
        scanpath = path
        files = os.listdir(scanpath)
        dates = []

        if len(files) > 0:
            # loop through files in current directory
            for f in files:

                # identify files with extensions  and assume ones without are folders
                len = f.rfind('.')

                # if folder, append to list of folders
                if len == -1:
                    dates.append(float(f))

            # now delete oldest folder
            foldername = path+ str(min(dates))
            logger.info(f'deleting folder: {foldername}')
            os.rmdir(foldername)
            deletions = deletions + 1
        else:
            logger.info('no more files to remove')
            break

def main():
    """
        Performs the image transfer to SD task

        Parameters:
             void
        Returns:
             void
    """
    config = Config()
    logger = create_logger("SD_Transfer","/media/SD1/logs.log")

    #check SD free space then create new directory on SD card, called the timestamp of the most recent pass
    SDpath = "/media/SD1" # mounting point for SD card
    check_free_storage(SDpath,config, logger)
    newdirectory = config.recentpasstimestamp()

    newdirectorypath = os.path.join(SDpath, newdirectory) # path to new directory on SD card

    os.makedirs(newdirectorypath, exist_ok=True) # create the directory

    logger.info("Target directory on SD card: " + str(newdirectorypath))

    # scan scheduler directory for the last pass' images
    scanpaths = ["/home/debian/Scheduler",
                 "/home/debian/Tasks/basler",
                 "/home/debian/Tasks/tau2"]

    # loop through scanned directories where images should be
    for dir in scanpaths:

        files =  os.listdir(dir)

        # loop through files in current directory
        for f in files:

            #identify file extensions
            len = f.rfind('.')
            extension = f[len:]

            #if tiff, JPEG, JPG then move Image to directory on SD card
            if extension == ".tiff" or extension == ".jpeg" or extension == ".jpg" or extension == ".dat":
                src = dir + "/" + f
                dst = newdirectorypath + "/"+ f
                shutil.copyfile(src,dst)

                logger.info("Saved " + f + " to" + str(dst))

                os.remove(src)

if __name__ == "__main__":
    main()