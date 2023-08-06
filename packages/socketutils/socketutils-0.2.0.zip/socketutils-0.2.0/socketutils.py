""" socketutils - socket utils """
import struct


def recvall(s, n):
    """ recv() n bytes, otherwise raise a ValueError """
    buflist = []
    got = 0

    while got < n:
        buf = s.recv(n-got)
        if not buf:
            break
        buflist.append(buf)
        got += len(buf)

    data = ''.join(buflist)

    if got != n:
        raise ValueError('got {} bytes, expected {}'.format(got, n), data)

    return data


def recvtillend(s, bufsize=4096):
    """ recv() till s is disconnected """
    buflist = []

    while True:
        buf = s.recv(bufsize)
        if not buf:
            break
        buflist.append(buf)

    return ''.join(buflist)


def recvsized(s, sizeformat='!I'):
    """receive a sized message"""
    header = recvall(s, struct.calcsize(sizeformat))
    [size] = struct.unpack('!I', header)
    return recvall(s, size)


def sendsized(s, data, sizeformat='!I'):
    """send a sized message"""
    header = struct.pack(sizeformat, len(data))
    s.sendall(header)
    s.sendall(data)
