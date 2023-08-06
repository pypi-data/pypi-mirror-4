''' 
    This is a set of blocks to read and write logs in ROS_ Bag format.
    
    You need the `rospy` package to be installed.
    
    .. _pytables: http://pytables.org
     
    .. _ROS: http://www.ros.org

'''

procgraph_info = {
    # List of python packages 
    'requires': ['ros']
}


# Smart dependency importing
from procgraph import import_magic
rosbag = import_magic(__name__, 'ros', 'rosbag')


from .bagread import BagRead
from .bagwrite import BagWrite
from .conversions import ros2python

from procgraph import pg_add_this_package_models
pg_add_this_package_models(__file__, __package__)
