#!/usr/bin/env python

import cyhdfs
from os import O_WRONLY, O_RDONLY
import os

from conf import *

conn = cyhdfs.HDFSConnection(HOST, 54310, USER)
conn.mkdir("/tmp/cyhdfs")

test_file = conn.open_file("/tmp/cyhdfs/test.txt", O_WRONLY)
wr = test_file.write("Hello from %s system." % str(os.uname()))
print "%d bytes written" % wr
test_file.close()

r_file = conn.open_file("/tmp/cyhdfs/test.txt", O_RDONLY)
rd_tuple = r_file.read(r_file.avail())
print "%d bytes read: %s" % rd_tuple
r_file.close()

conn.delete("/tmp/cyhdfs")
conn.close()

