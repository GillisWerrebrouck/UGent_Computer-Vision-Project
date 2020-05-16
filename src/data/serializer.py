import cv2
import pickle

# TODO: check if everything uses these


def pickle_serialize(obj):
    """
    Serialize the given object.

    Parameters
    ----------
    - obj -- The object to serialize.

    Returns
    -------
    The serialized version of the object.
    """
    if obj is None:
        return obj

    return pickle.dumps(obj)


def pickle_deserialize(obj):
    """
    Deserialize the given object.

    Parameters
    ----------
    - obj -- The object to deserialize.

    Returns
    -------
    The deserialized version of the object.
    """
    if obj is None:
        return obj

    return pickle.loads(obj)

