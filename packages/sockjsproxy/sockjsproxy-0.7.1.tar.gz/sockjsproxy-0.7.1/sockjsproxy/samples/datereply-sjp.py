#!/usr/bin/env python

import datetime

import zmq

def main():
    ctx = zmq.Context()
    in_socket = ctx.socket(zmq.PULL)
    in_socket.connect('tcp://localhost:9241')
    out_socket = ctx.socket(zmq.PUSH)
    out_socket.connect('tcp://localhost:9242')

    print 'Listening for messages'
    try:
        while True:
            (message_type, session_id, data) = in_socket.recv_multipart()

            if message_type == 'connect':
                print "{} connected".format(session_id)
            elif message_type == 'disconnect':
                print "{} disconnected".format(session_id)
            else:
                print "{}: {}".format(session_id, data)
                print "Sending date"
                out_socket.send_multipart(['message',
                                           session_id,
                                           'The time now is: ' + str(datetime.datetime.now())])
                out_socket.send_multipart(['disconnect', session_id, ''])
                # out_socket.send_multipart(['disconnectall', '', ''])
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()