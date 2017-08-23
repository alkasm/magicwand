import cv2
from magicwand import SelectionWindow

image = cv2.imread('lane.jpg', 0)
window = SelectionWindow('Selection Window', image)
window.show()
mean, stddev = window.getMeanStdDev()
minc, maxc = window.getMinMax()
print('Mean Color:   ', mean,
      '\nColor StdDev: ', stddev,
      '\nMin Color:    ', minc,
      '\nMax Color:    ', maxc, '\n')
