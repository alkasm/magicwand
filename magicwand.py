import cv2
import numpy as np
from collections import namedtuple
from itertools import cycle
import uuid  # for unique filenames


Point = namedtuple('Point', 'x, y')


class SelectionWindow:

    _displays = cycle(['selection', 'mask', 'applied mask'])

    def __init__(self, name, image, connectivity=4):

        # general params
        self.name = name
        self._image = image
        self._h, self._w = image.shape[:2]
        if len(image.shape) == 3:
            self._channels = 3
        else:
            self._channels = 1
        self._selection = image.copy()
        self._mask = 255*np.ones((self._h, self._w), dtype=np.uint8)
        self._applied_mask = image.copy()
        self._curr_display = next(self._displays)

        # parameters for floodfill
        self.connectivity = connectivity
        self._tolerance = (20,)*3
        self._seed_point = Point(0, 0)
        self._flood_mask = np.zeros((self._h+2, self._w+2), dtype=np.uint8)

    def _onchange(self, pos):
        self._tolerance = (pos,)*3
        self._magicwand()

    def _onclick(self, event, x, y, flags, param):
        if flags & cv2.EVENT_FLAG_LBUTTON:
            self._seed_point = Point(x, y)
            self._magicwand()

    def _magicwand(self):
        self._flood_mask[:] = 0
        flags = self.connectivity | 255 << 8   # bit shift
        flags |= cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY
        flood_image = self._image.copy()
        cv2.floodFill(flood_image, self._flood_mask, self._seed_point, 0,
                      self._tolerance, self._tolerance, flags)
        self._mask = self._flood_mask[1:-1, 1:-1].copy()
        self._update_window()

    def _drawselection(self):
        # find contours around mask
        self._selection = self._image.copy()
        self._contours = cv2.findContours(self._mask, cv2.RETR_LIST,
                                          cv2.CHAIN_APPROX_SIMPLE)[1]
        cv2.drawContours(self._selection, self._contours, -1,
                         color=(255,)*3, thickness=-1)  # highlight contours
        self._selection = cv2.addWeighted(
            self._image, 0.75, self._selection, 0.25, 0)  # outline contours
        cv2.drawContours(self._selection, self._contours, -1,
                         color=(255,)*3, thickness=1)

    def _flip_displays(self):
        self._curr_display = next(self._displays)
        self._update_window()
        if self.verbose:
            print('Displaying %s' % self._curr_display)

    def _print_stats(self):
        print('Mean Color:  ', self.mean,
              '\nStdDev Color:', self.stddev,
              '\nMin Color:   ', self.min,
              '\nMax Color:   ', self.max,
              '\nSeed Point:  ', self.seedpt)

    def _save(self):
        if self._curr_display == 'selection':
            filename = 'selection_' + uuid.uuid1().hex + '.png'
            cv2.imwrite(filename, self._selection)
        elif self._curr_display == 'mask':
            filename = 'mask_' + uuid.uuid1().hex + '.png'
            cv2.imwrite(filename, self._mask)
        elif self._curr_display == 'applied mask':
            filename = 'applied_mask_' + uuid.uuid1().hex + '.png'
            cv2.imwrite(filename, self._applied_mask)
        if self.verbose:
            print('Saved image as', filename)

    def _close(self):
        if self.verbose:
            print('Closing window')
            print('\n--------------------------------------')
            self._print_stats()
            print('--------------------------------------\n')
        cv2.destroyWindow(self.name)

    def _update_window(self):
        if self._curr_display == 'selection':
            self._drawselection()
            cv2.imshow(self.name, self._selection)
        elif self._curr_display == 'mask':
            cv2.imshow(self.name, self._mask)
        elif self._curr_display == 'applied mask':
            self._applied_mask = cv2.bitwise_and(
                self._image, self._image, mask=self._mask)
            cv2.imshow(self.name, self._applied_mask)

    def show(self, verbose=False):
        # create window, event callbacks
        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self._onclick)
        cv2.createTrackbar('Tolerance', self.name,
                           self._tolerance[0], 255, self._onchange)
        self.verbose = verbose

        if verbose:
            print('Click anywhere to select a region of similar colors.')
            print('Move the slider to include a wider range of colors.\n')
        print(('Press [m] to switch between displaying the selection, '
               'mask, or applied mask'))
        print('Press [p] to print color statistics of current selection')
        print('Press [s] to save the currently displayed image')
        print('Press [q] or [esc] to close the window')
        print('------------------------------------------------------------\n')

        # display the image and wait for a keypress or trackbar change
        cv2.imshow(self.name, self._image)

        while(True):

            k = cv2.waitKey() & 0xFF
            if k == ord('q') or k == 27:  # 27 is [esc]
                self._close()
                break
            elif k == ord('m'):
                self._flip_displays()
            elif k == ord('p'):
                self._print_stats()
            elif k == ord('s'):
                self._save()

    @property
    def mask(self):
        return self._mask

    @property
    def applied_mask(self):
        self._applied_mask = cv2.bitwise_and(
            self._image, self._image, mask=self._mask)
        return self._applied_mask

    @property
    def selection(self):
        self._drawselection()
        return self._selection

    @property
    def contours(self):
        self._drawselection()
        return self._contours

    @property
    def seedpt(self):
        return self._seed_point

    @property
    def mean(self):
        mean = cv2.meanStdDev(self._image, self._mask)[0]
        if self._channels == 1:
            return mean[0, 0]
        return mean[:, 0]

    @property
    def stddev(self):
        stddev = cv2.meanStdDev(self._image, self._mask)[1]
        if self._channels == 1:
            return stddev[0, 0]
        return stddev[:, 0]

    @property
    def min(self):
        if self._channels == 1:
            return cv2.minMaxLoc(self._image, self._mask)[0]
        min_val = [cv2.minMaxLoc(self._image[:, :, i], self._mask)[0]
                   for i in range(3)]
        return np.array(min_val, dtype=np.uint8)

    @property
    def max(self):
        if self._channels == 1:
            return cv2.minMaxLoc(self._image, self._mask)[1]
        max_val = [cv2.minMaxLoc(self._image[:, :, i], self._mask)[1]
                   for i in range(3)]
        return np.array(max_val, dtype=np.uint8)
