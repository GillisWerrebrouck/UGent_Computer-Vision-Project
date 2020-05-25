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

    Returns
    -------
    A reference to the requested database.
    """
    logger = get_root_logger()
    try:
        logger.info('Connecting to MongoDB...')
        # Connect to MongoDB (max. wait 5s for connection to be established)
        url = f'mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin&authMechanism=SCRAM-SHA-1'
        mongo_client = MongoClient(url, serverSelectionTimeoutMS=5000)

        # request a roundtrip to server because the connection is lazy
        mongo_client.server_info()
        logger.info('Connected to MongoDB on {}:{}/{}'.format(host, port, database))

        # Get the requested database from the url
        return mongo_client.get_database()
    except ServerSelectionTimeoutError as err:
        logger.critical('PyMongo could not connect to the database with url {}'.format(url))
