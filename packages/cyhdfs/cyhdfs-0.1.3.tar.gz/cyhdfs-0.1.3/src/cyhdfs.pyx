#cython: embedsignature=True

# cython imports
from libc.stdlib cimport malloc, free
from libc.stdint cimport *
from posix.fcntl cimport O_RDONLY, O_WRONLY

from cpython cimport PyErr_SetFromErrno
from cpython.string cimport PyString_GET_SIZE, PyString_Check, PyString_AS_STRING

# python imports
import os
from collections import namedtuple

DEF USE_STATS = 1
DEF MAX_PATH_LENGTH = 1024

include "config.pxi"

cdef extern from "hdfs.h":
    ctypedef void * hdfsFS

    ctypedef int32_t tSize
    ctypedef long    tTime
    ctypedef int64_t tOffset
    ctypedef uint16_t tPort

    ctypedef struct hdfsFile_internal
    ctypedef hdfsFile_internal* hdfsFile

    ctypedef enum tObjectKind:
        kObjectKindFile
        kObjectKindDirectory

    ctypedef struct hdfsFileInfo:
        tObjectKind mKind
        char *mName
        tTime mLastMod
        tOffset mSize
        short mReplication
        tOffset mBlockSize
        char *mOwner
        char *mGroup
        short mPermissions
        tTime mLastAccess

    hdfsFS hdfsConnectAsUser(char* host, tPort port, char *user)
    hdfsFS hdfsConnect(char* host, tPort port)

    hdfsFS hdfsConnectAsUserNewInstance(char* host, tPort port, char *user )
    hdfsFS hdfsConnectNewInstance(char* host, tPort port)
    hdfsFS hdfsConnectPath(char* uri)

    int hdfsDisconnect(hdfsFS fs)

    int hdfsExists(hdfsFS fs, char *path)
    int hdfsSeek(hdfsFS fs, hdfsFile file, tOffset desiredPos)
    tOffset hdfsTell(hdfsFS fs, hdfsFile file)

    tSize hdfsPread(hdfsFS fs, hdfsFile file, tOffset position, void* buffer, tSize length)

    int hdfsFlush(hdfsFS fs, hdfsFile file)
    IF HADOOP_HAS_HFLUSH:
        int hdfsHFlush(hdfsFS fs, hdfsFile file)
    int hdfsAvailable(hdfsFS fs, hdfsFile file)

    hdfsFile hdfsOpenFile(hdfsFS fs, char* path, int flags, int bufferSize, short replication, tSize blocksize)
    int hdfsCloseFile(hdfsFS fs, hdfsFile file)

    int hdfsRead(hdfsFS fs, hdfsFile file, void* buffer, tSize length)
    int hdfsWrite(hdfsFS fs, hdfsFile file, void* buffer,  tSize length)


    IF HADOOP_DELETE_RECURSIVE:
        int hdfsDelete(hdfsFS fs, char* path, int recursive)
    ELSE:
        int hdfsDelete(hdfsFS fs, char* path)

    int hdfsRename(hdfsFS fs, char* oldPath, char* newPath)

    char* hdfsGetWorkingDirectory(hdfsFS fs, char *buffer, size_t bufferSize)
    int hdfsSetWorkingDirectory(hdfsFS fs, char* path)

    int hdfsCreateDirectory(hdfsFS fs, char* path)
    int hdfsSetReplication(hdfsFS fs, char* path, int16_t replication)

    tOffset hdfsGetDefaultBlockSize(hdfsFS fs)
    tOffset hdfsGetCapacity(hdfsFS fs)
    tOffset hdfsGetUsed(hdfsFS fs)

    int hdfsChown(hdfsFS fs, char* path, char *owner, char *group)
    int hdfsChmod(hdfsFS fs, char* path, short mode)

    int hdfsUtime(hdfsFS fs, char* path, tTime mtime, tTime atime)

    int hdfsCopy(hdfsFS srcFS, char* src, hdfsFS dstFS, char* dst)
    int hdfsMove(hdfsFS srcFS, char* src, hdfsFS dstFS, char* dst)

    hdfsFileInfo *hdfsListDirectory(hdfsFS fs, char* path, int *numEntries)
    void hdfsFreeFileInfo(hdfsFileInfo *hdfsFileInfo, int numEntries)
    hdfsFileInfo *hdfsGetPathInfo(hdfsFS fs, char* path)

    char*** hdfsGetHosts(hdfsFS fs, char* path, tOffset start, tOffset length)
    void hdfsFreeHosts(char ***blockHosts)


