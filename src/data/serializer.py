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


def serialize_histograms(full_histogram, block_histogram):
  """
  Serialize the given numpy arrays.

  Parameters
  ----------
  - full_histogram -- Histogram of the full image.
  - block_histogram -- Histogram of blocked image.

  Returns
  -------
  Our better pickled (= serialized) version of the given histograms.
  """
  serialized_full = pickle.dumps(full_histogram)
  serialized_block = pickle.dumps(block_histogram)

  return {
    'full_histogram': serialized_full,
    'block_histogram': serialized_block
  }


def deserialize_histograms(full_histogram, block_histogram):
  """
  Deserialize the given numpy arrays.

  Parameters
  ----------
  - full_histogram -- Histogram of the full image to deserialize.
  - block_histogram -- Histogram of blocked image to deserialize.

  Returns
  -------
  The deserialized versions of the given histograms.
  """
  deserialized_full = pickle.loads(full_histogram)
  deserialized_block = pickle.loads(block_histogram)

  return {
    'full_histogram': deserialized_full,
    'block_histogram': deserialized_block
  }
