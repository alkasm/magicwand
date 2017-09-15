import cv2
from magicwand import SelectionWindow

image = cv2.imread('lane.jpg')
selection = SelectionWindow('Selection Window', image, connectivity=8)
selection.show(verbose=True)
