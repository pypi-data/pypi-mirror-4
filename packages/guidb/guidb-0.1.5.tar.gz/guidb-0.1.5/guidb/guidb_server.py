import sys
from server import Server

if __name__ == '__main__':
    server = Server(url_recv=sys.argv[1],
                    url_send=sys.argv[2],
                    rank = int(sys.argv[3]),
                    datafile = sys.argv[4])

    server.run()
