''' Blocks for encoding/decoding video based on MPlayer. '''

from .mp4conversion import convert_to_mp4
from .mencoder import *
from .mplayer import *
from .depth_buffer import *
from .fix_frame_rate import *

procgraph_info = {
    # List of python packages 
    'requires': ['qtfaststart']
}



from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)
