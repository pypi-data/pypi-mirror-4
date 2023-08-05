
"""A remote procedure call system on top of pushkey

Makes it easy to expose functions over the pushkey protocol. The
remote functions cannot return anything to the client, but exceptions
thrown while executing will be passed back as a string to the client.

The functions must have a signature of the form::

  def f(repo, ...)

Decorate it with the ``command`` decorator from this module to turn it
into a remote function::

  @pushkeyrpc.command
  def f(repo, ...)

The wrapper injects a ``ui`` argument infront of the other arguments
on the client side. Clients will thus call the remote function as::

  f(ui, remote, ...)

Call ``init`` to make the necessary pushkey registrations.
"""

# The pushkey namespaces are named 'lock-cmd' and 'locks-err-%s' to
# maintain compatibility with version 0.3.

import os, random

from mercurial import pushkey, encoding

from unrepr import unrepr

def init():
    pushkey.register('locks-cmd', dispatchcmd, nulllist)

commands = {}

def command(func):
    cmd = func.__name__
    commands[cmd] = func

    def wrapper(ui, remote, *args):
        ui.debug("pushkeyrpc: sending %s%r\n" % (cmd, args))
        arg = repr(args)
        errid = hex(random.getrandbits(80))[2:-1]
        if remote.pushkey('locks-cmd', cmd, arg, errid):
            return None
        else:
            err = remote.listkeys('locks-err-%s' % errid)
            msg = err.get('msg', '')
            return encoding.tolocal(msg.decode('string-escape'))

    return wrapper

def nullpush(repo, key, old, new):
    return False

def nulllist(repo):
    return {}

def registercallbacks(repo):
    if not os.path.isdir(repo.join('pushkeyrpc-errs')):
        return
    for errid in os.listdir(repo.join('pushkeyrpc-errs')):
        registercallback(errid)

def registermsg(repo, errid, errmsg):
    fp = repo.opener('pushkeyrpc-errs/%s' % errid, 'w')
    fp.write(errmsg)
    fp.close()
    registercallback(errid)

def registercallback(errid):
    namespace = 'locks-err-%s' % errid

    def listfunc(repo):
        del pushkey._namespaces[namespace]
        fp = repo.opener('pushkeyrpc-errs/%s' % errid)
        errmsg = fp.read()
        fp.close()
        os.unlink(fp.name)
        return dict(msg=errmsg.encode('string-escape'))

    pushkey.register(namespace, nullpush, listfunc)

def dispatchcmd(repo, cmd, arg, errid):
    try:
        args = unrepr(arg)
    except ValueError, e:
        registermsg(repo, errid, 'could not decode argument: %s' % e)
        return False
    except UnicodeEncodeError, e:
        registermsg(repo, errid, 'args: %r' % args)
        return False

    func = commands.get(cmd)
    if func:
        try:
            func(repo, *args)
            return True
        except Exception, e:
            registermsg(repo, errid, str(e)) # + '\n' + traceback.format_exc())
    else:
        registermsg(repo, errid, 'unknown cmd: %s' % cmd)
    return False
