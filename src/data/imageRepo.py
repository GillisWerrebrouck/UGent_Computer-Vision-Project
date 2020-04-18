from datetime import datetime

from data.connect import connect_mongodb_database
from core.logger import get_root_logger

logger = get_root_logger()
db_connection = connect_mongodb_database('localhost', 27017, 'computervision', 'devuser', 'devpwd')

if (db_connection == None):
  logger.error('Could not obtain a connection to the database, please check if the MongoDB Docker container is '
                'running.')
  exit(-1)

def create_image(filename, corners, room):
  """
  Insert a new image in the database. If you have an image with multiple paintings,
  add one image to the database per painting.

  Parameters
  ----------
  - filename -- The filename of the image saving info about.
  - corners -- The (uniform!) corners of a painting in the image.
  - room -- The room this painting is located in.

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
    'room': room,
    'createdAt': datetime.now()
  }

  logger.info('Saving image info for file {} in room {} with corners {}'.format(filename, room, corners))

  # Save the image to the database
  db_connection['images'].insert(image)


def update_paintings_of_file(filename, updates):
  """
  Parameters
  ----------
  - filename -- The filename of the paintings to update.
  - updates -- The MongoDB update statements (e.g. { $set: ... }).

  Returns
  -------
  Nothing
  """
  logger.info('Updating image(s) with filename {}'.format(filename))

  result = db_connection['images'].update_many({ 'filename': filename }, updates)

  logger.info('{} image(s) updated'.format(result.modified_count))
