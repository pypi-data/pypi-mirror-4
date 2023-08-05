#!/usr/bin/python

"""This module provides classes and functions for asynchronous multicast UDP clients and servers.

The `multicast` module has a default :class:`Poller` object in the `multicast._defaultPoller` attribute. The convenience funtions the module exposes use the default :class:`Poller` instance.

By default, instances of `multicast` classes register themselves with the default :class:`Poller` object. To implement custom polling setups, instantiate other :class:`Poller` objects and manually `register` the :class:`Multicaster` and :class:`MulticastListener` instances.
"""

from hashlib import md5
import socket, sys
import os
import logging
import select
from time import sleep

__version__ = '0.4'

_logger = logging.getLogger('multicast')

class Poller:
	"""Poller objects wrap :func:`select.epoll` `epoll objects <http://linux.die.net/man/4/epoll>`_.

	They implement a :func:`loop` function that loops and sleeps polling the underlying `epoll`
	object for events on registered file descriptors.
	"""

	def __init__(self):
		self._map = {}
		self.poller = select.epoll()
		self.polling = True

	def unregister(self, fd):
		'''Remove a tracked file descriptor'''

		del self._map[fd.fileno()]
		self.poller.unregister(fd)
		fd.close()

		if not self._map:
			self.polling = False

	def register(self, fd, flags=0):
		'''Register a file descriptor object with the :class:`Poller`. Future calls to
		:func:`poll` will check whether the file descriptor has any
		pending I/O events. `fd` must be an object that implements a **fileno()**
		method that returns an integer. It must also support implement the following
		methods:

			**handle_read()**
				To indicate that it wants to receive EPOLLIN and EPOLLPRI events

			**handle_write()**
				To indicate that it wants to receive EPOLLOUT events
		'''

		for flag, method in fd.__class__._method_map.items():
			if hasattr(fd, method):
				flags |= flag

		self.poller.register(fd, flags)
		self._map[fd.fileno()] = fd

	def poll(self, timeout=0):
		'''Polls the registered set  of file descriptors for events.

		When an event is detected on a file descriptor, the corresponding
		**handle_<event>()** method is called on the registered object.
		'''

		try:
			for fd, event in self.poller.poll(timeout=timeout):
				fd = self._map[fd]
				mname = fd.__class__._method_map[event]
				if hasattr(fd, mname):
					getattr(fd, mname)()
		except KeyboardInterrupt:
			raise SystemExit

	def loop(self, timeout=0, interval=0):
		'''Enter a polling loop that terminates when `self.polling` is False.

		The `interval` parameter indicates how long to `sleep` between polls. The
		`timeout` parameter is passed to the `poll` call. Both are expressed in
		seconds. `interval` and `timeout` both default to **0**.
		'''

		while True:
			self.poll(timeout=timeout)
			if not self.polling:
				break

			if interval:
				sleep(interval)

_defaultPoller = Poller()

poll = _defaultPoller.poll
loop = _defaultPoller.loop
register = _defaultPoller.register
unregister = _defaultPoller.unregister

class Dispatcher(object):
	'''Dispatcher objects are registered with `Poller` objects that use
	epoll to enter the system select loop.

	This class should not be extended directly; instead, use the `UDPDispatcher`
	class.
	'''

	_method_map = {
		select.EPOLLIN: 'handle_read',
		select.EPOLLOUT: 'handle_write',
		select.EPOLLPRI: 'handle_read'
	}

class UDPDispatcher(Dispatcher):
	'''Adapts a file descriptor object for registration with a :class:`Poller`
	instance'''

	def __init__(self, fd, poller=None):
		'''Initialize a file descriptor wrapper.

		`fd` can be either an integer, or an object with a :func:`fileno` method
		that returns an integer. File objects implement :func:`fileno`, so they
		can also be used as the argument.
		'''

		self._fd = fd
		self.logger = logging.getLogger('multicast.UDPDispatcher')

		self.poller = poller or _defaultPoller
		self.poller.register(self)

	def fileno(self):
		'Return the wrapped file descriptor'
		return self._fd.fileno()

	def close(self):
		'Unregister this dispatcher and close the wrapped file descriptor'
		self.poller.unregister(self._fd)
		self._fd.close()

import struct

