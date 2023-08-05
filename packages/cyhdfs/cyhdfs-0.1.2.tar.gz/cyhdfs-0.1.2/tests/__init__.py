#!/usr/bin/env python

import cyhdfs
from os import O_WRONLY, O_RDONLY
import random
import inspect
from pprint import pprint

from nose.tools import assert_raises, raises, eq_

conn = None

def setUp():
    global conn
    conn = cyhdfs.HDFSConnection('namenode_host', 54310, 'hduser')
    conn.mkdir("/tmp/cyhdfs")


def tearDown():
    conn.delete("/tmp/cyhdfs")
    conn.close()

def rn():
    """ random name """
    return "/tmp/cyhdfs/test_%s_.%0.6f" % (inspect.stack()[1][3], random.random())


def create_file_helper(name, data = "Hello world"):
    test_file = conn.open_file(name, O_WRONLY)
    test_file.write(data)
    test_file.close()

def test_write():
    name = rn()
    test_file = conn.open_file(name, O_WRONLY)
    test_file.write("Hello world")
    test_file.close()

def test_write_closed():
    name = rn()
    test_file = conn.open_file(name, O_WRONLY)
    test_file.close()
    with assert_raises(cyhdfs.HDFSIOError):
        test_file.write("Hello world")


def test_write_and_read():
    name = rn()
    test_str = "".join([chr(i) for i in range(256)])
    create_file_helper(name, test_str)
    r_file = conn.open_file(name, O_RDONLY)
    b_read, read_data = r_file.read(256)
    r_file.close()
    eq_(b_read, len(test_str))
    eq_(read_data, test_str)


def test_pread():
    name = rn()
    test_str = "".join([chr(i) for i in range(256)])
    create_file_helper(name, test_str)
    r_file = conn.open_file(name, O_RDONLY)
    b_read, read_data = r_file.pread(128, 128)
    r_file.close()
    eq_(b_read, 128)
    eq_(read_data, test_str[128:])


def test_hflush():
    name = rn()
    w_file = conn.open_file(name, O_WRONLY)
    w_file.write("Hello!")
    w_file.hflush()

    r_file = conn.open_file(name, O_RDONLY)
    b_read, read_data =  r_file.read(6)

    w_file.close()
    r_file.close()
    eq_(read_data, "Hello!")


def test_exists():
    name = rn()
    eq_(conn.exists("/tmp/cyhdfs"), True)
    eq_(conn.exists(name), False)


def test_chmod():
    name = rn()
    create_file_helper(name)
    conn.chmod(name, 0666)
    info = conn.path_info(name)
    eq_(info.permissions,0666)



def test_chown():
    name = rn()
    create_file_helper(name)
    conn.chown(name, "hive", "")
    info = conn.path_info(name)
    eq_(info.owner, "hive")

def test_noop():
    print "     used: %d bytes" % conn.used()
    print " capacity: %d bytes" % conn.capacity()
    print "default block size: %d" % conn.get_default_blocksize()


def test_set_cmd():
    original_cmd = conn.get_cwd()
    conn.set_cwd("/tmp/cyhdfs")
    eq_(conn.get_cwd(), "/tmp/cyhdfs")
    # restore
    conn.set_cwd( original_cmd )


def test_set_replication():
    name = rn()
    create_file_helper(name)
    conn.set_replication(name,1)
    info = conn.path_info(name)
    eq_(info.replication,1)


def test_get_hosts():
    name = rn()
    create_file_helper(name)
    print "get_hosts: %s " % conn.get_hosts(name, 0, 5)


def test_listdir():
    pprint(conn.list_dir("/tmp/cyhdfs"))


def test_tell():
    name = rn()
    test_file = conn.open_file(name, O_WRONLY)
    test_file.write("Hello")
    eq_(test_file.tell(), 5)
    test_file.close()

def test_seek():
    name = rn()
    test_file = conn.open_file(name, O_WRONLY)
    test_file.write("Hello world")
    test_file.close()

    r_file = conn.open_file(name, O_RDONLY)
    r_file.seek(5)
    _, data = r_file.read(1024)
    eq_(data, " world")


@raises(cyhdfs.HDFSIOError)
def test_open_non_exist_file():
    conn.open_file(rn(), O_RDONLY)






