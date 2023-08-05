#!/usr/bin/env python

"""
=====================================================
|     _ __ ___  __| |_      _____   ___   __| |     |
|    | '__/ _ \/ _` \ \ /\ / / _ \ / _ \ / _` |     |
|    | | |  __/ (_| |\ V  V / (_) | (_) | (_| |     |
|    |_|  \___|\__,_| \_/\_/ \___/ \___/ \__,_|     |
=====================================================

Redwood is a tool to analyze directory trees and flag all files that are
either too new or too old based on specifications. After it's flagged
the files it will then either just stop there, or it will delete the
flagged files depending on user specification.
"""

import sys
import os
import time
import optparse
import csv
import logging
import shutil


def main():
    """ Program main
        Gets options, runs code, logs output
    """
    opts = get_args()

    if opts.clean:  # Essentially just erases the old log
        open(opts.logfile, mode='w').close()

    # Defines logfile, log level, and log format
    logging.basicConfig(
                        filename=opts.logfile,
                        level=logging.DEBUG,
                        format='%(levelname)s\t|\t%(asctime)s\t-\t %(message)s')
    logging.debug(opts)  # For debug purposes, write opts to log
    logging.info('START')
    age, special_directories = declare_special_directories(opts)
    old_dirs                 = dir_scan(opts.directory, opts.empty,
                                age, special_directories, opts.reverse)
    report                   = open(opts.report, mode='w')
    report.write('%s\n' %(opts))
    for item in old_dirs:  # Write each file violation to a report
        report.write(time.ctime() + '    ----    ')  # Include time
        report.write(item + "\n")
    if opts.delete:
        cleanser(old_dirs, opts.force, opts.trash)


def cleanser(old_dirs, force, trash):
    """ Deletes files listed in old_dirs
        If the --force option is not supplied it will ask for confirmation
        before deleting any files.
        If the --force flag is present, it will automatically delete any
        files listed.
    """
    for item in old_dirs:
        if force:  # If --force was supplied, don't ask
            response = True
        elif force is False:  # Otherwise ask
            response = raw_input('Delete %s? (y/N) ' %(item))
            if response.lower() == 'y':
                response = True
            else:
                response = False

        if response is True:
            logging.warning('DELETING %s' %(item))
            if trash is not None:  # Use trash if present
                trash_location = trash + os.path.basename(item)
                os.rename(item, trash_location)
            else:
                remover(item)
            if os.listdir(os.path.dirname(item)) == []: # Delete empty dirs
                logging.warning('EMPTY DIRECTORY - DELETING %s'\
                                 %(os.path.dirname(item)))
                remover(os.path.dirname(item))


def remover(path):
    """ This function will delete any file or folder given"""
    try:
        os.remove(path)  # Delete the file
    except OSError:
        shutil.rmtree(path)  # Delete the tree


def declare_special_directories(opts):
    """ Scans the config files (default .redwoodrc) and puts all directories
        that the program is supposed to ignore in a list.
        This function actually reads the logfile as a .csv
    """
    dir_listing_file = open(opts.optionfile, mode='r')
    dir_listing = csv.reader(dir_listing_file)
    special_directories = []
    for item in dir_listing:
        if item[0][0] != '#':  # Ignore # commented lines
            special_directories.append(item)  # Otherwise add to list
    time = declare_time(special_directories[0])  # Define user time
    special_directories = special_directories[1:len(special_directories)]
    # ^ This line removes the header
    if opts.reverse:
        logging.info('Looking for files newer than %i days' %(time))
    else:
        logging.info('Looking for files older than %i days' %(time))
    logging.info('Ignoring %s' %(special_directories))
    return time, special_directories


def declare_time(head):
    """Determine the maximum/minimum age of the files
       It does this through converting the specified
       age to days.
    """
    types = ['y', 'mon', 'w', 'd', 'h', 'min', 's']
    for item in types:
        if item in head[0]:
            if item == 'y':
                age = float(head[0][0:len(head) - 2]) * 365
            if item == 'mon':
                age = float(head[0][0:len(head) - 4]) * 30
            if item == 'w':
                age = float(head[0][0:len(head) - 2]) * 7
            if item == 'd':
                age = float(head[0][0:len(head) - 2])
            if item == 'h':
                age = float(head[0][0:len(head) - 2]) / 24
            if item == 'min':
                age = (float(head[0][0:len(head) - 4]) / 24) / 60
            if item == 's':
                age = ((float(head[0][0:len(head) - 2]) / 24) / 60) / 60
    return age


