from cStringIO import StringIO
import threading
import logging
import sys

"""A circular buffer FIFO implementation that makes use of cStringIO"""

# pylint: disable=C0103,C0301

log = logging.getLogger(__package__)
con = logging.StreamHandler(stream=sys.stdout)
fmt = logging.Formatter('%(module)s-%(levelname)s: %(message)s')
con.setFormatter(fmt)
log.addHandler(con)
log.propagate = True


class FIFO(object):
  """A circular buffer FIFO implementation that makes use of cStringIO"""
  def __init__(self, max_size=None, debug=False):
    """A circular buffer FIFO implementation that makes use of cStringIO
    
    max_size limits FIFO size (excess data is truncated)
    debug turns on debugging
    """
    
    self.log = log
    if debug:
      self.log.setLevel(logging.DEBUG)
    
    self.buf  = StringIO()
    self.lock = threading.Lock()
    self.writecount = 0
    self.readcount  = 0
    self.bytesin    = 0
    self.bytesout   = 0
    self.size       = 0
    self.write_errors = 0
    self.max_size   = max_size
    self.purgecount = None
    self.resize_count = 0
    self.write_fp   = 0
    self.available  = 0
    self.lostbytes  = 0
    self.purge()
  
  
  def purge(self):
    "Reset the FIFO"
    self.lock.acquire()
    if self.purgecount is not None:
      self.purgecount += 1
    else:
      self.purgecount = 0
    self.available = 0
    self.write_fp  = 0
    self.buf.seek(0)
    self.lock.release()
  
  
  def _read(self, size = None):
    #Read without a lock
    if size is None:
      size = 1
    if size < 0 or size > self.available:
      size = self.available
    
    result = self.buf.read(size)
    self.available -= size
    
    if len(result) < size:
      self.buf.seek(0)
      result += self.buf.read(size - len(result))
      
    return result
  
  def read(self, size = None):
    """Reads size bytes from FIFO, limited by remaining data
    if size<0 all remaining data is returned
    if size is not provided, one byte is returned"""
    self.lock.acquire()
    self.readcount += 1
    result = self._read(size)
    self.bytesout  += len(result)
    self.lock.release()
    return result
  
  def isEmpty(self):
    "Returns true if FIFO is empty"
    return self.available == 0
  
  def len(self):
    "Returns the number of byte left in the FIFO"
    return self.available
  
  def __repr__(self):
    self.lock.acquire()
    s = "FIFO:\n"
    s += "Max Size: %s\n" % self.max_size
    s += "Cur Size: %d\n" % self.size
    s += "Readable: %d\n" % self.available
    s += "Writes (bytes):%d (%d)\n" % (self.writecount, self.bytesin)
    s += "Reads  (bytes):%d (%d)\n" % (self.readcount, self.bytesout)
    s += "Purges:   %d\n" % self.purgecount
    s += "write_fp: %d\n" % self.write_fp
    s += "write err:%d\n" % self.write_errors
    pclost = (float(self.lostbytes)*100)/float(self.bytesin)
    s += "lost data:%d (%2.2f%%)\n" % (self.lostbytes, pclost)
    s += "Resize:   %d\n" % self.resize_count
    self.lock.release()
    return s
  
  def write(self, data):
    """Appends data to FIFO"""
    l = len(data)
    self.lock.acquire()
    if self.size < self.available + l:
      #Allow expansion upto max_size
      if self.max_size is not None and self.available+l > self.max_size:
        self.log.error("Buffer size limited, data truncated")
        self.write_errors += 1
        data = data[:self.max_size-self.available]
        oldl = l
        l = len(data)
        self.lostbytes += oldl-l
      new_buf = StringIO()
      new_buf.write(self._read(-1))
      self.write_fp = self.available = new_buf.tell()
      read_fp = 0
      if self.size <= self.available + l:
        if self.max_size:
          r = self.size + min(l*2, self.max_size-self.size)
        else:
          r = self.size+l*2
        self.log.debug("Resize %d"%r)
        self.resize_count += 1
        self.size = r
      new_buf.write('0' * (self.size - self.write_fp))
      self.buf = new_buf
    else:
      read_fp = self.buf.tell()
    
    self.writecount += 1
    self.bytesin    += l
    
    self.buf.seek(self.write_fp)
    written = self.size - self.write_fp
    self.buf.write(data[:written])
    self.write_fp += l
    self.available += l
    if written < l:
      self.write_fp -= self.size
      self.buf.seek(0)
      self.buf.write(data[written:])
    self.buf.seek(read_fp)

    self.lock.release()
    return len(data)
  
  def __getitem__(self, idx):
    self.lock.acquire()
    #preserve the current read position
    read_fp = self.buf.tell()
    
    try:
      data = self.buf.read(self.available)
      if len(data)<self.available:
        self.buf.seek(0)
        data += self.buf.read(self.available - len(data))
      
    finally:
      self.buf.seek(read_fp)
      self.lock.release()
    
    return data[idx]
  
  def contents(self):
    "Returns the contents of the fifo without modifying it"
    return self[:]