cdef extern from *:
    # compile time definition
    cdef char * _CLASSPATH


# Module level constants
# hadoop object kinds
ENTRY_KIND_DIR = kObjectKindDirectory
ENTRY_KIND_FILE = kObjectKindFile

# struct hdfsFileInfo
# returned by hdfsListDirectory and hdfsGetPathInfo
EntryInfo = namedtuple('EntryInfo', ['kind', 'name', 'last_mod', 'size', 'replication', 'blocksize', 'owner', 'group', 'permissions', 'last_access'])

Stats = namedtuple('WriteStats', ['write_ops', 'write_bytes', 'read_ops', 'read_bytes'])

# Module exceptions
class HDFSError(Exception):
    pass

class HDFSConnectionError(HDFSError):
    pass

class HDFSIOError(HDFSError):
    pass

if 'CLASSPATH' not in os.environ:
    # set compile time classpath if not set
    if _CLASSPATH != b"":
        os.environ['CLASSPATH'] = _CLASSPATH
    else:
        raise HDFSError("environmnet variable CLASSPATH not set")


"""
    EntryInfo - named tuple representing info about file.
        .kind - object kind (cyhdfs.ENTRY_KIND_DIR or cyhdfs.ENTRY_KIND_FILE)
"""


cdef class HDFSfs:

    cdef:
        hdfsFS fs

    def __init__(self):
        raise TypeError("this class cant be instantinated from python")

    def __dealloc__(self):
        cdef int ret
        ret = hdfsDisconnect(self.fs)

        #if ret < 0:
        #    raise HDFSConnectionError("hdfsDisconnect error in %s" % repr(self))




