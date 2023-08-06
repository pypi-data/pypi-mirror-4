from procgraph import simple_block


@simple_block
def crop(rgb, left=0, right=0, top=0, bottom=0):
    ''' Crops an image by the given values'''

    #print('Cropping %s' % (str(rgb.shape)))
    rgb2 = rgb[top:-bottom, left:-right, :]

    #print('cropping %s -> %s' % (str(rgb.shape), str(rgb2.shape)))

#    if left > 0:
#        rgb = rgb[:, left:, :]
#
#    if right > 0:
#        rgb = rgb[:, :-right, :]
#
#    if top > 0:
#        rgb = rgb[top:, :, :]
#
#    if bottom > 0:
#        rgb = rgb[:-bottom, :, :]
    return rgb2


