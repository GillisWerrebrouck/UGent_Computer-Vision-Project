import os, errno
from datetime import datetime

def createFolders(path):
    """
    Creates all folders in the given path if they don't exist yet.

    Parameters
    ----------
    - path -- The folder path to create.
    """
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def createFile(filename):
    """
    Creates a file with the name and concatenates the current datetime to it.

    Parameters
    ----------
    - filename -- The filename for the file to create.

    Returns: The filename of the created file.
    """
    createFolders(filename)

    now = datetime.now()
    filename += '_' + now.strftime("%m-%d-%Y_%H-%M-%S") + '.txt'
    file = open(filename, 'x')
    file.close()

    return filename


def appendFile(filename, line):
    """
    Append text to an existing file.

    Parameters
    ----------
    - filename -- The filename of the file to append to.
    - line -- The text to append to the file.
    """
    file = open(filename, 'a')
    file.write(line)
    file.close()
