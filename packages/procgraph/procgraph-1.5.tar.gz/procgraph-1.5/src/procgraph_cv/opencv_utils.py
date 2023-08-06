import numpy

from procgraph import  simple_block
from procgraph.block_utils  import  check_2d_array

from . import cv


def numpy_to_cv(numpy_array):
    ''' Converts a HxW or HxWx3 numpy array to OpenCV 'image' '''
    dtype2depth = {
        'uint8': cv.IPL_DEPTH_8U,
        'int8': cv.IPL_DEPTH_8S,
        'uint16': cv.IPL_DEPTH_16U,
        'int16': cv.IPL_DEPTH_16S,
        'int32': cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }

    if len(numpy_array.shape) == 2:
        (height, width) = numpy_array.shape
        nchannels = 1
    elif len(numpy_array.shape) == 3:
        (height, width, nchannels) = numpy_array.shape
    else:
        raise ValueError('Invalid format shape %s' % str(numpy_array.shape))

    im_cv = cv.CreateImage((width, height),
                           dtype2depth[str(numpy_array.dtype)],
                           nchannels)
    cv.SetData(im_cv,
               numpy_array.tostring(),
               numpy_array.dtype.itemsize * width * nchannels)
    return im_cv


def cv_to_numpy(im):
    '''Converts opencv to numpy '''
    depth2dtype = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }

    #arrdtype = im.depth
    a = numpy.fromstring(
         im.tostring(),
         dtype=depth2dtype[im.depth],
         count=im.width * im.height * im.nChannels)
    a.shape = (im.height, im.width, im.nChannels)
    return a


@simple_block(num_outputs=2)
def gradient(grayscale, aperture_size=3):
    """ 
        Computes the gradient of an image using a Sobel filter.
    
        :param grayscale:  A field to derive.
        :type  grayscale:  HxW array float
        
        :param aperture_size: Aperture of the Sobel filter (odd).
        :type  aperture_size: int,odd,>=1
     
        :return: gx: Gradient in the *x* direction.
        :rtype: array(HxW,float)
        
        :return: gy: Gradient in the *y* direction.
        :rtype: array(HxW,float)
    """

    check_2d_array(grayscale, "grayscale")

    im = numpy_to_cv(grayscale)
    shape = (im.width, im.height)
    sobel = cv.CreateImage(shape, cv.IPL_DEPTH_32F, 1)
    cv.Sobel(im, sobel, 1, 0, aperture_size)
    gx = cv_to_numpy(sobel).squeeze()

    sobel = cv.CreateImage(shape, cv.IPL_DEPTH_32F, 1)
    cv.Sobel(im, sobel, 0, 1, aperture_size)
    gy = cv_to_numpy(sobel).squeeze()

    return gx.astype('float32'), gy.astype('float32')


@simple_block
def smooth(grayscale, gaussian_std=5.0):
    """ 
        Smooths an image with a Gaussian filter.
        
        :param grayscale:  A field to derive.
        :type  grayscale:  HxW array float
        
        :param gaussian_std: Std-deviation of the Gaussian filter.
        :type  gaussian_std: float,>0
     
        :return: smoothed: The smoothed image.
        :rtype: array(HxW,float)
        
    """

    check_2d_array(grayscale, "grayscale")
    grayscale = grayscale.astype('float32')

    im = numpy_to_cv(grayscale)
    shape = (im.width, im.height)
    smoothed = cv.CreateImage(shape, cv.IPL_DEPTH_32F, 1)

    cv.Smooth(im, smoothed, cv.CV_GAUSSIAN, 0, 0, gaussian_std)

    result_a = cv_to_numpy(smoothed).squeeze()
    return result_a

