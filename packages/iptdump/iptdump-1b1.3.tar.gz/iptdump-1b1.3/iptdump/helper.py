from iptdump import *
from extension import Tcp, Udp, Mac

def __DaemonAbstract__(ruleIn, ruleOut, args):
	"""
	__DaemonAbstract__(ruleIn, ruleOut, args) -> tuple
	"""
	if 'proto' in args:
		ruleIn.proto(args['proto'])
		ruleOut.proto(args['proto'])
		if args['proto'] == PROTO_TCP:
			ext = Tcp().dport(args['dport'])
			if 'sport' in args:
				ext.sport(args['sport'])
			ruleIn.addExtension(ext)
			ext = Tcp().sport(args['dport'])
			if 'sport' in args:
				ext.dport(args['sport'])
			ext.syn(True)
			ruleOut.addExtension(ext)
		elif args['proto'] == PROTO_UDP:
			ext = Udp().dport(args['dport'])
			if 'sport' in args:
				ext.sport(args['sport'])
			ruleIn.addExtension(ext)
			ext = Udp().sport(args['dport'])
			if 'sport' in args:
				ext.dport(args['sport'])
			ruleOut.addExtension(ext)
		elif args['proto'] == PROTO_41:
			pass
		else:
			assert 1 == 0
	if 'src' in args:
		ruleIn.src(args['src'])
		ruleOut.dst(args['src'])
	if 'dst' in args:
		ruleIn.dst(args['dst'])
		ruleOut.src(args['dst'])
	return (ruleIn, ruleOut)

def DaemonForward(ipt, **args):
	"""
	DaemonForward(ipt, **args) -> tuple
	"""
	chFw = ipt.table(TABLE_FILTER).chain(CHAIN_FORWARD)
	ruleOut = chFw.new().iIface(args['iface'])
	ruleIn = chFw.new().oIface(args['iface'])
	if 'oiface' in args:
		ruleOut.oIface(args['oiface'])
		ruleIn.iIface(args['oiface'])
	return __DaemonAbstract__(ruleIn, ruleOut, args)

def Daemon(ipt, **args):
	"""
	Daemon(ipt, **args) -> tuple
	"""
	ruleIn = ipt.table(TABLE_FILTER).chain(CHAIN_INPUT).new()
	ruleOut = ipt.table(TABLE_FILTER).chain(CHAIN_OUTPUT).new()
	if 'iface' in args:
		ruleIn.iIface(args['iface'])
		ruleOut.oIface(args['iface'])
	return __DaemonAbstract__(ruleIn, ruleOut, args)

def __ClientAbstract__(ruleIn, ruleOut, args):
	"""
	__ClientAbstract__(ruleIn, ruleOut, args) -> tuple
	"""
	if 'proto' in args:
		ruleIn.proto(args['proto'])
		ruleOut.proto(args['proto'])
		if args['proto'] == PROTO_TCP:
			ext = Tcp()
			if 'dport' in args:
				ext.sport(args['dport'])
			if 'sport' in args:
				ext.dport(args['sport'])
			ext.syn(True)
			ruleIn.addExtension(ext)
			ext = Tcp()
			if 'dport' in args:
				ext.dport(args['dport'])
			if 'sport' in args:
				ext.sport(args['sport'])
			ruleOut.addExtension(ext)
		elif args['proto'] == PROTO_UDP:
			ext = Udp()
			if 'dport' in args:
				ext.sport(args['dport'])
			if 'sport' in args:
				ext.dport(args['sport'])
			ruleIn.addExtension(ext)
			ext = Udp()
			if 'dport' in args:
				ext.dport(args['dport'])
			if 'sport' in args:
				ext.sport(args['sport'])
			ruleOut.addExtension(ext)
		elif args['proto'] not in PROTO_ALL_:
			assert 1 == 0
	if 'src' in args:
		ruleIn.dst(args['src'])
		ruleOut.src(args['src'])
	if 'dst' in args:
		ruleIn.src(args['dst'])
		ruleOut.dst(args['dst'])
	return (ruleIn, ruleOut)

