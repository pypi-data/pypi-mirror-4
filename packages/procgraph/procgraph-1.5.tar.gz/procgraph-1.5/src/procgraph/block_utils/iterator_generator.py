from procgraph import Generator
from abc import abstractmethod


class IteratorGenerator(Generator):
    ''' 

    '''

    @abstractmethod
    def get_iterator(self):
        """ Must return an iterator yielding signal, timestamp, values """
        raise NotImplementedError()

    def init(self):
        self.iterator = self.get_iterator()
        self._load_next()

    def _load_next(self):
        try:
            signal, timestamp, value = self.iterator.next()
            self.next_signal = signal
            self.next_timestamp = timestamp
            self.next_value = value
            self.has_next = True
        except StopIteration:
            self.has_next = False

    def next_data_status(self):
        if self.has_next:
            return (True, self.next_timestamp)
        else:
            return (False, None)

    def update(self):
        if not self.has_next:
            return  # XXX: error here?

        self.set_output(self.next_signal,
                        value=self.next_value, timestamp=self.next_timestamp)

        self._load_next()
