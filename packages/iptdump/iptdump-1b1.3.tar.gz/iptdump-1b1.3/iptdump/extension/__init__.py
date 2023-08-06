"""
This modul containt extension.
"""

import re
import iptdump as iptd

class AbstractExtension:
	"""
	Is a abstract class for iptable extensions.
	"""
	def __init__(self, chains):
		"""
		x.__init__(chains)

		Constructor.
		chains
		"""
		self._allow_chains_ = chains

	def dump(self, name, options):
		"""
		x.dump(name, options) -> str

		Return the extension name for a rule in the iptables-save form.
		"""
		return "-m %s %s" % (name, options)

	def provideChain(self):
		"""
		x.provideChain() -> object

		Return the rules.
		"""
		return self._allow_chains_

class Icmp(AbstractExtension):
	"""
	The ICMP extension.
	"""
	name = 'icmp'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, iptd.CHAIN_ALL_)
		self.__type = None
		self.__invert = None

	def type(self, icmpType, invert=False):
		"""
		x.type(icmpType [,invert]) -> self

		Set the type of ICMP.
		Set invert true for negation.
		"""
		assert type(icmpType) in (str, int)
		self.__type = icmpType
		assert type(invert) == bool
		self.__invert = invert
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__type:
			if self.__invert:
				result.append("!")
			result += ("--%s-type" % self.name, str(self.__type))
		return AbstractExtension.dump(self, self.name, " ".join(result))

class Icmpv6(Icmp):
	"""
	The ICMPv6 extension.
	"""
	name = 'icmpv6'

class Mac(AbstractExtension):
	"""
	The MAC extension.
	"""
	name = 'mac'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, (iptd.CHAIN_PREROUTING, iptd.CHAIN_INPUT, iptd.CHAIN_FORWARD))
		self.__src = None
		self.__invert = None

	def __check__(self, mac):
		"""
		x.__check__(mac) -> bool
		"""
		return bool(re.match('^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}$', mac))

	def source(self, src, invert=False):
		"""
		x.source(src [,invert]) -> self

		Set invert true for negation.
		"""
		assert True == self.__check__(src)
		self.__src = src
		self.__invert = invert
		return self

	def src(self, src, invert=False):
		"""
		x.src(src [,invert]) -> self

		Alias for source().
		"""
		return self.source(src, invert)

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__src:
			if self.__invert:
				result.append("!")
			result += ("--mac-source", self.__src)
		return AbstractExtension.dump(self, Mac.name, " ".join(result))

class Multiport(AbstractExtension):
	"""
	Is the multiport extension.
	"""
	name = 'multiport'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, iptd.CHAIN_ALL_)
		self.__ports = None
		self.__portsInvert = None
		self.__sports = None
		self.__sportsInvert = None
		self.__dports = None
		self.__dportsInvert = None

	def ports(self, ports, invert=False):
		"""
		x.ports(ports [,invert]) -> self

		Set the source/destination ports.
		Set invert true for negation.
		"""
		self.__ports = ports
		self.__portsInvert = invert
		return self

	def sports(self, ports, invert=False):
		"""
		x.sports(ports [,invert]) -> self

		Set the source ports.
		Set invert true for negation.
		"""
		self.__sports = ports
		self.__sportsInvert = invert
		return self

	def dports(self, ports, invert=False):
		"""
		x.dports(ports [,invert]) -> self

		Set the destination ports.
		Set invert true for negation.
		"""
		self.__dports = ports
		self.__dportsInvert = invert
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__sports:
			if self.__sportsInvert:
				result.append("!")
			result += ("--sports", self.__sports)
		if self.__dports:
			if self.__dportsInvert:
				result.append("!")
			result += ("--dports", self.__dports)
		if self.__ports:
			if self.__portsInvert:
				result += ("--ports %s", self.__ports)
		return AbstractExtension.dump(self, Multiport.name, " ".join(result))

class Owner(AbstractExtension):
	"""
	Is the owner extension.
	"""
	name = 'owner'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, (iptd.CHAIN_OUTPUT,))
		self.__uidOwner = None
		self.__uidOwnerInvert = None
		self.__gidOwner = None
		self.__gidOwnerInvert = None

	def uidOwner(self, owner, invert=False):
		"""
		x.uidOwner(owner [, invert]) -> self

		Set the user id of the owner.
		Set invert true for negation.
		"""
		self.__uidOwner = owner
		self.__uidOwnerInvert = invert
		return self

	def gidOwner(self, owner, invert=False):
		"""
		x.gidOwner(owner [, invert]) -> self

		Set the group id of the owner.
		Set invert true for negation.
		"""
		self.__gidOwner = owner
		self.__gidOwnerInvert = invert
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__uidOwner:
			if self.__uidOwnerInvert:
				result.append(" !")
			result += ("--uid-owner", self.__uidOwner)
		if self.__gidOwner:
			if self.__gidOwnerInvert:
				result.append(" !")
			result += ("--gid-owner", self.__gidOwner)
		return AbstractExtension.dump(self, Owner.name, " ".join(result))

