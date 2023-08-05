"""
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
"""
import os
import os.path
import shutil
from SCons import Util
from SCons.Action import CommandGeneratorAction
from SCons.Scanner import Scanner
from SCons.Script.SConscript import DefaultEnvironmentCall
from modulefinder import ModuleFinder as MF
from SCons.Script import *
import re
import hashlib
import tempfile
import base64
from itertools import chain
import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

class PyScanner(MF):
    """
    A scanner for py files which finds all the import dependencies.
    """
    def __init__(self, path_filter, *args, **kwargs):
        self.path_filter = path_filter
        MF.__init__(self, *args, **kwargs)

    def import_hook(self, name, caller, *arg, **karg):
        if caller.__file__ == self.name: 
            return MF.import_hook(self, name, caller, *arg, **karg) 

    def __call__(self, node, env, path):
        if str(node).split('.')[-1] not in ['py', 'pyc', 'pyo']: return []
        self.modules = {}; 
        self.name = str(node)

        try: self.run_script(self.name)
        except: pass

        imports = [m.__file__ for m in self.modules.values() if m.__file__ != None]

        if str(node).split('.')[-1] in ["py", "pyscons", "scons"]:
            contents = open(str(node)).read()
            D = re.findall("#"+"##(.+)", contents) + re.findall("#" +"DEPENDS(.+)", contents, re.I)
            D = [f for f in chain(*(f.split() for f in D))]
            d = os.path.dirname(str(node))
            for f in D:
                f = os.path.join(d,f)
                if os.path.exists(f): imports.append(f)
        
        imports = list(os.path.abspath(m) for m in imports if self.path_filter(m))
        return imports

def ToList(input):
    if input is None: input = [] 
    elif not Util.is_List(input): input = [input]
    return input

_USED_DIRS = set()

def _PyScript(env, target, source, command = "python $SOURCES", capture=None,
        execute=None, tempdir=None, exit=False, clean=True, lightweight=True, *args, **kwargs): 
    """
    A new Builder added to a scons environment which has the same syntax as Command.
    """
    target = ToList(target)
    source = ToList(source) 
    subst = list(source)
    command = ToList(command)

    for n,s in enumerate(source): 
        s = str(s)
        if s.strip()[:3] == "-m ":
            module = s.strip()[3:]
            s = os.popen("python -c 'import %s as M; print M.__file__'" 
                                    % module).read().strip()
        if s[-3:] in ["pyc", "pyo"]: s = s[:-1]
        source[n] = s

    if capture in ["stdout", "out", "output"]: command[-1] += " > $TARGET"
    elif capture in ["stderr", "err", "error"]: command[-1] += " 2> $TARGET"
    elif capture == "join": command[-1] += " &> $TARGET"
    elif capture == "both": command[-1] += " > ${TARGETS[0]} 2> ${TARGETS[1]}"
    elif capture == None: pass

    command_sig = [ env.subst(c, target=target, source=subst) for c in command ]

    if exit and "exit" in ARGUMENTS: execute = "exit %s #" % (ARGUMENTS["exit"])

    if tempdir == None:
        m = hashlib.sha1()
        m.update("\n".join(command_sig))
        basename = os.path.join("temp", "." + base64.b64encode(m.digest(),
            "_-").strip("="), '')
    else: basename = tempdir

    if env.GetOption("clean") and basename:
        if os.path.exists(basename): env.Execute(Delete(basename))
    elif execute:
        if not os.path.exists(basename): mkdir_p(basename)
        scons = """from pyscons import *
targets, sources, basename = PySconsSetup()

env = DefaultEnvironment()

command_sig = %s

stargets = [t + ".shadow" for t in targets]
command =  [env.subst(c, target=stargets, source=sources) for c in %s ]
command += ["mv %%s %%s" %% (s, t) for s,t in zip(stargets, targets)]

gen = lambda source, target, env, for_signature: command_sig if for_signature else command
PyScript(targets, sources, CommandGeneratorAction(gen,{}), clean=False)
""" % (repr(command_sig), repr(command))
        scons = re.sub("\$", "\$", scons)

        arg = " ".join(["in%g=%s" % (n+1, str(s)) for n,s in enumerate(source)])
        arg += " " + " ".join(["out%g=%s" % (n+1, str(s)) for n,s in enumerate(target)])
        vars = " temp=" + basename

        exe = os.path.join(basename, "EXECUTE")
        file = open(exe, 'w')
        comments = "\n".join(["#TARGET\t%s" % s for s in target] + ["#SOURCE\t%s"
            %s for s in source + [exe]])
        print >>file, "#!/bin/bash\n%s\nscons %s %s -f <( cat <<ENDOFSCONS\n%s\nENDOFSCONS\n) $*" % (comments, vars, arg, scons)
        os.chmod(exe, 0755)
        file.close()

        if not lightweight: command = exe + " -Q"

    if execute: command = [execute + " " + basename]

    ftargets = [t + ".force" for t in target]
    if reduce(lambda a,b: a&b, (os.path.exists(t) for t in ftargets)):
        command = ["mv %s %s" %(f,t) for f,t in zip(ftargets,target)]

    if clean and not execute and os.path.exists(basename): env.Execute("rm -rf %s" % basename)

    gen = lambda source, target, env, for_signature: command_sig if for_signature else command
    return env.Command(target, source, CommandGeneratorAction(gen,{}), *args, **kwargs)

