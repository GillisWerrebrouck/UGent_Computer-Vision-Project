# Group 10

Welcome on the repository of group 10's assignment for the course Computer Vision (Ghent University). In the sections below you can find instructions on how to setup and run the different assignments in this project.

## Paper
The paper can be found in the directory `paper`. A built version can be found in `main.pdf`.

## Setup

#### Prerequisites

This tutorial assumes you have the following dependencies already installed on your pc.
- Python3
- OpenCV
- Numpy

First, install all required Python-packages:

``bash
pip3 install -r requirements.txt
``

Thereafter, start MongoDB. This command will automatically start a Node container to populate the database. Please make sure this container is shut down before you start any Python scripts after task 1.

``bash
docker-compose up --force-recreate
``

If you want to check if the Node container is done with seeding, use the following command. If this commands exits, the seeding is done.

``bash
docker logs -f seed
``

Finally, run the project:

``bash
python src/index.py
``

## Unsupervised painting detection tool

For the unsupervised painting detection, a series of actions are executed. The way this works is as follow. All the contours are being detected by a naive method; however, these contours are not being shown yet. A graphical user interface has been made to make the unsupervised image detection easy and user friendly by providing a variaty of actions. The available actions are the following:

1. Add
2. Remove
3. Draw
4. Drag
5. Convert
6. Clear canvas
7. Save to database
8. Next image

### Add action
The `Add` action allows the user to click onto the image. The idea is that the user clicks on a painting to be `detect`. For this action, the contours that were found at the beginning are being used. When clicking on a painting in an image, the code checks if that click event has been triggered in the bounding box of a detected painting, if so then a rectangle is being drawn on the image. All contours in which the user clicked will be made visible.

### Remove action
The `Remove` action allows the user to click into visible contours to remove them. This is a necessary action because the algorithm sometimes detects more contours than it should, so these can be removed.

### Draw action
The `Draw` action has been provided in case the algorithm can't recognize a painting. The user can drag a new contour on the image in case a painting hasn't been detected by the algorithm.

### Drag action
The `Drag` action makes it possible to drag the individual corners. This is the most useful part of the unsupervised painting detection because the user can adjust individual corners if necessary. The contours need to be converted before the `Drag` action can work. The corners will have little squares on them once the contours are converted.

### Convert action
The `Convert` action will convert the contours from rectangles into draggable quadrilaterals. This action needs to be executed to be able to drag individual corners.

### Clear canvas action
The `Clear canvas` action will remove all the visible contours. This is perfect to reset the image to the original state.

### Save to database action
The `Save to database` action will save all the quadrilaterals that are visible to the database. This action will also display the next image.

### Next image action
The `Next image` action will display the next image on which all above actions can be performed.
