import numpy

from procgraph  import Block, BadInput
from procgraph.block_utils import make_sure_dir_exists

from . import tables
from .tables_cache import tc_open_for_writing, tc_close
import os


# TODO: write original order


PROCGRAPH_LOG_GROUP = 'procgraph'


class HDFwrite(Block):
    ''' This block writes the incoming signals to a file in HDF_ format.
     
    The HDF format is organized as follows: ::
    
         /            (root)
         /procgraph             (group with name procgraph)
         /procgraph/signal1     (table)
         /procgraph/signal2     (table)
         ...
         
    Each table has the following fields:
    
         time         (float64 timestamp)
         value        (the datatype of the signal)
         
    If a signal changes datatype, then an error is thrown.
    
    '''

    Block.alias('hdfwrite')
    Block.input_is_variable('Signals to be written', min=1)
    Block.config('file', 'HDF file to write')
    Block.config('compress', 'Whether to compress the hdf table.', 1)
    Block.config('complib', 'Compression library (zlib, bzip2, blosc, lzo).',
                 default='zlib')
    Block.config('complevel', 'Compression level (0-9)', 9)

    def init(self):
        make_sure_dir_exists(self.config.file)
        self.tmp_filename = self.config.file + '.active'
        self.info('Writing to file %r.' % self.tmp_filename)
        self.hf = tc_open_for_writing(self.tmp_filename)

        self.group = self.hf.createGroup(self.hf.root, 'procgraph')
        # TODO: add meta info

        # signal name -> table in hdf file
        self.signal2table = {}
        # signal name -> last timestamp written
        self.signal2timestamp = {}

    def update(self):
        signals = self.get_input_signals_names()
        for signal in signals:
            self.log_signal(signal)

    def log_signal(self, signal):
        timestamp = self.get_input_timestamp(signal)
        value = self.get_input(signal)
        # only do something if we have something 
        if value is None:
            return
        assert timestamp is not None

        if not isinstance(value, numpy.ndarray):
            # TODO: try converting
            try:
                value = numpy.array(value)
            except:
                msg = 'I can only log numpy arrays, not %r' % value.__class__
                raise BadInput(msg, self, signal)

        # also check that we didn't already log this instant
        if (signal in self.signal2timestamp) and \
           (self.signal2timestamp[signal] == timestamp):
            return
        self.signal2timestamp[signal] = timestamp

        # check that we have the table for this signal
        table_dtype = [('time', 'float64'),
                       ('value', value.dtype, value.shape)]

        table_dtype = numpy.dtype(table_dtype)

        # TODO: check that the dtype is consistnet

        if not signal in self.signal2table:
            # a bit of compression. zlib is standard for hdf5
            # fletcher32 writes by entry rather than by rows
            if self.config.compress:
                filters = tables.Filters(
                            complevel=self.config.complevel,
                            complib=self.config.complib,
                            fletcher32=True)
            else:
                filters = tables.Filters(fletcher32=True)

            try:
                table = self.hf.createTable(
                        where=self.group,
                        name=signal,
                        description=table_dtype,
                        #expectedrows=10000, # large guess
                        byteorder='little',
                        filters=filters
                    )
            except NotImplementedError as e:
                msg = 'Could not create table with dtype %r: %s' % \
                      (table_dtype, e)
                raise BadInput(msg, self, input_signal=signal)

            self.debug('Created table %r' % table)
            self.signal2table[signal] = table
        else:
            table = self.signal2table[signal]

        row = numpy.ndarray(shape=(1,), dtype=table_dtype)
        row[0]['time'] = timestamp
        if value.size == 1:
            row[0]['value'] = value
        else:
            row[0]['value'][:] = value
        # row[0]['value'] = value  <--- gives memory error
        table.append(row)

    def finish(self):
        tc_close(self.hf)
        if os.path.exists(self.config.file):
            os.unlink(self.config.file)
        os.rename(self.tmp_filename, self.config.file)

