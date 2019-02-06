## magicwand
A Python+OpenCV implementation similar to Adobe Photoshop's magic wand selection tool.

Displays an image with a tolerance trackbar. A user can click anywhere on the image to select a region with similar colors, where the range of allowable deviation from a color is given by the trackbar value.

## usage

```python
import cv2
from magicwand import SelectionWindow
image = cv2.imread('lane.jpg', 0)
window = SelectionWindow('Selection Window', image)
window.show()
```

## files

```python
example.py     An example script showing usage of the module magicwand.py
lane.jpg       An example image for the example script
LICENSE.txt    MIT license
magicwand.py   Main module containing the SelectionWindow class
```

## methods

There are some internal ("private") methods to run the selection task and modify the displayed image, and there are some public methods implemented in `magicwand.py` which can help get some information about the accepted selection:  

```python
mini, maxi = getMinMax()          # returns the min and max color inside the selection
mean, stddev = getMeanStdDev()  # returns the mean and standard deviation of color inside the selection
```

Both functions return two 3-vector numpy arrays if the image is 3-channel, otherwise they return two single values.

## future

In the future, support will be added to add to the current selection, and maybe subtract as well. Allowing the change of colorspaces may be helpful, but will only make sense if each channel will have their own sliders; having a range of hue values the the same range of saturation values doesn't really make sense otherwise. I may build out the `SelectionWindow` class to a more general `ImageWindow` class to make it easier for people to add trackbars and mouseclick events and listen to them.
