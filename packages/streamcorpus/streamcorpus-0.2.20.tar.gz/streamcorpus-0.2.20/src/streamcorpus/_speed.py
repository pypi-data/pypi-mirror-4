## {{{ http://code.activestate.com/recipes/286222/ (r1)                                                                                                                                                    
import sys
import os

_proc_status = '/proc/%d/status' % os.getpid()

_scale = {'kB': 1024.0, 'mB': 1024.0*1024.0,
          'KB': 1024.0, 'MB': 1024.0*1024.0}

def _VmB(VmKey):
    '''Private.                                                                                                                                                                                            
    '''
    global _proc_status, _scale
     # get pseudo file  /proc/<pid>/status                                                                                                                                                                 
    try:
        t = open(_proc_status)
        v = t.read()
        t.close()
    except:
        return 0.0  # non-Linux?                                                                                                                                                                           
     # get VmKey line e.g. 'VmRSS:  9999  kB\n ...'                                                                                                                                                        
    i = v.index(VmKey)
    v = v[i:].split(None, 3)  # whitespace                                                                                                                                                                 
    if len(v) < 3:
        return 0.0  # invalid format?                                                                                                                                                                      
     # convert Vm value to bytes                                                                                                                                                                           
    return float(v[1]) * _scale[v[2]]


def memory(since=0.0):
    '''Return memory usage in bytes.                                                                                                                                                                       
    '''
    return _VmB('VmSize:') - since


def resident(since=0.0):
    '''Return resident memory usage in bytes.                                                                                                                                                              
    '''
    return _VmB('VmRSS:') - since


def stacksize(since=0.0):
    '''Return stack size in bytes.                                                                                                                                                                         
    '''
    return _VmB('VmStk:') - since
## end of http://code.activestate.com/recipes/286222/ }}}    



from streamcorpus import Chunk

TEST_PATH = os.path.join(os.path.dirname(__file__), '../../../test-data/john-smith-tagged-by-lingpipe-0.sc')

count = 0
while 1:
    ochunk = Chunk(mode='wb')
    for si in Chunk(TEST_PATH):
        ochunk.add(si)
    ochunk.close()

    count += 1
    print count
    print memory()
    print resident()
    print stacksize()
    sys.stdout.flush()

    
