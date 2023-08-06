class AbstractTarget:
	"""
	Is a abstract class for targets.
	"""
	def __init__(self, ipv=(4, 6)):
		"""
		x.__init__([ipv])

		Constructor.
		ipv is a tuple of allow ip versions.
		"""
		self._ipv_list = ipv

	def provideIPVersion(self):
		"""
		x.provideIPVersion() -> tuple
		"""
		return self._ipv_list

class Log(AbstractTarget):
	"""
	The log target extension.
	"""
	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractTarget.__init__(self)
		self.__level = None
		self.__prefix = None
		self.__tcpOptions = None
		self.__ipOptions = None
		self.__uid = None

	def level(self, level):
		"""
		x.level(level) -> self
		"""
		self.__level = level
		return self

	def prefix(self, prefix):
		"""
		x.prefix() -> self
		"""
		self.__prefix = prefix
		return self

	def tcpOptions(self):
		"""
		x.tcpOptions() -> self
		"""
		self.__tcpOptions = True
		return self

	def ipOptions(self):
		"""
		x.ipOptions() -> self
		"""
		self.__ipOptions = True
		return self

	def uid(self):
		"""
		x.uid() -> self
		"""
		self.__uid = True
		return self

	def __str__(self):
		"""
		x.__str__() -> str
		"""
		result = ["LOG"]
		if self.__level:
			result += ("--log-level", self.__level)
		if self.__prefix:
			result.append("--log-prefix \"%s \"" % self.__prefix)
		if self.__tcpOptions:
			result.append("--log-tcp-options")
		if self.__uid:
			result.append("--log-uid")
		return " ".join(result)

class Masquerade(AbstractTarget):
	"""
	The masquerade target extension.
	"""
	def __init__(self):
		"""
		x.__init__()

		Constructor.
		"""
		AbstractTarget.__init__(self, (4,))
		self.__random = None

	def random(self):
		"""
		x.random() -> self
		"""
		self.__random = True
		return self

	def __str__(self):
		"""
		x.__str__() -> str
		"""
		result = ["MASQUERADE"]
		if self.__random:
			result.append("--random")
		return " ".join(result)

REJECT_ICMP_NET_UNREACHABLE = "icmp-net-unreachable"
REJECT_ICMP_NET_PROHIBITED = "icmp-net-prohibited"
REJECT_ICMP_HOST_UNREACHABLE = "icmp-host-unreachable"
REJECT_ICMP_HOST_PROHIBITED = "icmp-host-prohibited"
REJECT_ICMP_PORT_UNREACHABLE = "icmp-port-unreachable"
REJECT_ICMP_PROTO_UNREACHABLE = "icmp-proto-unreachable"
REJECT_ICMP_ADMIN_PROHIBITED = "icmp-admin-prohibited"
REJECT_TCP_RESET = "tcp-reset"
REJECT_ICMP6_NO_ROUTE = "icmp6-no-route"
REJECT_NO_ROUTE = "no-route"
REJECT_ICMP6_ADM_PROHIBITED = "icmp6-adm-prohibited"
REJECT_ADM_PROHIBITED = "adm-prohibited"
REJECT_ICMP6_ADDR_UNREACHABLE = "icmp6-addr-unreachable"
REJECT_ADDR_UNRECHABLE = "addr-unreachable"
REJECT_ICMP6_PORT_UNRECHABLE = "icmp6-port-unreachable"
REJECT_PORT_UNREACH = "port-unreach"
_REJECT_ALL_ = (REJECT_ICMP_NET_UNREACHABLE, REJECT_ICMP_NET_PROHIBITED, REJECT_ICMP_HOST_UNREACHABLE, REJECT_ICMP_HOST_PROHIBITED, REJECT_ICMP_PORT_UNREACHABLE, REJECT_ICMP_PROTO_UNREACHABLE, REJECT_ICMP_ADMIN_PROHIBITED, REJECT_TCP_RESET, REJECT_ICMP6_NO_ROUTE, REJECT_NO_ROUTE, REJECT_ICMP6_ADM_PROHIBITED, REJECT_ADM_PROHIBITED, REJECT_ICMP6_ADDR_UNREACHABLE, REJECT_ADDR_UNRECHABLE, REJECT_ICMP6_PORT_UNRECHABLE, REJECT_PORT_UNREACH)

class Reject:
	"""
	The reject target extension.
	"""
	def __init__(self, type=None):
		"""
		x.__init__()

		Constructor.
		"""
		assert type in _REJECT_ALL_ + (None,)
		self.__type = type

	def provideIPVersion(self):
		"""
		x.provideIPVersion() -> tuple
		"""
		if self.__type and self.__type != REJECT_TCP_RESET:
			if '6' in self.__type:
				return (6,)
			else:
				return (4,)
		else:
			return (4, 6)

	def __str__(self):
		"""
		x.__str__() -> str
		"""
		result = ["REJECT"]
		if self.__type:
			result += ("--reject-with", self.__type)
		return " ".join(result)
