from procgraph import Block, Generator
from rospy.rostime import Time
from contracts import contract
from procgraph import BadConfig

# warnings.warn('Remove limit')

class BagRead(Generator):
    ''' 
        This block reads a bag file (ROS logging format).
    '''
    Block.alias('bagread')
    Block.output_is_defined_at_runtime('The signals read from the log.')
    Block.config('file', 'Bag file to read')
    Block.config('limit', 'Limit in seconds on how much data we want. (0=no limit)', default=0)
    Block.config('topics', 'Which signals to output (and in what order). '
                 'Should be a comma-separated list. If you do not specify it '
                 '(or if empty) it will be all signals.',
                 default=None)
 
    Block.config('quiet', 'If true, disables advancements status messages.',
                 default=False)
                 
    def get_output_signals(self):
        from ros import rosbag  # @UnresolvedImport
        self.bag = rosbag.Bag(self.config.file)
        
        limit = self.config.limit
        if not isinstance(limit, (float, int)):
            raise BadConfig('I require a number; 0 for none.', self, 'limit')

        if self.config.topics is not None:
            given_topics = self.config.topics.strip()
        else:
            given_topics = None

        # self.info('Given: %s' % given_topics)    
        if given_topics:
            topics = given_topics.split(',')
        else:
            all_topics = [c.topic for c in self.bag._get_connections()]
            topics = sorted(set(all_topics))

        self.topics = topics
        # self.info('Tppics: %s' % topics)    

        self.topic2signal = {}
        signals = []
        for t in topics:
            self.info(t)
            if ':' in t:
                tokens = t.split(':')
                assert len(tokens) == 2
                t = tokens[0]
                signal_name = tokens[1]
            else:
                signal_name = str(t).split('/')[-1]
            if signal_name in signals:
                self.error('Warning: repeated name %s' % signal_name)
                signal_name = ("%s" % t).replace('/', '_')
                self.error('Using long form %r.' % signal_name)
            signals.append(signal_name)
            self.topic2signal[t] = signal_name

        topics = self.topic2signal.keys()

        self.info(self.topic2signal)

        limit = self.config.limit
        start_time, end_time = self._get_start_end_time(limit)
        self.iterator = self.bag.read_messages(topics=topics, start_time=start_time, end_time=end_time)

        return signals
    
    @contract(limit='None|number')
    def _get_start_end_time(self, limit):
        """ 
            Returns the start and end time to use (rospy.Time).
        
            also sets self.start_stamp, self.end_stamp
            
        """
        self.info('limit: %r' % limit)
        if limit is not None and limit != 0:
#             try:
            chunks = self.bag.__dict__['_chunks']
            self.start_stamp = chunks[0].start_time.to_sec()
            self.end_stamp = chunks[-1].end_time.to_sec()
            start_time = Time.from_sec(self.start_stamp)
            end_time = Time.from_sec(self.start_stamp + limit)
            return start_time, end_time
#             except Exception as e:
#                 self.error('Perhaps unindexed bag?')
#                 self.error(traceback.format_exc(e))
#                 raise
#                 start_time = None
#                 end_time = None
#                 
#             self.info('start_stamp: %s' % self.start_stamp)
#             self.info('end_stamp: %s' % self.end_stamp)
        else:
            self.start_stamp = None
            self.end_stamp = None
            return None, None
                

    def init(self):
        self._load_next()

    def _load_next(self):
        try:
            topic, msg, timestamp = self.iterator.next()
            self.next_timestamp = timestamp.to_sec()
            self.next_value = msg
            self.next_topic = topic
            self.next_signal = self.topic2signal[topic]
            self.has_next = True
        except StopIteration:
            self.has_next = False

    def next_data_status(self):
        if self.has_next:
            return (self.next_signal, self.next_timestamp)
        else:
            return (False, None)

    def update(self):
        if not self.has_next:
            return  # XXX: error here?

        self.set_output(self.next_signal,
                        value=self.next_value,
                        timestamp=self.next_timestamp)

        self._load_next()
        
        # write status message if not quiet
#         if self.next_signal == self.topics[0] and not self.config.quiet:
#             self.write_update_message(index, len(table), next_signal)

#    def write_update_message(self, index, T, signal, nintervals=10):
#        interval = int(numpy.floor(T * 1.0 / nintervals))
#        if (index > 0 and 
#            index != interval * (nintervals) and 
#            index % interval == 0): 
#            percentage = index * 100.0 / T
#            T = str(T)
#            index = str(index).rjust(len(T))
#            self.debug('%s read %.0f%% (%s/%s) (tracking signal %r).' % 
#                        (self.config.file, percentage, index, T, signal))
#         
    def finish(self):
        self.bag.close()


