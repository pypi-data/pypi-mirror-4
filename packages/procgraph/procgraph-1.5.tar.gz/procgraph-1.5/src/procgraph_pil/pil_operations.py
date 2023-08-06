import numpy as np

from procgraph import simple_block

from .pil_conversions import Image_from_array


@simple_block
def resize(value, width=None, height=None):
    ''' 
        Resizes an image.
        
        You should pass at least one of ``width`` or ``height``.
        
        :param value: The image to resize.
        :type value: image
        
        :param width: Target image width.
        :type width: int,>0
        
        :param height: Target image height.
        :type height: int,>0

        :return: image: The image as a numpy array.
        :rtype: rgb
    '''

    image = Image_from_array(value)

    if width is None and height is None:
        raise ValueError('You should pass at least one of width and height.')

    if width is None and height is not None:
        width = (height * image.size[0]) / image.size[1]
    elif height is None and width is not None:
        height = (width * image.size[1]) / image.size[0]

    # TODO: RGBA?
    image = image.resize((width, height))
    return np.asarray(image.convert("RGB"))


