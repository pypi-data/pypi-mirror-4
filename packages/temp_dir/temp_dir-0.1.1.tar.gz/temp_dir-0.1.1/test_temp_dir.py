import os

import temp_dir as m

import unittest


class Test_in_temp_dir(unittest.TestCase):

    def test_block_is_executed_in_a_temporary_directory(self):
        orig_working_directory = os.getcwd()

        with m.in_temp_dir():
            working_directory_in_block = os.getcwd()

        self.assertNotEqual(orig_working_directory, working_directory_in_block)

    def test_after_block_original_working_directory_is_restored(self):
        orig_working_directory = os.getcwd()

        with m.in_temp_dir():
            pass

        self.assertEqual(orig_working_directory, os.getcwd())


class Test_within_temp_dir(unittest.TestCase):

    def test_function_is_executed_in_a_temporary_directory(self):
        orig_working_directory = os.getcwd()

        @m.within_temp_dir
        def f():
            return os.getcwd()

        working_directory_in_function = f()

        self.assertNotEqual(
            orig_working_directory, working_directory_in_function)

    def test_after_function_call_original_working_directory_is_restored(self):
        orig_working_directory = os.getcwd()

        @m.within_temp_dir
        def f():
            pass

        f()

        self.assertEqual(orig_working_directory, os.getcwd())

    def test_arguments_are_passed_over_to_function(self):
        @m.within_temp_dir
        def f(a, *args, **kwargs):
            return (a, args, kwargs)

        self.assertEqual(('a', ('b',), dict(c='c')), f('a', 'b', c='c'))
        self.assertEqual(('a', tuple(), dict(x='x')), f(a='a', x='x'))
