import numpy

from procgraph import simple_block

from . import Image
from procgraph import Block
from procgraph.core.block import Generator

class StaticImage(Generator):
    Block.alias('static_image')
    Block.config('file', 'Static image to read')
    Block.output('rgb', 'Image rgb')
    
    def init(self):
        self.done = False

    def next_data_status(self):
        #print('Status')
        if self.done:
            #print ('Return False, none')
            return (False, None)
        else:
            #print ('Return True, none')
            return (True, 0) # XXX: not sure
    
    def update(self):
        #print('update')
        self.set_output('rgb', imread(self.config.file), 0)
        self.done = True
    

@simple_block
def imread(filename):
    ''' 
        Reads an image from a file.
        
        :param filename: Image filename.
        :type filename: string
        
        :return: image: The image as a numpy array.
        :rtype: image
    '''
    try:
        im = Image.open(filename)
    except Exception as e:
        msg = 'Could not open filename "%s": %s' % (filename, e)
        raise Exception(msg)

    data = numpy.array(im)

    return data
