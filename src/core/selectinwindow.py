import cv2
import numpy as np


# Based on https://github.com/arccoder/opencvdragrect
# edited to work with quadrilateral instead of rectangles

class Point:
    x = None
    y = None

    def printit(self):
        return str('(' + str(self.x) + ',' + str(self.y) + ')')

class Quadrilateral:
    TLPoint = Point()
    TRPoint = Point()
    BLPoint = Point()
    BRPoint = Point()

class Rect:
    x = None
    y = None
    w = None
    h = None

    def printit(self):
        print(str(self.x) + ',' + str(self.y) + ',' + str(self.w) + ',' + str(self.h))


# endclass

class dragRect:
    # Limits on the canvas
    keepWithin = Rect()
    # To store rectangle
    outQuad = Quadrilateral()
    # Selection marker size
    sBlk = 4

    # Image
    original_image = None
    image = None

    # Window Name
    wname = ""

    # FLAGS
    # Rect already present
    active = True
    # Marker flags by positions
    TL = False
    TR = False
    BL = False
    BR = False
    hold = False
# endclass

def init(dragObj, image, contours, windowName, windowWidth, windowHeight, resize_factor):
    # Window name
    dragObj.wname = windowName

    # Limit the selection box to the canvas
    dragObj.keepWithin.x = 0
    dragObj.keepWithin.y = 0
    dragObj.keepWithin.w = windowWidth
    dragObj.keepWithin.h = windowHeight

    # Set rect to zero width and height
    (x, y, w, h) = contours[0]
    x = round(x / resize_factor)
    y = round(y / resize_factor)
    w = round(w / resize_factor)
    h = round(h / resize_factor)

    dragObj.outQuad.TLPoint.x = x
    dragObj.outQuad.TLPoint.y = y
    dragObj.outQuad.TRPoint.x = x + w
    dragObj.outQuad.TRPoint.y = y
    dragObj.outQuad.BLPoint.x = x
    dragObj.outQuad.BLPoint.y = y + h
    dragObj.outQuad.BRPoint.x = x + w
    dragObj.outQuad.BRPoint.y = y + h

    # Image
    dragObj.original_image = image
    tmp = image.copy()
    pts = [[dragObj.outQuad.TLPoint.x, dragObj.outQuad.TLPoint.y],
           [dragObj.outQuad.TRPoint.x, dragObj.outQuad.TRPoint.y],
           [dragObj.outQuad.BRPoint.x, dragObj.outQuad.BRPoint.y],
           [dragObj.outQuad.BLPoint.x, dragObj.outQuad.BLPoint.y]]
    pts = np.array(pts, np.int32)
    pts = pts.reshape((-1, 1, 2))
    tmp = cv2.polylines(tmp, [pts], True, (0, 255, 0), thickness=2)
    dragObj.image = tmp

# enddef

def dragrect(event, x, y, flags, dragObj):
    if x < dragObj.keepWithin.x:
        x = dragObj.keepWithin.x
    # endif
    if y < dragObj.keepWithin.y:
        y = dragObj.keepWithin.y
    # endif
    if x > (dragObj.keepWithin.x + dragObj.keepWithin.w - 1):
        x = dragObj.keepWithin.x + dragObj.keepWithin.w - 1
    # endif
    if y > (dragObj.keepWithin.y + dragObj.keepWithin.h - 1):
        y = dragObj.keepWithin.y + dragObj.keepWithin.h - 1
    # endif

    if event == cv2.EVENT_LBUTTONDOWN:
        mouseDown(x, y, dragObj)
    # endif
    if event == cv2.EVENT_LBUTTONUP:
        mouseUp(x, y, dragObj)
    # endif
    if event == cv2.EVENT_MOUSEMOVE:
        mouseMove(x, y, dragObj)
    # endif

# enddef

def pointInRect(pX, pY, rX, rY, rW, rH):
    if rX <= pX <= (rX + rW) and rY <= pY <= (rY + rH):
        return True
    else:
        return False
    # endelseif

# enddef

