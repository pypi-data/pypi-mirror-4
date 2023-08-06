#!/usr/bin/env python

"""Unittests for threadpool library"""

import unittest
import time
from ..threadpool import ThreadPool

def echo_exception():
    print("Doing some stuff")
    raise Exception

class Testy(object):
    def sum(self, num1, num2):
        time.sleep(1)
        return num1 + num2

def pow(x):
    return x*x

class ThreadPoolTest(unittest.TestCase):

    def test_class_func_multi_tasks(self):
        tp = ThreadPool(debug = True)
        tt = Testy()
        tasks = [(tt.sum, [1, 2], {}),]
        tp.add_tasks_to_queue(tasks)
        results = tp.get_results(tasks)
        expected_results = [3]
        self.assertEqual(results, expected_results, msg = "Unexpected output from threadpool")

    def test_func_exception(self):
        """Test running a function that throws an exception.
        Thread should not except as that would kill it"""
        tp = ThreadPool(debug = True)
        tp.add_task_to_queue(echo_exception)
        tasks = range(0, 1)
        self.assertEqual(tp.get_results(tasks), [None], msg = "Got no output from thread")

    def test_threadpool_output(self):
        tp = ThreadPool(debug = True)
        tp.add_task_to_queue(pow, 2)
        tp.add_task_to_queue(pow, 3)
        tasks = range(0, 2)
        results = tp.get_results(tasks)
        expected_results = [4, 9]
        # Order of returned output is non-deterministic because of being running in threads
        expected_results.sort()
        results.sort()
        self.assertEqual(results, expected_results, msg = "Unexpected output from threadpool, got %s, expected %s" %
                         (results, expected_results))

if __name__ == '__main__':
    unittest.main()
