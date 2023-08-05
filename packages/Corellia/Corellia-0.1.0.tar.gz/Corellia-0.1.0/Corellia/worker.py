from port import ObjPort
from gevent import socket as socket
import snappy
import gevent

class Worker(object):
	def __init__(self, C, *args):
		self.instance = C(*args)

	def run_alone(self, port):
		listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		listen_sock.bind(("", port))
		listen_sock.listen(10000)
		while True:
			sock, _ = listen_sock.accept()
			gevent.spawn(self.handle_let, sock)

	def handle_let(self, sock):
		port = ObjPort(sock)
		while True:
			message = port.read()
			if message:
				port.write(self.handle(message))
			else:
				break
		
	def run(self, broker_addr):
		listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listen_sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		listen_sock.connect(broker_addr)
		self.port = ObjPort(listen_sock)
		while True:
			message = self.port.read()
			if message:
				self.port.write(self.handle(message))
			else:
				break

	def handle(self, message):
		func, args = message
		f = getattr(self.instance, func, lambda _: None)
		return f(*args)

class Client(object):
	def __init__(self, worker_addr):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		sock.connect(worker_addr)
		self.port = ObjPort(sock)

	def shutdown(self):
		self.port.close()

	def __getattr__(self, func):
		def call(*args):
			st = self.port.write((func, args))
			if st:
				msg = self.port.read()
				if msg:
					return msg
		return call

def call(addr, func, args):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(addr)
	port = ObjPort(sock)
	port.write((func, args))
	return port.read()