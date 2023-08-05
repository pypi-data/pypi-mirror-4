#===============================================================================
# Copyright (C) 2011-2012 by Andrew Moffat
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#===============================================================================


__version__ = "1.02"
__project_url__ = "https://github.com/amoffat/sh"



import platform

if "windows" in platform.system().lower():
    raise ImportError("sh 1.0 is currently only supported on linux and osx. \
please install pbs 0.109 (http://pypi.python.org/pypi/pbs) for windows support.")



import sys
IS_PY3 = sys.version_info[0] == 3

import traceback
import os
import re
from glob import glob as original_glob
import shlex
from types import ModuleType
from functools import partial
import inspect
import time as _time


if IS_PY3:
    from io import StringIO
    from io import BytesIO as cStringIO
    from queue import Queue, Empty
else:
    from StringIO import StringIO
    from cStringIO import OutputType as cStringIO
    from Queue import Queue, Empty
    
IS_OSX = platform.system() == "Darwin"
THIS_DIR = os.path.dirname(os.path.realpath(__file__))


import errno
import warnings


from threading import Thread, Event
import pty
import termios
import signal
import select
import atexit
import gc
import threading
import tty
import pickle
import fcntl
import struct
import resource
from collections import deque
import logging


# this is ugly, but we've added a module-level logging kill switch.  the reason
# for it (vs letting the user disable/enable logging through the logging
# module's facilities) is because to enable/disable logging using logging
# facilities, modules need to have their loggers (retrieved with
# logging.getLogger()) named using dot notation.  so for example:
#
# log = logging.getLogger("sh.process")
#
# we don't do that though, because we cram a lot of info into the logger name
# for example, a logger name may be
# "<Process 1373 ['/usr/bin/python3.2', '/tmp/tmp2c18zp']>"
# because of this, a user can't disable our loggers (because we lack dot
# notation), and I won't add dot notation because I can't include all the
# data i need in my logger name.  so this is really a shortcoming of the
# logging module.  
logging_enabled = False









if IS_PY3:
    raw_input = input
    unicode = str
    basestring = str




class ErrorReturnCode(Exception):
    truncate_cap = 750

    def __init__(self, full_cmd, stdout, stderr):
        self.full_cmd = full_cmd
        self.stdout = stdout
        self.stderr = stderr


        if self.stdout is None: tstdout = "<redirected>"
        else:
            tstdout = self.stdout[:self.truncate_cap] 
            out_delta = len(self.stdout) - len(tstdout)
            if out_delta: 
                tstdout += ("... (%d more, please see e.stdout)" % out_delta).encode()
            
        if self.stderr is None: tstderr = "<redirected>"
        else:
            tstderr = self.stderr[:self.truncate_cap]
            err_delta = len(self.stderr) - len(tstderr)
            if err_delta: 
                tstderr += ("... (%d more, please see e.stderr)" % err_delta).encode()

        msg = "\n\n  RAN: %r\n\n  STDOUT:\n%s\n\n  STDERR:\n%s" %\
            (full_cmd, tstdout.decode(), tstderr.decode())
        super(ErrorReturnCode, self).__init__(msg)

class CommandNotFound(Exception): pass

rc_exc_regex = re.compile("ErrorReturnCode_(\d+)")
rc_exc_cache = {}

def get_rc_exc(rc):
    rc = int(rc)
    try: return rc_exc_cache[rc]
    except KeyError: pass
    
    name = "ErrorReturnCode_%d" % rc
    exc = type(name, (ErrorReturnCode,), {})
    rc_exc_cache[rc] = exc
    return exc




def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program): return program
    else:
        if "PATH" not in os.environ: return None
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def resolve_program(program):
    path = which(program)
    if not path:
        # our actual command might have a dash in it, but we can't call
        # that from python (we have to use underscores), so we'll check
        # if a dash version of our underscore command exists and use that
        # if it does
        if "_" in program: path = which(program.replace("_", "-"))        
        if not path: return None
    return path


# we add this thin wrapper to glob.glob because of a specific edge case where
# glob does not expand to anything.  for example, if you try to do
# glob.glob("*.py") and there are no *.py files in the directory, glob.glob
# returns an empty list.  this empty list gets passed to the command, and
# then the command fails with a misleading error message.  this thin wrapper
# ensures that if there is no expansion, we pass in the original argument,
# so that when the command fails, the error message is clearer
def glob(arg):    
    return original_glob(arg) or arg




