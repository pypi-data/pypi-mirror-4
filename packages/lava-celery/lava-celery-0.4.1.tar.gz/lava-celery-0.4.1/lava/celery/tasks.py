"""
lava.celery.tasks
=================

Task definitions imported by celeryd when configured to use lava.celery.config
"""

import os
import select
import sys
import traceback

from celery.messaging import establish_connection
from celery.task import task
from kombu.compat import Publisher

from lava.celery.queues import StreamExchange


__all__ = ["run_command"]

def _rw(readset, fd, publisher, stream):
    data = os.read(fd.fileno(), 1024)
    if data == "":
        fd.close()
        readset.remove(fd)
    else:
        try:
            data = data.decode('utf-8', errors='ignore')
            if len(data) > 0:
                publisher.send({stream: data})
        except:
            traceback.print_exc()
            print "error sending bytes:",data

def _exec_command(publisher, args, arg0):
    """
    A traditional fork/exec style action that prints stdout/stderr to the
    publisher
    """
    (out_read, out_write) = os.pipe()
    (err_read, err_write) = os.pipe()

    pid = os.fork()
    if pid == 0:
        try:
            os.close(out_read)
            os.close(err_read)

            os.dup2(out_write, 1)
            os.dup2(err_write, 2)
            args.insert(0, arg0)
            os.execvp(args[0], args)
            print >>sys.stderr, "lava celeryd error executing ",args
        except:
            traceback.print_exc()
        finally:
            os._exit(1)

    try:
        os.close(out_write)
        os.close(err_write)
        out_read = os.fdopen(out_read)
        err_read = os.fdopen(err_read)

        readset = [out_read, err_read]
        while readset:
            rlist, wlist, xlist = select.select(readset, [], [])
            if out_read in rlist:
                _rw(readset, out_read, publisher, 'stdout')
            if err_read in rlist:
                _rw(readset, err_read, publisher, 'stderr')
    except:
        traceback.print_exc()
    finally:
        (pid, retval) = os.waitpid(pid,0)
    publisher.send({'done': retval})

def _copy_files(files):
    """
    run command can take a dictionary of filname->content pairs that
    the remote side of the command needs
    """
    if files is None:
        return []
    deletes = []
    for k,v in files.items():
        # if path exists, let's assume the celery worker and lava scheduler
        # running on the same local system, so we don't need to create the file
        if not os.path.exists(k):
            with open(k, 'w') as f:
                f.write(v)
                deletes.insert(0, k)
    return deletes

@task(acks_late=True, ignore_result=True)
def run_command(queue_name, args, arg0="lava", files=None):
    """
    Run a lava-tool command with the specified arguments
    """
    print "command received:", args
    connection = establish_connection()
    channel = connection.channel()
    publisher = Publisher(
        connection=channel,
        exchange=StreamExchange,
        routing_key=queue_name,
        exchange_type="direct")

    try:
        files = _copy_files(files)
        _exec_command(publisher, args, arg0)
    except:
        traceback.print_exc()
    finally:
        publisher.close()
        connection.close()

        for f in files:
            os.unlink(f)

    print "command complete for:",args
