========
temp_dir
========

Change into newly created temporary directory for executing a block of code.

Upon leaving the code block the temporary directory and all its contents are
removed and the original working directory is restored.

Intended as a tool to ease "integration" testing.

The package contains only two functions: `in_temp_dir` to be used with the `with` statement
and `within_temp_dir` to decorate a function.


--------
Examples
--------

Function decorator::

    @within_temp_dir
    def f():
        return os.getcwd()


    class TestScript(unittest.TestCase):

        @within_temp_dir
        def test_output_file_created(self):
            self.create_input_file()
            call_script('input')
            self.assertTrue(os.path.exists('output'))


Context manager::

    with in_temp_dir():
        with open('tempfile', 'w') as f:
            f.write(...)
        process_file('tempfile')


-------------------------------
Similar functionality elsewhere
-------------------------------

Similar functionality can be found at

- test.test_support.temp_cwd
  (http://docs.python.org/3/library/test.html#test.support.temp_cwd)
  in the Python distribution
  - temp_cwd is quite close to this module,
  unfortunately it is not in the standard library,
  but packaged together with the regression tests.
  temp_cwd's source shows some special cases
  and runs the code in a directory that can be guessed

- tempdir (https://bitbucket.org/another_thomas/tempdir)

- tempdirs (https://github.com/thelinuxkid/tempdirs)
  - for creating any number of temporary directories

- path.py (https://github.com/jaraco/path.py/blob/master/path.py)
  - tempdir at the end of the file
