from Queue import PriorityQueue
from multiprocessing import Process
import multiprocessing
import time
from traceback import format_exc

__version__ = '0.4'
__author__ = 'Tikitu de Jager <tikitu@logophile.org>'


class PacketID(object):

    def __init__(self, window=None, value=0):
        """
        Packet ID in a system in which at most window-many packets ever exist
        at any given moment.
        """
        self._window = window
        self._base = window * 2 + 1
        self._value = value % self._base

    @property
    def value(self):
        return self._value

    def from_value(self, value):
        return self.__class__(window=self._window, value=value)

    def next(self):
        return self.from_value(self._value + 1)

    def __str__(self):
        return '<{0}>'.format(self._value)

    def __repr__(self):
        return 'PacketID(window={0},base={1},value={2})'.format(self._window,
                                                                self._base,
                                                                self._value)

    def __add__(self, other):
        """
        Other will be an *int*, not a PacketID
        """
        return self.from_value(self._value + other)

    def __sub__(self, other):
        """
        Other will be an *int*, not PacketID
        """
        return self + -other

    def __eq__(self, other):
        if other is None:
            return False
        if self._base != other._base or self._window != other._window:
            return False
        return self._value == other._value

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        if other is None:
            return True
        if self._base != other._base or self._window != other._window:
            raise ValueError('Incomparable Packet IDs {0} and {1}'.format(
                self.__repr__(), other.__repr__()))
        self_v = self._value
        other_v = other._value
        if abs(self_v - other_v) > self._window:  # cycle wrap-around
            if self_v > other_v:
                self_v -= self._base
            else:
                other_v -= self._base
            assert -self._window <= self_v <= self._window, "{0},{1},{2},{3}".format(self_v, other_v, self.__repr__(), other.__repr__())
            assert -self._window <= other_v <= self._window, "{0},{1},{2},{3}".format(self_v, other_v, self.__repr__(), other.__repr__())
        assert abs(self_v - other_v) <= self._window, "{0},{1},{2},{3}".format(self_v, other_v, self.__repr__(), other.__repr__())
        return self_v >= other_v

    def __gt__(self, other):
        return self >= other and self != other

    def __le__(self, other):
        return not self.__gt__(other)

    def __lt__(self, other):
        return self <= other and self != other


class Worker(Process):

    def __init__(self, task_fn, worker_in_q, worker_out_q, max_packet_id_v, progress_event):
        super(Worker, self).__init__()
        self.task_fn = task_fn
        self.worker_in_q = worker_in_q
        self.worker_out_q = worker_out_q
        self.max_packet_id_v = max_packet_id_v
        self.progress_event = progress_event

    def run(self):
        while True:
            packet_id, data = self.worker_in_q.get()
            try:
                if packet_id is None:
                    self.worker_out_q.put((None, None, None))
                    break
                args, kwargs = data
                processed_data = self.task_fn(*args, **kwargs)
                while packet_id > packet_id.from_value(self.max_packet_id_v.value):
                    # In the gap where this comment sits (after reading value but before waiting on event) it's
                    # possible that the consumer increments the value and sets the event. That would introduce a
                    # deadlock if the consumer is then waiting for this packet_id. The timeout on the wait() avoids
                    # the deadlock, at the (unlikely) cost of a short delay.
                    self.progress_event.wait(5)  # timeout
                self.worker_out_q.put((packet_id, processed_data, None))
            except Exception as e:
                e.stack_trace = format_exc()
                self.worker_out_q.put((packet_id, None, e))


