import struct
import snappy

def safe_recv(sock, len):
    try:
        buf = sock.recv(len)
        if buf:
            return buf
    except:
        sock.close()
        return False    


def safe_send(sock, buf):
    try:
        sock.sendall(buf)
        return True
    except:
        sock.close()
        return False

class Port(object):
    HEADER_STRUCT = ">L"
    HEADER_LEN = struct.calcsize(HEADER_STRUCT)

    def __init__(self, sock):
        self._sock = sock

    def read(self):
        header = safe_recv(self._sock, self.HEADER_LEN)
        if not header: return False
        length = struct.unpack(self.HEADER_STRUCT, header)[0]
        chunks = []
        while length:
            recv = safe_recv(self._sock, length)
            if not recv: return False
            chunks.append(recv)
            length -= len(recv)
        return snappy.decompress("".join(chunks))

    def write(self, bytes):
        bytes = snappy.compress(bytes)
        msg = struct.pack(self.HEADER_STRUCT, len(bytes)) + bytes
        return safe_send(self._sock, msg)

    def close(self):
        self._sock.close()
