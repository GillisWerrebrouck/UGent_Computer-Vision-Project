from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from core.logger import get_root_logger

def connect_mongodb_database(host, port, database, username, password):
  """
  Connect to the given MongoDB-database.

  Parameters
  ----------
  - host -- The host where MongoDB is running.
  - port -- The port on which MongoDB listens.
  - database -- The database to connect to.

  Returns: a reference to the requested database.
  """
<<<<<<< HEAD
  url = 'mongodb://{}:{}@{}:{}/{}?authSource=admin&authMechanism=SCRAM-SHA-1'.format(username, password, host, port, database)
  print('=> Connected to MongoDB on {}:{}/{}'.format(host, port, database))
  mongoClient = MongoClient(url)
  return mongoClient[database]
=======
  logger = get_root_logger()
  try:
    logger.info('Connecting to MongoDB...')
    # Connect to MongoDB (max. wait 5s for connection to be established)
    url = 'mongodb://{}:{}@{}:{}/{}?authSource=admin&authMechanism=SCRAM-SHA-1'.format(username, password, host, port, database)
    mongoClient = MongoClient(url, serverSelectionTimeoutMS=5000)

    # request a roundtrip to server because the connection is lazy
    mongoClient.server_info()
    logger.info('Connected to MongoDB on {}:{}/{}'.format(host, port, database))

    # Get the requested database from the url
    return mongoClient.get_database()
  except ServerSelectionTimeoutError as err:
    logger.critical('PyMongo could not connect to the database with url {}'.format(url))



>>>>>>> 157a82723b85c883df8b19a88dc84238bf7a8e0d
