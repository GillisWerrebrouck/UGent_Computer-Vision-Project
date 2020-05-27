import os
import errno
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


def create_folders(path):
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


def create_file(filename):
    """
    Creates a file with the name and concatenates the current datetime to it.

    Parameters
    ----------
    - filename -- The filename for the file to create.

    Returns
    -------
    The filename of the created file.
    """
    create_folders(filename)

    now = datetime.now()
    filename += '_' + now.strftime("%m-%d-%Y_%H-%M-%S") + '.txt'
    file = open(filename, 'x')
    file.close()

    return filename


def append_file(filename, line):
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


def save_plot(data, title, filename, style='seaborn-muted'):
    """
    Saves the plot as png.

    Parameters
    ----------
    - data -- The data (dist) to plot.
    - title -- The title for the plot.
    - filename -- The filename for the png.
    - style (optional) -- The style to aply to the plot.
    """
    plt.style.use(style)
    pd.DataFrame(data).plot(kind='bar', figsize=(18,6))
    # plt.title(title, fontsize=20)
    plt.legend(prop={'size': 18})
    plt.xticks(rotation=45, fontsize=18)
    plt.yticks(fontsize=18)
    plt.tight_layout()
    plt.savefig(filename)
