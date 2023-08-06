import numpy

from ..core.exceptions import BadInput


# TODO: make naming uniform
def check_2d_array(value, name=None):
    ''' Checks that we have 2D numpy array '''
    if not isinstance(value, numpy.ndarray):
        raise BadInput('Expected 2d array, got %s.' % value.__class__.__name__,
                       None, name)

    if len(value.shape) != 2:
        raise BadInput('Expected 2D array, got %s.' % str(value.shape),
                       None, name)


def assert_rgb_image(image, name=None):
    if not isinstance(image, numpy.ndarray):
        raise BadInput('Expected RGB image for %r, got %s.' %
                       (name, image.__class__.__name__),
                        None, name)

    if image.dtype != 'uint8':
        raise BadInput('Expected RGB image for %r, got an array %s %s.' %
                            (name, str(image.shape), image.dtype), None, name)

    if len(image.shape) != 3 or image.shape[2] != 3:
        raise BadInput('Bad shape for %s, expected RGB, got %s.' %
                        (name, str(image.shape)), None, name)


def assert_gray_image(image, name=None):
    if not isinstance(image, numpy.ndarray):
        raise BadInput('Expected a grayscale image for %r, got %s.' %
                       (name, image.__class__.__name__), None, name)

    if image.dtype != 'uint8':
        raise BadInput('Expected a grayscale image for %r, got an array %s %s.'
                       %
                            (name, str(image.shape), image.dtype),
                             None, name)

    if len(image.shape) != 2:
        raise BadInput('Bad shape for %r, expected grayscale, got %s.' %
                        (name, str(image.shape)), None, name)


def check_rgb_or_grayscale(block, input): #@ReservedAssignment
    ''' Checks that the selected input is either a grayscale or RGB image.
        That is, a numpy array of uint8 either H x W,  H x W x 3,
        or HxWx4. 
        Raises BadInput if it is not. 
    '''
    # TODO: write this better
    image = block.get_input(input)
    if not isinstance(image, numpy.ndarray):
        raise BadInput('Expected RGB or grayscale, this is not even a '
            'numpy array: %s' % image.__class__.__name__, block, input)
    if image.dtype != 'uint8':
        raise BadInput('Expected an image, got an array %s %s.' %
                            (str(image.shape), image.dtype), block, input)
    shape = image.shape
    if len(shape) == 3:
        depth = shape[2]
        if not depth in [3, 4]:
            raise BadInput('Bad shape for image: %s' % str(shape),
                           block, input)
    elif len(shape) == 2:
        pass
    else:
        raise BadInput('Bad shape for image: %s' % str(shape), block, input)


def check_rgb(block, input): #@ReservedAssignment
    ''' Checks that the selected input is either  a RGB image.
        That is, a numpy array of uint8 of shape H x W x 3. 
        Raises BadInput if it is not. 
    '''
    image = block.get_input(input)
    if not isinstance(image, numpy.ndarray):
        raise BadInput('Expected RGB, this is not even a '
            'numpy array: %s' % image.__class__.__name__, block, input)
    if image.dtype != 'uint8':
        raise BadInput('Expected an image, got an array %s %s.' %
                            (str(image.shape), image.dtype), block, input)
    shape = image.shape
    if len(shape) == 3:
        if shape[2] != 3:
            raise BadInput('Bad shape for image: %s' % str(shape),
                           block, input)
    else:
        raise BadInput('Bad shape for image: %s' % str(shape), block, input)