cdef class HDFSConnection:
    """
        HDFSConnection.__init__(host = 'default', unsigned short port = 0, user = '')
         * @param host A string containing either a host name, or an ip address
         * of the namenode of a hdfs cluster. host should be passed as empry string '' if
         * you want to connect to local filesystem. host should be passed as
         * 'default' (and port as 0) to used the 'configured' filesystem
         * (core-site/core-default.xml).
         * @param port The port on which the server is listening.
         * @param user the user name (this is hadoop domain user). Or empry string '' is equivelant to hhdfsConnect(host, port)

        :Example:

        import os
        conn = HDFSConnection("1.1.1.1", 54310, 'hduser')
        conn.mkdir("/tmp/cyhdfs")

        test_file = conn.open_file("/tmp/cyhdfs/hello_world.txt", os.O_WRONLY)
        test_file.write("hello world")
        test_file.flush()
        test_file.close()

        print conn.list_dir("/tmp/cyhdfs")

        conn.delete("/tmp/cyhdfs")
        conn.close()

    """
    cdef:
        hdfsFS fs
        object host
        object user
        unsigned short port

        HDFSfs hdfsfs

    def __repr__(self):
        return "<HDFSConnection host=%s port=%s user=%s >" % (self.host, self.port, self.user)

    def __cinit__(self, host = 'default', unsigned short port = 0, user = ''):
        cdef:
            char * _host

        if not PyString_Check(host):
            raise TypeError("host must be of type string got %s instead." % type(host))

        if not PyString_Check(user):
            raise TypeError("user must be of type string got %s instead." % type(host))

        self.host = host
        self.user = user
        self.port = port

        if not PyString_GET_SIZE(host):
            _host = NULL
        else:
            _host = PyString_AS_STRING(host)

        if PyString_GET_SIZE(user):
            fs = hdfsConnectAsUser(_host, port, PyString_AS_STRING(user))
        else:
            fs = hdfsConnect(_host, port)
        if fs is NULL:
            raise HDFSConnectionError("Cant connect to %s:%d" % (host, port))

        self.fs = fs
        self.hdfsfs = HDFSfs.__new__(HDFSfs)
        self.hdfsfs.fs = fs


    def utime(self, char * path, tTime mtime, tTime, atime):
        """
            :param path: the path to the file or directory
            :param mtime: new modification time or 0 for only set access time in seconds
            :param atime: new access time or 0 for only set modification time in seconds
            :return: None
        """
        if hdfsUtime(self.fs, path, mtime, atime) < 0:
            raise HDFSIOError("hdfsUtime error in %s" % repr(self))


    def chmod(self, char * path, short mode):
        """
            :param path: the path to the file or directory
            :param mode: the bitmask to set it to
            :return: None
        """
        if hdfsChmod(self.fs, path, mode) < 0:
            raise HDFSIOError("hdfsChmod error in %s" % repr(self))


    def chown(self, char * path, char * owner, char * group):
        """
            :param path: the path to the file or directory
            :param owner: this is a string in Hadoop land. Set to "" if only setting group
            :param group: this is a string in Hadoop land. Set to "" if only setting user
            :return: None
        """
        if hdfsChown(self.fs, path, owner, group) < 0:
            raise HDFSIOError("hdfsChown error in %s" % repr(self))


    def used(self):
        """
            :return: the total raw size of all files in the filesystem.
        """
        cdef:
            tOffset ret
        ret = hdfsGetUsed(self.fs)
        if ret < 0:
            raise HDFSIOError("hdfsGetUsed error in %s" % repr(self))
        return ret

    def capacity(self):
        """
            :return: the raw capacity of the filesystem.
        """
        cdef:
            tOffset ret
        ret = hdfsGetCapacity(self.fs)
        if ret < 0:
            raise HDFSIOError("hdfsGetCapacity error in %s" % repr(self))
        return ret

    def get_default_blocksize(self):
        """
            :return: default configured block size
        """
        cdef:
            tOffset ret
        ret = hdfsGetDefaultBlockSize(self.fs)
        if ret < 0:
            raise HDFSIOError("hdfsGetDefaultBlockSize error in %s" % repr(self))
        return ret


    def open_file(self, path, int flags, int bufferSize = 0, short replication = 0, int blocksize = 0):
        """
            :param path: The full path to the file.
            :param flags: - an | of bits/fcntl.h file flags - supported flags are O_RDONLY, O_WRONLY (meaning create or overwrite i.e., implies O_TRUNCAT).
            :param bufferSize: Size of buffer for read/write - pass 0 if you want to use the default configured values.
            :param replication: Block replication - pass 0 if you want to use  the default configured values.
            :param blocksize: Size of block - pass 0 if you want to use the default configured values.
            :return: opened file instance
            :rtype: HDFSReadFile or HDFSWriteFile instance
        """
        cdef:
            HDFSWriteFile hdfs_w_file
            HDFSReadFile hdfs_r_file
        if not PyString_Check(path):
            raise TypeError("expected string type got %s instead." % type(path))

        h_file = hdfsOpenFile(self.fs, PyString_AS_STRING(path), flags, bufferSize, replication, blocksize)
        if h_file is NULL:
            raise HDFSIOError("""Cant open file at "%s" flags=%d bufferSize=%d replication=%d blocksize=%d""" % (
            path, flags, bufferSize, replication, blocksize))

        if flags & O_WRONLY == O_WRONLY:
            fl = HDFSWriteFile.__new__(HDFSWriteFile)
        elif flags & O_RDONLY == O_RDONLY:
            fl = HDFSReadFile.__new__(HDFSReadFile)
        else:
            raise HDFSIOError("Open mode %d not supported." % flags)
        hdfs_file_factory(fl, self.hdfsfs, path, h_file, flags, bufferSize, replication, blocksize)
        return fl

    def exists(self, char * path):
        """
            :return: Checks if a given path exsits on the filesystem
            :rtype: bool
        """
        if hdfsExists(self.fs, path) == 0:
            return True
        return False


    def delete(self, char * path, int recursive = 1):
        """
            Delete file
            :param path: The path of the file.
            :return: None
        """
        cdef:
            int res
        IF HADOOP_DELETE_RECURSIVE:
            res = hdfsDelete(self.fs, path, recursive)
        ELSE:
            res = hdfsDelete(self.fs, path)
        if res < 0:
            raise HDFSIOError("hdfsDelete error in %s" % repr(self))

    def rename(self, char * old_path, char * new_path):
        """
            Rename file.
            :param oldPath: The path of the source file. 
            :param newPath: The path of the destination file. 
            :return: None
        """
        if hdfsRename(self.fs, old_path, new_path) < 0:
            raise HDFSIOError("hdfsRename error in %s" % repr(self))



    def get_cwd(self):
        """
            Get the current working directory for the given filesystem.
            :return: current working directory path
            :rtype: string

            .. note::
                max path length can be set at compile time defaults to 1024
        """
        cdef:
            char * ret
            char[MAX_PATH_LENGTH] buf
        ret = hdfsGetWorkingDirectory(self.fs, buf, MAX_PATH_LENGTH)
        if ret is NULL:
            raise HDFSError("hdfsGetWorkingDirectory error in %s" % repr(self))
        return ret

    def set_cwd(self, char * path):
        """
            Set the working directory. All relative  paths will be resolved relative to it.
            :param path: The path of the new 'cwd'. 
            :return: None
        """
        if hdfsSetWorkingDirectory(self.fs,path) < 0:
            raise HDFSIOError("hdfsSetWorkingDirectory error in %s" % repr(self))


    def set_replication(self, char * path, int16_t replication):
        """
            Set the replication of the specified file to the supplied value
            :param path: The path of the file. 
            :return: None
        """
        if hdfsSetReplication(self.fs, path, replication) < 0:
            raise HDFSIOError("hdfsSetReplication error in %s" % repr(self))


    def mkdir(self, char * path):
        """
            Make the given file and all non-existent parents into directories.
            :param path: The path of the directory. 
            :return: None
        """
        if hdfsCreateDirectory(self.fs, path) < 0:
            raise HDFSIOError("hdfsCreateDirectory error in %s" % repr(self))


    def list_dir(self, char * path):
        """
            Get list of files/directories for a given directory-path. 
            :param path: The path of the directory. 
            :rtype: List of EntryInfo instances

        """
        cdef:
            int i = 0
            int num_entries = 0
            hdfsFileInfo * entry_list  # entry list
            hdfsFileInfo entry

        entry_list = hdfsListDirectory(self.fs, path, &num_entries)
        if entry_list is NULL:
            raise HDFSIOError("hdfsListDirectory(path=%s) error in %s" % (path, repr(self)))
        if num_entries == 0:
            return []
        try:
            ret_list = []
            while i < num_entries:
                entry = entry_list[i]
                e = EntryInfo(entry.mKind, 
                              entry.mName, 
                              entry.mLastMod, 
                              entry.mSize, 
                              entry.mReplication, 
                              entry.mBlockSize, 
                              entry.mOwner, 
                              entry.mGroup, 
                              entry.mPermissions, 
                              entry.mLastAccess)
                ret_list.append(e)
                i += 1
        finally:
            hdfsFreeFileInfo(entry_list, num_entries)
        return ret_list

    def path_info(self, char * path):
        """
            Get information about a path.
            :param path: The path of the file. 
            :rtype: list of EntryInfo instances

            :Example:

            conn.path_info('/tmp/cyhdfs/test.txt') ->
            EntryInfo(kind=70, 
                      name='hdfs://foo.ru:54310/tmp/cyhdfs/test.txt', 
                      last_mod=1347653165, 
                      size=0, 
                      replication=3, 
                      blocksize=67108864, 
                      owner='hduser', 
                      group='supergroup', 
                      permissions=420, 
                      last_access=1347653165
                    )

        """
        cdef hdfsFileInfo * entry

        entry = hdfsGetPathInfo(self.fs, path)
        if entry is NULL:
            raise HDFSError("hdfsGetPathInfo(path=%s) error in %s" % (path, repr(self)))
        try:
            e = EntryInfo(entry.mKind, 
                          entry.mName, 
                          entry.mLastMod, 
                          entry.mSize, 
                          entry.mReplication, 
                          entry.mBlockSize, 
                          entry.mOwner, 
                          entry.mGroup, 
                          entry.mPermissions, 
                          entry.mLastAccess)
        finally:
            hdfsFreeFileInfo(entry, 1)
        return e

    def get_hosts(self, char * path, tOffset start, tOffset length):
        """
            Get hostnames where a particular block (determined by
             pos & blocksize) of a file is stored. 
            :param path: The path of the file. 
            :param start: The start of the block.
            :param length: The length of the block.

            :Example:

            conn.get_hosts("/tmp/cyhdfs/test.txt", 0, 5) -> [['node1.foo.com', 'node2.foo.com']]
        """
        cdef:
            int block = 0
            int host
            char ** _tmp_hosts
            char *** hosts

        hosts = hdfsGetHosts(self.fs, path, start, length)
        if hosts is NULL:
            raise HDFSError("hdfsGetHosts(path=%s start=%s length=%s) error in %s" % (path, start, length, repr(self)))
        try:
            result = []
            while 1:
                if hosts[block] is NULL:
                    break
                _tmp_hosts =  hosts[block]
                block_hosts = []
                result.append(block_hosts)
                host = 0
                while 1:
                    if _tmp_hosts[host] is NULL:
                        break
                    block_hosts.append(_tmp_hosts[host])
                    host += 1
                block += 1
        finally:
            hdfsFreeHosts(hosts)
        return result


    def close(self):
        """
            Closes all opened with this connection object files.
            Then calls hdfsDisconnect.
            Any usage of files opened with this connection after this call will raise error.
        """
        pass



