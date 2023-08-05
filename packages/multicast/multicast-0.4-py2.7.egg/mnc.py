#!/usr/bin/python -u

import logging
logging.basicConfig(level=logging.INFO)
from hashlib import sha1
from time import time

def main(args, logger=None):
	from multicast import sendto, poll
	from uuid import uuid4

	def packet_yielder():
		x = int(time())
		if args.messagepart == ['-']:
			import sys
			for line in sys.stdin:
				line = line.strip()
				yield ':'.join([str(uuid4())] + line.split())
		else:
			suffix = ':'.join(args.messagepart)
			suffix = ':' + suffix

			for i in range(args.packets):
				yield '%d%s' % (x, suffix)
				x += 1


	sendto(packet_yielder(), args.ip, args.port, args.ttl)

def _main(args):
	for i in range(args.x_pound):
		import os
		pid = 0
		if pid == 0:
			main(args, logger)
			break
#		os.waitpid(0, 0)

def argmain():
	import argparse

	p = argparse.ArgumentParser()

	p.add_argument('messagepart', nargs='*', help='The message to send')
	p.add_argument('-p', '--port', type=int, default=4242, help='Port to send on (defaults to %(default)s)')
	p.add_argument('--ip', '--ip', default='224.0.42.42', help='Multicast IP to send to (defaults to %(default)s)')
	p.add_argument('--ttl', '-t', default=1, type=int, help='TTL for packets')
	p.add_argument('--x-pound', default=1, type=int)
	p.add_argument('--packets', default=1, type=int)
	p.add_argument('--profile', default=None)

	#logsetup.add_cli_opts(p)
	args = p.parse_args()

	#logger = logsetup.setup('mcast', args)
	logger = logging.getLogger('mcast')

	if args.profile:
		import cProfile
		cProfile.run('_main(args)', args.profile)
		import pstats
		p = pstats.Stats(args.profile)

		print 'Most time --------------------------------'
		p.sort_stats('cumulative').print_stats(10)
		print 'Looping most -----------------------------'
		p.sort_stats('time').print_stats(10)


	else:
		_main(args)
#!/usr/bin/python

from datetime import datetime
from multicast import listen

from syslog import syslog

x = [0]
def packet_handler(packet, addr):
	x[0] += 1
	print '%8d %s from <%s:%s>' % (x[0], packet, addr[0], addr[1])

f = lambda: listen(packet_handler, limit=15000)
'''
import cProfile
cProfile.run('f()', 'fooprof')
import pstats
p = pstats.Stats('fooprof')

print 'Most time --------------------------------'
p.sort_stats('cumulative').print_stats(10)
print 'Looping most -----------------------------'
p.sort_stats('time').print_stats(10)
'''