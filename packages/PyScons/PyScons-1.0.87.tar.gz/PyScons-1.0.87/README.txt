
=======

PyScons
=======

PyScons is a tool which works with Scons_. It 
is installed into a new environment with either of the two commands::

    from pyscons import PYTOOL
    env = Environment(tools = ['default', PYTOOL()])

or::

    from pyscons import PYTOOL
    env = Environment()
    PYTOOL()(env)

This does three things:

1. Installs a builder: PyScript.
2. Installs a builder: PyScons.
3. Installs a new scanner for python scripts.

PyScript
--------

This Builder runs python scripts and modules. 

First, it will automatically find the ".py" files referred to when 
running a module as a script with the '-m' option. For example
the following code will run a module as script and add the appriate files
to the dependencies::

   env.PyScript("out", ["-m timeit", "myscript.py"], "python $SOURCES > $TARGET")

Second, it defaults the command string to "python $SOURCES" and using the "capture"
keyword argument, can automatically append the appropriate strings to capture
the output or error (or both) to the targets::

   env.PyScript("out", ["-m timeit", "myscript.py"], capture="output")
   
or to capture both the output and error::
  
   env.PyScript(["out","err"], ["-m timeit", "myscript.py"], capture="both")
   
Just like Command, multiple steps can be used to create a file::

   env.PyScript("out", ["step1.py", "step2.py"], 
        ["python ${SOURCES[0]} > temp", "python ${SOURCES[1]} > $TARGET", Delete("temp")])

PyScons (experimental)
----------------------

This Builder enables running a python script as if it is a scons script. 

This is distinct from SConscript which functions like an include. Instead, PyScons spawns a new scons process.
Spawning a new process allows for temporary files to be automatically deleted without triggering a rebuild.

To use this builder, create a .py file with, for example, the following code in a file (my_scons.py)::

    from pyscons import PySconsSetup
    targets, sources, basename = PySconsSetup()
   
    temp = basename + ".temp"

    PyScript(temp, ["step1.py"] + sources, capture="out")
    Pyscript(targets, ["step2.py", temp], capture="out")
 
Now, this file can be called from a SConstruct file like so::

    PyScons(targets, sources, "my_scons.py", options = "-j4")

The string in the options keyword is NOT added to the command signature. Options that do affect the output
should be added to the sig_options keyword, and these will be added to the signature::

    PyScons(targets, sources, "my_scons.py", options = "-j4", sig_options = "--critical_opt")

The temp file be generated if it is required to generate targets, but will be immediately deleted.
This is useful for builders which generate large intermediate files which would should be deleted
without triggering a rebuild. This can be better than passing a list to the Command function for a 
few special cases:

1. PyScons enables parallel execution of a multistep submodule(if you pass the -j option to the spawned scons) 
2. PyScons creates a workflow environment (like Pipeline Pilot) in scons which enables complex tasks to be packaged in scons files for use in other scons files.
3. PyScons can turn intermediate file deletion on and off with a single flag::

    PyScons(targets, sources, "my_scons.py", clean = True) # intermediate file deleted
    PyScons(targets, sources, "my_scons.py", clean = False) # intermediate file retained

4. PyScons ignores the "options" parameter when constructing the command's signature, enabling you to change parameters (e.g. the -j number of procs) without triggering a rebuild.

Unfortunately, dependency tracking does not propagate up from the spawned scons. In this example, 
"step1.py" and "step2.py" will not be tracked and changes to them will not trigger a rebuild. There
is a trick around this, add the following two lines to "my_scons.py"::

    ### step1.py
    #DEPENDS step2.py

These two comments illustrate the two ways of explicetely including the dependency on the two 
scripts used on the scons file. To help distinguish files which are to be run in this ways 
(being called by PyScons), they may be given the extensions ".scons" or ".pyscons" as well. 
In this example, this would amount to renaming "my_scons.py" to "my_scons.scons" 

PyScanner
---------

This scanner uses the modulefinder module to find all import dependencies 
in all sources with a 'py' extension. It can take two options in its constructor:

1. filter_path: a callable object (or None) which takes a path as input and returns true
   if this file should be included as a dependency by scons, or false if it should be ignored.
   By default, this variable becomes a function which ensures that no system python modules
   or modules from site-packages are tracked. To track all files, use "lambda p: True".

2. recursive: with a true (default) or false, it enables or disables recursive dependency 
   tracking. 

For example to track all files (including system imports) in a nonrecursive scanner, use
the following install code in your SConstruct::

    from pyscons import PYTOOL
    env = Environment(tools = ['default', PYTOOL(recursive = False, filter_path = lambda p: True)])

Known Issues
------------

Relative imports do not work. This seems to be a bug in the modulefinder package that I do not 
know how to fix.

Author
------

S. Joshua Swamidass (homepage_)

.. _homepage: http://swami.wustl.edu/
.. _Scons: http://www.scons.org/
