from csFIFO import *

import difflib
import random, string
import time

# pylint: disable=C0103,C0301

def randString(length):
  s = ""
  p = string.punctuation+string.digits+string.ascii_letters
  for n in xrange(0, length):
    s += p[random.randint(0, len(p)-1)]
  return s

def debug(f, si, so):
  print "Len si:", len(si)
  print "Len so:", len(so)
  print "Differences"
  d = difflib.SequenceMatcher(a=si, b=so)
  for tag, i1, i2, j1, j2 in d.get_opcodes():
    if tag is not 'equal':
      print ("%7s si[%d:%d] (%s) so[%d:%d] (%s)" %
      (tag, i1, i2, si[i1:i2], j1, j2, so[j1:j2]))
    if tag == 'delete':
      print f
      f.buf.seek(i1)
      print "si:", f.buf.read(i2-i1)
      f.buf.seek(j1)
      print "so:", f.buf.read(j2-j1)

def testFIFO(f):
  si = ""
  so = ""
  for n in xrange(10000):
    #Read and write in different size chunks
    sizein  = random.randint(0, 120)
    sizeout = random.randint(0, 200)    #Make sizeout sometimes larger than sizein to test underflows
    r = randString(sizein)
    r = f.write(r)
    si = si+r
    so = so+f.read(sizeout)
    try:
      #Check what was written was read
      if len(si)<len(so):
        assert so.startswith(si)
      else:
        assert si.startswith(so)
    except AssertionError:
      print "Error during test"
      debug(f, si, so)
      raise
  
  #Finally read what is left in the buffer
  if not f.isEmpty():
    so += f.read(-1)
  
  try:
    #Funally check the two buffers are equal
    assert si == so
  except AssertionError:
    print "Error at cleanup"
    debug(f, si, so)
    raise

class writeThread(threading.Thread):
  
  def __init__(self, fifo):
    super(writeThread, self).__init__()
    self.fifo = fifo
    self.running = threading.Event()
    self.running.set()
    self.written = ""
    print "writeThread starting"
    self.start()
    
  def run(self):
    print "writeThread started"
    while self.running.isSet():
      l = random.randint(0, 1050)
      s = randString(l)
      l = self.fifo.write(s)
      #We clip the written string to the length actually written
      self.written += s[:l]
      t = random.random()/100
      time.sleep(t)
    print "writeThread stopped"
      
  def kill(self):
    self.running.clear()
      

class readThread(threading.Thread):
  
  def __init__(self, fifo):
    super(readThread, self).__init__()
    self.fifo = fifo
    self.running = threading.Event()
    self.running.set()
    self.read = ""
    print "readThread starting"
    self.start()

    
  def run(self):
    print "readThread started"
    while self.running.isSet():
      l = random.randint(0, 1000)
      s = self.fifo.read(l)
      t = random.random()/100
      time.sleep(t)
      self.read += s
    
    print "readThread stopped"
    if not f.isEmpty():
      print "%d bytes left in fifo, draining" % f.available
      #drain the fifo on exit
      self.read += self.fifo.read(-1)
      
  def kill(self):
    self.running.clear()

if __name__ == "__main__":
  
  print "Testing FIFO"
  f = FIFO(600)
  
  #print f
  #
  #for n in xrange(10):
  #  sys.stdout.write(".")
  #  sys.stdout.flush()
  #  testFIFO(f)
  #  f.purge()
  #
  #print
  #print f
  #
  #f.purge()
  
  #FIFOs also support indexing
  print "\n\nTesting non-destructive slice access\n"
  s = randString(50)
  f.write(s)
  
  print f
  
  print s
  print f[:]
  
  #Start+len
  a = f[:10]
  b = s[:10]
  print a
  print b
  assert a == b
  
  #len To End
  a = f[-10:]
  b = s[-10:]
  print a
  print b
  assert a == b
  
  #Mid
  a = f[30:40]
  b = s[30:40]
  print a
  print b
  assert a == b
  
  #Mid Reverse
  a = f[40:30:-1]
  b = s[40:30:-1]
  print a
  print b
  assert a == b
  
  #Make sure the fifo is unmodified
  assert f.read(-1)==s
  
  
  
  f.purge()
  f.write("The quick brown fox jumps over the lazy dog")
  
  print f.contents()
  
  assert ("fox" in f[:]) == True
  assert ("zebara" in f[:]) == False
  
  #Test multiple threads accessing the same fifo
  print "\n\nTesting threaded access\n"
  f = FIFO(max_size=10000, debug=True)
  
  #Create two threads and producer and consumer
  tx = writeThread(f)
  rx = readThread(f)

  #Run for a bit
  time.sleep(30)
  
  #OK, time up...
  tx.kill()
  rx.kill()
  
  #Wait for the threads to stop to ensure all data is processed
  tx.join()
  rx.join()
  
  diff = difflib.SequenceMatcher(a=tx.written, b=rx.read)
  print "Written", len(tx.written)
  print "Read   ", len(rx.read)
  print f
  
  try:
    assert tx.written == rx.read
  except AssertionError:
    print "Data did not match"
    print diff.get_matching_blocks()
  else:
    print "Threading test PASS"

  



