''' ProcGraph: what you would get if simulink was written in python 
    and was actually useful for dealing with log data. '''

__version__ = '1.5'

import logging
logging.basicConfig()
from logging import getLogger
logger = getLogger(__name__)

# If true, does not allow .pgc caches
deny_pgc_cache = True

from .core.exceptions import *

from .core.block import Block, Generator

from .core.model_loader import pg_add_this_package_models

from .core.registrar_other import (register_model_spec,
                                    register_simple_block, simple_block)

from .scripts import pg

from .core.import_magic import import_magic, import_succesful

from .core.constants import *



# TODO: parse .4 as 0.4
