import cv2
import sys
import PySimpleGUI as sg


def is_sharp_image(img, threshHold=100):
    """
    Determin is a given grayscale image is sharp
    Parameters
    ----------
    - img -- grayscale image to be examined
    - threshHold -- (optional) default is 100. Lower threshHold equals more unsharp images
    Returns: bool indicating if the image is sharp enough
    """

    blurIndex = cv2.Laplacian(img, cv2.CV_64F).var()
    if (blurIndex > threshHold):
        return True
    return False
