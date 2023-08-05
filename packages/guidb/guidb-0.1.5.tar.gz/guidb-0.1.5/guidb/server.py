import zmq
import leveldb
from query_pb2 import Query,Response

class Server(object):
    """
    Data server for my implementation of a parallel scalable key value
    database.

    The server is very simple. It listens to google buffer protocol
    messages on a zeromq socket. The messages are specified in the
    *.proto files in this folder.

    It uses google's leveldb for persistent storage, with the
    pyleveldb. The messaging platform is zeromq.

    With these simple pieces and a little knowledge of parallel
    scalable systems we can build an embedded scalable database that
    can be accessed for an arbitrary amount of connections at the same
    time.
    """
    def __init__(self,
                 url_recv='tcp://127.0.0.1:10001',
                 url_send='tcp://127.0.0.1:10002',
                 rank = 1,
                 datafile='./datastore.db'):
        """
        Creates a server instance.

        The server listens to two different sockets, one (recv) to
        recieve queries and a second one (send) to send the status and
        query results. Every server must have a unique rank, it
        doesn't have to be ordered or contiguous, it only has to be
        unique.

        Finaly, it needs a name of the folder where leveldb will store
        its things.
        """
        self.db = leveldb.LevelDB(datafile)
        self.context  = zmq.Context()
        self.sender   = self.context.socket(zmq.PUSH)
        self.sender.bind(url_send)
        self.recver   = self.context.socket(zmq.PULL)
        self.recver.bind(url_recv)
        self.mainloop = True
        self.rank = rank

    def ping_handler(self,tag):
        """
        Returns an empty message. It is only a prototype now
        """
        response = Response()
        response.rank = self.rank
        response.tag = tag
        print "LOG: got a ping"
        return response

    def query_handler(self,query):
        """
        Function that takes care of the queries and gives the required
        response to them. It can also return a status message when the
        method is *status*
        """
        #Get rid of this conditional when status is fully implemented
        if query.method == 'ping':
            response = self.ping_handler(query.tag)
        
        else:
            response = Response()
            response.tag = query.tag
            response.rank = self.rank
            if query.method == 'get':
                try:
                    data = self.db.Get(query.key)
                    response.data = data
                    
                except KeyError:
                    response.data = ''

            if query.method == 'put':
                self.db.Put(query.key,query.data)
                response.data = 'success'

            if query.method == 'delete':
                try:
                    self.db.Delete(query.key)
                    response.data = 'success'
                except KeyError:
                    response.data = ''

            if query.method == 'keys':
                #Fix some leveldb strange behavior
                try:
                    if query.key_from and query.key_to:
                        iterkeys = self.db.RangeIter(include_value=False,
                                                     key_from = query.key_from,
                                                     key_to = query.key_to)
                    elif query.key_from:
                        iterkeys = self.db.RangeIter(key_from = query.key_from,
                                                     include_value=False)
                    elif query.key_to:
                        iterkeys = self.db.RangeIter(key_to = query.key_to,
                                                     include_value=False)
                    else:
                        iterkeys = self.db.RangeIter(include_value=False)
                    
                    response.data = ' '.join([k for k in iterkeys])
                
                except KeyError:
                    print 'LOG: keys method failed in the server'
                    response.data = ''

        return response


    def run(self):
        """
        This function makes the server run.
        """
        while(self.mainloop):
            query = Query()
            query.ParseFromString(self.recver.recv())
            response = self.query_handler(query)
            self.sender.send(response.SerializeToString())


    def close(self):
        del self.db
        self.context.destroy()


