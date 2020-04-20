# Report group 10
This document is group 10's report for the project of Computer Vision

# Assignment 1
## General
for the execution of unsupervised painting detection, a series of actions are executed. The way this works is as following. When the image gets loaded in, all the contours are being tracked. however, these contours are not being shown yet. Next we made a graphical user interface, where it's possible to chose which action you want to execute. Each of these actions work in it's own way. The actions are the following: 
1. Add
2. Remove
3. Draw
4. Drag
5. Convert
6. Clear canvas
7. Save to database
8. Next image
   
### Add action
The `Add` action allows the user to click onto the image. The idea is that the user actually click in the painting he wants to "detect". For this action, the contours that were found at the beginning are being used. These contours are used to get an approach but creating rectangles out of them. The code will use the coordinates of the point in the contour and use the width en height of the contour to check if the click was inside of it. Like this, all contours that are clicked inside will be made visible.

### Remove action
The `Remove` action allows the user to click into visible contours and remove these again. This is needed because the algorith sometimes finds more contours than it should, so these can be removed.

### Draw action
The `Draw` action is here in case the program can not recognize a painting. It needs to be possible to draw a contour by ourselves. This works by selecting the top left and the bottom right corners.

### Drag action
The `Drag` action makes it possible to drag the individual corners. This makes it possible to perfectly position the individual corners. The contours need to be converted before the `Drag` action can work.

### Convert action
The `Convert` action will convert the contours from rectangles into draggable quadrilaterals. This action needs to be done before the dragging can begin.

### Clear canvas action
The `Clear canvas` action will remove all the visible contours. This is perfect to reset the image to the original state.

### Save to database action
The `Save to database` action will save all the quadrilaterals that are visible to the datebase. This action will also go to the next image.

### Next image action
The `Next image` action will make the program go to the next image.

## Contour detection
The contour detection is the actual logic part. This is the part that decides what contours are in the image and it works as described below.

The first step of the process is to remove the details. This is to prevent finding contours inside of the painting. This is done by resizing the painting down and back up with a factor 5.

The second afterwards, the painting is grayscaled. This is done to make it easier to differentiate certain parts. This grayscaled image is then dilated and eroded to remove noise at the borders. The last step of removing noise is to do a medianblur over it. The idea of these steps is to make it easier to detect de borders and remove noise in the background.

The next step is to detect edges with Canny. The result of the Canny function will then be dilated once again and last but not least, the contours are found.

A small detail to prevent unlogical solutions, any contour where the width or height is 10 times bigger than the other dimension will be removed.