class RunningCommand(object):
    def __init__(self, cmd, call_args, stdin, stdout, stderr):
        
        self.call_args = call_args
        self.cmd = cmd
        self.ran = " ".join(cmd)
        self.process = None

        self.should_wait = True
        spawn_process = True


        # with contexts shouldn't run at all yet, they prepend
        # to every command in the context
        if call_args["with"]:
            spawn_process = False
            Command._prepend_stack.append(cmd)
            

        if callable(call_args["out"]) or callable(call_args["err"]):
            self.should_wait = False
            
        if call_args["piped"] or call_args["iter"] or call_args["iter_noblock"]:
            self.should_wait = False
            
        # we're running in the background, return self and let us lazily
        # evaluate
        if call_args["bg"]: self.should_wait = False

        # redirection
        if call_args["err_to_out"]: stderr = STDOUT
        
        
        # set up which stream should write to the pipe
        # TODO, make pipe None by default and limit the size of the Queue
        # in oproc.OProc
        pipe = STDOUT
        if call_args["iter"] == "out" or call_args["iter"] is True: pipe = STDOUT
        elif call_args["iter"] == "err": pipe = STDERR
        
        if call_args["iter_noblock"] == "out" or call_args["iter_noblock"] is True: pipe = STDOUT
        elif call_args["iter_noblock"] == "err": pipe = STDERR
        
        
        if spawn_process:
            self.process = OProc(cmd, stdin, stdout, stderr, 
                self.call_args, pipe=pipe)
            
            if self.should_wait:
                self.wait()
        

    def wait(self):
        self._handle_exit_code(self.process.wait())
        return self
    
    # here we determine if we had an exception, or an error code that we weren't
    # expecting to see.  if we did, we create and raise an exception
    def _handle_exit_code(self, code):
        if code not in self.call_args["ok_code"] and code >= 0: raise get_rc_exc(code)(
            " ".join(self.cmd),
            self.process.stdout,
            self.process.stderr
        )        

    @property
    def stdout(self):
        self.wait()
        return self.process.stdout
    
    @property
    def stderr(self):
        self.wait()
        return self.process.stderr
    
    @property
    def exit_code(self):
        self.wait()
        return self.process.exit_code
    
    @property
    def pid(self):
        return self.process.pid
    
    def __len__(self):
        return len(str(self))
    
    def __enter__(self):
        # we don't actually do anything here because anything that should
        # have been done would have been done in the Command.__call__ call.
        # essentially all that has to happen is the comand be pushed on
        # the prepend stack.
        pass
    
    def __iter__(self):
        return self
    
    def next(self):
        # we do this because if get blocks, we can't catch a KeyboardInterrupt
        # so the slight timeout allows for that.
        while True:
            try: chunk = self.process._pipe_queue.get(False, .001)
            except Empty:
                if self.call_args["iter_noblock"]: return errno.EWOULDBLOCK
            else:
                if chunk is None:
                    self.wait()
                    raise StopIteration()
                try: return chunk.decode(self.call_args["encoding"])
                except UnicodeDecodeError: return chunk
            
    # python 3
    __next__ = next

    def __exit__(self, typ, value, traceback):
        if self.call_args["with"] and Command._prepend_stack:
            Command._prepend_stack.pop()
   
    def __str__(self):
        if IS_PY3: return self.__unicode__()
        else: return unicode(self).encode(self.call_args["encoding"])
        
    def __unicode__(self):
        if self.process: 
            if self.stdout: return self.stdout.decode(self.call_args["encoding"])
        return ""

    def __eq__(self, other):
        return unicode(self) == unicode(other)

    def __contains__(self, item):
        return item in str(self)

    def __getattr__(self, p):
        # let these three attributes pass through to the OProc object
        if p in ("signal", "terminate", "kill"):
            if self.process: return getattr(self.process, p)
            else: raise AttributeError
        return getattr(unicode(self), p)
     
    def __repr__(self):
        try: return str(self)
        except UnicodeDecodeError:
            if self.process: 
                if self.stdout: return repr(self.stdout)
            return repr("")

    def __long__(self):
        return long(str(self).strip())

    def __float__(self):
        return float(str(self).strip())

    def __int__(self):
        return int(str(self).strip())





