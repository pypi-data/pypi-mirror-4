from .containers import (CONTAINERS, supports_full_metadata, guess_container,
    CONTAINER_MP4, do_quickstart)
from .metadata import get_ffmpeg_metadata_args, write_extra_metadata_for
from .vcodecs import VCODECS, guess_vcodec
from .video_info import pg_video_info
from contracts import contract
from procgraph import logger
from procgraph.utils import system_cmd_result, CmdException
import os
import warnings


@contract(timestamp='None|float', metadata='dict', vcodec_params='dict')
def pg_video_convert(filename,
                     out,
                     quiet=True,
                     container=None,
                     vcodec=None,
                     vcodec_params={},
                     timestamp=None,
                     metadata={}):
    """
        Converts a video file (e.g. an AVI) to another format.
        
        It makes sure to write information to preserve timestamp and the given metadata.
        
        One can then be guaranteed to access this data using the pg_info_video() function. 
    """
    logger.info('pg_video_convert:\n<- %s\n-> %s' % (filename, out))
    
    if container is None:
        container = guess_container(out)
        
    assert container in CONTAINERS 

    if vcodec is None:
        vcodec, vcodec_params = guess_vcodec(container)
    
    logger.info('container: %s' % container)
    logger.info('vcodec: %s' % vcodec)
    logger.info('vcodec_params: %s' % vcodec_params)

    cmds = ['ffmpeg']
    cmds += ['-y']
    cmds += ['-i', filename]
    
    cmds += VCODECS[vcodec](**vcodec_params)
    
    info = pg_video_info(filename)
    info['metadata'].update(metadata) 
    
    if timestamp is None:
        timestamp = info['timestamp']
        
    cmds += get_ffmpeg_metadata_args(metadata, timestamp)
    # cmds += ['-f', container]
    
    if container == CONTAINER_MP4:
        out1 = out + '.firstpass.mp4'
        cmds += [out1]
    else:
        out1 = out
        cmds += [out1]
    
    try:
        system_cmd_result('.', cmds,
                  display_stdout=not quiet,
                  display_stderr=not quiet,
                  raise_on_error=True,
                  capture_keyboard_interrupt=False)
    except CmdException:
        if os.path.exists(out1):
            os.unlink(out1)
        raise
    
    assert os.path.exists(out1)
    
    if container == CONTAINER_MP4:
        # do_quickstart(out1, out)
        warnings.warn("Not sure why quickstart does not work.")
        os.rename(out1, out)
    else:
        assert out1 == out 
        
    if not supports_full_metadata(container):
        write_extra_metadata_for(out, metadata)
        



    
