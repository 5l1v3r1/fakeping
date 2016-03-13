#!/usr/bin/python
#
# Uses Scapy to send ping to the destination networks with any dest IP and source IP
#
# Requires root privileges and configuration before use
#
# Licensed under the GPL (v2), please see the COPYING file that accompanies this
# program, or https://github.com/majava3000/fakeping
#

import sys, os

# disable stderr while importing scapy to get rid of ipv6 default route missing
real = (sys.stdout, sys.stderr)
sys.stdout, sys.stderr = open('/dev/null','w'), open('/dev/null','w')
from scapy.all import Ether, IP, ICMP, sendp, conf
sys.stdout, sys.stderr = real

# disable verbosity of Scapy, we don't really need it
conf.verb = False

# This is the routing table to load.
# It assumes that local interfaces are configured, up and the gateways
# are available through them
#
# Order: network, via gateway. And no, Scapy doesn't parse shorthand
# CIDR networks so you'll have to spell out the four octets (yup, it's
# slightly meh).
#
# Note that locally connected networks will be automatically in the
# Scapy internal FDB, so don't add them. Also note that default
# gateways will be removed from the Scapy FDB for your (and our) safety.
#
#ROUTES = (
#  ( "10.0.0.0/16",   "192.168.0.1"),
#  ( "172.16.4.0/23", "192.168.200.201"),
#  ( "1.2.3.4/24",    "10.123.123.23") )
#
# When you have configured the ROUTES list above, comment the
# the two lines below. Yup, it's ugly.

print >> sys.stderr, "You have to configure your virtual route table (edit the source code)"
sys.exit(1)

def printUsageAndExit():
  print >> sys.stderr, """USAGE: fakeping.py source-ip dest-ip

fakeping contains a built in list of routes that will be selected based on
destination only (it might be extended to eval src-ip at some point, and
use a different routing table because of that). It will then generate
the ICMP echo request packet on the upstream interface going to the
next router. It doesn't listen for responses (use this:
 sudo tcpdump -e -i eth0 -n -s0
). In order to run properly, fakeping needs root access"""
  sys.exit(1)

if __name__ == '__main__':

  if len(sys.argv) != 3:
    printUsageAndExit()
  sourceIP = sys.argv[1]
  destIP = sys.argv[2]

  # check that we have effective root
  if os.geteuid() != 0:
    print >> sys.stderr, "\nNOT ROOT (operations will probably fail)\n"
    # continue anyway

  # start by creating the local routing table
  # we need to blow away the old default gateway though.
  delEntries = []
  for idx in range(len(conf.route.routes)):
    destNet, destMask, dummy1, dummy2, dummy3 = conf.route.routes[idx]
    if destNet == 0 and destMask == 0:
      delEntries.append(conf.route.routes[idx])
  # remove them all
  for e in delEntries:
    conf.route.remove(e)
  #print conf.route

  # make the table
  for network, via in ROUTES:
    conf.route.add(net=network, gw=via)

  conf.route.invalidate_cache()
  #print conf.route

  # check whether the destination can be routed
  resp = conf.route.route(destIP)
  if resp[0] == 'lo':
    print >> sys.stderr, "Don't know how to route to %s, please check your params" % destIP
    sys.exit(1)
  # otherwise we get the interface to send on
  sendIface = resp[0]

  # form the test packet
  tp = Ether()/IP(dst=destIP,src=sourceIP)/ICMP()
  sendp(tp, iface=sendIface)
  print "Sent (hopefully)"
