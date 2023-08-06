# -*- coding: utf-8 -*-

# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.python import log
from twisted.internet import defer, task
import sys, traceback, os, re, json, glob, fnmatch
import socket
from platform import *

logTrace    = False
logDebug    = True
shutdown    = False
config      = None

pLogo       = None
app         = None
appModule   = None
appPath     = None

DEBUG       = 1
TRACE       = 2
WARN        = 3
CRIT        = 4
INFO        = 5

uname     = uname()[0]

widgets  = []

shutdownCBs = []

def replaceValue(dct, val):
    if isinstance(val, dict) and '_path' in dct:
        from wallaby.common.pathHelper import PathHelper
        val = PathHelper.getValue(val, dct['_path'])

    if val == None: 
        val = "-"

    if isinstance(val, (bool, int, float)):
        val = str(val)

    if val in dct:
        val = dct[val]
    elif "*" in dct:
        val = dct["*"].replace("*", val)

    return val

def renderType(val, type, args, edit=False, fct=replaceValue):
    if type == 'datetime':
        if val != None and len(val) >= 5:
            val = ('%02d.%02d.%04d %02d:%02d' % (val[2], val[1], val[0], val[3], val[4]))
        else:
            val = "-"
    if type == 'date':
        if val != None and len(val) >= 3:
            val = ('%02d.%02d.%04d' % (val[2], val[1], val[0]))
        else:
            val = "-"
    elif isinstance(type, (str, unicode)) and type in ('markdown'):
        import markdown
        val = markdown.markdown(val)
    elif isinstance(type, (str, unicode)) and type in ('number' or 'numberedit'):
        if edit:
            try:
                val = unicode(float(val))
            except:
                val = "0.0"
        else:
            try:
                if len(args) > 0:
                    val = ("%." + args[0] + "f") % float(val)
                else:
                    val = ("%d") % int(val)
            except:
                val = "0"

    elif isinstance(type, (str, unicode)) and type in ('currency' or 'currencyedit'):
        if edit:
            try:
                val = unicode(float(val))
            except:
                val = "0.0"
        else:
            try:
                val = u"€ %.2f" % float(val)
            except:
                val = "-"
    elif isinstance(type, dict):
        if val == None:
            val = "-"
        if isinstance(val, list):
            lst = []
            for v in val:
                lst.append(fct(type, v))

            return lst
        else:
            val = fct(type, val)

    if isinstance(val, (dict, list)):
        if isinstance(type, (str, unicode)) and type in ('stringedit', 'autoedit', 'dictedit', 'listedit'):
            import json
            return json.dumps(val)
        else:
            return unicode(len(val)) + u" items"
    return val

def convertType(t):
    if t == None: return t
    if '{' in t:
        try:
            import json
            t = json.loads(t)
        except Exception as e:
            print 'ERROR - Json parse error', str(e), 'in', t

    return t

def extractType(lst, json=True):
    firstList  = []
    secondList = []
    thirdList  = []


    for e in lst:
        m = re.match(r'^<([^>]*)>(.*)', e)
        if m != None:
            type = m.group(1)

            args = []

            if '{' in type:
                if json:
                    try:
                        type = json.loads(type)
                    except Exception as e:
                        print 'ERROR - Json parse error', str(e), 'in', type

            elif ',' in type:
                args = type.split(',')
                type = args.pop(0)

            firstList.append(type)
            secondList.append(args)
            thirdList.append(m.group(2))
        else:
            firstList.append('string')
            secondList.append([])
            thirdList.append(e)

    return firstList, secondList, thirdList

def splitList(lst, sep):
    firstList = []
    secondList = []

    for e in lst:
        if e is None:
            continue

        t = e.rsplit(sep, 1)
        first = t[0]
        if len(t) > 1:
            second = t[1]
        else:
            second = first

        firstList.append(first)
        secondList.append(second)

    return firstList, secondList

def addShutdownCB(cb):
    shutdownCBs.append(cb)

def callShutdownCBs():
    for cb in shutdownCBs:
        cb()

def Property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)

def packagePath(package):
    pathes = []
    try:
        pkg = __import__(package, globals(), locals(), ["*"], 0)
        for p in pkg.__path__: pathes.append(p)  
    except:
        pass 

    return pathes

def imp(name, trace=False):
    m = re.match(".*?\.?(wallaby.*)", name)
    if m:
        name = m.group(1)

    try:
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod
    except Exception as e:
        if trace or not isinstance(e, ImportError):
            import traceback 
            traceback.print_exc(file=sys.stdout)
        return None

def info(*msg):
    log.msg(toMessage("INFO" ,msg), logLevel=INFO)
    
def warn(*msg):    
    log.msg(toMessage("WARNING" ,msg), logLevel=WARN)
        
def crit(*msg):    
    log.err(toMessage("CRITICAL" ,msg), logLevel=CRIT)
        
def debug(*msg):    
    print toMessage("DEBUG", msg) #TODO: remove
    if not logDebug:
        return

    log.msg(toMessage("DEBUG" , msg), logLevel=DEBUG)
    
def trace(*params):
    if not logTrace:
        return

    log.msg(toMessage("TRACE" , params), logLevel=TRACE)
    
    type, value, trace = sys.exc_info()   
    stack = traceback.extract_stack()
    call  = stack[len(stack)-2]
    msg   = "FILE: " + call[0] + "  LINE: " + str(call[1])  
    log.msg(msg, logLevel=TRACE)

def toMessage(prefix, list):
    msg = prefix
    for m in list:
        msg = msg + " " + str(m)
    return msg
    
def deferredSleep(seconds):
    d = defer.Deferred()

    from twisted.internet import reactor
    reactor.callLater(seconds, d.callback, seconds)
    return d

def splitPath(path):
    return path.split('.');

def deferredCall(*args):
    from twisted.internet import reactor
    return task.deferLater(reactor, 0, *args)

## Code borrowed from wxPython's setup and config files
## Thanks to Robin Dunn for the suggestion.
## I am not 100% sure what's going on, but it works!
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_data_files(prefix, srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append( (prefix + "/" + dirname, names ) )

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

def wallabyPackages(packages):
    lst = []
    dirs = {}
    s = set(packages)

    import wallaby as w
    for path in w.__path__:
        packages = find_packages(path, base="wallaby")     
        for p in packages:
            if not '.apps.' in p or 'inspector' in p:
                s.add(p) 
                dirs[p] = packages[p]

    for p in s: lst.append(p)
    return lst, dirs

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item

            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

