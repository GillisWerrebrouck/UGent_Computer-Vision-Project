import cv2

cpdef is_sharp_image(img, threshHold):
    """
    Determine if a given grayscale image is sharp
    Parameters
    ----------
    - img -- grayscale image to be examined
    - threshHold -- Lower threshHold equals more unsharp images
    Returns: bool indicating if the image is sharp enough
    """

    cdef int blurIndex = cv2.Laplacian(img, cv2.CV_64F).var()
    return blurIndex > threshHold
