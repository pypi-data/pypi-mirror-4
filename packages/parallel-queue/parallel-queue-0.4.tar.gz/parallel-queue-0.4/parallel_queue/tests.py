from Queue import PriorityQueue, Full, Empty
import multiprocessing
from unittest import TestCase
from . import ParallelSingleTaskQueue, PacketID, ParallelQueue
import itertools

__author__ = 'Tikitu de Jager <tikitu@logophile.org>'


class PermutationTask(object):

    def __init__(self, events, permutation):
        self.events = events
        self.permutation = permutation

    def __call__(self, data):
        self.events[self.permutation[data]].wait()
        return data


def raise_():
    raise ValueError('Bad value, bad bad value!')


class Ordering(TestCase):

    def setUp(self):
        self.queue = None

    def tearDown(self):
        """
        Convenience stopping a queue and tidying up: to use it, assign the queue you test to self.queue
        """
        if self.queue is not None and self.queue.is_alive():
            self.queue.stop()
            self.queue.join(timeout=1)
            self.assertFalse(self.queue.is_alive())

    def test_ordering_on_lots_of_permutations(self):
        num_workers = 3
        num_data_points = num_workers + 1
        timeout = 1  # seconds

        events = [multiprocessing.Event() for _ in range(num_data_points)]

        for permutation in itertools.permutations(range(num_data_points)):
            progress_semaphore = multiprocessing.Semaphore(0)
            queue = ParallelSingleTaskQueue(PermutationTask(events, permutation), num_workers=num_workers,
                                  in_q_max=num_data_points, out_q_max=num_data_points,
                                  worker_q_max=1, consumer_buffer_max=num_workers,
                                  daemon=True,
                                  progress_semaphore=progress_semaphore)

            for event in events:
                event.clear()

            for i in range(num_data_points):
                try:
                    queue.put(i, timeout=timeout)
                except Full:
                    self.assertFalse(True, u'Permutation {0} timed out putting {1}'.format(permutation, i))

            for event in events:
                event.set()  # release a task
                progress_semaphore.acquire(timeout=0.1)  # wait for the Consumer to get the task
                # timeout is necessary because in problematic orderings the consumer won't get any task until at least
                # two have been released. This makes the test slow, but reliable.

            queue.stop()
            queue.join(timeout=timeout)
            self.assertFalse(queue.is_alive(), u'Permutation {0} timed out'.format(permutation))

    def test_timeouts(self):
        self.queue = ParallelQueue(num_workers=3)

        self.queue.join(timeout=1)
        self.assertTrue(self.queue.is_alive())

    def test_exceptions(self):
        self.queue = ParallelQueue(num_workers=1, daemon=True)
        self.queue.put(raise_)
        got_exception = False
        try:
            self.queue.get(timeout=1)
        except ValueError as e:
            got_exception = True
            self.assertIsInstance(e.stack_trace, basestring,
                                  "queue should add process-internal stack trace to rethrown exceptions")
        self.assertTrue(got_exception)

    def test_id_wraparound(self):
        self.queue = ParallelQueue(num_workers=3, in_q_max=2, out_q_max=2, worker_q_max=2, daemon=True)
        for i in range(50):
            self.queue.put(4 * i, timeout=1)
            self.queue.put(4 * i + 1, timeout=1)
            self.queue.put(4 * i + 2, timeout=1)
            self.queue.put(4 * i + 3, timeout=1)
            self.assertEquals(self.queue.get(timeout=3), 4 * i)
            self.assertEquals(self.queue.get(timeout=3), 4 * i + 1)
            self.assertEquals(self.queue.get(timeout=3), 4 * i + 2)
            self.assertEquals(self.queue.get(timeout=3), 4 * i + 3)


class IDs(TestCase):

    def test_heap(self):
        heap = PriorityQueue(maxsize=10)
        packet_id = PacketID(window=5)
        for i in range(100):
            heap.put(packet_id)
            packet_id = packet_id.next()
            if i >= 5:
                val = heap.get().value
                self.assertEqual((i - 5) % packet_id._base, val, "failed at i={0} with value {1}".format(i, val))

    def test_gt(self):
        id_0 = PacketID(window=5, value=0)
        id_1 = id_0.next()
        id_2 = id_1.next()
        id_3 = id_2.next()
        id_4 = id_3.next()
        id_5 = id_4.next()
        self.assertGreater(id_1, id_0)
        self.assertLessEqual(id_0, id_1)
        self.assertGreater(id_2, id_0)
        self.assertLessEqual(id_0, id_2)
        self.assertGreater(id_3, id_0)
        self.assertLessEqual(id_0, id_3)
        self.assertGreater(id_4, id_0)
        self.assertLessEqual(id_0, id_4)
        self.assertGreater(id_5, id_0)
        self.assertLessEqual(id_0, id_5)
        self.assertGreater(id_0, id_5.next())  # wraparound
        self.assertLessEqual(id_5.next(), id_0)
        self.assertGreater(id_1, id_5.next().next())
        self.assertLessEqual(id_5.next().next(), id_1)


# These must be pickleable so cannot be lambda's. Sigh.
def task_1(): return 1
def task_2(): return 2
def task_3(): return 3
def task(*args, **kwargs): return (args, kwargs)
class TaskQueue(TestCase):

    def setUp(self):
        self.queue = None

    def tearDown(self):
        """
        Convenience stopping a queue and tidying up: to use it, assign the queue you test to self.queue
        """
        if self.queue is not None and self.queue.is_alive():
            self.queue.stop()
            self.queue.join(timeout=1)
            self.assertFalse(self.queue.is_alive())

    def test_simple(self):
        q = ParallelQueue(num_workers=3, in_q_max=2, out_q_max=2, worker_q_max=2, daemon=True)
        self.queue = q
        q.put(task_1)
        q.put(task_2)
        q.put(task_3)
        self.assertEqual(q.get(), 1)
        self.assertEqual(q.get(), 2)
        self.assertEqual(q.get(), 3)

        q.put(int, 4)
        self.assertEquals(q.get(), 4)

        q.put(5)
        self.assertEquals(q.get(), 5, "Non-callables should not be called")

        self.assertRaises(ValueError, q.put, 6, 7)

    def test_timeouts(self):
        q = ParallelQueue(num_workers=3, in_q_max=2, out_q_max=2, worker_q_max=2, daemon=True)
        self.queue = q
        q.put(task)
        q.put(task, 'val')
        q.put(task, timeout=1, otherarg=2)
        self.assertEquals(q.get(), ((), {}))
        self.assertEquals(q.get(), (('val',), {}))
        self.assertEquals(q.get(), ((), {'otherarg': 2}))

    def test_args(self):
        q = ParallelSingleTaskQueue(task, num_workers=3, in_q_max=2, out_q_max=2, worker_q_max=2, daemon=True)
        self.queue = q
        q.put()
        q.put('val')
        q.put(timeout=1, otherarg=2)
        self.assertEquals(q.get(), ((), {}))
        self.assertEquals(q.get(), (('val',), {}))
        self.assertEquals(q.get(), ((), {'otherarg': 2}))
