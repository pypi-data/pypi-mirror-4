def test(path='../dagger', tests=[]):
  """Run tests and return if all passed."""
  # Import local dagger in src tree.
  import sys
  from os.path import normpath, dirname, join

  local_module = normpath( join(dirname(__file__), path) )
  sys.path.insert(0, local_module)
  
  n = len(tests)
  npass = 0
  ctr = 1
  for t in tests:
    if t(): print 'PASS:',; npass += 1
    else: print 'FAIL:',
    print '%d.%s' % (ctr, t.__name__)
    ctr += 1
    
  print '%d of %d passed\n' % (npass, n)
  return n == npass
