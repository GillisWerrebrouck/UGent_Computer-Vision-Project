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
  - filename -- The filename of the image saving info about
  - corners -- The corners of a painting in the image

  Returns
  -------
  Nothing
  """

  image = {
    'filename': filename,
    'corners': corners,
    'createdAt': datetime.now()
  }

  logger.info('Saving image info for file {} with corners {}'.format(filename, corners))

  res = db_connection['images'].insert(image)
  print(res)

