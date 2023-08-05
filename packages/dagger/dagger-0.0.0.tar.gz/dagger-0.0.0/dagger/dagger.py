# Dagger is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dagger is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dagger.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2012 Remik Ziemlinski

import os, datetime
import hashlib
from collections import deque

VERSION = "0.0.0"

###############################################################  
class hashdb(object):
  """Loads, queries, computes and exports "file,hash" per line."""
  def __init__(self, fn=''):
    self.filename = fn
    self.db = {}
    
  def get(self, fn):
    """Get hash for given filename in db."""
    return self.db.get(fn,None)
    
  def export(self):
    """Write out db to text file with file names and hashes."""
    try:
      f = open(self.filename,'w')
      [f.write('%s,%s\n'%(k,self.db[k])) for k in self.db]
      f.close()
    except:
      print 'Error: failed to write "%s"' % (self.filename)
      
  def load(self, silent=False):
    """Loads db text file."""
    try:
      f = open(self.filename)
      lines = f.read().split()
      self.db = dict([x.split(',') for x in lines])
      f.close()
    except:
      if not silent:
        print 'Warning: failed to load "%s"' % (self.filename)
      
  @staticmethod
  def md5(fn):
    """Return md5 checksum for file named 'fn' or None if error."""
    try:
      fh = open(fn, 'rb')
      m = hashlib.md5()
      while True:
        data = fh.read(8192)
        if not data: break
        m.update(data)
      
      return m.hexdigest()
    except: return None
    
  def set(self, fn, hash):
    """Put hash for file into table."""
    self.db[fn] = hash
    
  def update(self, fn):
    """Compute hash for file and update db entry."""
    hash = hashdb.md5(fn)
    self.set(fn, hash)
    
###############################################################  
class hashdb_sqlite(hashdb):
  """Uses an ondisk sqlite file. Doesn't use :memory:."""
  
  def __init__(self, fn=''):
    self.filename = fn
    # Connection to file.
    self.db = None

  def export(self):
    """Write out db to file with file names and hashes."""
    try:
      if self.db: self.db.close()
    except:
      print 'Error: failed to write "%s"' % (self.filename)

  def get(self, fn):
    """Get hash for given filename in db."""
    if not self.db: return ''
    c = self.db.cursor()
    c.execute('SELECT hash FROM db WHERE file=?', (fn,))
    h = c.fetchone()
    if h: return h
    else: return None

  def load(self, silent=False):
    """Loads sqlite db file."""
    import sqlite3
    try:
      # Create schema if file doesn't exist yet.
      maketable = not os.path.exists(self.filename)
      self.db = sqlite3.connect(self.filename)
      if maketable:
        c = self.db.cursor()
        c.execute('''CREATE TABLE db (file text, hash text)''')
        self.db.commit()
    except:
      if not silent:
        print 'Warning: failed to connect to "%s"' % (self.filename)
  
  def set(self, fn, hash):
    """Put hash for file into table."""
    if not self.db: return
    c = self.db.cursor()
    c.execute("INSERT INTO db VALUES ('%s','%s')" % (fn, hash))
    self.db.commit()

###############################################################  
def time2strings(t):
  """Convert time (from os.path.getmtime) to date and time strings."""
  tstr = str(datetime.datetime.fromtimestamp(t))
  return tstr.split(' ')
  