class Command(object):
    _prepend_stack = []
    
    _call_args = {
        # currently unsupported
        #"fg": False, # run command in foreground
        
        "bg": False, # run command in background
        "with": False, # prepend the command to every command after it
        "in": None,
        "out": None, # redirect STDOUT
        "err": None, # redirect STDERR
        "err_to_out": None, # redirect STDERR to STDOUT
        
        # stdin buffer size
        # 1 for line, 0 for unbuffered, any other number for that amount
        "in_bufsize": 0,
        # stdout buffer size, same values as above
        "out_bufsize": 1,
        "err_bufsize": 1,
        
        # this is how big the output buffers will be for stdout and stderr.
        # this is essentially how much output they will store from the process.
        # we use a deque, so if it overflows past this amount, the first items
        # get pushed off as each new item gets added.
        # 
        # NOTICE
        # this is not a *BYTE* size, this is a *CHUNK* size...meaning, that if
        # you're buffering out/err at 1024 bytes, the internal buffer size will
        # be "internal_bufsize" CHUNKS of 1024 bytes
        "internal_bufsize": 3 * 1024**2,
        
        "env": None,
        "piped": None,
        "iter": None,
        "iter_noblock": None,
        "ok_code": 0,
        "cwd": None,
        
        # this is for programs that expect their input to be from a terminal.
        # ssh is one of those programs
        "tty_in": False,
        "tty_out": True,
        
        "encoding": "utf8",
        
        # how long the process should run before it is auto-killed
        "timeout": 0,
    }
    
    # these are arguments that cannot be called together, because they wouldn't
    # make any sense
    _incompatible_call_args = (
        #("fg", "bg", "Command can't be run in the foreground and background"),
        ("err", "err_to_out", "Stderr is already being redirected"),
        ("piped", "iter", "You cannot iterate when this command is being piped"),
    )

    @classmethod
    def _create(cls, program):
        path = resolve_program(program)
        if not path: raise CommandNotFound(program)
        return cls(path)
    
    def __init__(self, path):            
        self._path = path
        self._partial = False
        self._partial_baked_args = []
        self._partial_call_args = {}
        
    def __getattribute__(self, name):
        # convenience
        getattr = partial(object.__getattribute__, self)
        
        if name.startswith("_"): return getattr(name)    
        if name == "bake": return getattr("bake")         
        return getattr("bake")(name)

    
    @staticmethod
    def _extract_call_args(kwargs, to_override={}):
        kwargs = kwargs.copy()
        call_args = {}
        for parg, default in Command._call_args.items():
            key = "_" + parg
            
            if key in kwargs:
                call_args[parg] = kwargs[key] 
                del kwargs[key]
            elif parg in to_override:
                call_args[parg] = to_override[parg]
        
        # test for incompatible call args
        s1 = set(call_args.keys())
        for args in Command._incompatible_call_args:
            args = list(args)
            error = args.pop()

            if s1.issuperset(args):
                raise TypeError("Invalid special arguments %r: %s" % (args, error))
            
        return call_args, kwargs


    def _format_arg(self, arg):
        if IS_PY3: arg = str(arg)
        else: arg = unicode(arg).encode("utf8")
        return arg

    def _compile_args(self, args, kwargs):
        processed_args = []
                
        # aggregate positional args
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if not arg:
                    warnings.warn("Empty list passed as an argument to %r. \
If you're using glob.glob(), please use sh.glob() instead." % self.path, stacklevel=3)
                for sub_arg in arg: processed_args.append(self._format_arg(sub_arg))
            else: processed_args.append(self._format_arg(arg))

        # aggregate the keyword arguments
        for k,v in kwargs.items():
            # we're passing a short arg as a kwarg, example:
            # cut(d="\t")
            if len(k) == 1:
                processed_args.append("-"+k)
                if v is not True: processed_args.append(self._format_arg(v))

            # we're doing a long arg
            else:
                k = k.replace("_", "-")

                if v is True: processed_args.append("--"+k)
                else: processed_args.append("--%s=%s" % (k, self._format_arg(v)))

        return processed_args
 
    
    def bake(self, *args, **kwargs):
        fn = Command(self._path)
        fn._partial = True

        call_args, kwargs = self._extract_call_args(kwargs)
        
        pruned_call_args = call_args
        for k,v in Command._call_args.items():
            try:
                if pruned_call_args[k] == v:
                    del pruned_call_args[k]
            except KeyError: continue
        
        fn._partial_call_args.update(self._partial_call_args)
        fn._partial_call_args.update(pruned_call_args)
        fn._partial_baked_args.extend(self._partial_baked_args)
        fn._partial_baked_args.extend(self._compile_args(args, kwargs))
        return fn
       
    def __str__(self):
        if IS_PY3: return self.__unicode__()
        else: return unicode(self).encode("utf8")
        
    def __eq__(self, other):
        try: return str(self) == str(other)
        except: return False

    def __repr__(self):
        return str(self)
        
    def __unicode__(self):
        baked_args = " ".join(self._partial_baked_args)
        if baked_args: baked_args = " " + baked_args
        return self._path + baked_args

    def __enter__(self):
        self(_with=True)

    def __exit__(self, typ, value, traceback):
        Command._prepend_stack.pop()
            
    
    def __call__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        args = list(args)

        cmd = []

        # aggregate any 'with' contexts
        for prepend in self._prepend_stack: cmd.extend(prepend)

        cmd.append(self._path)
        
        # here we extract the special kwargs and override any
        # special kwargs from the possibly baked command
        tmp_call_args, kwargs = self._extract_call_args(kwargs, self._partial_call_args)
        call_args = Command._call_args.copy()
        call_args.update(tmp_call_args)


        if not isinstance(call_args["ok_code"], (tuple, list)):    
            call_args["ok_code"] = [call_args["ok_code"]]
            
        
        # check if we're piping via composition
        stdin = call_args["in"]
        if args:
            first_arg = args.pop(0)
            if isinstance(first_arg, RunningCommand):
                # it makes sense that if the input pipe of a command is running
                # in the background, then this command should run in the
                # background as well
                if first_arg.call_args["bg"]: call_args["bg"] = True
                stdin = first_arg.process._pipe_queue
                
            else:
                args.insert(0, first_arg)
            
        processed_args = self._compile_args(args, kwargs)

        # makes sure our arguments are broken up correctly
        split_args = self._partial_baked_args + processed_args

        final_args = split_args

        cmd.extend(final_args)


        # stdout redirection
        stdout = call_args["out"]
        if stdout \
            and not callable(stdout) \
            and not hasattr(stdout, "write") \
            and not isinstance(stdout, (cStringIO, StringIO)):
            
            stdout = open(str(stdout), "wb")
        

        # stderr redirection
        stderr = call_args["err"]
        if stderr and not callable(stderr) and not hasattr(stderr, "write") \
            and not isinstance(stderr, (cStringIO, StringIO)):
            stderr = open(str(err), "wb")
            

        return RunningCommand(cmd, call_args, stdin, stdout, stderr)




# used in redirecting
STDOUT = -1
STDERR = -2



