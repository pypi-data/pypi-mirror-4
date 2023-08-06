# This code is released into public domain.

__version__ = '0.3'
__author__ = 'anatoly techtonik <techtonik@gmail.com>'

import datetime
import inspect
import os
import sys


class XTracer(object):
    """container for xtrace module state"""
    def __init__(self):
        self.oldfunc = None    #: placeholder to save old trace function if any
        self.cwd = os.getcwd() #: current directory is stripped from filenames
        self.filter = ['/usr/lib/python'] # [ ] detect stdlib location

        # [ ] check what will happen with depth when trace started deep inside and
        #     moved out (also check for Xdebug)
        self.depth = 0         #: depth is reset on each run of start()

    def start(self):
        self.depth = 0
        self.oldfunc = sys.gettrace()
        print datetime.datetime.now().strftime('TRACE START [%Y-%m-%d %H:%M:%S]')
        sys.settrace(self.function_trace_xdebug)

    def stop(self):
        print datetime.datetime.now().strftime('TRACE END   [%Y-%m-%d %H:%M:%S]')
        sys.settrace(self.oldfunc)

    def _strip_cwd(self, filename):
        if self.cwd and filename.startswith(self.cwd):
            return os.path.normpath(filename.replace(self.cwd, '.', 1))
        else:
            return filename
 
    def function_trace_xdebug(self, frame, event, arg):
        '''print function trace in default xdebug human-readable format 
           http://xdebug.org/docs/execution_trace'''
        if event == 'call': # generated before any function call
            self.depth += 1
            funcname = frame.f_code.co_name
            filename = self._strip_cwd(frame.f_code.co_filename)
            lineno = frame.f_lineno
            param = ''
            if funcname == '<module>':
                module = inspect.getmodule(frame.f_code)
                if module:
                    funcname = '<%s>' % module.__name__
                else: # inspect.getmodule() seem to fail on __import__(...) stmts
                    funcname = '<>'
                # by analogy with PHP require() trace in Xdebug, the format is
                # <mod.name>(module_location) file_imported_from:line
                param = filename
                if frame.f_back:
                   filename = self._strip_cwd(frame.f_back.f_code.co_filename)
                else:
                   filename = ''  # top frame, no parent
            # skip paths mentioned in trace_filter
            if (funcname[0] is not '<' # not module import
                    and any( [filename.startswith(x) for x in self.filter] )):
                pass
            else:
                print '%*s-> %s(%s) %s:%s' % (self.depth*2, '', funcname, param,
                                      filename, lineno)
            return self.function_trace_xdebug
        elif event == 'return':
            self.depth -= 1
        else:
            pass #print 'TRACE: UNKNOWN %s EVENT WITH ARG %s' % (event, arg)
            return

_xtracer = XTracer()
def start():
    _xtracer.start()
def stop():
    _xtracer.stop()


def main():
    if not sys.argv[1:] or sys.argv[1] in ['-h', '--help']:
        # [ ] detect when run as a module
        sys.exit("Usage: %s <script.py> [param] ..." % sys.argv[0])
    
    script = sys.argv[1]
    # strip xtrace from sys.argv
    sys.argv = sys.argv[1:]
    
    start()
    execfile(script)
    stop()

if __name__ == '__main__':
    main()

