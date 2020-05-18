import cv2

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

def equalize(image):
    """
    Equalize the given image.

    Parameters
    ----------
    - image -- The image to equalize.

    Returns
    -------
    The equalized image
    """
    # we only need the light (L) value not all colors for equalization
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab[...,0] = clahe.apply(lab[...,0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