cdef class HDFSFile:
    """
        This is a base class for 
        HDFSWriteFile and HDFSReadFile and is not meant
        to be instantinated from python.
    """
    cdef:
        hdfsFile h_file
        hdfsFS fs

        HDFSfs hdfsfs

        object path
        int flags
        int bufferSize
        short replication
        int blocksize

        int _open

    IF USE_STATS:
        cdef unsigned long long _write_ops
        cdef unsigned long long _write_bytes
        cdef unsigned long long _read_ops
        cdef unsigned long long _read_bytes

        def get_stats(self):
            return Stats(self._write_ops, self._write_bytes, self._read_ops, self._read_bytes)

    def __init__(self):
        raise TypeError("This class cannot be instantiated from Python")

    def __repr__(self):
        return """<HDFSFile path="%s" is_open=%d flags=%d bufferSize=%d replication=%d blocksize=%d>""" % (self.path, self._open, self.flags, self.bufferSize, self.replication, self.blocksize)


    def tell(self):
        """
            Get the current offset in the file, in bytes.
            :rtype: int
        """
        cdef tOffset ret
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        ret = hdfsTell(self.fs, self.h_file)
        if ret < 0:
            raise HDFSIOError("hdfsTell returned error code file: %s" % repr(self))
        return ret

    cdef int _close(self):
        cdef:
            int ret
        if self._open:
            ret = hdfsCloseFile(self.fs, self.h_file)
            if ret == 0:
                self._open = 0
            return ret
        return 0


    def close(self):
        """
            Closes file.

            .. note::
                may raise HDFSIOError error.
        """
        cdef:
            int ret

        if not self._open:
            raise HDFSIOError("%s already closed" % repr(self))
        ret = self._close()
        if ret < 0:
            raise HDFSIOError("Cant close: %s" % repr(self))


    def __dealloc__(self):
        if self._open:
            self.close()


