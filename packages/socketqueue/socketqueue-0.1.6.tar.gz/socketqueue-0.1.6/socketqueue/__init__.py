
"""
  socket queue module
  author: Marcelo Aires Caetano
  date: 01 fev 2012, 27 apr 2012
  email: marcelo@fiveti.com
 
  this module is used to add a queue for event in io,
  using epoll on linux, kqueue on bsd and darwin, e poll/select on windows
  selecting automatically the best method for used platform
"""




import select
import socket as _socket
import logging

logger = logging.getLogger(__name__)

AUTO, SELECT, POLL, EPOLL, KQUEUE = xrange(5)
IN, PRI,  OUT, ERR, HUP = (1 << i for i in xrange(5))
try:
  ET = select.EPOLLET
except:
  ET = -1
KQ_FILTER_READ = -1
KQ_FILTER_WRITE = -2

SUCCESS = 0
EOF = ~0


class SocketQueue(object):
    
    def _auto_select_mode(self):
        try:
            select.epoll
            self.engine = _SocketQueueEPoll
            logger.debug("using epoll")
            return EPOLL
        except:
            logger.debug("not epoll available")
        
        try:
            select.kqueue
            self.engine = _SocketQueueKQueue
            logger.debug("using kqueue")
            return KQUEUE
        except:
            logger.debug("kqueue is not available")
        
        try:
            select.poll
            self.engine = _SocketQueuePoll
            logger.debug("using poll")
            return POLL
        except:
            logger.debug("not poll available")
        
        logger.debug("using select")
        self.engine = _SocketQueueSelect
        return SELECT
    
    def __init__(self, method=AUTO):
        self.queue = [];
        
        if method == AUTO:
            method = self._auto_select_mode()
        elif method == KQUEUE:
            method = self._auto_select_mode()
        elif method == EPOLL:
            method = self._auto_select_mode()
        
        elif method == POLL:
            try:
                select.poll
                self.engine = _SocketQueuePoll
            except:
                method = self._auto_select_mode()
                
        elif method == SELECT:
            self.engine = _SocketQueueSelect
            
        self.runtime = self.engine()
        
    def register(self, socket, mode=IN):
        return self.runtime.register(socket, mode)
        
    
    def unregister(self, socket):
        #print "unregistering socket", socket
        return self.runtime.unregister(socket)
    
    def poll(self, timeout=-1, ignore=[], maxevents=-1, notypes=False):
        return self.runtime.poll(timeout, ignore, maxevents, notypes)
    
    
    
class _SocketQueuePoll(object):
    
    def __init__(self):
        self._sockets = {}
        self._revsockets = {}
        self._poll = select.poll()
        

    def register(self, socket, mode=IN):
        try:
            if hasattr(socket, "fileno"): 
                self._sockets[socket.fileno()] = socket
                self._revsockets[socket] = socket.fileno()
                self._poll.register(socket, mode)
                #print self._sockets
                #print self._revsockets
            else:
                print "registering a fd"
                fd = socket
                self._sockets[fd] = fd
                self._revsockets[fd] = fd
            return SUCCESS
        except:
            return EOF
        
    
    def unregister(self, socket):
        try:
            self._poll.unregister(socket)
            fileno = self._revsockets[socket]
            del self._revsockets[socket]
            del self._sockets[fileno]
            #print self._sockets
            #print self._revsockets
            return SUCCESS
        except:
            return EOF  
        
    def poll(self, timeout=-1, ignore=[], maxevents=-1, notypes=False):
        evts = self._poll.poll(timeout)
        if maxevents != -1:
            evts = evts[:maxevents]

        if notypes:
            if ignore:
                _ignore = []
                for i in ignore:
                    try:
                        ign = self._revsockets[i] 
                    except:
                        ign = -1
                    _ignore.append(i)
                ignore = _ignore
                evts = [self._sockets[i] for i, j in evts if not i in ignore]
            else:
                evts = [self._sockets[i] for i, j in evts]
                
            return evts
            
            
        if ignore:
            _ingnore = []
            for i in ignore:
                try:
                    ign = self._revsockets[i]
                except: 
                    ign = -1
                _ignore.append(ign)
            ignore = _ignore 
            evts = [(self._sockets[i],j) for i, j in evts if not i in ignore]
        else:
            evts = [(self._sockets[i],j) for i, j in evts]
            
        return evts