###############################################################
class node(object):
  """
  File node for dependecy graph.
  """
  
  def __init__(self, name):
    self.hash = None
    self.name = name
    # Children. Deque allows O(1) popleft.
    self.nodes = deque() 
    # None means no parent. 
    # [] means was added as child by another.
    # dagger will populate lists of node references during tree evaluation.
    # Multiple paths from roots may exist, so this is a list of lists.
    self.paths = None 
    # None means TBD by graph walk. 
    # Otherwise 0 is uptodate, 1 means needs refresh.
    self.stale = None
    # Missing files will always by older relative to real files.
    self.time = 0
    
  def add(self, *nodes):
    """Add one or more nodes as children."""
    self.nodes.extend(nodes)
    # Reset paths.
    for f in nodes: f.paths = []
    
  def dump(self):
    """Return string with basic node info."""
    return '%s: stale=%s, time=%s, hash=%s' % (self.name, str(self.stale), str(self.time), str(self.hash))
    
  def format(self, pat=None):
    """
    @return formatted string. 
    @param pat: Supported format specifiers:
    %a: absolute name
    %d: date
    %b: base name
    %r: root name (no directory prefix or extension suffix)
    %m: modified time
    None: as-is name
    """
    if pat:
      if '%a' in pat:
        a = os.path.abspath(self.name)
        pat = pat.replace('%a',a)
      
      if '%d' in pat or '%t' in pat:
        d,t = time2strings(self.time)
        pat = pat.replace('%d',d)
        pat = pat.replace('%t',t)
      
      if '%b' in pat:
        b = os.path.basename(self.name)
        pat = pat.replace('%b',b)
        
      if '%r' in pat:
        b = os.path.basename(self.name)
        idx = b.rfind('.') # Allow dot files, eg. .bashrc
        if idx > 0: r = b[:idx]
        else: r = b
        pat = pat.replace('%r',r)
        
      return pat
    else:
      return self.name
        
  def reset(self):
    """Reset staleness, hash and time."""
    self.stale = None
    self.time = 0
    self.hash = None
    
  def update(self, time=True, hash=False):
    """Get modified time for file from system and optionally compute hash."""
    self.stale = None
    if time and os.path.exists(self.name):
      self.time = os.path.getmtime(self.name)

    if hash: self.hash = hashdb.md5(self.name)
    