def ClientForward(ipt, **args):
	"""
	ClientForward(ipt, **args) -> tuple
	"""
	chFw = ipt.table(TABLE_FILTER).chain(CHAIN_FORWARD)
	ruleOut = chFw.new().iIface(args['iface'])
	ruleIn = chFw.new().oIface(args['iface'])
	if 'oiface' in args:
		ruleOut.oIface(args['oiface'])
		ruleIn.iIface(args['oiface'])
	if 'mac' in args:
		ruleOut.addExt(Mac().src(args['mac']))
	return __ClientAbstract__(ruleIn, ruleOut, args)

def Client(ipt, **args):
	"""
	Client(ipt, **args) -> tuple
	"""
	ruleIn = ipt.table(TABLE_FILTER).chain(CHAIN_INPUT).new()
	ruleOut = ipt.table(TABLE_FILTER).chain(CHAIN_OUTPUT).new()
	if 'iface' in args:
		ruleIn.iIface(args['iface'])
		ruleOut.oIface(args['iface'])
	if 'mac' in args:
		ruleIn.addExt(Mac().src(args['mac']))
	return __ClientAbstract__(ruleIn, ruleOut, args)

def __TracerouteAbstract__(ruleIn, ruleOut, args):
	"""
	__TracerouteAbstract__(ruleIn, ruleOut, args) -> tuple
	"""
	ext = Udp().dport('33434:33523')
	ruleIn.protoUDP().addExtension(ext)
	ruleOut.protoUDP().addExtension(ext)
	return (ruleIn, ruleOut)

def TracerouteForward(ipt, **args):
	"""
	TracerouteForward(ipt, **args) -> tuple
	"""
	chFw = ipt.table(TABLE_FILTER).chain(CHAIN_FORWARD)
	ruleIn = chFw.new().iIface(args['oiface']).oIface(args['iface'])
	ruleOut = chFw.new().iIface(args['iface']).oIface(args['oiface'])
	return __TracerouteAbstract__(ruleIn, ruleOut, args)

def Traceroute(ipt, **args):
	"""
	Traceroute(ipt, **args) -> tuple
	"""
	ruleIn = ipt.table(TABLE_FILTER).chain(CHAIN_INPUT).new()
	ruleOut = ipt.table(TABLE_FILTER).chain(CHAIN_OUTPUT).new()
	if 'iface' in args:
		ruleIn.iIface(args['iface'])
		ruleOut.oIface(args['iface'])
	return __TracerouteAbstract__(ruleIn, ruleOut, args)

def __IcmpAbstract__(ruleIn, ruleOut, args):
	"""
	x.__IcmpAbstract__(ruleIn, ruleOut, args) -> tuple
	"""
	assert args['IPV'] in IPTABLE_ALL_
	if args['IPV'] == IPTABLE_V4:
		ruleIn.protoICMP()
		ruleOut.protoICMP()
	else:
		ruleIn.protoICMPv6()
		ruleOut.protoICMPv6()
	return (ruleIn, ruleOut)

def IcmpForward(ipt, **args):
	"""
	IcmpForward(ipt, **args) -> tuple
	"""
	args['IPV'] = ipt.getIPversion()
	chFw = ipt.table(TABLE_FILTER).chain(CHAIN_FORWARD)
	ruleIn = chFw.new().iIface(args['oiface']).oIface(args['iface'])
	ruleOut = chFw.new().iIface(args['iface']).oIface(args['oiface'])
	return __IcmpAbstract__(ruleIn, ruleOut, args)

def Icmp(ipt, **args):
	"""
	Icmp(ipt **args) -> tuple
	"""
	args['IPV'] = ipt.getIPversion()
	ruleIn = ipt.table(TABLE_FILTER).chain(CHAIN_INPUT).new()
	ruleOut = ipt.table(TABLE_FILTER).chain(CHAIN_OUTPUT).new()
	if 'iface' in args:
		ruleIn.iIface(args['iface'])
		ruleOut.oIface(args['iface'])
	return __IcmpAbstract__(ruleIn, ruleOut, args)
