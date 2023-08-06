from FIFO import *

import difflib
import random,string,sys

def randString(length):
  s=""
  p=string.punctuation+string.digits+string.ascii_letters
  for n in xrange(0,length):
      s+=p[random.randint(0,len(p)-1)]
  return s
  
def debug(f,si,so):
  print "Len si:",len(si)
  print "Len so:",len(so)
  print "Differences"
  d=difflib.SequenceMatcher(a=si,b=so)
  for tag, i1, i2, j1, j2 in d.get_opcodes():
    if tag is not 'equal':
      print ("%7s si[%d:%d] (%s) so[%d:%d] (%s)" %
        (tag, i1, i2, si[i1:i2], j1, j2, so[j1:j2]))
    if tag=='delete':
      print f
      f.buf.seek(i1)
      print "si:",f.buf.read(i2-i1)
      f.buf.seek(j1)
      print "so:",f.buf.read(j2-j1)

def testFIFO(f):    
  si=""
  so=""
  for n in xrange(10000):
    #Read and write in different size chunks
    sizein=random.randint(0,120)
    sizeout=random.randint(0,200)    #Make sizeout sometimes larger than sizein to test underflows
    r=randString(sizein)
    r=f.write(r)
    si=si+r
    so=so+f.read(sizeout)
    try:
      #Check what was written was read
      if len(si)<len(so):
        assert so.startswith(si)
      else:
        assert si.startswith(so)
    except AssertionError:
      print "Error during test"
      debug(f,si,so)
      raise
    
  #Finally read what is left in the buffer
  if not f.isEmpty():
    so+=f.read(-1)

  try:
    #Funally check the two buffers are equal
    assert si==so
  except AssertionError:
    print "Error at cleanup"
    debug(f,si,so)
    raise
      

if __name__=="__main__":
  
  print "Testing FIFO"
  f=FIFO(600)
  
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
  s=randString(50)
  f.write(s)
  
  print f
  
  print s
  print f[:]
  
  a=f[:10]
  b=s[:10]
  print a
  print b
  assert a==b
  
  a=f[-10:]
  b=s[-10:]
  print a
  print b
  assert a==b
  
  a=f[30:40]
  b=s[30:40]
  print a
  print b
  assert a==b
  
  a=f[40:30:-1]
  b=s[40:30:-1]
  print a
  print b
  assert a==b
  
  f.purge()
  
  f.write("The quick brown fox jumps over the lazy dog")
  
  print f[:]
  
  print "fox" in f[:]
  print "zebara" in f[:]

  
  
