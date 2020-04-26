import cv2
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


def deserialize_keypoints(keypoint):
  """
  OpenCV sucks in defining good serializable classes, so we again (pun inteded)
  need to do things ourselves. This function deserializes the keypoints and descriptors
  as saved in MongoDB.

  Parameters
  ----------
  - keypoint -- The ORB keypoint to deserialize.

  Returns
  -------
  Our better pickled (= serialized) version of the OpenCV keypoints
  and descriptors.
  """
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

  return (cvKeypoint, descriptor)
