from Acquisition import aq_inner
from zope.interface import implements
from Products.cron4plone.interfaces import ICronTickView
from Products.cron4plone.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
#from plone.memoize import view
import time
#import random
import logging
from threading import Lock
from ZODB.POSException import ConflictError

logger = logging.getLogger(PROJECTNAME)
_mutex=Lock()

try:
    from unimr.memcachedlock.memcachedlock import DontLock, lock_getter
    import atexit
    _acquired_lock = None

    def cleanup_lock_at_program_exit():
        try:
            if _acquired_lock:
                _acquired_lock.release()
        except:
            pass

    MEMCACHED=True
except:
    MEMCACHED=False


# define an invariant unique key of an instance
def get_key(*args, **kargs):
    instance = args[0].context
    return '/'.join(instance.getPhysicalPath())+'-cron4plone-memcached-key'


class CronTick(BrowserView):
    implements(ICronTickView)

    if MEMCACHED:

        def locked(get_key, timeout=30, intervall=0.05):

            def decorator(fun):

                def replacement(*args, **kwargs):
                    try:
                        key = get_key(*args, **kwargs)
                    except DontLock:
                        return fun(*args, **kwargs)

                    key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)

                    global _acquired_lock
                    lock = lock_getter(key, timeout, intervall)

                    reserved = False
                    acquired_lock = False
                    try:

                        acquired_lock = lock.acquire(blocking=0)
                        if not acquired_lock:
                            logger.warning('could not acquire lock')
                            return None
                        else:
                            _acquired_lock = lock
                        try:
                            result = fun(*args, **kwargs)
                        except ConflictError, msg:
                            reserved = lock.acquire(blocking=0, timeout=1)

                            if reserved:
                                logger.warning('ConflictError, lock reserved (1s) for retry')

                            raise ConflictError, msg

                    finally:
                        # only release if not raised a ConflictError
                        if acquired_lock and not reserved:
                            lock.release()

                    return result

                return replacement
            return decorator

        atexit.register(cleanup_lock_at_program_exit)

    if not MEMCACHED:

        # decorator to only allow one thread to run the decorated method
        def locked(*unused, **kw_unused):

            def decorator(fn):

                def wrapper(*args, **kwargs):
                    lock = _mutex.acquire(False) # non-blocking lock
                    if not lock:
                        return # already running..
                    try:
                        return fn(*args)
                    finally:
                        _mutex.release()
                return wrapper
            return decorator

    @locked(get_key, timeout=86400)
    def tick(self):
        logger.debug("CronTick %s" % time.ctime())
        context = aq_inner(self.context)
        crontool = getToolByName(context, 'CronTool')
        result = crontool.run_tasks(context)
        return result