class Consumer(Process):

    def __init__(self, worker_out_q, max_packet_id_v, num_workers,
                 consumer_out_q, progress_event,
                 buffer_size,
                 max_possible_packets,
                 progress_semaphore=None):
        """
        @type progress_semaphore: multiprocessing.Semaphore
        @arg progress_semaphore used only for testing! Ensures repeatable ordering (release one packet then wait for progress)
        """
        super(Consumer, self).__init__()
        self.worker_out_q = worker_out_q
        self.max_packet_id_v = max_packet_id_v
        self.num_workers = num_workers
        self.consumer_out_q = consumer_out_q
        self.progress_event = progress_event
        self.buffer_size = buffer_size
        self._max_possible_packets = max_possible_packets
        self._progress_semaphore = progress_semaphore
        self._output_buffer = PriorityQueue(maxsize=self.buffer_size)

    @property
    def _buffer_size(self):
        """
        Private because interface is not thought through yet.
        """
        return self._output_buffer.qsize()

    def run(self):
        def get_if_ready(output_buffer, expected_id):
            if output_buffer.empty():
                return None
            else:
                (packet_id, data, exception) = output_buffer.get()
                if packet_id is None:  # poison pill
                    self.num_workers -= 1
                    return None
                if packet_id == expected_id:
                    return (data, exception)
                else:
                    output_buffer.put((packet_id, data, exception))
                    return None
        next_packet_id = PacketID(window=self._max_possible_packets)
        self.max_packet_id_v.value = (next_packet_id + self._output_buffer.maxsize - 1).value
        while True:
            self.progress_event.clear()
            next_data = None
            while next_data is None:
                next_data = get_if_ready(self._output_buffer, next_packet_id)
                if next_data is None:
                    if not self.num_workers:
                        return
                    next_val = self.worker_out_q.get()
                    self._output_buffer.put(next_val)
                    if self._progress_semaphore is not None:
                        self._progress_semaphore.release()
            if not self.num_workers:
                break
            self.consumer_out_q.put(next_data)
            next_packet_id += 1
            self.max_packet_id_v.value = next_packet_id.from_value(self.max_packet_id_v.value + 1).value
            self.progress_event.set()


class ParallelSingleTaskQueue(object):

    def __init__(self, task_fn, num_workers=None, daemon=False,
                 in_q_max=1000, out_q_max=1000, worker_q_max=100,
                 consumer_buffer_max=None,
                 progress_semaphore=None):
        """
        @type progress_semaphore multiprocessing.Semaphore
        @arg progress_semaphore used only for testing! Ensures repeatable ordering (release one packet then wait for progress)
        """
        num_workers = num_workers or multiprocessing.cpu_count()
        if consumer_buffer_max is None:
            consumer_buffer_max = num_workers * 10
        max_possible_packets = in_q_max + worker_q_max + num_workers + consumer_buffer_max

        self._workers = []
        self._packet_id = PacketID(window=max_possible_packets)

        self.in_q = multiprocessing.Queue(maxsize=in_q_max)
        self.out_q = multiprocessing.Queue(maxsize=out_q_max)

        worker_out_q = multiprocessing.Queue(maxsize=worker_q_max)
        self._worker_out_q = worker_out_q
        max_packet_id_v = multiprocessing.Value('i', 0)
        progress_event = multiprocessing.Event()

        self._consumer = Consumer(worker_out_q, max_packet_id_v, num_workers,
                                  self.out_q, progress_event,
                                  consumer_buffer_max,
                                  max_possible_packets,
                                  progress_semaphore=progress_semaphore)
        self._consumer.daemon = daemon
        self._consumer.start()

        for _ in range(num_workers):
            worker = Worker(task_fn, self.in_q, worker_out_q,
                            max_packet_id_v, progress_event)
            worker.daemon = daemon
            worker.start()
            self._workers.append(worker)

    @property
    def _queue_size(self):
        """
        Private because interface is not entirely settled yet (potentially we want finer-grained information); use with caution.
        """
        return self.in_q.qsize() + self.out_q.qsize() + self._worker_out_q.qsize() + self._consumer._buffer_size

    def put(self, *args, **kwargs):
        """
        Not thread-safe!
        """
        timeout = kwargs.pop('timeout', None)
        self.in_q.put((self._packet_id, (args, kwargs)), timeout=timeout)
        self._packet_id += 1

    def get(self, **kwargs):
        """
        Not thread-safe!
        """
        (value, exception) = self.out_q.get(**kwargs)
        if exception is not None:
            raise exception
        else:
            return value

    def stop(self):
        for _ in self._workers:
            self.in_q.put((None, None))

    def join(self, timeout=None):
        for worker in self._workers:
            if timeout is not None:
                now = time.time()
            worker.join(timeout=timeout)
            if timeout is not None:
                timeout = max(0, timeout - (time.time() - now))
        self._consumer.join(timeout=timeout)

    def is_alive(self):
        for worker in self._workers:
            if worker.is_alive():
                return True
        return self._consumer.is_alive()

def identity(a):
    return a
class ParallelQueue(ParallelSingleTaskQueue):

    def __init__(self, **kwargs):
        super(ParallelQueue, self).__init__(lambda *a, **kw: a[0](*a[1:], **kw), **kwargs)

    def put(self, *args, **kwargs):
        if args and not callable(args[0]):
            timeout = kwargs.pop('timeout', None)
            if kwargs or len(args) != 1:
                raise ValueError('put() expects either a callable first argument or exactly one (non-callable) argument')
            kwargs['timeout'] = timeout
            args = (identity,) + args
        super(ParallelQueue, self).put(*args, **kwargs)