# Process open = Popen
# Open Process = OProc
class OProc(object):
    _procs_to_cleanup = []
    _registered_cleanup = False
    _default_window_size = (24, 80)

    def __init__(self, cmd, stdin, stdout, stderr, call_args,
            persist=False, pipe=STDOUT):

        self.call_args = call_args

        self._single_tty = self.call_args["tty_in"] and self.call_args["tty_out"]

        # this logic is a little convoluted, but basically this top-level
        # if/else is for consolidating input and output TTYs into a single
        # TTY.  this is the only way some secure programs like ssh will
        # output correctly (is if stdout and stdin are both the same TTY)
        if self._single_tty:
            self._stdin_fd, self._slave_stdin_fd = pty.openpty()
            
            self._stdout_fd = self._stdin_fd
            self._slave_stdout_fd = self._slave_stdin_fd
            
            self._stderr_fd = self._stdin_fd
            self._slave_stderr_fd = self._slave_stdin_fd
        
        # do not consolidate stdin and stdout
        else:
            if self.call_args["tty_in"]:
                self._slave_stdin_fd, self._stdin_fd = pty.openpty()
            else:
                self._slave_stdin_fd, self._stdin_fd = os.pipe()
            
            # tty_out is usually the default
            if self.call_args["tty_out"]:
                self._stdout_fd, self._slave_stdout_fd = pty.openpty()
            else:
                self._stdout_fd, self._slave_stdout_fd = os.pipe()
                
            # unless STDERR is going to STDOUT, it ALWAYS needs to be a pipe,
            # and never a PTY.  the reason for this is not totally clear to me,
            # but it has to do with the fact that if STDERR isn't set as the
            # CTTY (because STDOUT is), the STDERR buffer won't always flush
            # by the time the process exits, and the data will be lost.
            # i've only seen this on OSX.
            if stderr is not STDOUT:
                self._stderr_fd, self._slave_stderr_fd = os.pipe()
            
        
        self.pid = os.fork()


        # child
        if self.pid == 0:
            # this piece of ugliness is due to a bug where we can lose output
            # if we do os.close(self._slave_stdout_fd) in the parent after
            # the child starts writing.
            # see http://bugs.python.org/issue15898
            if IS_OSX and IS_PY3: _time.sleep(0.01)
            
            os.setsid()
            
            if self.call_args["tty_out"]:
                # set raw mode, so there isn't any weird translation of newlines
                # to \r\n and other oddities.  we're not outputting to a terminal
                # anyways
                #
                # we HAVE to do this here, and not in the parent thread, because
                # we have to guarantee that this is set before the child process
                # is run, and we can't do it twice.
                tty.setraw(self._stdout_fd)
                
                
            os.close(self._stdin_fd)
            if not self._single_tty:
                os.close(self._stdout_fd)
                if stderr is not STDOUT: os.close(self._stderr_fd)                
                    
                    
            if self.call_args["cwd"]: os.chdir(self.call_args["cwd"])
            os.dup2(self._slave_stdin_fd, 0)
            os.dup2(self._slave_stdout_fd, 1)
            
            # we're not directing stderr to stdout?  then set self._slave_stderr_fd to
            # fd 2, the common stderr fd
            if stderr is STDOUT: os.dup2(self._slave_stdout_fd, 2) 
            else: os.dup2(self._slave_stderr_fd, 2)
            
            # don't inherit file descriptors
            max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
            os.closerange(3, max_fd)
                    

            # set our controlling terminal
            if self.call_args["tty_out"]:
                tmp_fd = os.open(os.ttyname(1), os.O_RDWR)
                os.close(tmp_fd)
                    

            if self.call_args["tty_out"]:
                self.setwinsize(1)
            
            # actually execute the process
            if self.call_args["env"] is None: os.execv(cmd[0], cmd)
            else: os.execve(cmd[0], cmd, self.call_args["env"])

            os._exit(255)

        # parent
        else:
            if not OProc._registered_cleanup:
                atexit.register(OProc._cleanup_procs)
                OProc._registered_cleanup = True
        
        
            self.started = _time.time()
            self.cmd = cmd
            self.exit_code = None
            self._done_callbacks = []
            
            self.stdin = stdin or Queue()
            self._pipe_queue = Queue()
        
            # this is used to prevent a race condition when we're waiting for
            # a process to end, and the OProc's internal threads are also checking
            # for the processes's end
            self._wait_lock = threading.Lock()
        
            # these are for aggregating the stdout and stderr.  we use a deque
            # because we don't want to overflow
            self._stdout = deque(maxlen=self.call_args["internal_bufsize"])
            self._stderr = deque(maxlen=self.call_args["internal_bufsize"])
            
            if self.call_args["tty_in"]: self.setwinsize(self._stdin_fd)
            
            
            self.log = logging.getLogger("process %r" % self)
            
            os.close(self._slave_stdin_fd)
            if not self._single_tty:
                os.close(self._slave_stdout_fd)
                if stderr is not STDOUT: os.close(self._slave_stderr_fd)
            
            if logging_enabled: self.log.debug("started process")
            if not persist: OProc._procs_to_cleanup.append(self)


            if self.call_args["tty_in"]:
                attr = termios.tcgetattr(self._stdin_fd)
                attr[3] &= ~termios.ECHO  
                termios.tcsetattr(self._stdin_fd, termios.TCSANOW, attr)



            # this represents the connection from a Queue object (or whatever
            # we're using to feed STDIN) to the process's STDIN fd
            self._stdin_stream = StreamWriter("stdin", self, self._stdin_fd,
                self.stdin, self.call_args["in_bufsize"])
                           
            stdout_pipe = self._pipe_queue if pipe is STDOUT else None
            
            # this represents the connection from a process's STDOUT fd to
            # wherever it has to go, sometimes a pipe Queue (that we will use
            # to pipe data to other processes), and also an internal deque
            # that we use to aggregate all the output
            self._stdout_stream = StreamReader("stdout", self, self._stdout_fd, stdout,
                self._stdout, self.call_args["out_bufsize"], stdout_pipe)
                
                
            if stderr is STDOUT or self._single_tty: self._stderr_stream = None 
            else:
                stderr_pipe = self._pipe_queue if pipe is STDERR else None   
                self._stderr_stream = StreamReader("stderr", self, self._stderr_fd, stderr,
                    self._stderr, self.call_args["err_bufsize"], stderr_pipe)
            
            # start the main io threads
            self._input_thread = self._start_thread(self.input_thread, self._stdin_stream)
            self._output_thread = self._start_thread(self.output_thread, self._stdout_stream, self._stderr_stream)
            
            
    def __repr__(self):
        return "<Process %d %r>" % (self.pid, self.cmd)        
            

    # also borrowed from pexpect.py
    @staticmethod
    def setwinsize(fd):
        rows, cols = OProc._default_window_size
        TIOCSWINSZ = getattr(termios, 'TIOCSWINSZ', -2146929561)
        if TIOCSWINSZ == 2148037735: # L is not required in Python >= 2.2.
            TIOCSWINSZ = -2146929561 # Same bits, but with sign.

        s = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(fd, TIOCSWINSZ, s)


    @staticmethod
    def _start_thread(fn, *args):
        thrd = threading.Thread(target=fn, args=args)
        thrd.daemon = True
        thrd.start()
        return thrd
    
    def in_bufsize(self, buf):
        self._stdin_stream.stream_bufferer.change_buffering(buf)
                
    def out_bufsize(self, buf):
        self._stdout_stream.stream_bufferer.change_buffering(buf)
    
    def err_bufsize(self, buf):
        if self._stderr_stream:
            self._stderr_stream.stream_bufferer.change_buffering(buf)


    def input_thread(self, stdin):
        done = False
        while not done and self.alive:
            if logging_enabled: self.log.debug("%r ready for more input", stdin)
            done = stdin.write()

        stdin.close()
            
            
    def output_thread(self, stdout, stderr):
        readers = []
        errors = []

        if stdout is not None:
            readers.append(stdout)
            errors.append(stdout)
        if stderr is not None:
            readers.append(stderr)
            errors.append(stderr)

        while readers:
            outputs, inputs, err = select.select(readers, [], errors, 0.1)

            # stdout and stderr
            for stream in outputs:
                if logging_enabled: self.log.debug("%r ready to be read from", stream)
                done = stream.read()
                if done: readers.remove(stream)
                
            for stream in err:
                pass
            
            # test if the process has been running too long
            if self.call_args["timeout"]:
                now = _time.time()
                if now - self.started > self.call_args["timeout"]:
                    if logging_enabled: self.log.debug("we've been running too long")
                    self.kill()


        # this is here because stdout may be the controlling TTY, and
        # we can't close it until the process has ended, otherwise the
        # child will get SIGHUP.  typically, if we've broken out of
        # the above loop, and we're here, the process is just about to
        # end, so it's probably ok to aggressively poll self.alive
        #
        # the other option to this would be to do the CTTY close from
        # the method that does the actual os.waitpid() call, but the
        # problem with that is that the above loop might still be
        # running, and closing the fd will cause some operation to
        # fail.  this is less complex than wrapping all the ops
        # in the above loop with out-of-band fd-close exceptions
        while self.alive: _time.sleep(0.001)
        if stdout: stdout.close()
        if stderr: stderr.close()


    @property
    def stdout(self):
        return "".encode(self.call_args["encoding"]).join(self._stdout)
    
    @property
    def stderr(self):
        return "".encode(self.call_args["encoding"]).join(self._stderr)
    
    
    def signal(self, sig):
        if logging_enabled: self.log.debug("sending signal %d", sig)
        try: os.kill(self.pid, sig)
        except OSError: pass

    def kill(self):
        if logging_enabled: self.log.debug("killing")
        self.signal(signal.SIGKILL)

    def terminate(self):
        if logging_enabled: self.log.debug("terminating")
        self.signal(signal.SIGTERM)

    @staticmethod
    def _cleanup_procs():
        for proc in OProc._procs_to_cleanup:
            proc.kill()
            proc.wait()


    def _handle_exit_code(self, exit_code):
        # if we exited from a signal, let our exit code reflect that
        if os.WIFSIGNALED(exit_code): return -os.WTERMSIG(exit_code)
        # otherwise just give us a normal exit code
        elif os.WIFEXITED(exit_code): return os.WEXITSTATUS(exit_code)
        else: raise RuntimeError("Unknown child exit status!")

    @property
    def alive(self):
        if self.exit_code is not None: return False
         
        # what we're doing here essentially is making sure that the main thread
        # (or another thread), isn't calling .wait() on the process.  because
        # .wait() calls os.waitpid(self.pid, 0), we can't do an os.waitpid
        # here...because if we did, and the process exited while in this
        # thread, the main thread's os.waitpid(self.pid, 0) would raise OSError
        # (because the process ended in another thread).
        #
        # so essentially what we're doing is, using this lock, checking if
        # we're calling .wait(), and if we are, let .wait() get the exit code
        # and handle the status, otherwise let us do it.
        acquired = self._wait_lock.acquire(False)
        if not acquired:
            if self.exit_code is not None: return False
            return True
         
        try:
            # WNOHANG is just that...we're calling waitpid without hanging...
            # essentially polling the process
            pid, exit_code = os.waitpid(self.pid, os.WNOHANG)
            if pid == self.pid:
                self.exit_code = self._handle_exit_code(exit_code)
                return False
             
        # no child process   
        except OSError: return False
        else: return True
        finally: self._wait_lock.release()
            

    def wait(self):
        if logging_enabled: self.log.debug("acquiring wait lock to wait for completion")
        with self._wait_lock:
            if logging_enabled: self.log.debug("got wait lock")
            
            if self.exit_code is None:
                if logging_enabled: self.log.debug("exit code not set, waiting on pid")
                pid, exit_code = os.waitpid(self.pid, 0)
                self.exit_code = self._handle_exit_code(exit_code)
            else:
                if logging_enabled: self.log.debug("exit code already set (%d), no need to wait", self.exit_code)
            
            self._input_thread.join()
            self._output_thread.join()
            
            for cb in self._done_callbacks: cb()
        
            return self.exit_code




