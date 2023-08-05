
import sys
sys.path.insert(0, '../')

import os
import signal
import subprocess
import pyuv

from optparse import OptionParser


RESPONSE = b"HTTP/1.1 200 OK\r\n" \
           "Content-Type: text/plain\r\n" \
           "Content-Length: 12\r\n" \
           "\r\n" \
           "hello world\n"

loop = None
server = None
process = None
clients = []


def on_client_shutdown(client, error):
    client.close()
    clients.remove(client)

def on_read(client, data, error):
    if data is None:
        client.close()
        clients.remove(client)
        return
    if not data.strip():
        return
    client.write(RESPONSE)
    client.shutdown(on_client_shutdown)

def on_connection(server, error):
    client = pyuv.TCP(server.loop)
    server.accept(client)
    clients.append(client)
    client.start_read(on_read)

def proc_exit_cb(proc, exit_status, term_signal):
    global server, process
    process.close()
    server.close()


def main(options):
    global loop, server, process
    cmd = 'ab'
    args = []
    args.extend(['-n', str(options.num_requests)])
    args.extend(['-c', str(options.concurrency)])
    if options.quiet:
        args.append('-q')
    if options.keepalive:
        args.append('-k')
    args.append('127.0.0.1:1234/')

    loop = pyuv.Loop.default_loop()

    server = pyuv.TCP(loop)
    server.bind(("127.0.0.1", 1234))
    server.listen(on_connection)
    server.simultaneous_accepts(False)

    stdio = []
    stdio.append(pyuv.StdIO(fd=sys.stdin.fileno(), flags=pyuv.UV_INHERIT_FD))
    stdio.append(pyuv.StdIO(fd=sys.stdout.fileno(), flags=pyuv.UV_INHERIT_FD))
    stdio.append(pyuv.StdIO(fd=sys.stderr.fileno(), flags=pyuv.UV_INHERIT_FD))

    process = pyuv.Process(loop)
    process.spawn(file=cmd, args=args, env=os.environ.copy(), exit_callback=proc_exit_cb, stdio=stdio)

    loop.run()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-n", dest="num_requests", default=15000, help="Number of requests to perform")
    parser.add_option("-c", dest="concurrency", default=25, help="Number of multiple requests to make")
    parser.add_option("-q", dest="quiet", action="store_true", default=False, help="Don't print progress to stderr")
    parser.add_option("-k", dest="keepalive", action="store_true", default=False, help="Use HTTP KeepAlive feature")
    options, args = parser.parse_args()
    main(options)


