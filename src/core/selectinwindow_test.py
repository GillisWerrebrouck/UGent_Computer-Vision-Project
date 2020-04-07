import cv2
from visualize import resize_image

import sys
# Set recursion limit
sys.setrecursionlimit(10 ** 9)

import selectinwindow

# Define the drag object
rectI = selectinwindow.dragRect

# Initialize the  drag object
wName = "select region"
image = cv2.imread('/Users/jochen/Ugent/Master/Computervisie/Project/images/Computervisie 2020 Project Database/dataset_pictures_msk/zaal_1/IMG_20190323_111717.jpg')
image = resize_image(image, 0.2)
selectinwindow.init(rectI, image, wName, image.shape[0], image.shape[1])

cv2.namedWindow(rectI.wname)
cv2.setMouseCallback(rectI.wname, selectinwindow.dragrect, rectI)

# keep looping until rectangle finalized
while True:
    # display the image
    cv2.imshow(wName, rectI.image)
    key = cv2.waitKey(1) & 0xFF

    # if returnflag is True, break from the loop
    if rectI.returnflag == True:
        break

print("Dragged rectangle coordinates")
print(str(rectI.outRect.x) + ',' + str(rectI.outRect.y) + ',' + \
      str(rectI.outRect.w) + ',' + str(rectI.outRect.h))

# close all open windows
cv2.destroyAllWindows()