def mouseDown(eX, eY, dragObj):
    if dragObj.active:

        if pointInRect(eX, eY, dragObj.outQuad.TLPoint.x - dragObj.sBlk,
                       dragObj.outQuad.TLPoint.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            print(dragObj.TL)
            dragObj.TL = True
            print(dragObj.TL)
            return
        # endif
        if pointInRect(eX, eY, dragObj.outQuad.TRPoint.x - dragObj.sBlk,
                       dragObj.outQuad.TRPoint.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.TR = True
            return
        # endif
        if pointInRect(eX, eY, dragObj.outQuad.BLPoint.x - dragObj.sBlk,
                       dragObj.outQuad.BLPoint.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.BL = True
            return
        # endif
        if pointInRect(eX, eY, dragObj.outQuad.BRPoint.x - dragObj.sBlk,
                       dragObj.outQuad.BRPoint.y - dragObj.sBlk,
                       dragObj.sBlk * 2, dragObj.sBlk * 2):
            dragObj.BR = True
            return
        # endif

    # endelseif

# enddef

def mouseMove(eX, eY, dragObj):
    if dragObj.TL:
        dragObj.outQuad.TLPoint.x = eX
        dragObj.outQuad.TLPoint.y = eY
        clearCanvasNDraw(dragObj)
        return
    # endif
    if dragObj.TR:
        dragObj.outQuad.TRPoint.x = eX
        dragObj.outQuad.TRPoint.y = eY
        clearCanvasNDraw(dragObj)
        return
    # endif
    if dragObj.BL:
        dragObj.outQuad.BLPoint.x = eX
        dragObj.outQuad.BLPoint.y = eY
        clearCanvasNDraw(dragObj)
        return
    # endif
    if dragObj.BR:
        dragObj.outQuad.BRPoint.x = eX
        dragObj.outQuad.BRPoint.y = eY
        clearCanvasNDraw(dragObj)
        return
    # endif

# enddef

def mouseUp(eX, eY, dragObj):
    disableResizeButtons(dragObj)

    clearCanvasNDraw(dragObj)

# enddef

def disableResizeButtons(dragObj):
    dragObj.TL = dragObj.TR = False
    dragObj.BL = dragObj.BR = False
    dragObj.hold = False

# enddef

def  clearCanvasNDraw(dragObj):
    # Draw
    tmp = dragObj.original_image.copy()
    pts = [[dragObj.outQuad.TLPoint.x, dragObj.outQuad.TLPoint.y],
           [dragObj.outQuad.TRPoint.x, dragObj.outQuad.TRPoint.y],
           [dragObj.outQuad.BRPoint.x, dragObj.outQuad.BRPoint.y],
           [dragObj.outQuad.BLPoint.x, dragObj.outQuad.BLPoint.y]]
    pts = np.array(pts, np.int32)
    pts = pts.reshape((-1,1,2))
    tmp	= cv2.polylines(tmp, [pts], True, (0, 255, 0), thickness = 2)

    drawSelectMarkers(tmp, dragObj)
    cv2.imshow(dragObj.wname, tmp)
    cv2.waitKey()

# enddef

def drawSelectMarkers(image, dragObj):
    # Top-Left
    cv2.rectangle(image,
                  (dragObj.outQuad.TLPoint.x - dragObj.sBlk, dragObj.outQuad.TLPoint.y - dragObj.sBlk),
                  (dragObj.outQuad.TLPoint.x + dragObj.sBlk, dragObj.outQuad.TLPoint.y + dragObj.sBlk),
                  (0, 255, 0), 2)
    # Top-Right
    cv2.rectangle(image,
                  (dragObj.outQuad.TRPoint.x - dragObj.sBlk, dragObj.outQuad.TRPoint.y - dragObj.sBlk),
                  (dragObj.outQuad.TRPoint.x + dragObj.sBlk, dragObj.outQuad.TRPoint.y + dragObj.sBlk),
                  (0, 255, 0), 2)
    # Bottom-Left
    cv2.rectangle(image,
                  (dragObj.outQuad.BLPoint.x - dragObj.sBlk, dragObj.outQuad.BLPoint.y - dragObj.sBlk),
                  (dragObj.outQuad.BLPoint.x + dragObj.sBlk, dragObj.outQuad.BLPoint.y + dragObj.sBlk),
                  (0, 255, 0), 2)
    # Bottom-Right
    cv2.rectangle(image,
                  (dragObj.outQuad.BRPoint.x - dragObj.sBlk, dragObj.outQuad.BRPoint.y - dragObj.sBlk),
                  (dragObj.outQuad.BRPoint.x + dragObj.sBlk, dragObj.outQuad.BRPoint.y + dragObj.sBlk),
                  (0, 255, 0), 2)

# enddef