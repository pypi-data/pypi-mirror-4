from cStringIO import StringIO
import threading
import logging

class FIFO(object):
  """A circular buffer FIFO implementation that makes use of cStringIO"""
  def __init__(self,max_size=None,debug=False):
    
    LOGLEVEL=logging.ERROR
    
    if debug:
      LOGLEVEL=logging.DEBUG

    self.log=logging.getLogger(__package__)
    self.log.setLevel(LOGLEVEL)
    con=logging.StreamHandler()
    con.setLevel(LOGLEVEL)
    self.log.addHandler(con)
    
    self.buf = StringIO()
    self.lock=threading.Lock()
    self.writecount=0
    self.readcount=0
    self.bytesin=0
    self.bytesout=0
    self.size = 0
    self.write_errors=0
    self.max_size=max_size
    self.purgecount=None
    self.resize_count=0
    self.purge()


  def purge(self):
    "Reset the FIFO"
    self.lock.acquire()
    if self.purgecount is not None:
      self.purgecount+=1
    else:
      self.purgecount=0
    self.available=0
    self.write_fp=0
    self.buf.seek(0)
    self.lock.release()
    
  
  def _read(self, size = None):
    #Read without a lock
    """Reads size bytes from buffer, limited by remaining data
    if size<0 all remaining data is returned
    if size is not provided, one byte is returned"""
    if size is None:
      size=1
    if size<0 or size > self.available:
      size = self.available
      
    self.readcount+=1
    self.bytesin+=size

    result=self.buf.read(size)
    self.available -= size
  
    if len(result) < size:
      self.buf.seek(0)
      result += self.buf.read(size - len(result))
    return result
  
  def read(self, size = None):
    """Reads size bytes from buffer, limited by remaining data
    if size<0 all remaining data is returned
    if size is not provided, one byte is returned"""
    self.lock.acquire()
    result=self._read(size)
    self.lock.release()
    return result
      
  def isEmpty(self):
    "Returns true if FIFO is empty"
    return self.available==0
  
  def len(self):
    "Returns the number of byte left in the FIFO"
    return self.available
  
  def __repr__(self):
    self.lock.acquire()
    s="FIFO:\n"
    s+="Max Size: %s\n"%self.max_size
    s+="Size:     %d\n"%self.size
    s+="Readable: %d\n"%self.available
    s+="Writes (bytes):%d (%d)\n"%(self.writecount,self.bytesin)
    s+="Reads  (bytes):%d (%d)\n"%(self.readcount,self.bytesout)
    s+="Purges:   %d\n"%self.purgecount
    s+="write_fp: %d\n"%self.write_fp
    s+="write err:%d\n"%self.write_errors
    s+="Resize:   %d\n"%self.resize_count
    self.lock.release()
    return s

    
  
  def write(self, data):
    """Appends data to buffer"""
    l=len(data)
    self.lock.acquire()
    if self.size < self.available + l:
      #Allow expansion upto max_size
      if self.max_size is not None and self.available+l>self.max_size:
        self.log.error("Buffer size limited, data truncated")
        self.write_errors+=1
        data=data[:self.max_size-self.available]
        l=len(data)
      new_buf = StringIO()
      new_buf.write(self._read(-1))
      self.write_fp = self.available = new_buf.tell()
      read_fp = 0
      if self.size <= self.available + l:
        if self.max_size:
          r=self.size+min(l*2,self.max_size-self.size)
        else:
          r=self.size+l*2
        self.log.debug("Resize %d"%r)
        self.resize_count+=1
        self.size = r
      new_buf.write('0' * (self.size - self.write_fp))
      self.buf = new_buf
    else:
      read_fp = self.buf.tell()
      
    self.writecount+=1
    self.bytesout+=l

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
    #Return what was actually written in case it was truncated
    self.lock.release()
    return data
  
  def __getitem__(self,idx):
    self.lock.acquire()
    #preserve the current read position
    fp=self.buf.tell()
    data=""
    
    try:
      if isinstance(idx,(int,long)):
        if idx>min(self.size,self.write_fp):
          raise IndexError,"Outside of buffer"
        rng=xrange(idx,idx+1,1)
      elif isinstance(idx,slice):
        start=idx.start if idx.start is not None else 0
        stop=idx.stop if idx.stop is not None else self.available
        if start<0:
          start=self.available+start
        if stop<0:
          start=self.available+stop
        mul=1 if start<=stop else -1
        step=idx.step if idx.step is not None else mul
        rng=xrange(start,stop,step)
      elif isinstance(idx,tuple):
        rng=idx
      else:
        raise ValueError,"Invalid index"
      
      self.log.debug(rng)
      
      for n in rng:
        #Don't try and read outside of our buffer
        if abs(n)>self.size:
          continue
        if n>=0:
          p=n+fp
          #If we are trying to read past the end, wrap
          if p>self.size:
            p-=self.size
        else:
          p=self.write_fp-n
          #If we are trying to read past the start, wrap
          if p<0:
            p+=self.size
        self.buf.seek(p)
        data+=self.buf.read(1)

    finally:
      self.buf.seek(fp)
      self.lock.release()
    
    return data
        
        
          

  