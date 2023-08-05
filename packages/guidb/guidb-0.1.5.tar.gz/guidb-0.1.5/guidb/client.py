import zmq
import struct
from random import randint,choice
from query_pb2 import Query,Response

class Client(object):
    """
    Stupid client that now is used only to test how the database works
    """
    def __init__(self,servers):
        """
        The server needs only a list of servers to run.

        servers is a list of tuples (PUSH TO, PULL FROM)
        """
        #Sockets for all the PUSH servers
        self.push = list()
        #Sockest for all the PULL servers
        self.pull = list()
        #Server statuses go here.
        self.status = list()

        self.context = zmq.Context()
        for server in servers:
            self.push.append(self.context.socket(zmq.PUSH))
            self.pull.append(self.context.socket(zmq.PULL))
            self.push[-1].connect(server[0])
            self.pull[-1].connect(server[1])


        # The tag is just a random number not to get confused
        tag = randint(1,1000000)

        #Query the status of the given servers.
        for server in self.push:
            query = Query()
            query.method='ping'
            query.tag = tag
            server.send(query.SerializeToString())

        for server in self.pull:
            ping = Response()            
            ping.ParseFromString(server.recv())
            # if ping.tag == tag:
            #     print 'DEBUG: Server {} OK'.format(ping.rank)


    def server_status(self):
        pass


    def delete(self,key):
        tag = randint(1,100000)

        query = Query()
        query.method = 'delete'
        query.tag = tag
        query.key = key

        for push,pull in zip(self.push,self.pull):
            push.send(query.SerializeToString())
            response = Response()
            response.ParseFromString(pull.recv())
            # if response.data and response.tag == tag:
            #     print "LOG: Key {} successfully deleted".format(key)

    def put(self,key,data):
        """
        Put to the server cluster. It picks one random server and
        sends a put query
        """
        #Given that the key may be anywhere, delete the key.
        self.delete(key)
        
        tag = randint(1,100000)

        query = Query()
        query.method = 'put'
        query.tag = tag
        query.key = key
        query.data = data #This packs the data as binary string
        
        serverlist = [(push,pull) for (push,pull) in zip(self.push,self.pull)]

        push,pull = choice(serverlist)
        push.send(query.SerializeToString())
        response = Response()
        response.ParseFromString(pull.recv())

        # All this should become logs and exceptions
        # if not response.data == 'success':
        #     print 'LOG: Put {} not successful'.format(key)

        # elif not response.tag == tag:
        #     print 'LOG: Tag is not correct {},{}'.format(response.tag,tag)
            
        # else:
        #     print 'LOG: Put {} successful'.format(key)

    def get(self,key):
        """
        Sends a key, gets the data
        """
        tag = randint(1,100000)
        responses = list()

        query = Query()
        query.method = 'get'
        query.tag = tag
        query.key = key

        for push,pull in zip(self.push,self.pull):
            push.send(query.SerializeToString())
            response = Response()
            response.ParseFromString(pull.recv())
            if response.data and response.tag == tag:
                responses.append(response.data)

        return responses


    def keys(self,key_from=None,key_to=None):
        tag = randint(1,100000)
        responses = list()
        query = Query()
        query.method = 'keys'
        query.tag = tag
        if key_from:
            query.key_from = key_from
        if key_to:
            query.key_to = key_to

        for push,pull in zip(self.push,self.pull):
            push.send(query.SerializeToString())
            response = Response()
            response.ParseFromString(pull.recv())
            if response.data and response.tag == tag:
                responses.append(response.data)

        return ' '.join(responses)

    def close(self):
        self.context.destroy()


