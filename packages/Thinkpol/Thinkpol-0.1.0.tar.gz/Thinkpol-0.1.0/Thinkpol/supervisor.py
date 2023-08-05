import psutil
from subprocess import PIPE
from telescreen import Telescreen
import gevent
import signal
from gevent import socket

class Worker(Telescreen):
	def __init__(self, cmd):
		super(Worker, self).__init__()
		self._keeplet = gevent.spawn(self.keep_alive)
		self.cmd = cmd

	def keep_alive(self):
		self._p = psutil.Popen(self.cmd, shell=False, stdout=PIPE)
		self._running = True
		while self._running:
			if str(self._p.status) == "zombie":
				self._p = psutil.Popen(self.cmd, shell=False, stdout=PIPE)
			if not self._p.is_running():
				self._p = psutil.Popen(self.cmd, shell=False, stdout=PIPE)
			gevent.sleep(5)

	def stop(self):
		self._running = False
		self._p.terminate()
		try:
			self._p.wait(3)
		except TimeoutExpired:
			self._p.kill()

	def info(self):
		return {'cpu_percent'		:	round(self._p.get_cpu_percent(), 2),
				'memory_percent'	:	round(self._p.get_memory_percent(), 2),
				'status'			:	str(self._p.status),
				'memory_info'		:	self._p.get_memory_info()}


class Node(Telescreen):
	def start(self, cmd, num):
		self._workers = [Worker(cmd) for i in xrange(num)]
		self.num_cpus = psutil.NUM_CPUS

	def stop(self):
		for worker in self._workers:
			worker.stop()

	def connect(self, addr, conn_workers=False):
		self._connect(addr)
		if conn_workers:
			for worker in self._workers:
				worker._connect(addr)

	def collect_vm_info(self):
		vm_info = psutil.virtual_memory()
		self.vm_total = vm_info.total
		self.vm_available = vm_info.available
		self.vm_percent = vm_info.percent
		self.vm_used = vm_info.used
		self.vm_active = vm_info.active
		self.vm_inactive = vm_info.inactive
		self.vm_cached = vm_info.cached

	def collect_cpu_info(self):
		cpu_times = psutil.cpu_times()
		self.user_time = cpu_times.user
		self.sys_time = cpu_times.system
		self.idle_time = cpu_times.idle
		self.cpu_percent = psutil.cpu_percent()

	def fetch_trigger(self):
		self.worker_info = {str(w):w.info() for w in self._workers}
		self.ip = socket.gethostbyname(socket.gethostname())
		self.collect_cpu_info()
		self.collect_vm_info()

if __name__ == '__main__':
	sv = Node()
	sv.start("yes", 2)
	sv.connect(("localhost", 10000))

	gevent.signal(signal.SIGTERM, sv.stop)
	gevent.signal(signal.SIGQUIT, sv.stop)
	gevent.signal(signal.SIGINT, sv.stop)

	gevent.sleep(100)
