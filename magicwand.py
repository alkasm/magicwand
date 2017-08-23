import cv2
import numpy as np


class SelectionWindow:

    def __init__(self, name, image):
        # general params
        self.name = name
        self.image = image          # displayed image; modify this
        self._image = image.copy()  # input image; don't modify
        self.h, self.w = image.shape[:2]
        if len(image.shape) == 3:
            self.channels = 3
        else:
            self.channels = 1
        # parameters for floodfill
        self.tolerance = (20,)*3
        self.seed_point = 0, 0
        self.mask = np.ones((self.h, self.w), dtype=np.uint8)
        self.flood_mask = np.zeros((self.h+2, self.w+2), dtype=np.uint8)
        self.connectivity = 4
        self.flags = self.connectivity | 255 << 8   # bit shift
        self.flags |= cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY

    def _onChange(self, pos):
        self.tolerance = (pos,)*3
        self._magicWand()

    def _onClick(self, event, x, y, flags, param):
        if flags & cv2.EVENT_FLAG_LBUTTON:
            self.seed_point = x, y
            self._magicWand()

    def _magicWand(self):
        self.flood_mask[:] = 0
        cv2.floodFill(self._image, self.flood_mask, self.seed_point, 0,
                      self.tolerance, self.tolerance, self.flags)
        self.mask = self.flood_mask[1:self.h+1, 1:self.w+1].copy()
        self._drawSelection()

    def _drawSelection(self):
        # find contours around mask
        self.contours = cv2.findContours(
            self.mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]
        cv2.drawContours(self.image, self.contours, -1,
                         color=(255,)*3, thickness=-1)  # highlight contours
        self.image = cv2.addWeighted(self._image, 0.75,
                                     self.image, 0.25, 0)  # outline contours
        cv2.drawContours(self.image, self.contours, -1,
                         color=(255,)*3, thickness=1)
        cv2.imshow(self.name, self.image)
        self.image = self._image.copy()

    def show(self):
        # create window, event callbacks
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self._onClick)
        cv2.createTrackbar('Tolerance', self.name,
                           self.tolerance[0], 255, self._onChange)

        # display the image and wait for a keypress or trackbar change
        print('Click anywhere to select a region of similar colors.')
        print('Move the slider to include a wider range of colors.')
        print('Press any key to close the window.\n')
        cv2.imshow(self.name, self.image)
        cv2.waitKey()
        cv2.destroyWindow(self.name)

    def getMask(self):
        return self.mask

    def getContours(self):
        return self.contours

    def getMeanStdDev(self):
        mean, stddev = cv2.meanStdDev(self._image, self.mask)
        if self.channels == 1:
            return mean[0, 0], stddev[0, 0]
        return mean[:, 0], stddev[:, 0]

    def getMinMax(self):
        if self.channels == 1:
            return cv2.minMaxLoc(self._image, self.mask)[:2]
        minVal = np.empty(3, dtype=np.uint8)
        maxVal = np.empty(3, dtype=np.uint8)
        for i in range(0, 3):
            minVal[i], maxVal[i] = cv2.minMaxLoc(self._image[:, :, i],
                                                 self.mask)[:2]
        return minVal, maxVal

