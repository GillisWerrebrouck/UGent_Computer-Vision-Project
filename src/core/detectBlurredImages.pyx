import cv2

cpdef is_sharp_image(img, threshold):
    """
    Determine if a given grayscale image is sharp.

    Parameters
    ----------
    - img -- grayscale image to be examined
    - threshold -- Lower threshHold equals more unsharp images

    Returns
    -------
    Bool indicating if the image is sharp enough.
    """

    cdef int blur_index = cv2.Laplacian(img, cv2.CV_64F).var()
    return blur_index > threshold
