import socket
import uselect as select
from machine import Timer

CONTENT = b"""\
HTTP/1.0 200 OK

Hello #%d from MicroPython!
"""
counter = 0 


def Client_handler(client, micropython_optimize):
    global counter
    client_sock = client[0]
    client_addr = client[1]
    print("Client address:", client_addr)
    print("Client socket:", client_sock)

    if not micropython_optimize:
            # To read line-oriented protocol (like HTTP) from a socket (and
            # avoid short read problem), it must be wrapped in a stream (aka
            # file-like) object. That's how you do it in CPython:
        client_stream = client_sock.makefile("rwb")
    else:
            # .. but MicroPython socket objects support stream interface
            # directly, so calling .makefile() method is not required. If
            # you develop application which will run only on MicroPython,
            # especially on a resource-constrained embedded device, you
            # may take this shortcut to save resources.
        client_stream = client_sock

    print("Request:")
    req = client_stream.readline()
    print(req)
    '''''''''
    while True:
        h = client_stream.readline()
        if h == b"" or h == b"\r\n" or h == b"\n":
            break
        print(h)
    '''
    client_stream.write(CONTENT % counter)
    '''''''''
    client_stream.close()
    if not micropython_optimize:
        client_sock.close()
    '''
    print()
    counter += 1


def main(micropython_optimize=False):
    global counter
    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("Listening, connect your browser to http://<this_host>:8080/")

    counter = 0

    def Update(param):
        r, w, err = select.select((s,), (), (), 1)
        if r:
            for readable in r:
                client = s.accept()
                Client_handler(client, micropython_optimize)
        
        
    tim1 = Timer(0)
    tim1.init(period=5000, mode=Timer.PERIODIC, callback=Update)


main()
