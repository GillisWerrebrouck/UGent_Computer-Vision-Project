from datetime import datetime
from bson.objectid import ObjectId

from data.connect import connect_mongodb_database
from data.serializer import deserialize_keypoints, deserialize_histograms, pickle_deserialize
from core.logger import get_root_logger

logger = get_root_logger()
db_connection = connect_mongodb_database(
    'localhost', 27017, 'computervision', 'devuser', 'devpwd')

if (db_connection == None):
    logger.error('Could not obtain a connection to the database, please check if the MongoDB Docker container is '
                 'running.')
    exit(-1)


def create_image(image):
    """
    Insert a new image in the database. If you have an image with multiple paintings,
    add one image to the database per painting.

    Parameters
    ----------
    - image -- The image to create, it can have the following keys:
      - filename -- The filename of the image saving info about.
      - corners -- The (uniform!) corners of a painting in the image.
      - room -- The room this painting is located in.
      - histograms -- Object with serialized keys 'full_histogram' and 'block_histogram'. (optional)
      - good_features -- The serialized good features of the image. (optional)
      - keypoints -- The serialized ORB keypoints and descriptors. (optional)

    Returns
    -------
    Nothing
    """

    image['createdAt'] = datetime.now()

    logger.info('Saving image info for file {}'.format(image['filename']))

    # Save the image to the database
    db_connection['images'].insert(image)


def get_all_images(projection = None):
    """
    Get all images in the database.
    Please use the project parameter for rapid image fetching and deserialization. For example,
    it's not necessary to fetch the ORB keypoints when you only need the histograms.
    So be smart!

    Parameters
    ----------
    - projection -- Optional selection of image fields to fetch.

    Returns
    -------
    Nothing
    """
    logger.info('Fetching all images')
    images = db_connection['images'].find({}, projection)
    logger.info('Fetched {} images'.format(images.count()))
    return __deserialize_images(images)


def get_image_by_id(id):
    """
    Parameters
    ----------
    - id -- The id of the image to get.

    Returns
    -------
    The image.
    """

    return __deserialize_features(db_connection['images'].find_one({'_id': ObjectId(id)}))


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

    result = db_connection['images'].update_many(
        {'filename': filename}, updates)

    logger.info('{} image(s) updated'.format(result.modified_count))


def update_by_id(id, updates):
    """
    Parameters
    ----------
    - id -- The id of the painting to update.
    - updates -- The MongoDB update statements (e.g. { $set: ... }).

    Returns
    -------
    Nothing
    """
    logger.info('Updating image(s) with id {}'.format(id))

    result = db_connection['images'].update_one({'_id': ObjectId(id)}, updates)

    logger.info('{} image(s) updated'.format(result.modified_count))


def get_paintings_for_image(filename, projection=None):
    """
    Parameters
    ----------
    - filename -- The filename of the paintings to update.
    - projection -- Fields to fetch.

    Returns
    -------
    - paintings -- The paintings of the image (being 4 corners)
    """
    logger.info('Getting paintings for image with filename {}'.format(filename))
    result = db_connection['images'].find({'filename': filename}, projection)
    logger.info('{} painting(s) found'.format(result.count()))

    # deserialize the features if present
    return __deserialize_images(result)


def __deserialize_images(images):
    """
    Deserialize a cursor of images.

    Parameters
    ----------
    - images -- Images to deserialize. (Cursor from PyMongo)

    Returns
    -------
    The deserialized images.
    """
    if images is None:
        raise Exception('No images given to deserialize!')

    logger.info('Deserializing {} images'.format(images.count()))
    deserialized = []

    for image in images:
        deserialized.append(__deserialize_features(image))

    logger.info('Done deserializing')
    return deserialized


def __deserialize_features(image):
    """
    Deserialize the features of the given image.

    Parameters
    ----------
    - image -- Image to deserialize features of.

    Returns
    -------
    The image with deserialized features.
    """
    if image is None:
        return image

    if 'histograms' in image:
        if 'full_histogram' in image['histograms']:
            image['histograms']['full_histogram'] = pickle_deserialize(
                image.get('histograms')['full_histogram'])

        if 'block_histogram' in image['histograms']:
            image['histograms']['block_histogram'] = pickle_deserialize(
                image.get('histograms')['block_histogram'])

    if 'keypoints' in image:
        image['keypoints'] = deserialize_keypoints(image.get('keypoints'))

    if 'sobel' in image:
        image['sobel'] = pickle_deserialize(image.get('sobel'))

    if 'good_features' in image:
        image['good_features'] = pickle_deserialize(image.get('good_features'))

    return image