def _PyScons(env, target, source, scons, execute=None, options="-Q",
        sig_options="", clean = True, tempdir = None, exit=False):
    global _USED_DIRS
    target = ToList(target)
    source = ToList(source)

    args = " ".join(["in%g=%s" % (n+1, str(s)) for n,s in enumerate(source)])
    args += " " + " ".join(["out%g=%s" % (n+1, str(s)) for n,s in enumerate(target)])

    sig = "scons %s -f%s %s" % (sig_options, scons, args)
    if tempdir == None:
        m = hashlib.sha1()
        m.update(sig)
        basename = os.path.join("temp", "." + base64.b64encode(m.digest(),
            "-_").strip("="), '')
    else: basename = tempdir

    USE_DIR = tuple(os.path.split(basename))
    if USE_DIR in _USED_DIRS: raise ValueError("Cannot use temp directory %s in more than one PyScript or PyScons." % basename)
    else: _USED_DIRS.add(USE_DIR)

    vars = " temp=" + basename

    if not os.path.exists(basename): mkdir_p(basename)
    exe = os.path.join(basename, "EXECUTE")
    file = open(exe, 'w')
    comments = "\n".join(["#TARGET\t%s" % s for s in target] + ["#SOURCE\t%s" %s for s in source + [scons, exe]])
    print >>file, "#!/bin/bash\n%s\nscons %s %s -f%s %s $*" % (comments, vars, sig_options, scons, args)
    os.chmod(exe, 0755)
    file.close()

    if "exit" in ARGUMENTS: options += " -k exit=%s" % ARGUMENTS["exit"]
    cmd = " ".join([exe, options])
    cleancmd = cmd + " --clean"

    if env.GetOption("clean") and not clean: 
        env.Execute(cleancmd)
        env.Execute(Delete(basename))

    if not execute: cmd = [cmd, cleancmd] if clean else [cmd]
    else: cmd = [execute + " " + basename]

    if exit and "exit" in ARGUMENTS: cmd = "exit %s # %s" % (ARGUMENTS["exit"], basename)

    ftargets = [t + ".force" for t in target]
    if reduce(lambda a,b: a&b, (os.path.exists(t) for t in ftargets)):
        cmd = ["mv %s %s" %(f,t) for f,t in zip(ftargets,target)]

    gen = lambda source, target, env, for_signature: sig if for_signature else cmd
    return env.Command(target, source + [scons], CommandGeneratorAction(gen,{}))

PyScons = DefaultEnvironmentCall("PyScons")
PyScript = DefaultEnvironmentCall("PyScript")

class PYTOOL:
    def __init__(self, path_filter = None, recursive=True):
        if path_filter == None: 
            path_filter = lambda p: self.env.GetLaunchDir() == p[:len(self.env.GetLaunchDir())]
        self.path_filter = path_filter
        self.recursive = recursive

    def __call__(self, env):
        self.env = env
        env.Append(SCANNERS = Scanner(function = PyScanner(self.path_filter), 
                    name = "PyScanner", skeys = ['.scons', '.pyscons', '.py', '.pyo', '.pyc'], recursive=self.recursive))
        env.AddMethod(_PyScript, "PyScript")
        env.AddMethod(_PyScons, "PyScons")
        return env

def PySconsSetup(env=None, args=ARGUMENTS, tools=['default', PYTOOL()]):
    if env == None: env = DefaultEnvironment(ENV=os.environ, tools=tools, IMPLICIT_COMMAND_DEPENDENCIES=0)

    sources = []
    targets = []

    for a in args:
        if a[:2] == "in":
            try: sources.append((int(a[2:]), args[a]))
            except: pass
        if a[:3] == "out":
            try: targets.append((int(a[3:]), args[a]))
            except: pass

    if "exclude" in args: #exlude files names listed in this file from SHIP.tz2
        exclude = set(L.strip() for L in file(args["exclude"]))
    else: exclude = set()

    basename = args["temp"]
    env.SConsignFile(os.path.join(env.GetLaunchDir(), basename, "sconsign"))

    sources = [a for i,a in sorted(sources)]
    targets = [a for i,a in sorted(targets)]

    env.NoClean(targets)
    env.Default(targets)

    ftargets = [t + ".force" for t in targets]
    if "print" not in args and reduce(lambda a,b: a&b, (os.path.exists(t) for t in ftargets)):
        for f,t in zip(ftargets,targets): 
            print "Move(%s,%s)"%(f,t)
            shutil.move(f,t)
        env.Exit(0)

    exe = os.path.join(basename, "EXECUTE")
    SIGNATURES = os.path.join(basename, ".sconsign.dblite")

    return targets, sources, basename