cdef class HDFSReadFile(HDFSFile):

    def avail(self):
        """
            :return: Number of bytes that can be read from this input stream without blocking.
            :rtype: int
        """
        cdef int ret
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        ret = hdfsAvailable(self.fs, self.h_file)
        if ret < 0:
            raise HDFSIOError("hdfsAvailable returned error code file: %s" % repr(self))
        return ret

    def seek(self, tOffset pos):
        """
            Seek to given offset in file. 
            This works only for files opened in read-only mode. 
            :param desiredPos: Offset into the file to seek into.
            :return: None
        """
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        if hdfsSeek(self.fs, self.h_file, pos) < 0:
            raise HDFSIOError("hdfsSeek returned error code file: %s" % repr(self))


    def read(self, int length):
        """
            Read data from an open file.
            :param length: desired length of read.
            :return: the number of bytes actually read, possibly less than 
                    the @length and the read string
            :rtype: tuple(bytes_read, read_data_string)
        """
        cdef:
            int bytes_read
            void * buf
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        buf = <void *>malloc( sizeof(char) * length)
        if buf is NULL:
            raise MemoryError("in read(): buf = <void *>malloc( sizeof(char) * length)")
        bytes_read = hdfsRead(self.fs, self.h_file, buf, length)
        IF USE_STATS:
            self._read_ops += 1
        if bytes_read < 0:
            free(buf)
            raise HDFSIOError("Io read error in %s" % repr(self))
        IF USE_STATS:
            self._read_bytes += bytes_read
        try:
            ret_string = (<char *>buf)[:bytes_read]
        finally:
            free(buf)
        bytes_read_py = bytes_read
        return (bytes_read_py, ret_string)

    def pread(self, tOffset position, tSize length):
        """
            Positional read of data from an open file.
            :param position: Position from which to read
            :param length: The length of the buffer.
            :return: the number of bytes actually read, possibly less than 
                    the @length and the read string
            :rtype: tuple(bytes_read, read_data_string)
        """
        cdef tSize bytes_read
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        buf = <void *>malloc( sizeof(char) * length)
        if buf is NULL:
            raise MemoryError("in read(): buf = <void *>malloc( sizeof(char) * length)")
        bytes_read = hdfsPread(self.fs, self.h_file, position, buf, length)
        IF USE_STATS:
            self._read_ops += 1
        if bytes_read < 0:
            free(buf)
            raise HDFSIOError("Io read error in %s" % repr(self))
        IF USE_STATS:
            self._read_bytes += bytes_read
        try:
            ret_string = (<char *>buf)[:bytes_read]
        finally:
            free(buf)
        bytes_read_py = bytes_read
        return (bytes_read_py, ret_string)


