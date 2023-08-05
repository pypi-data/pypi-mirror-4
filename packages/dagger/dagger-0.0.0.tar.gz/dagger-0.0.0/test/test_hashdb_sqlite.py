def test_load_missing():
  import os,dagger
  d = dagger.hashdb_sqlite()
  d.load(silent=True)
  return 1

def test_get_missing():
  import os,dagger
  d = dagger.hashdb_sqlite()
  return not d.get('tmp')

def test_update():
  import os,dagger
  os.system('touch tmp')
  d = dagger.hashdb_sqlite('tmp.sqlite')
  d.load()
  d.update('tmp')
  h = d.get('tmp'); #print h
  return h

def test_export():
  import os,dagger
  os.system('echo 1 > tmp1')
  os.system('echo 1 > tmp2')
  os.system('echo 2 > tmp3')
  d = dagger.hashdb_sqlite('tmp.sqlite')
  d.load()
  d.update('tmp1')
  d.update('tmp2')
  d.update('tmp3')
  d.export()
  del d
  
  d = dagger.hashdb_sqlite('tmp.sqlite')
  d.load()

  h1 = d.get('tmp1')
  h2 = d.get('tmp2')
  h3 = d.get('tmp3'); #print h1,h2,h3
  
  return d.db and h1 and h1 == h2 and h1 <> h3

#############################################
tests = [
test_load_missing,
test_get_missing,
test_update,
test_export,
]

from tester import test
import sys
sys.exit( not test(tests=tests) )