class DoneReadingStdin(Exception): pass
class NoStdinData(Exception): pass



# this guy is for reading from some input (the stream) and writing to our
# opened process's stdin fd.  the stream can be a Queue, a callable, something
# with the "read" method, a string, or an iterable
class StreamWriter(object):
    def __init__(self, name, process, stream, stdin, bufsize):
        self.name = name
        self.process = process
        self.stream = stream
        self.stdin = stdin
        
        self.log = logging.getLogger(repr(self))
        
        
        self.stream_bufferer = StreamBufferer(self.process.call_args["encoding"],
            bufsize)
        
        # determine buffering for reading from the input we set for stdin
        if bufsize == 1: self.bufsize = 1024
        elif bufsize == 0: self.bufsize = 1
        else: self.bufsize = bufsize
            
        
        if isinstance(stdin, Queue):
            log_msg = "queue"
            self.get_chunk = self.get_queue_chunk
            
        elif callable(stdin):
            log_msg = "callable"
            self.get_chunk = self.get_callable_chunk
            
        # also handles stringio
        elif hasattr(stdin, "read"):
            log_msg = "file descriptor"
            self.get_chunk = self.get_file_chunk
            
        elif isinstance(stdin, basestring):
            log_msg = "string"
            
            if bufsize == 1:
                # TODO, make the split() be a generator
                self.stdin = iter((c+"\n" for c in stdin.split("\n")))
            else:
                self.stdin = iter(stdin[i:i+self.bufsize] for i in range(0, len(stdin), self.bufsize))
            self.get_chunk = self.get_iter_chunk
            
        else:
            log_msg = "general iterable"
            self.stdin = iter(stdin)
            self.get_chunk = self.get_iter_chunk
            
        if logging_enabled: self.log.debug("parsed stdin as a %s", log_msg)
        
            
    def __repr__(self):
        return "<StreamWriter %s for %r>" % (self.name, self.process)
    
    def fileno(self):
        return self.stream
    
    def get_queue_chunk(self):
        try: chunk = self.stdin.get(True, 0.01)
        except Empty: raise NoStdinData
        if chunk is None: raise DoneReadingStdin
        return chunk
        
    def get_callable_chunk(self):
        try: return self.stdin()
        except: raise DoneReadingStdin
        
    def get_iter_chunk(self):
        try:
            if IS_PY3: return self.stdin.__next__()
            else: return self.stdin.next()
        except StopIteration: raise DoneReadingStdin
        
    def get_file_chunk(self):
        if self.stream_bufferer.type == 1: chunk = self.stdin.readline()
        else: chunk = self.stdin.read(self.bufsize)
        if not chunk: raise DoneReadingStdin
        else: return chunk


    # the return value answers the questions "are we done writing forever?"
    def write(self):
        # get_chunk may sometimes return bytes, and sometimes returns trings
        # because of the nature of the different types of STDIN objects we
        # support
        try: chunk = self.get_chunk()
        except DoneReadingStdin:
            if logging_enabled: self.log.debug("done reading")
                
            if self.process.call_args["tty_in"]:
                # EOF time
                try: char = termios.tcgetattr(self.stream)[6][termios.VEOF]
                except: char = chr(4).encode()
                os.write(self.stream, char)
            
            return True
        
        except NoStdinData:
            if logging_enabled: self.log.debug("received no data")
            return False
        
        # if we're not bytes, make us bytes
        if IS_PY3 and hasattr(chunk, "encode"):
            chunk = chunk.encode(self.process.call_args["encoding"])
        
        for chunk in self.stream_bufferer.process(chunk):
            if logging_enabled: self.log.debug("got chunk size %d: %r", len(chunk), chunk[:30])
            
            if logging_enabled: self.log.debug("writing chunk to process")
            try:
                os.write(self.stream, chunk)
            except OSError:
                if logging_enabled: self.log.debug("OSError writing stdin chunk")
                return True
        
        
    def close(self):
        if logging_enabled: self.log.debug("closing, but flushing first")
        chunk = self.stream_bufferer.flush()
        if logging_enabled: self.log.debug("got chunk size %d to flush: %r", len(chunk), chunk[:30])
        try:
            if chunk: os.write(self.stream, chunk)
            if not self.process.call_args["tty_in"]:
                if logging_enabled: self.log.debug("we used a TTY, so closing the stream")
                os.close(self.stream)
        except OSError: pass
        