cdef class HDFSWriteFile(HDFSFile):

    def write(self, w_data):
        """
            Write data into an open file.
            :return: Returns the number of bytes written
        """
        cdef:
            int ret
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        if not PyString_Check(w_data):
            raise TypeError("expected string got: %s instead" % type(w_data))

        ret = hdfsWrite(self.fs, self.h_file, PyString_AS_STRING(w_data), PyString_GET_SIZE(w_data))
        IF USE_STATS:
            self._write_ops += 1
        if ret < 0:
            raise HDFSIOError("write error in %s" % repr(self))
        IF USE_STATS:
            self._write_bytes += ret
        return ret

    def write_all(self, w_data):
        """
            Writes string @w_data using endless loop.
            breaks loop when all data written or hdfsWrite 
            returns error.
            :param w_data: string to write to file
            :return: None
        """
        cdef:
            int ret 
            int sent
            int must_send

        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        if not PyString_Check(w_data):
            raise TypeError("expected string got: %s instead" % type(w_data))

        sent = 0
        must_send = <int>PyString_GET_SIZE(w_data)
        while must_send > 0:
            ret = hdfsWrite(self.fs, self.h_file, PyString_AS_STRING(w_data) + sent, must_send)
            IF USE_STATS:
                self._write_ops += 1
            if ret < 0:
                raise HDFSIOError("write error in %s" % repr(self))
            IF USE_STATS:
                self._write_bytes += ret
            sent += ret
            must_send -= ret


    def flush(self):
        """
            Flush the data. calls hdfsFlush()
            :return: None
        """
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        if hdfsFlush(self.fs, self.h_file) < 0:
            raise HDFSIOError("Can't flush %s" % repr(self))


    def hflush(self):
        """
            Flush the data. calls hdfsHFlush() if defined.
            :return: None

            .. note::
                if hdfsHFlush() is not defined in libhdfs 
                this functions does nothing.
        """
        if not self._open:
            raise HDFSIOError("File %s is closed" % repr(self))
        IF HADOOP_HAS_HFLUSH:
            if hdfsHFlush(self.fs, self.h_file) < 0:
                PyErr_SetFromErrno(IOError)


cdef void hdfs_file_factory(HDFSFile hdfs_file, 
                            HDFSfs hdfsfs, path, 
                            hdfsFile h_file, 
                            int flags, 
                            int bufferSize, 
                            short replication, 
                            int blocksize):
    hdfs_file.hdfsfs = hdfsfs
    hdfs_file.path = path

    hdfs_file.h_file = h_file
    hdfs_file.fs = hdfsfs.fs
    hdfs_file.flags = flags
    hdfs_file.bufferSize = bufferSize
    hdfs_file.replication = replication
    hdfs_file.blocksize = blocksize
    hdfs_file._open = 1
    IF USE_STATS:
        hdfs_file._write_ops = 0
        hdfs_file._write_bytes = 0
        hdfs_file._read_ops = 0
        hdfs_file._read_bytes = 0


def copy(HDFSConnection src_conn, char * src, HDFSConnection dst_conn, char * dst):
    """
       Copy file from one filesystem to another.
       :param src_conn: The handle to source filesystem.
       :param src: The path of source file. 
       :param dst_conn: The handle to destination filesystem.
       :param dst: The path of destination file. 
       :return: Returns 0 on success, -1 on error
       :rtype: int
    """
    return hdfsCopy(src_conn.fs, src, dst_conn.fs, dst)


def move(HDFSConnection src_conn, char * src, HDFSConnection dst_conn, char * dst):
    """
       Move file from one filesystem to another.
       :param src_conn: The handle to source filesystem.
       :param src: The path of source file. 
       :param dst_conn: The handle to destination filesystem.
       :param dst: The path of destination file. 
       :return: Returns 0 on success, -1 on error
       :rtype: int
    """
    return hdfsMove(src_conn.fs, src, dst_conn.fs, dst)