def dir_scan(directory, empty, age, special_directories, reverse):
    """ This function runs through the specified directory using os.walk()
        os.walk() generates a tuple that is then sorted
    """
    old_dirs = []
    for item in directory:  # Look through all directories supplied
        logging.info(item)
        directoryscan = os.walk(item)
        for path, dirs, files in directoryscan:
            if empty:  # Whether or not to look for empty directories
                if files == []:
                    old_dirs.append(path)
            for entry in files:  # Just looking at files
                age_tag = False
                full_path = path_checker(path, entry)  # Make sure path is good
                logging.info('Checking %s' %(full_path))
                ignore_flag = ignore_det(special_directories, full_path)
                if ignore_flag:  # If we have to look at the file
                    age_tag = file_scan(full_path, age, reverse)
                elif ignore_flag == False:  # If we ignore the file
                    logging.info('Ignoring %s' %(full_path))
                if age_tag:  # If the file is too old
                    old_dirs.append(full_path)
    return old_dirs


def ignore_det(special_directories, full_path):
    """ Determines if the current directory is to be ignored or not """
    ignore_flag = 1
    for field in special_directories:
        if full_path.startswith(field[0]):
            ignore_flag *= 0
    if ignore_flag == 1:
        return True  # Return True if it is not ignored
    else:
        return False  # Return False if it's ignored


def file_scan(full_path, age, reverse):
    """ Individual file logic for the scan """
    try:
        flag = time_checker(full_path, age, reverse)
        if flag:  # If the file is fine
            return False
        else:
            if reverse:
                logging.info('----%s is new----' %(full_path))
            else:
                logging.info('----%s is old----' %(full_path))
            return True
    except OSError:
        logging.error('Unable to open %s, do you have permission?' %(full_path))
        return False


def time_checker(cfile, age, reverse):
    """ Determines if the file is too old or too new """
    now = time.time()  # Get current time
    timestamp = os.path.getmtime(cfile)  # Get last modified time
    if reverse:
        if (now - timestamp) < (age * 86400):  # Seconds in a day
            return False
        else:
            return True
    else:
        if (now - timestamp) > (age * 86400):
            return False
        else:
            return True


def path_checker(path, entry):
    '''
    All this does is check that the path of the file doesn't have double //
    If the file has this // in the path, it will fix it
    '''
    full_path = path + '/' + entry
    if '//' in full_path:
        full_path = full_path.replace('//', '/')
    return full_path


def get_args():
    """ Acquires command line input from user """
    global opts
    global args
    parser = optparse.OptionParser(usage = './%prog <options>')
    parser.add_option('-c', '--clean', action='store_true',
                        default=False,
                        help='Clean logfile first?')
    parser.add_option('-d', '--directory', action='append',
                        default=None,
                        type='string',
                        help='Target Directory(s). If you wish\
                                to include multiple directories, seperate\
                                them using multiple -d arguments')
    parser.add_option('-e', '--empty', action='store_true',
                        default=False,
                        help='Flag empty directories as well?')
    parser.add_option('--delete', action='store_true',
                        default=False,
                        help='Delete flagged files?')
    parser.add_option('--force', action='store_true',
                        default=False,
                        help='Whether or not to ask for confirmation when\
                                deleting files. If this flag is included,\
                                it will NOT ask for confirmation.')
    parser.add_option('-l', '--logfile', action='store',
                        default='./',
                        type='string', help='Directory for the logfile')
    parser.add_option('-o', '--optionfile', action='store',
                        default='./',
                        type='string', help='Which config file to use')
    parser.add_option('-r', '--report', action='store',
                        default='./',
                        type='string', help='Directory for the report')
    parser.add_option('--reverse', action='store_true',
                        default=False,
                        help='Whether or not to pick files that are newer\
                                or older than the specified time. If this\
                                option is included, any files that are newer\
                                than the time set in .redwoodrc will be flagged\
                                or deleted, depending on other options.')
    parser.add_option('-t', '--trash', action='store',
                        default=None,
                        help='Location for trash. If this flag is present\
                        redwood will move old files to this directory\
                        instead of deleting them.')
    opts, args = parser.parse_args()

    if opts.optionfile[-1] == '/':
        opts.optionfile = path_checker(opts.optionfile, '.redwoodrc')

    if opts.logfile[-4:len(opts.logfile)] != '.txt':
        opts.logfile = path_checker(opts.logfile, 'log.txt')

    if opts.report[-4:len(opts.report)] != '.txt':
        opts.report = path_checker(opts.report, 'report.txt')

    if opts.directory is None:
        logging.critical('ERROR - NO DIRECTORY SPECIFIED')
        sys.exit(0)

    if opts.force is None:
        opts.force = False

    return opts

if __name__ == "__main__":
    sys.exit(main())
