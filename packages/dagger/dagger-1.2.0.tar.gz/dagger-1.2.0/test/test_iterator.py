def test_iter():
  import dagger
  
  d = dagger.dagger()
  d.add('1', ['2','3','4'])
  d.add('4', ['5','6'])
  d.stale('6')
  d.run(allpaths=True)
  
  iter = d.iter()
  ldict = iter.ldict  
  
  for name in '1 4 6'.split():
    if not ldict.get( d.nodes[name] ): return False
  
  for name in '2 3 5'.split():
    if ldict.get( d.nodes[name] ): return False
  
  return True

def test_iterator(names=[], remove='', nexts=[]):
  import dagger
  
  d = dagger.dagger()
  d.add('1', ['2','3','4'])
  d.add('4', ['5','6'])
  d.add('7', ['6'])
  d.stale('5')
  d.stale('6')
  d.run(allpaths=True)
  
  remove = remove.split()
  
  it = d.iter(names)
  next = it.next(2)
  while remove:
    if next <> nexts[0]: return False
    
    try:
      name = remove.pop(0)
      nexts.pop(0)
      it.remove(name)
    except: return False
    
    next = it.next(2)
  
  return True

def test_iterator_all():
  return test_iterator([], '5 6 7 4 1', [['5','6'], ['6'], ['4','7'], ['4'], ['1']])

def test_iterator_names():
  return test_iterator(['6'], '6 4 1 7', [['6'], ['4','7'], ['1','7'], ['7']])

#############################################
tests = [
test_iter,
test_iterator_all,
test_iterator_names
]

from tester import test
import sys
sys.exit( not test(tests=tests) )