TCP_FLAG_SYN = "SYN"
TCP_FLAG_RST = "RST"
TCP_FLAG_ACK = "ACK"
TCP_FLAG_FIN = "FIN"
TCP_FLAG_ALL_ = (TCP_FLAG_SYN, TCP_FLAG_RST, TCP_FLAG_ACK, TCP_FLAG_FIN)

class Tcp(AbstractExtension):
	"""
	Is the TCP extension.
	"""
	name = 'tcp'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, iptd.CHAIN_ALL_)
		self.__sport = None
		self.__sportInvert = None
		self.__dport = None
		self.__dportInvert = None
		self.__flags = None
		self.__flagsInvert = None

	def sport(self, port, invert=False):
		"""
		x.sport(port [,invert]) -> self

		Set the source port.
		Set invert true for negation.
		"""
		self.__sport = port
		self.__sportInvert = invert
		return self

	def dport(self, port, invert=False):
		"""
		x.dport(port [,invert]) -> self

		Set the destination port.
		Set invert true for negation.
		"""
		self.__dport = port
		self.__dportInvert = invert
		return self
	"""
	def flags(self, mask, comp, invert=False):
		self.__flags = (mask, comp)
		self.__flagsInvert = invert
		return self
	"""
	def syn(self, invert=False):
		"""
		x.syn([invert]) -> self

		Set the syn flag.
		Set invert true for negation.
		"""
		self.__flags = ((TCP_FLAG_FIN, TCP_FLAG_RST, TCP_FLAG_ACK), TCP_FLAG_SYN)
		self.__flagsInvert = invert
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__sport:
			if self.__sportInvert:
				result.append("!")
			result += ("--sport", str(self.__sport))
		if self.__dport:
			if self.__dportInvert:
				result.append("!")
			result += ("--dport", str(self.__dport))
		if self.__flags:
			if self.__flagsInvert:
				result.append("!")
			result += ("--tcp-flags", ",".join(self.__flags[0]), self.__flags[1])
		return AbstractExtension.dump(self, Tcp.name, " ".join(result))

class Udp(AbstractExtension):
	"""
	Is the UDP extension.
	"""
	name = 'udp'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, iptd.CHAIN_ALL_)
		self.__sport = None
		self.__sportInvert = None
		self.__dport = None
		self.__dportInvert = None

	def sport(self, port, invert=False):
		"""
		x.sport(port [,invert]) -> self

		Set the source port.
		Set invert true for negation.
		"""
		self.__sport = port
		self.__sportInvert = invert
		return self

	def dport(self, port, invert=False):
		"""
		x.dport(port [,invert]) -> self

		Set the destination port.
		Set invert true for negation.
		"""
		self.__dport = port
		self.__dportInvert = invert
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__sport:
			if self.__sportInvert:
				result.append("!")
			result += ("--sport", str(self.__sport))
		if self.__dport:
			if self.__dportInvert:
				result.append("!")
			result += ("--dport", str(self.__dport))
		return AbstractExtension.dump(self, Udp.name, " ".join(result))

LIMIT_SECOND = 'second'
LIMIT_MINUTE = 'minute'
LIMIT_HOUR = 'hour'
LIMIT_DAY = 'day'
LIMIT_ALL_ = (LIMIT_SECOND, LIMIT_MINUTE, LIMIT_HOUR, LIMIT_DAY)

class Limit(AbstractExtension):
	"""
	Is the limit extension.
	"""
	name = 'limit'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, iptd.CHAIN_ALL_)
		self.__rate = 3
		self.__unit = LIMIT_HOUR
		self.__number = 5

	def limit(self, rate, unit):
		"""
		x.limit(rate, unit) -> self
		"""
		assert type(rate) in (int, str)
		self.__rate = rate
		assert unit in LIMIT_ALL_
		self.__unit = unit
		return self

	def burst(self, number):
		"""
		x.burst(number) -> self
		"""
		assert type(number) in (int, str)
		self.__number = number
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = [
			'--limit',
			"%s/%s" % (self.__rate, self.__unit),
			'--limit-burst',
			str(self.__number)
		]
		return AbstractExtension.dump(self, Limit.name, " ".join(result))

class Connlimit(AbstractExtension):
	"""
	Is the connlimit extension.
	"""
	name = 'connlimit'

	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractExtension.__init__(self, iptd.CHAIN_ALL_)
		self.__prefixLength = None
		self.__number = None
		self.__numberInvert = None

	def above(self, n, invert=False):
		"""
		x.above(m [, invert]) -> self
		"""
		assert type(n) in (int, str)
		self.__number = n
		assert type(invert) == bool
		self.__numberInvert = invert
		return self

	def mask(self, pLength):
		"""
		x.mask(pLength) -> self
		"""
		self.__prefixLength = pLength
		return self

	def dump(self):
		"""
		x.dump() -> str

		Return the extension part for a rule in the iptables-save form.
		"""
		result = []
		if self.__numberInvert:
			result.append('!')
		result += [
			'--connlimit-above',
			str(self.__number),
			'--connlimit-mask',
			str(self.__prefixLength)
		]
		return AbstractExtension.dump(self, Connlimit.name, " ".join(result))
