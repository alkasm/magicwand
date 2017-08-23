## magicwand
A Python+OpenCV implementation similar to Adobe Photoshop's magic wand selection tool.

Displays an image with a tolerance trackbar. A user can click anywhere on the image to select a region with similar colors, where the range of allowable deviation from a color is given by the trackbar value.

## usage

    import cv2
    from magicwand import SelectionWindow
    image = cv2.imread('lane.jpg', 0)
    window = SelectionWindow('Selection Window', image)
    window.show()

## files

    example.py     An example script showing usage of the module magicwand.py
    lane.jpg       An example image for the example script
    LICENSE.txt    MIT license
    magicwand.py   Main module containing the SelectionWindow class