class StreamReader(object):

    def __init__(self, name, process, stream, handler, buffer, bufsize, pipe_queue=None):
        self.name = name
        self.process = process
        self.stream = stream
        self.buffer = buffer
        self.pipe_queue = pipe_queue

        self.log = logging.getLogger(repr(self))
        
        self.stream_bufferer = StreamBufferer(self.process.call_args["encoding"],
            bufsize)
        
        # determine buffering
        if bufsize == 1: self.bufsize = 1024
        elif bufsize == 0: self.bufsize = 1 
        else: self.bufsize = bufsize
        
        
        # here we're determining the handler type by doing some basic checks
        # on the handler object
        self.handler = handler
        if callable(handler): self.handler_type = "fn"
        elif isinstance(handler, StringIO): self.handler_type = "stringio"
        elif isinstance(handler, cStringIO):
            self.handler_type = "cstringio"
        elif hasattr(handler, "write"): self.handler_type = "fd"
        else: self.handler_type = None
        
        
        self.should_quit = False
        
        # here we choose how to call the callback, depending on how many
        # arguments it takes.  the reason for this is to make it as easy as
        # possible for people to use, without limiting them.  a new user will
        # assume the callback takes 1 argument (the data).  as they get more
        # advanced, they may want to terminate the process, or pass some stdin
        # back, and will realize that they can pass a callback of more args
        if self.handler_type == "fn":
            implied_arg = 0
            if inspect.ismethod(handler):
                implied_arg = 1
                num_args = len(inspect.getargspec(handler).args)
            
            else:
                if inspect.isfunction(handler):
                    num_args = len(inspect.getargspec(handler).args)
                    
                # is an object instance with __call__ method
                else:
                    implied_arg = 1
                    num_args = len(inspect.getargspec(handler.__call__).args)
                
                
            self.handler_args = ()
            if num_args == implied_arg + 2: self.handler_args = (self.process.stdin,)
            elif num_args == implied_arg + 3: self.handler_args = (self.process.stdin, self.process)

    def fileno(self):
        return self.stream
            
    def __repr__(self):
        return "<StreamReader %s for %r>" % (self.name, self.process)

    def close(self):
        chunk = self.stream_bufferer.flush()
        if logging_enabled: self.log.debug("got chunk size %d to flush: %r", len(chunk), chunk[:30])
        if chunk: self.write_chunk(chunk)
        
        if self.handler_type == "fd" and hasattr(self.handler, "close"):
            self.handler.flush()
        
        if self.pipe_queue: self.pipe_queue.put(None)
        try: os.close(self.stream)
        except OSError: pass


    def write_chunk(self, chunk):
        # in PY3, the chunk coming in will be bytes, so keep that in mind
        
        if self.handler_type == "fn" and not self.should_quit:
            # try to use the encoding first, if that doesn't work, send
            # the bytes
            try: to_handler = chunk.decode(self.process.call_args["encoding"])
            except UnicodeDecodeError: to_handler = chunk
            self.should_quit = self.handler(to_handler, *self.handler_args)
            
        elif self.handler_type == "stringio":
            self.handler.write(chunk.decode(self.process.call_args["encoding"]))

        elif self.handler_type in ("cstringio", "fd"):
            self.handler.write(chunk)
            

        if self.pipe_queue:
            if logging_enabled: self.log.debug("putting chunk onto pipe: %r", chunk[:30])
            self.pipe_queue.put(chunk)
        self.buffer.append(chunk)

            
    def read(self):
        # if we're PY3, we're reading bytes, otherwise we're reading
        # str
        try: chunk = os.read(self.stream, self.bufsize)
        except OSError as e:
            if logging_enabled: self.log.debug("got errno %d, done reading", e.errno)
            return True
        if not chunk:
            if logging_enabled: self.log.debug("got no chunk, done reading")
            return True
                
        if logging_enabled: self.log.debug("got chunk size %d: %r", len(chunk), chunk[:30])
        for chunk in self.stream_bufferer.process(chunk):
            self.write_chunk(chunk)   
    



