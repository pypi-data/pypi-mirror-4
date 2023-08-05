
This library is a thin and fast cython wrapper around libhdfs.   
It allows easy access files stored in HDFS from python.


Simple usage example:

    :::python
    import cyhdfs

    conn = cyhdfs.HDFSConnection('namenode_hostname', 54310, 'hduser')

    test_file = conn.open_file("/tmp/cyhdfs/test.txt", os.O_WRONLY)
    bytes_written = test_file.write("Hello world.")
    test_file.close()

    conn.delete("/tmp/cyhdfs")
    conn.close()

See other usage examples in example directory in source.

Note:
    First Call to libhdfs API takes long time because Java initializes its jvm.
    Further call takes significally less time. So if you going to timeit - please 
    take it into account.  
    I have been able to write into HDFS using this lib with speed of 90Mb per second on a
    1Gb channel.

