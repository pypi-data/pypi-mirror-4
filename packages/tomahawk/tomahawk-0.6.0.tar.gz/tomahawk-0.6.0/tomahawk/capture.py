import cStringIO
import sys

class IOCapture(object):
    def __init__(self, stdout = True, stderr = True):
        self.captured_stdout = None
        self.captured_stderr = None
        if stdout:
            self.captured_stdout = cStringIO.StringIO()
        if stderr:
            self.captured_stderr = cStringIO.StringIO()

    def start(self):
        if self.captured_stdout:
            sys.stdout = self.captured_stdout
        if self.captured_stderr:
            sys.stderr = self.captured_stderr
        return self

    def stop(self):
        if self.captured_stdout:
            sys.stdout = sys.__stdout__
        if self.captured_stderr:
            sys.stderr = sys.__stderr__
        return self
 
    def captured_stdout(self):
        self.captured_stdout.flush()
        return self.captured_stdout.getvalue()

    def captured_stderr(self):
        self.captured_stderr.flush()
        return self.captured_stderr.getvalue()
 
    def close(self):
        if self.captured_stdout:
            self.captured_stdout.close()
        if self.captured_stderr:
            self.captured_stderr.close()
        return self

    def __enter__(self):
        return self.start()
 
    def __exit__(self, type, value, traceback):
        self.stop().close()