# this is used for feeding in chunks of stdout/stderr, and breaking it up into
# chunks that will actually be put into the internal buffers.  for example, if
# you have two processes, one being piped to the other, and you want that,
# first process to feed lines of data (instead of the chunks however they
# come in), OProc will use an instance of this class to chop up the data and
# feed it as lines to be sent down the pipe
class StreamBufferer(object):
    def __init__(self, encoding="utf8", buffer_type=1):
        # 0 for unbuffered, 1 for line, everything else for that amount
        self.type = buffer_type
        self.buffer = []
        self.n_buffer_count = 0
        self.encoding = encoding
        
        # this is for if we change buffering types.  if we change from line
        # buffered to unbuffered, its very possible that our self.buffer list
        # has data that was being saved up (while we searched for a newline).
        # we need to use that up, so we don't lose it
        self._use_up_buffer_first = False
        
        # the buffering lock is used because we might chance the buffering
        # types from a different thread.  for example, if we have a stdout
        # callback, we might use it to change the way stdin buffers.  so we
        # lock
        self._buffering_lock = threading.RLock()
        self.log = logging.getLogger("stream_bufferer")
        
        
    def change_buffering(self, new_type):
        # TODO, when we stop supporting 2.6, make this a with context
        if logging_enabled: self.log.debug("acquiring buffering lock for changing buffering")
        self._buffering_lock.acquire()
        if logging_enabled: self.log.debug("got buffering lock for changing buffering")
        try:                
            if new_type == 0: self._use_up_buffer_first = True
                
            self.type = new_type
        finally:
            self._buffering_lock.release()
            if logging_enabled: self.log.debug("released buffering lock for changing buffering")
            
        
    def process(self, chunk):
        # MAKE SURE THAT THE INPUT IS PY3 BYTES
        # THE OUTPUT IS ALWAYS PY3 BYTES
        
        # TODO, when we stop supporting 2.6, make this a with context
        if logging_enabled: self.log.debug("acquiring buffering lock to process chunk (buffering: %d)", self.type)
        self._buffering_lock.acquire()
        if logging_enabled: self.log.debug("got buffering lock to process chunk (buffering: %d)", self.type)
        try:
            # we've encountered binary, permanently switch to N size buffering
            # since matching on newline doesn't make sense anymore
            if self.type == 1:
                try: chunk.decode(self.encoding)
                except:
                    if logging_enabled: self.log.debug("detected binary data, changing buffering")
                    self.change_buffering(1024)
                
            # unbuffered
            if self.type == 0:
                if self._use_up_buffer_first:
                    self._use_up_buffer_first = False
                    to_write = self.buffer
                    self.buffer = []
                    to_write.append(chunk)
                    return to_write
                
                return [chunk]
            
            # line buffered
            elif self.type == 1:
                total_to_write = []
                chunk = chunk.decode(self.encoding)
                while True:
                    newline = chunk.find("\n")
                    if newline == -1: break
                    
                    chunk_to_write = chunk[:newline+1]
                    if self.buffer:
                        # this is ugly, but it's designed to take the existing
                        # bytes buffer, join it together, tack on our latest
                        # chunk, then convert the whole thing to a string.
                        # it's necessary, i'm sure.  read the whole block to
                        # see why.
                        chunk_to_write = "".encode(self.encoding).join(self.buffer) \
                            + chunk_to_write.encode(self.encoding)
                        chunk_to_write = chunk_to_write.decode(self.encoding)
                        
                        self.buffer = []
                        self.n_buffer_count = 0
                    
                    chunk = chunk[newline+1:]
                    total_to_write.append(chunk_to_write.encode(self.encoding))
                         
                if chunk:
                    self.buffer.append(chunk.encode(self.encoding))
                    self.n_buffer_count += len(chunk)
                return total_to_write
              
            # N size buffered  
            else:
                total_to_write = []
                while True:
                    overage = self.n_buffer_count + len(chunk) - self.type
                    if overage >= 0:
                        ret = "".encode(self.encoding).join(self.buffer) + chunk
                        chunk_to_write = ret[:self.type]
                        chunk = ret[self.type:]
                        total_to_write.append(chunk_to_write)
                        self.buffer = []
                        self.n_buffer_count = 0
                    else:
                        self.buffer.append(chunk)
                        self.n_buffer_count += len(chunk)
                        break
                return total_to_write
        finally:
            self._buffering_lock.release()
            if logging_enabled: self.log.debug("released buffering lock for processing chunk (buffering: %d)", self.type)
            

    def flush(self):
        if logging_enabled: self.log.debug("acquiring buffering lock for flushing buffer")
        self._buffering_lock.acquire()
        if logging_enabled: self.log.debug("got buffering lock for flushing buffer")
        try:
            ret = "".encode(self.encoding).join(self.buffer)
            self.buffer = []
            return ret
        finally:
            self._buffering_lock.release()
            if logging_enabled: self.log.debug("released buffering lock for flushing buffer")
    




