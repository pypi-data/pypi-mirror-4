import collections
import ctypes
import ctypes.util
import errno
libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
import mmap as stdlib_mmap
import os


PAGESIZE = stdlib_mmap.PAGESIZE


MmapInfo = collections.namedtuple('MmapInfo', ('fd', 'size', 'pointer'))


def init_mmap(filename, size=PAGESIZE):
    """Create an mmap given a location `filename` and minimum `size` in bytes

    Returns an MmapInfo tuple with the file descriptor, actual size, and a
    pointer to the begging of the mmap.

    Note that the size returned is rounded up to the nearest PAGESIZE.
    """
    # Create new empty file to back memory map on disk
    fd = os.open(filename, os.O_CREAT | os.O_TRUNC | os.O_RDWR)
    if size > PAGESIZE:
        if size % PAGESIZE:
            size = size + (PAGESIZE - (size % PAGESIZE))
    else:
        size = PAGESIZE

    # Zero out the file
    os.ftruncate(fd, size)
    m_ptr = mmap(size, fd)
    return MmapInfo(fd, size, m_ptr)


# Linux consts from /usr/include/bits/mman.h
MS_ASYNC = 1
MS_SYNC = 4


libc.mmap.restype = ctypes.c_void_p
libc.mmap.argtypes = [
    ctypes.c_void_p, # address
    ctypes.c_size_t, # size of mapping
    ctypes.c_int,    # protection
    ctypes.c_int,    # flags
    ctypes.c_int,    # fd
    ctypes.c_int,    # offset (needs to be off_t type?)
]


def mmap(size, fd):
    m_ptr = libc.mmap(None,
                      size,
                      stdlib_mmap.PROT_READ | stdlib_mmap.PROT_WRITE,
                      stdlib_mmap.MAP_SHARED,
                      fd,
                      0
            )
    if m_ptr == -1:
        # Error
        e = ctypes.get_errno()
        raise OSError(e, errno.errorcode[e])
    return m_ptr


libc.msync.restype = ctypes.c_int
libc.msync.argtypes = [
    ctypes.c_void_p, # address
    ctypes.c_size_t, # size of mapping
    ctypes.c_int,    # flags
]


def msync(mm_ptr, size, async=False):
    if async:
        flags = MS_ASYNC
    else:
        flags = MS_SYNC
    status = libc.msync(mm_ptr, size, flags)
    if status == -1:
        e = ctypes.get_errno()
        raise OSError(e, errno.errorcode[e])


libc.munmap.restype = ctypes.c_int
libc.munmap.argtypes = [
    ctypes.c_void_p, # address
    ctypes.c_size_t, # size of mapping
]


def munmap(mm_ptr, size):
    status = libc.munmap(mm_ptr, size)
    if status == -1:
        e = ctypes.get_errno()
        raise OSError(e, errno.errorcode[e])
