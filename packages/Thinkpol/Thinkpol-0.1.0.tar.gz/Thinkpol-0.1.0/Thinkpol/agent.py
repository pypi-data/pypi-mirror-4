import yajl as json
import socket
from port import Port

class Agent(object):
	def __init__(self, addr):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(addr)
		self.port = Port(sock)

	def list(self):
		self.port.write("?")
		return json.loads(self.port.read())

	def fetch(self, want="*"):
		if want == "*":
			req = "*"
		else:
			req = json.dumps(want)
		self.port.write(req)
		return json.loads(self.port.read())

if __name__ == '__main__':
	Smith = Agent(("210.72.68.189", 10001))
	print Smith.fetch(["Node_32d7490cfcc511e1b81afa163e22777e"])