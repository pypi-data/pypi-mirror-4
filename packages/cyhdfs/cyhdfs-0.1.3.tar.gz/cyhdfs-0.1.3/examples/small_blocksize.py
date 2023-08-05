#!/usr/bin/env python

import cyhdfs
from os import O_WRONLY, O_RDONLY
import os

from conf import *

conn = cyhdfs.HDFSConnection(HOST, 54310, USER)
conn.mkdir("/tmp/cyhdfs")

print "Default block size: %d" % conn.get_default_blocksize()
print "Capacity: %d" % conn.capacity()
print "Used: %d" % conn.used()

test_file = conn.open_file("/tmp/cyhdfs/test.txt", O_WRONLY, blocksize = 512)
wr = test_file.write("Hello from %s system.\n" % str(os.uname()) * 100)
print "%d bytes written" % wr
test_file.close()

print "Used: %d" % conn.used()

print "Exists:", 
print conn.exists("/tmp/cyhdfs/test.txt")
print 

print "ListDir:",
print conn.list_dir("/tmp/cyhdfs")
print 

print "PathInfo:",
print conn.path_info("/tmp/cyhdfs/test.txt")
print 

print "GetHosts:", 
print conn.get_hosts("/tmp/cyhdfs/test.txt", 0, 2048)
print 

conn.delete("/tmp/cyhdfs/test.txt")
print "Exists after delete:", 
print conn.exists("/tmp/cyhdfs/test.txt")
print 

conn.delete("/tmp/cyhdfs")
conn.close()

