from datetime import datetime

from data.connect import connect_mongodb_database
from core.logger import get_root_logger

logger = get_root_logger()
db_connection = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')

if (db_connection == None):
  logger.error('Could not obtain a connection to the database, please check if the MongoDB Docker container is '
                'running.')
  exit(-1)

def create_image(filename, corners):
  """
  Insert a new image in the database. If you have an image with multiple paintings,
  add one image to the database per painting.

  Parameters
  ----------
  - filename -- The filename of the image saving info about.
  - corners -- The (uniform!) corners of a painting in the image.
  - width -- The width of the image.
  - height -- The height of the image.

  Returns
  -------
  Nothing
  """

  # sort the corners on y-coordinate, then on x: order will be TL, TR, BL, BR
  # then map the values to a uniform percentage of the width or height
  # this way, the image can be of any size
  corners = sorted(corners, key = lambda c: (c[1], c[0]))

  image = {
    'filename': filename,
    'corners': corners,
    'createdAt': datetime.now()
  }

  logger.info('Saving image info for file {} with corners {}'.format(filename, corners))

  # Save the image to the database
  db_connection['images'].insert(image)

