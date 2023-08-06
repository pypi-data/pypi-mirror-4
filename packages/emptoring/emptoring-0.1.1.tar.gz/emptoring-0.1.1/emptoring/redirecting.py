""" Temporarily redirect stdout stderr with context manager
    
See LICENSE.txt for Licensing details
Copyright (c) <2013> <Samuel M. Smith>

"""


import os
import sys
import cStringIO

class Redirector(object):
    """
        Create Context manager
        Open io.StringIO streams and redirect stdout and stderr to io stream
        Stream is available  or.stream attribute or .getvalue() method before close
        Close stream and restore stdout stderr
    """
    def __init__(self):
        self.stream = cStringIO.StringIO()

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self.stream, self.stream
        return self.stream

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.close()
        sys.stdout, sys.stderr = self.old_stdout,  self.old_stderr



class RedirectStdStreams(object):
    """ http://stackoverflow.com/questions/6796492/python-temporarily-redirect-stdout-stderr
        if __name__ == '__main__':
            devnull = open(os.devnull, 'w')
            
            print('Foobar')
            with RedirectStdStreams(stdout=devnull, stderr=devnull):
               print("You'll never see me")
    
            print("I'm back!")
    """
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        return False