class _SocketQueueEPoll(_SocketQueuePoll):
    
    def __init__(self):
        self._sockets = {}
        self._revsockets = {}
        self._poll = select.epoll()
    
    def poll(self, timeout=-1, ignore=[], maxevents=-1, notypes=False):
        evts = self._poll.poll(timeout, maxevents)
        
        if notypes:
            if ignore:
                _ignore = []
                for i in ignore:
                    try:
                        ign = self._revsockets[i] 
                    except:
                        ign = -1
                    _ignore.append(ign)
                ignore = _ignore
                evts = [self._sockets[i] for i, j in evts if not i in ignore]
            else:
                evts = [self._sockets[i] for i, j in evts]
                
            return evts
        
        if ignore:
            _ignore = []
            for i in ignore:
                try:
                    ign = self._revsockets[i]
                except: 
                    ign = -1
                _ignore.append(ign)
            ignore = _ignore
            evts = [(self._sockets[i],j) for i, j in evts if not i in ignore]
        else:
            evts = [(self._sockets[i],j) for i, j in evts]
        return evts
        
class _SocketQueueKQueue(object):
    type_translation = {IN: KQ_FILTER_READ, OUT: KQ_FILTER_WRITE}
    def __init__(self):
        self._kqueue_events = []
        self.kqueue = select.kqueue()
        self.sockets = {}
        self.rev_sockets = {}
        
    def register(self, socket, mode=IN):
        r = EOF 
        fileno = socket.fileno()
   
        if mode & IN:
            ke = select.kevent(socket, select.KQ_FILTER_READ)
            if not ke in self._kqueue_events:
                self._kqueue_events.append(ke)
            self.sockets[socket.fileno()] = socket 
            self.rev_sockets[socket] = fileno
            
            r = SUCCESS
            
        if mode & OUT:
            ke = select.kevent(socket, select.KQ_FILTER_WRITE)
            if not ke in self._kqueue_events:
                self._kqueue_events.append(ke)
            self.sockets[socket.fileno()] = socket 
            self.rev_sockets[socket] = socket.fileno()
            r = SUCCESS
            
        if mode & ERR and not socket in self._select_err:
            print "ERR is not available on kqueue"
        return r 
            
            
    def unregister(self, socket):
        #print "unregistering", socket
        fileno = self.rev_sockets[socket]
        sockets = [i for i  in self._kqueue_events if i.ident == fileno]
        for ke in sockets:
            while i in self._kqueue_events:
                del self._kqueue_events[self._kqueue_events.index(ke)]
        fileno = self.rev_sockets[socket]
        del self.rev_sockets[socket]
        del self.sockets[fileno]
            
    def poll(self, timeout=-1, ignore=[], maxevents=-1, notypes=False):
        
        if maxevents == -1:
            maxevents = len(self._kqueue_events)
        if timeout == -1:
            timeout=None
        
           
        evs = self.kqueue.control(self._kqueue_events, maxevents, timeout)
        
        out1 = []            
        if ignore:
            ign_ids = []
            for i in ignore:
                ign_ids.append(self.rev_sockets[i])
            for  i in evs:
                if not i.ident in ign_ids:
                    out1.append(i)
            evs = out1
            del out1 

        if notypes:
            return [self.sockets[i.ident] for i in evs]
        
        return [(self.sockets[i.ident], self.type_translation[self.filter]) for i in evs]
   
    
class _SocketQueueSelect(object):
    
    def __init__(self):
        self._select_in = []
        self._select_out = []
        self._select_err = []
        
    def register(self, socket, mode=IN):
        r = EOF 
        if mode & IN and not socket in self._select_in:
            self._select_in.append(socket)
            r = SUCCESS
            
        if mode & OUT and not socket in self._select_out:
            self._select_out.append(socket)
            r = SUCCESS
            
        if mode & ERR and not socket in self._select_err:
            self._select_err.append(socket)
            r = SUCCESS
        
        return EOF
            
            
    def unregister(self, socket):
        #print "unregistering", socket
        if socket in self._select_in:
            self._select_in.remove(socket)
        
        if socket in self._select_out:
            self._select_out.remove(socket)
            
        if socket in self._select_err:
            self._select_err.remove(socket)
            
    def poll(self, timeout=-1, ignore=[], maxevents=-1, notypes=False):
        if timeout == -1:
            s_in, s_out, s_err = select.select(self._select_in, self._select_out, self._select_err)
        else:
            s_in, s_out, s_err = select.select(self._select_in, self._select_out, self._select_err, timeout)
            
            
        if maxevents != -1:
            s_in = s_in[:maxevents]
            s_out = s_out[:maxevents]
            s_err = s_err[:maxevents]
            
        if ignore:
            s_in = [i for i in s_in if not i  in ignore]
            s_out = [i for i in s_out if not i in ignore]
            s_err = [i for i in s_err if not i in ignore]

        out = []     
        if notypes:
            return s_in + s_out + s_err
        
        for i in s_in:
            out.append((i,IN))
        
        for i in s_out:
            out.append((i, OUT))
            
        for i in s_err:
            out.append((i, ERR))
            
        if maxevents != -1:
            return out[:maxevents]
        
        return out 
