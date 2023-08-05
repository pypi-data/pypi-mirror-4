# Python Dagger - The File Dependency Graph Engine

![Banner image](banner.png "Dagger graphs.")

Overview
--------
[Dagger](http://sourceforge.net/projects/pythondagger) evaluates file dependencies in a directed-acyclic-graph (DAG) 
like GNU make, but timestamps or hashes can be enabled per-file. 
This allows you to use fast timestamp comparisons with large files, 
and hashing on small files. When hashing is used, it's stored in a 
simple 2 column text file with filename,hash per line or in a sqlite 
database. Dagger can be used as a building block for a larger build 
system.

Dagger is written in Python to make it portable and extensible. It's 
graph evaluation engine is non-recursive, so it can handle very deep
dependency paths. A benchmark tool (see below) is available to test and visualize
complex graphs.

Features
--------
-   Dependency based on modified time or hash (md5) for individual or all files.
-   Force individual files as stale or uptodate.
-   All paths computation for every node and discovery order.
-   Written in pure Python to be platform agnostic.
-   Non-recursive graph algorithm.
-   Hash database in text or sqlite file.
-   Graphviz dot file export that colors stale file nodes.

Quick Example
-------------
    import dagger
    
    dag = dagger.dagger()
    dag.add('1', ['2','3'])
    dag.add('3', ['4','5'])
    dag.add('6', ['3','7'])
    
    # Force this node to be old, and all dependent parents.
    dag.stale('4') # You can force "freshness" with dag.stale(name, 0).
    dag.run()
    dag.dot('example.dot')

![Example image](dot.png "Example of dot export with color enabled.")

__example.dot__ visualized with kgraphviewer. Old/stale nodes are colored in red by dagger.

Download
--------
[Source code](http://sourceforge.net/projects/pythondagger/files/)

Testing
-------
    make test

Installation
------------
    sudo python setup.py install

Benchmarking
------------
There is a helper script in `bench/` to help you see how fast dagger can be.
You can specify how many children and depth the mock graph should use.

    # Small trees visualized with dot.
    $ python bench.py --levels 3 --width 2 --dot 3x2.dot
    nodes: inner=6 outer=8 total=14
    0.0s Run   
    
![dot3x2 image](dot3x2.png "Small trees output by bench.py with 1 old node.")

Small 3 level, 2 child wide graph output by bench.py with 1 old node ('7').

    # Larger test case. Does your project use 56,000 files?
    $ python bench.py --levels 6 --width 6 --allpaths
    nodes: inner=9330 outer=46656 total=55986
    0.24s Run   
    
    # See if even faster with pypy.
    $ pypy bench.py --levels 6 --width 6 --allpaths
    nodes: inner=9330 outer=46656 total=55986
    0.16s Run   

    # Try extreme case of simulating 1 million files.
    $ python bench.py --levels 7 --width 7 --allpaths
    nodes: inner=137256 outer=823543 total=960799
    6.35s Run   
    
    # pypy reports a shorter runtime for the 1 million node graph.
    $ pypy ...
    3.17s Run

Example: Hashing
----------------
    # Use a text file for file hashes.
    # It's ok if it doesn't exist. 
    dag = dagger.dagger('/home/project/hash.txt')
    
    # dag.add(...)
    
    # Enable hashing for all files.
    dag.hashall = 1
    
    # Evaluates the dependencies and computes hashes if none existed.
    dag.run()
    
    # Export the file.
    dag.exporthash()

Example: Hashing and Sqlite
---------------------------
    # This time use sqlite database instead of a text file.
    # Ok if it doesn't exist yet. It will be created.
    dag = dagger.dagger('hash.sqlite', sqlite=1)
    
    # dag.add(...)
    
    # Export the file, but not needed since all updates are atomically commited.
    dag.exporthash()
    
Example: Control Hashing for Specific Files
-------------------------------------------
    dag.hash('myfile.txt', 1) # Enable hashing for file.
    dag.hash('myfile.txt', 0) # Turn it off (hashing is off by default).

Example: Using Graph Search Results
-----------------------------------
    dag.add(...)
    dag.run()
    # See the depth-first-search node order.
    print dag.ordernames() 
    # 2,4,5,3,1,7,6
    
    # Access the nodes directly.
    print dag.order
    # [<dagger.node object at ...>, <dagger.node object at ...>, ...]

    # Find all possible paths in graph. Path order will be bottom-up.
    dag.run(allpaths=1)
    
    # Now each node will have list of all possible paths to dependents.
    print dag.get('4').paths # Lists will have node references.
    
    # Or get paths as just names. For our quick example graph:
    print dag.paths2names('4')
    # [['3', '1'], ['3', '6']]
    
News
----
v0.0.0 2012/10/15

- Initial release.

Distribution
------------
    make html
    make dist VER=0.0.0

Publishing
----------
    ssh -t rsz,pythondagger@shell.sourceforge.net create
    scp html/* rsz,pythondagger@shell.sourceforge.net:/home/project-web/pythondagger/htdocs
    scp ../pythondagger-0.0.0.tar.gz rsz,pythondagger@shell.sourceforge.net:/home/frs/project/p/py/pythondagger

License
-------
Copyright 2012 Remik Ziemlinski under the terms of the GNU General Public License

<link rel="stylesheet" href="http://yandex.st/highlightjs/7.0/styles/default.min.css">
<script src="http://yandex.st/highlightjs/7.0/highlight.min.js"></script>
<script>hljs.initHighlightingOnLoad();</script>

<style type="text/css">
body {
  font-family: Sans-Serif;
}
</style>
