# Copyright 2012-2013, Damian Johnson
# Copyright 2012, Sean Robinson
# See LICENSE for licensing information

"""
Helper functions and classes to support tests which need to connect through
the tor network.

::

  ProxyError - Base error for proxy issues.
    +- SocksError - Reports problems returned by the SOCKS proxy.

  Socks - Communicate through a SOCKS5 proxy with a socket interface

  SocksPatch - Force socket-using code to use test.network.Socks
"""

import functools
import socket
import struct

import stem.util.connection

# Store a reference to the original class so we can find it after
# monkey patching.
_socket_socket = socket.socket

SOCKS5_NOAUTH_GREETING = (0x05, 0x01, 0x00)
SOCKS5_NOAUTH_RESPONSE = (0x05, 0x00)
SOCKS5_CONN_BY_IPV4 = (0x05, 0x01, 0x00, 0x01)
SOCKS5_CONN_BY_NAME = (0x05, 0x01, 0x00, 0x03)


class ProxyError(Exception):
  "Base error for proxy issues."


class SocksError(ProxyError):
  """
  Exception raised for any problems returned by the SOCKS proxy.

  :var int code: error code returned by the SOCKS proxy
  """

  # Error messages copied from http://en.wikipedia.org/wiki/SOCKS,
  # retrieved 2012-12-15 17:09:21.
  _ERROR_MESSAGE = {
    0x01: "general failure",
    0x02: "connection not allowed by ruleset",
    0x03: "network unreachable",
    0x04: "host unreachable",
    0x05: "connection refused by destination host",
    0x06: "TTL expired",
    0x07: "command not supported / protocol error",
    0x08: "address type not supported",
  }

  def __init__(self, code):
    self.code = code

  def __str__(self):
    code = 0x01
    if self.code in self._ERROR_MESSAGE:
      code = self.code
    return "[%s] %s" % (code, self._ERROR_MESSAGE[code])


class Socks(_socket_socket):
  """
  A **socket.socket**-like interface through a SOCKS5 proxy connection.
  Tor does not support proxy authentication, so neither does this class.

  This class supports the context manager protocol.  When used this way, the
  socket will automatically close when leaving the context.  An example:

  ::

    from test.network import Socks

    with Socks(('127.0.0.1', 9050)) as socks:
      socks.settimeout(2)
      socks.connect(('www.torproject.org', 443))
  """

  def __init__(self, proxy_addr, family = socket.AF_INET,
                  type_ = socket.SOCK_STREAM, proto = 0, _sock = None):
    """
    Creates a SOCKS5-aware socket which will route connections through the
    proxy_addr SOCKS5 proxy. Currently, only IPv4 TCP connections are
    supported, so the defaults for family and type_ are your best option.

    :param tuple proxy_addr: address of the SOCKS5 proxy, for IPv4 this
      contains (host, port)
    :param int family: address family of the socket
    :param int type_: address type of the socket (see **socket.socket** for
      more information about family and type_)

    :returns: :class:`~test.network.Socks`
    """

    _socket_socket.__init__(self, family, type_, proto, _sock)
    self._proxy_addr = proxy_addr

  def __enter__(self, *args, **kwargs):
    return self

  def __exit__(self, exit_type, value, traceback):
    self.close()
    return False

  def _recvall(self, expected_size):
    """
    Returns expected number bytes from the socket, or dies trying.

    :param int expected_size: number of bytes to return

    :returns:
      * **str** in Python 2 (bytes is str)
      * **bytes** in Python 3

    :raises:
      * :class:`socket.error` for socket errors
      * :class:`test.SocksError` if the received data was more that expected
    """

    while True:
      response = self.recv(expected_size * 2)

      if len(response) == 0:
        raise socket.error("socket closed unexpectedly?")
      elif len(response) == expected_size:
        return response
      elif len(response) > expected_size:
        raise SocksError(0x01)

  def _ints_to_bytes(self, integers):
    """
    Returns a byte string converted from integers.

    :param list integers: list of ints to convert

    :returns:
      * **str** in Python 2 (bytes is str)
      * **bytes** in Python 3
    """

    if bytes is str:
      bytes_ = ''.join([chr(x) for x in integers])  # Python 2
    else:
      bytes_ = bytes(integers)                      # Python 3
    return bytes_

  def _bytes_to_ints(self, bytes_):
    """
    Returns a tuple of integers converted from a string (Python 2) or
    bytes (Python 3).

    :param str,bytes bytes_: byte string to convert

    :returns: **list** of ints
    """

    try:
      integers = [ord(x) for x in bytes_]  # Python 2
    except TypeError:
      integers = [x for x in bytes_]       # Python 3
    return tuple(integers)

  def _pack_string(self, string_):
    """
    Returns a packed string for sending over a socket.

    :param str string_: string to convert

    :returns:
      * **str** in Python 2 (bytes is str)
      * **bytes** in Python 3
    """

    try:
      return struct.pack(">%ss" % len(string_), string_)
    except struct.error:
      # Python 3: encode str to bytes
      return struct.pack(">%ss" % len(string_), string_.encode())

  def connect(self, address):

    """
    Establishes a connection to address through the SOCKS5 proxy.

    :param tuple address: target address, for IPv4 this contains
      (host, port)

    :raises: :class:`test.SocksError` for any errors
    """

    _socket_socket.connect(self, (self._proxy_addr[0], self._proxy_addr[1]))
    # ask for non-authenticated connection
    self.sendall(self._ints_to_bytes(SOCKS5_NOAUTH_GREETING))
    response = self._bytes_to_ints(self._recvall(2))
    if response != SOCKS5_NOAUTH_RESPONSE:
      raise SocksError(0x01)

    if stem.util.connection.is_valid_ipv4_address(address[0]):
      header = self._ints_to_bytes(SOCKS5_CONN_BY_IPV4)
      header = header + socket.inet_aton(address[0])
    else:
      # As a last gasp, try connecting by name
      header = self._ints_to_bytes(SOCKS5_CONN_BY_NAME)
      header = header + self._ints_to_bytes([len(address[0])])
      header = header + self._pack_string(address[0])

    header = header + struct.pack(">H", address[1])
    self.sendall(header)
    response = self._bytes_to_ints(self._recvall(10))
    # check the status byte
    if response[1] != 0x00:
      raise SocksError(response[1])

  def connect_ex(self, address):
    """
    Not Implemented.
    """

    raise NotImplementedError


class SocksPatch(object):
  """
  Monkey-patch **socket.socket** to use :class:`~test.network.Socks`, instead.
  Classes in the patched context (e.g. urllib.urlopen in the example below)
  do not use the SOCKS5 proxy for domain name resolution and such information
  may be leaked.

  ::

    import urllib
    from test.network import SocksPatch

    with SocksPatch(('127.0.0.1', 9050)):
      with urllib.urlopen("https://www.torproject.org") as f:
        for line in f.readline():
          print line
  """

  def __init__(self, *args, **kwargs):
    self._partial = functools.partial(Socks, *args, **kwargs)

  def __enter__(self):
    socket.socket = self._partial
    return self

  def __exit__(self, exit_type, value, traceback):
    socket.socket = _socket_socket
