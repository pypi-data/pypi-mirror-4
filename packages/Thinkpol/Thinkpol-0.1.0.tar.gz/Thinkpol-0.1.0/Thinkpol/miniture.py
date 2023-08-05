from gevent import socket
from gevent import pool
from port import Port
import yajl as json
import gevent


class Miniture(object):
	def __init__(self):
		self.ggroup = pool.Group()
		self.telescreens = {}

	def listen_thinkpol(self, listen_port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		sock.bind(("", listen_port))
		sock.listen(10000)
		while True:
			client_sock, _ = sock.accept()
			self.collect(Port(client_sock))

	def listen_telescreens(self, listen_port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		sock.bind(("", listen_port))
		sock.listen(10000)
		while True:
			client_sock, _ = sock.accept()
			port = Port(client_sock)
			uuid = port.read()
			self.telescreens[uuid] = port

	def pingall(self, uuid):
		if uuid not in self.telescreens:
			return
		port = self.telescreens[uuid]
		port.write("S")
		if not port.read():
			del self.telescreens[uuid]

	def fetch_state(self, uuid):
		if uuid not in self.telescreens:
			return (uuid, None)
		port = self.telescreens[uuid]
		port.write("S")
		res = port.read()
		if res:
			return (uuid, json.loads(res))
		else:
			del self.telescreens[uuid]
			return (uuid, None)

	def collect(self, port):
		while True:
			req = port.read()
			if not req:
				break
			if req == "?":
				self.ggroup.map(self.pingall, self.telescreens.iterkeys())
				port.write(json.dumps(self.telescreens.keys()))
				continue
			if req == "*":
				want_list = self.telescreens.iterkeys()
			else:
				want_list = json.loads(req)
			rep = self.ggroup.map(self.fetch_state, want_list)
			port.write(json.dumps({k:v for k,v in rep if v}))

	def run(self, ts_port, tp_port):
		gevent.joinall([
			gevent.spawn(self.listen_thinkpol, tp_port),
			gevent.spawn(self.listen_telescreens, ts_port)
			])

if __name__ == '__main__':
	ccp = Miniture()
	ccp.run(10000, 10001)

		