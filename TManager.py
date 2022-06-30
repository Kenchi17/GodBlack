import asyncio
import threading
from utils import createID


class StoppableThread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class HandleThread(object):
    def __init__(self,targetfunc=None,args=(),update=None):
        self.id = createID(12)
        self.args = args
        self.handle = targetfunc
        self.update = update
        self.tstore = {}
        pass
    async def start(self,loop):
        if self.handle:
                asyncio.ensure_future(self.handle(self.args))

    def start_normal(self,loop):
        if self.handle:
                asyncio.ensure_future(self.handle(self.args))

    def stop(self):
        if self.handle:
            self.handle.join()
        pass
    def store(self,name,obj):
        self.tstore[name] = obj
    def getStore(self,name):
        try:
            return self.tstore[name]
        except:pass
        return None

class ThreadManager(object):

    def __init__(self,loop=None):
        self.threads = {}
        self.this_thread = None
        self.max_runing_threads = 3
        self.loop = loop
        pass

    async def wait_for_free(self):
        while len(self.threads) >= self.max_runing_threads:
            pass

    async def start(self,targetfunc=None,args=(),update=None):
        self.this_thread = HandleThread(targetfunc=targetfunc, args=args, update=update)
        self.threads[self.this_thread.id] = self.this_thread
        await self.this_thread.start(self.loop)
        pass

    def start_normal(self,targetfunc=None,args=(),update=None):
        self.this_thread = HandleThread(targetfunc=targetfunc, args=args, update=update)
        self.threads[self.this_thread.id] = self.this_thread
        self.this_thread.start_normal(self.loop)
        pass

    async def get(self,id=''):
        for t in self.threads:
            if t.id==id:
                return t
        return None

    async def dispose(self,id=''):
        if self.threads[id]:
            del self.threads[id]
