fakeping
========

A simple tool which I needed while testing routing across policy routed networks
without actual hosts but with one part of the path implemented by a Linux
box running policy routing. It can be useful for other scenarios as well,
when it's necessary to "fake" test traffic from networks that don't have
anything connected to them.

Unfortunately the program needs root privileges AND is python. So will not
want to use this in a production setup.

Basic operation
---------------

Since it's likely that the box on which you run this program has policy routing
in place, it's useful to know that Scapy actually implements its own FDB (alas
only a global one).

Upon startup, Scapy inits this FDB based on local FDBs (i.e., the old boring
regular routing table) which might contain a default route or several.

So that this program won't send traffic on dangerous paths, the default
gateways are removed automatically from the Scapy FDB (fear not, the actual
FDBs are not touched by this program. At least not intentionally).

After that, the Scapy routing table is populated with new network routes
which are hardcoded in the top of the source (destination network and
locally connected via gateway pairs, which you will want to modify). If
someone will implement a sane configuration method for these, feel free
to do a pull request.

In order to send actual traffic, we "bypass" the regular Scapy L3 send, and
use L2 send instead. For this to work, we select the sending interface
based on the Scapy internal FDB. So far in my scenarios it has worked
well, but you might want to add support for specifying the output interface
explicitly on command line.

Once the output route is chosen, we just let Scapy form the L2 packet
and send it on the selected interface. The program does only one send,
and does not wait for responses. Because of this, it's useful to run
something like:

sudo tcpdump -e -i eth0 -n -s0

in another ssh terminal (I use tagged VLANs which all fall on eth0 in
this case, your scenario might obviously be different).

Parting words
-------------

Development methodology for this project was the Ballmer Peak. Be warned.
I don't really expect anything to find this useful, but if you do, drop
me a note and help me stay on the peak.
