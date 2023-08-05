from subprocess import Popen
from Queue import Queue, Empty
import string
import threading
import functools

import weakref
import itertools
from dvipy.read import read_pre, read_bop, read_eop, DviState
from dvipy.render import DviSlave

import logging
logger = logging.getLogger(__name__)

#import parse_tex_out as pto
import time
import subprocess as sp
import os

def repeat_func(f, *args):
    """Repeatedly apply a function, returning an iterator of the results"""
    return itertools.starmap(f, itertools.repeat(args))


# Thread functions
# write_tex is the writer,

# Really big TODO...
# Handle errors gracefully. Convert to python exceptions? 

def write_tex(filename, in_queue, debug=logger.debug, Queue=Queue):
    """Open filename for writing and read stuff from in_queue"""

    with open(filename, 'w', buffering=1) as f:
        debug('Opened %s for writing' % filename)

        while True:
            x = in_queue.get()

            if x:
                debug('Writing')
                print >>f, x
                in_queue.task_done()
            else:
                in_queue.task_done()
                break

    debug('Terminate writer')


# Read the dvi file
def read_dvi(filename, out_queue, order_queue, debug=logging.debug):
    # Magic happens here
    #print "opening..."
    with open(filename, 'rb') as f:
        debug('Opened %s for reading' % filename)
        state = DviState()
        slave = DviSlave()
        state.set_callbacks(**slave.callbacks)

        try:
            s = itertools.imap(ord, repeat_func(f.read, 1))
        except:
            return

        # Let's read the preamble
        read_pre(s, state)
        debug("Read preamble")

        while True:
            # Let's wait...
            if not order_queue.get():
                break

            read_bop(s, state)
            read_eop(s, state)

            out_queue.put(slave.clear_page())
            order_queue.task_done()
            debug("Read page")

        order_queue.task_done()
        debug('Terminate reader')

#def inspect_tex_out(stdout, status_queue):
#    stream = pto.stream_read(stdout)
#    first = True
#    while True:
#        print 'Finding page'
#        pto.read_page_open(stream, first)
#        print 'Reading page'
#        print pto.read_page(stream)
#        first = False

def unlink_silent(filenames, unlink=os.unlink):
    for filename in filenames:
        try:
            unlink(filename)
        except OSError:
            pass

def mkfifos(*filenames):
    """Make fifos of the given filenames. If any fail, clean up the created ones
    and throw an exception"""
    created = []
    try:
        for filename in filenames:
            os.mkfifo(filename)
            created.append(filename)
    except OSError as e:
        for f in created:
            os.unlink(f)
        raise

class TexRunner(object):
    def __init__(self):

        tex_file = 'test.tex'
        dvi_file = 'test.dvi'
        aux_file = 'test.aux'
        log_file = 'test.log'

        # How to clean these up
        cleanup_files = functools.partial(
            unlink_silent, (tex_file, dvi_file, aux_file, log_file))

        cleanup_files()
        tex_write_queue = Queue()
        dvi_read_queue = Queue()
        tex_status_queue = Queue()
        order_queue = Queue()

        devnull = open('/dev/null', 'w')

        writer_t = threading.Thread(
            target=write_tex, args=(tex_file, tex_write_queue))
        reader_t = threading.Thread(
            target=read_dvi, args=(dvi_file, dvi_read_queue, order_queue))
        reader_t.daemon = True
        writer_t.daemon = True

        # This can safely fail, as there's no threads up yet
        mkfifos(tex_file, dvi_file)

        try:
            # If process creation does fail, then we have fun
            process = sp.Popen(["latex", "-interaction=nonstopmode", "-ipc", tex_file],
                               stdin=sp.PIPE,
                               stdout=devnull
                              )

            # We can now fail her
            with open(tex_file, 'w', buffering=1) as f:
                print >>f

        
            # Unfortunately this is actually necessary for cleanup. Not a huge fan
            # of such a long declaration, but rest assured it's not for performance
            # reasons -- we need to guarantee that the objects don't get garbage
            # collected before the class, and things do break without this.
            def callback(_, wq=tex_write_queue, oq=order_queue,
                         process=process, sleep=time.sleep,
                         cleanup_files=cleanup_files,
                         debug=logger.debug, sp=sp): #, sk=sp.SIGKILL):

                debug('Cleaning!!!')

                try:
                    wq.put('\end{document}')
                    # Give latex time to die
                    wq.join()

                    # Kindness is a virtue
                    process.terminate()

                    process.wait()

                    # Now let's kill our threads off properly
                    wq.put(None)
                    oq.put(None)
                    wq.join()

                # This is by far the most important thing, next to leaving latex
                # processes lying around...
                finally:
                    cleanup_files()

            self.ref = weakref.ref(self, callback)

        except:
            try:
                process.kill()
            except NameError:
                pass

            cleanup_files()
            raise

        reader_t.start()
        writer_t.start()

        self._process = process

        self._write_queue = tex_write_queue

        self._read_queue = dvi_read_queue
        self._order_queue = order_queue

        tex_write_queue.put(
r"""
\documentclass[12pt]{article}
\usepackage[active]{preview}
\begin{document}
""")


    def page(self, tex, Empty=Empty, sleep=time.sleep):
        rq = self._read_queue
        self._write_queue.put("\\begin{preview}\n  %s\n\end{preview}\n" % tex)
        self._order_queue.put(True)
        # One may indeed question, "why not just use Queue.get(timeout=1.0)".
        # Well, it is quite tragic really: it breaks ctrl+c almost as bad as
        # get() itself
        for i in xrange(2000):
            # This seems to be optimal *on my system*. YMWV.
            sleep(0.0005)
            try:
                return rq.get_nowait()
            except Empty:
                pass

        raise RuntimeError('Tex is not responding...')