# this allows lookups to names that aren't found in the global scope to be
# searched for as a program name.  for example, if "ls" isn't found in this
# module's scope, we consider it a system program and try to find it.
class Environment(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        
        self["Command"] = Command
        self["CommandNotFound"] = CommandNotFound
        self["ErrorReturnCode"] = ErrorReturnCode
        self["ARGV"] = sys.argv[1:]
        for i, arg in enumerate(sys.argv):
            self["ARG%d" % i] = arg
        
        # this needs to be last
        self["env"] = os.environ
        
    def __setitem__(self, k, v):
        # are we altering an environment variable?
        if "env" in self and k in self["env"]: self["env"][k] = v
        # no?  just setting a regular name
        else: dict.__setitem__(self, k, v)
        
    def __missing__(self, k):
        # the only way we'd get to here is if we've tried to
        # import * from a repl.  so, raise an exception, since
        # that's really the only sensible thing to do
        if k == "__all__":
            raise ImportError("Cannot import * from sh. \
Please import sh or import programs individually.")

        # if we end with "_" just go ahead and skip searching
        # our namespace for python stuff.  this was mainly for the
        # command "id", which is a popular program for finding
        # if a user exists, but also a python function for getting
        # the address of an object.  so can call the python
        # version by "id" and the program version with "id_"
        if not k.endswith("_"):
            # check if we're naming a dynamically generated ReturnCode exception
            try: return rc_exc_cache[k]
            except KeyError:
                m = rc_exc_regex.match(k)
                if m: return get_rc_exc(int(m.group(1)))
                
            # are we naming a commandline argument?
            if k.startswith("ARG"):
                return None
                
            # is it a builtin?
            try: return getattr(self["__builtins__"], k)
            except AttributeError: pass
        elif not k.startswith("_"): k = k.rstrip("_")
        
        # how about an environment variable?
        try: return os.environ[k]
        except KeyError: pass
        
        # is it a custom builtin?
        builtin = getattr(self, "b_"+k, None)
        if builtin: return builtin
        
        # it must be a command then
        return Command._create(k)
    
    
    # methods that begin with "b_" are custom builtins and will override any
    # program that exists in our path.  this is useful for things like
    # common shell builtins that people are used to, but which aren't actually
    # full-fledged system binaries
    
    def b_cd(self, path):
        os.chdir(path)
        
    def b_which(self, program):
        return which(program)




def run_repl(env):
    banner = "\n>> sh v{version}\n>> https://github.com/amoffat/sh\n"
    
    print(banner.format(version=__version__))
    while True:
        try: line = raw_input("sh> ")
        except (ValueError, EOFError): break
            
        try: exec(compile(line, "<dummy>", "single"), env, env)
        except SystemExit: break
        except: print(traceback.format_exc())

    # cleans up our last line
    print("")




# this is a thin wrapper around THIS module (we patch sys.modules[__name__]).
# this is in the case that the user does a "from sh import whatever"
# in other words, they only want to import certain programs, not the whole
# system PATH worth of commands.  in this case, we just proxy the
# import lookup to our Environment class
class SelfWrapper(ModuleType):
    def __init__(self, self_module):
        # this is super ugly to have to copy attributes like this,
        # but it seems to be the only way to make reload() behave
        # nicely.  if i make these attributes dynamic lookups in
        # __getattr__, reload sometimes chokes in weird ways...
        for attr in ["__builtins__", "__doc__", "__name__", "__package__"]:
            setattr(self, attr, getattr(self_module, attr))

        self.self_module = self_module
        self.env = Environment(globals())
    
    def __getattr__(self, name):
        return self.env[name]





# we're being run as a stand-alone script
if __name__ == "__main__":
    try: arg = sys.argv.pop(1)
    except: arg = None

    if arg == "test":
        import subprocess

        def run_test(version):
            py_version = "python%s" % version
            py_bin = which(py_version)

            if py_bin:
                print("Testing %s" % py_version.capitalize())
                
                p = subprocess.Popen([py_bin, os.path.join(THIS_DIR, "test.py")]
                    + sys.argv[1:])
                p.wait()
            else:
                print("Couldn't find %s, skipping" % py_version.capitalize())

        versions = ("2.6", "2.7", "3.1", "3.2")
        for version in versions: run_test(version)

    else:
        globs = globals()
        f_globals = {}
        for k in ["__builtins__", "__doc__", "__name__", "__package__"]:
            f_globals[k] = globs[k]
        env = Environment(f_globals)
        run_repl(env)
    
# we're being imported from somewhere
else:
    self = sys.modules[__name__]
    sys.modules[__name__] = SelfWrapper(self)
