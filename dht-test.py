#!/usr/bin/env python3
import socket, os, sys

host = sys.argv[1] if len(sys.argv) > 1 else "dht.transmissiontorrent.com"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 6881
want = sys.argv[3] if len(sys.argv) > 3 else None
fam_filter = {"4": socket.AF_INET, "6": socket.AF_INET6}.get(want)

def bstr(b): return str(len(b)).encode() + b":" + b

nid, target = os.urandom(20), os.urandom(20)
a   = b"d" + bstr(b"id") + bstr(nid) + bstr(b"target") + bstr(target) + b"e"
msg = (b"d" + bstr(b"a") + a + bstr(b"q") + bstr(b"find_node")
       + bstr(b"t") + bstr(b"aa") + bstr(b"y") + bstr(b"q") + b"e")

infos = socket.getaddrinfo(host, port, fam_filter or 0, socket.SOCK_DGRAM)
if not infos:
    print(f"FAIL: no {'IPv'+want if want else ''} address for {host}"); sys.exit(1)
fam, _, _, _, addr = infos[0]

s = socket.socket(fam, socket.SOCK_DGRAM); s.settimeout(5)
try:
    s.sendto(msg, addr); data, src = s.recvfrom(4096)
except socket.timeout:
    print(f"FAIL: no response from {host}:{port} (addr {addr[0]}) within 5s"); sys.exit(1)

if b"1:y1:r" not in data:
    print(f"FAIL: got a packet but not a valid response: {data[:80]!r}"); sys.exit(1)

n4 = n6 = 0
i = data.find(b"5:nodes")
if i != -1:
    j = data.find(b":", i + 7); n4 = int(data[i+7:j]) // 26
i = data.find(b"6:nodes6")
if i != -1:
    j = data.find(b":", i + 8); n6 = int(data[i+8:j]) // 38
print(f"PASS: valid KRPC response from {src[0]}:{src[1]} "
      f"({len(data)} bytes, {n4} v4 + {n6} v6 nodes)")