###########################################################
class dagger(object):
  def __init__(self, hashfile='', sqlite=False):
    """
    Check if nodes are stale based on modified time or hash log (each line has file,hash).
    
    hashfile: filename for hash log file.
    """
    # Loaded hash db.
    self.db = None
    # Which files to force as stale or uptodate.
    self.forced = {}
    # Globally hash all files.
    self.hashall = False
    # Filename for db.
    self.hashfile = hashfile
    # Allow hashing per file. Default is no.
    self.useshash = {}
    # Store DAG eval order from bottom to top in node tree.
    self.order = []
    # Nodes are only unique by name.
    self.nodes = {}
    # Use SQLite database instead of text file.
    self.sqlite = sqlite
    
  def add(self, target, sources=[]):
    """Make target depend on optional sources."""
    tnode = self.get(target)
    
    for s in sources: 
      snode = self.get(s)
      tnode.add(snode)
  
  def dot(self, out=None, format=None, color=True):
    """
    Return dot graph as string and optionally write to file 'out'.
    Stale nodes will be colored red.
    
    You can set the file name 'format' for node labels.
    """
    red = '"#ff8888"'
    s = 'digraph dagger {\nbgcolor = white;\n'
    
    # Just create parent->child lines.
    for p in self.nodes.values():
      pformat = p.format(format)
      atts = []
      if color and p.stale: atts.append( "fillcolor = %s" % (red) )
      else: atts.append( "fillcolor = white" )
      
      if atts: s += '%s [%s]\n' % (pformat, ','.join(atts) )
        
      for c in p.nodes:
        cformat = c.format(format)
        atts = []
        if color and c.stale: atts.append( "fillcolor = %s" % (red) )
        else: atts.append( "fillcolor = white" )
        
        if atts: s += '%s [%s]\n' % (cformat, ','.join(atts) )
        
        s += '%s -> %s;\n'%(pformat, cformat)

    s += '}'
    
    if out: f = open(out,'w'); f.write(s); f.close()
    
    return s
    
  def dump(self):
    """Text dump of nodes."""
    out = ''
    for n in self.nodes.values(): out += n.dump() + '\n'
      
    return out
    
  def exporthash(self):
    """Write hashdb for all nodes."""
    db = hashdb(self.hashfile)
    db.load()
    
    for k in self.nodes:
      f = self.nodes[k]
      if f.hash: db.set(k, f.hash)
      else: db.update(k)
  
    db.export()
    
  def get(self, name):
    """Get node by name."""
    if name not in self.nodes:
      self.nodes[name] = node(name)

    return self.nodes[name]
  
  def ordernames(self):
    """Return names of files discovered during graph evaluation."""
    return ','.join([n.name for n in self.order])
  
  def paths2names(self, name):
    """Return list of lists where paths use names instead of object references."""
    n = self.nodes[name]
    if not n.paths: return n.paths
    return [[r.name for r in p] for p in n.paths]

  def resetnodes(self):
    """Reset all nodes."""
    [n.reset() for n in self.nodes.values()]
    
  def stale(self, name, force=1):
    """Force node with name to be stale (force=1) or uptodate (force=0)."""
    self.forced[name] = force

  def hash(self, name, enable=1):
    """Enable hashing for file node."""
    self.useshash[name] = enable
    
  def tree(self):
    """Return simple tree string of all nodes."""
    out = ''
    for f in self.nodes:
      thenode = self.nodes[f]
      if thenode.nodes:
        out += f + ': '
        for c in thenode.nodes:
          out += c.name + ' '
        out += '\n'
        
    return out

  def run(self, allpaths=False):
    """
    Find stale nodes based on modtime or hash.
    
    allpaths: If true, also find all paths from roots to leaf nodes.
    """
    if (not self.db) and self.hashfile:
      if self.sqlite:
        self.db = hashdb_sqlite(self.hashfile)
      else:
        self.db = hashdb(self.hashfile)
      
      self.db.load()
      
    # First pass get their latest info.
    for f in self.nodes:
      hash = self.hashall or self.useshash.get(f,0)
      self.nodes[f].update( time=not hash, hash=hash )
    
    # Second pass, have each node check for a stale child,
    # check hash, and find all paths in graph.
    # Also store the search order.
    self.order = []
    
    # Quick check to prevent adding duplicates into self.order.
    ordered = {}
    
    # Get only roots.
    roots = [f for f in self.nodes.values() if f.paths == None]
    # Clear previous paths.
    for f in self.nodes.values(): 
      if f.paths: f.paths = []
    
    visit = {} # Children lists are copied and popped to find all paths.
    for root in roots:
      # deque pops are faster than list, and we want paths ordered
      # left to right.
      q = deque([root])
      if allpaths or root not in visit:
        visit[root] = deque(root.nodes)
      
      while q:
        top = q[0]
        if visit[top]:
          child = visit[top].popleft()
          q.appendleft(child)
          if allpaths or child not in visit:
            visit[child] = deque(child.nodes)
        else:
          # Done visiting all children. 
          # Determine staleness only once.
          # Redundant visits are only for building all paths.
          if top.stale == None: 
            if top.name in self.forced:
              top.stale = self.forced[top.name]
            else:
              usehash = self.hashall or self.useshash.get(top.name,0)
              if usehash and self.db: dbhash = self.db.get(top.name)
              else: dbhash = None
              # If db doesn't have hash for file, then its not stale.
              if dbhash and dbhash <> top.hash:
                top.stale = 1
              else:
                nOlder = 0
                for child in top.nodes:
                  if child.stale or \
                    ( (not usehash) and (top.time < child.time) ):
                    top.stale = 1
                  else: nOlder +=1
                
                if nOlder == len(top.nodes):
                  top.stale = 0
                  
          q.popleft()
          if top.paths <> None: # If not root node.
            # Store this depth-first-search path. One per parent.
            path = list(q) # Deep copy.
            top.paths.append(path)
        
          if top not in ordered:
            # Build ordered node visit history.
            self.order.append(top)
            ordered[top] = 1