class Multicaster(UDPDispatcher):
	'''Make sub-classes of this class iterable and yield packets to multicast.

	The TTL of packets sent by the multicaster defaults to 1 (ie. the
	local segment). See the table below for suggested TTL values.

	================  ======
	same host			0
	same subnet			1
	same site			32
	same region			64
	same continent		128
	unrestricted		255
	================  ======
	'''

	def __init__(self, ip='224.0.42.42', port=4242, ttl=1):
		self.ip = ip
		self.port = port

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

		self.packets = iter(self)
		UDPDispatcher.__init__(self, self.sock)

	def __iter__(self):
		'''Sub-types should override this method to return an iterator that
		yields packets to be multicast.

		:raises: NotImplementedError

		'''
		raise NotImplementedError

	def handle_write(self):
		try:
			packet = self.packets.next()
			if packet:
				self.logger.debug('Sending %r to <%s:%s>', packet, self.ip, self.port)
				self.sock.sendto(packet, (self.ip, self.port))
		except StopIteration:
			self.close()

from string import Template
import re

def sendto(packets, ip='224.0.42.42', port=4242, ttl=1):
	"""Send `packets` to the multicast group at `ip` on `port`.

	The packet is sent with a TTL of 1 by default; see below for suggested
	TTL values:

		================  ======
		same host			0
		same subnet			1
		same site			32
		same region			64
		same continent		128
		unrestricted		255
		================  ======
	"""

	class A(Multicaster):
		def __iter__(self):
			for p in packets:
				yield p

	A(ip, port, ttl)
	loop()

class MulticastListener(UDPDispatcher):
	'''MulticastListeners join a multicast IP group and call their
	:func:`handle_packet` method when packets are sent to the group.

	Packets are read up to `mtu` bytes of each packet, and only listen for
	packets that match `filter`.

	`filter` can be a callable **filter(packet, addr)** that returns `True`
	if the packet should be accepted or `False` to drop the packet; or it
	can be a regular expression, in which case it is compiled and packets
	that match it are accepted.
	'''

	def __init__(self, filter=None, ip='224.0.42.42', port=4242, mtu=4096):
		self.ip = ip
		self.port = port
		self.mtu = mtu

		mreq = struct.pack("4sl", socket.inet_aton(ip), socket.INADDR_ANY)

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((ip, port))
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		self.sock = sock

		if isinstance(filter, basestring):
			s = Template(filter).safe_substitute(self.__dict__)
			regex = re.compile(s)
			self.filter = lambda packet, addr: regex.match(packet)
		elif callable(filter):
			self.filter = filter
			s = filter
		elif not filter:
			s = '**'
			self.filter = filter
		else:
			raise ValueError('filter must be either of type basestring or callable')

		UDPDispatcher.__init__(self, self.sock)

		self.logger = logging.getLogger('multicast.MulticastListener')
		self.logger.debug('listening for packets matching %r on %s:%s' % (s, self.ip, self.port))

	def handle_read(self):
		try:
			print 'calling hanle ************************************************'
			while True:
				packet, addr = self.sock.recvfrom(self.mtu)
				print packet, addr

				if self.filter and not self.filter(packet, addr):
					continue
				print 'handling packet'
				if self.handle_packet(packet, addr):
					self.close()
					return
		except Exception, e:
			print e

	def handle_packet(self, packet, addr):
		'''Implemented by sub-classes as a callback when packets matching the
		`filter` are received.'''
		raise NotImplementedError

class PacketDispatcher(MulticastListener):
	_limit = None
	packet_handler = None

	def handle_packet(self, packet, addr):
		if self._limit:
			self._limit -= 1
			if self._limit == 0:
				return
		return self.packet_handler(packet, addr)

def listen(packet_handler, ip='224.0.42.42', port=4242, mtu=4096, limit=None):
	'''Calls a `packet_handler` with a `packet` and an `addr` argument each time
	a packet is received by the	multicast group at `ip` on `port`.

	.. note::

		This function does not return until the `packet_handler` returns non-`False`

	`mtu` is the maximum packet size in bytes.

	>>> from multicast import listen, sendto, poll
	>>> listener = listen()
	>>> sendto('test')
	>>> poll()
	>>> listener.next()
	'test'

	.. warning::

		Clients of this function **must** call :func:`multicast.poll` after each call
		to the returned generator's :func:`next` method.

		Failure to do so will result in no packets being delivered.
	'''

	listener = PacketDispatcher(None, ip, port, mtu)
	listener._limit = limit
	listener.packet_handler = packet_handler

	loop()
