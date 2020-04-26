import cv2
import pickle
import numpy as np

def serialize_keypoints(keypoints, descriptors):
  """
  OpenCV sucks in defining good serializable classes, so we again (pun inteded)
  need to do things ourselves. This function serializes the given keypoints
  and descriptors in one possible way. It creates an object that can be
  saved in MongoDB.

  Parameters
  ----------
  - keypoints -- The ORB keypoints to serialize.
  - descriptors -- The ORB descriptors to serialize.

  Returns
  -------
  Our better pickled (= serialized) version of the OpenCV keypoints
  and descriptors.
  """
  keypointObjects = []

  for i in range(0, len(keypoints)):
    keypoint = keypoints[i]
    descriptor = descriptors[i]

    keypointObjects.append({
      'point': keypoint.pt,
      'size': keypoint.size,
      'angle': keypoint.angle,
      'response': keypoint.response,
      'octave': keypoint.octave,
      'class_id': keypoint.class_id,
      'descriptor': descriptor.tolist()
    })

  return keypointObjects


def deserialize_keypoints(input_keypoints):
  """
  OpenCV sucks in defining good serializable classes, so we again (pun intended)
  need to do things ourselves. This function deserializes the keypoints and descriptors
  as saved in MongoDB.

  Parameters
  ----------
  - input_keypoints -- The ORB keypoints to deserialize.

  Returns
  -------
  The deserialized keypoints.
  """
  keypoints = []
  descriptors = []

  for keypoint in input_keypoints:
    cvKeypoint = cv2.KeyPoint(
      x=keypoint.get('point')[0],
      y=keypoint.get('point')[1],
      _size=keypoint.get('size'),
      _angle=keypoint.get('angle'),
      _response=keypoint.get('response'),
      _octave=keypoint.get('octave'),
      _class_id=keypoint.get('class_id')
    )
    descriptor = np.array(keypoint.get('descriptor'))
    keypoints.append(cvKeypoint)
    descriptors.append(descriptor)

  return {
    'keypoints': keypoints,
    'descriptors': descriptors,
  }


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
