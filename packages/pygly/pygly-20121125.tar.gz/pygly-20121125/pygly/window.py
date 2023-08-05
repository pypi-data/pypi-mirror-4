"""Window management functions.
"""
import numpy


def create_rectangle( window ):
    """Creates a rectangle object representing the window
    size in pixels.
    The rectangle is in the format of Pyrr.rectangle.

    Returns:
        The size of the window in pixels represented as a
        NumPy array with shape (2,2).
    """
    return numpy.array(
        [
            [ 0, 0 ],
            [ window.width, window.height ]
            ],
        dtype = numpy.int
        )

def aspect_ratio( rect ):
    """Calculates the aspect ratio of the rectangle.

    Aspect ratio is the ratio of width to height
    a value of 2.0 means width is 2*height

    The rectangle is in the format of Pyrr.rectangle.

    Returns:
        The aspect ratio of the rectangle.
    """
    width = float(rect[ 1,0 ])
    height = float(rect[ 1,1 ])
    return width / height

