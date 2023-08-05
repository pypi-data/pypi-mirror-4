import unittest
from time import sleep
from server import Server
from client import Client
import subprocess
import struct

class TestSequence(unittest.TestCase):
    """
    This only tests the client. You need to be running some servers
    for that. For mysterious reasons python is not able to launch the
    server process so you will have to launch and to kill them
    separately. There is a runservers script for that.
    """
    def setUp(self):
        self.urls = [('tcp://127.0.0.1:10001',
                      'tcp://127.0.0.1:10002'),
                     ('tcp://127.0.0.1:10011',
                      'tcp://127.0.0.1:10012'),
                     ('tcp://127.0.0.1:10021',
                      'tcp://127.0.0.1:10022')
                     ]


    def test_client_connection(self):
        #Now test a single client and a single server
        client = Client(self.urls)
        client.close()
        

    def test_put_get_one(self):
        client = Client(self.urls)
        key = '/root'
        value = struct.pack('i',134234123)
        client.put(key,value)
        self.assertEqual(134234123,struct.unpack('i',client.get(key)[0])[0])
        client.delete('/root')
        client.close()

    def test_put_many(self):
        client = Client(self.urls)
        
        for i in range(1000):
            key = '/test{}'.format(i)
            value = 'some longer string with the number {}'.format(i)
            client.put(key,value)

        value = 'some longer string with the number 123'
        key = '/test123'
        self.assertEqual(value,client.get(key)[0])

        for i in range(1,1000):
            key = '/test{}'.format(i)
            client.delete(key)

        #Only one key should be left
        self.assertEqual('/test0',client.keys())

        client.close()
        

if __name__ == '__main__':
    unittest.main()

