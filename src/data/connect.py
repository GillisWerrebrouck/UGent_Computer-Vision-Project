from pymongo import MongoClient

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
    url = 'mongodb://{}:{}@{}:{}/{}?authSource=admin&authMechanism=SCRAM-SHA-1'.format(username, password, host, port, database)
    print('=> Connected to MongoDB on {}:{}/{}'.format(host, port, database))
    mongoClient = MongoClient(url)
    return mongoClient[database]
