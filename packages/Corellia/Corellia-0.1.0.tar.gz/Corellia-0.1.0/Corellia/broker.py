import gevent
import gevent.socket as socket
from gevent.queue import Queue
from port import Port


class Broker(object):
	def __init__(self, client_port, worker_port):
		self.client_port = client_port
		self.worker_port = worker_port
		self.tdq = Queue()

	def waiter(self, s0):
		while True:
			p0 = Port(s0)
			req = p0.read()
			if not req: 
				break
			p1 = self.tdq.get()
			while not p1.write(req):
				p1 = self.tdq.get()
			rep = p1.read()
			if rep:
				self.tdq.put(p1)
				if not p0.write(rep):
					break

	def listen_client(self):
		client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		client_sock.bind(("", self.client_port))
		client_sock.listen(10000)
		while True:
			sock, _ = client_sock.accept()
			gevent.spawn(self.waiter, sock)

	def listen_worker(self):
		worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		worker_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		worker_sock.bind(("", self.worker_port))
		worker_sock.listen(10000)
		while True:
			sock, _ = worker_sock.accept()
			self.tdq.put(Port(sock)) 

	def run(self):
		gevent.joinall([
			gevent.spawn(self.listen_worker),
			gevent.spawn(self.listen_client)
			])

		