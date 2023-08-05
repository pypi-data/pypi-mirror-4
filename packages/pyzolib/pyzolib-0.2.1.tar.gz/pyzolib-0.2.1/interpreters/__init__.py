
# -*- coding: utf-8 -*-
# Copyright (c) 2012, Almar Klein

""" 
This module implements functionality to list installed Python 
interpreters, as well as Pyzo interpreters.

This list is compiled by looking at common location, and on Windows
the registry is searched as well.
"""

import sys
import os
from pyzolib import paths
from pyzolib import ssdf

from pyzolib.interpreters.pythoninterpreter import PythonInterpreter, PyzoInterpreter, _versionStringToTuple
from pyzolib.interpreters.inwinreg import get_interpreters_in_reg


def get_interpreters(minimumVersion=None):
    """ get_interpreters(minimumVersion=None)
    Returns a list of PythonInterpreter instances.
    If minimumVersion is given, return only the interprers with at least that
    version, and also sort the result by version number.
    """
    
    # Get Python interpreters
    if sys.platform.startswith('win'):
        pythons = _get_interpreters_win() 
    else:
        pythons = _get_interpreters_posix()
    pythons = set([PythonInterpreter(p) for p in pythons])
    
    # Get Pyzo paths
    pyzos = set([PyzoInterpreter(p) for p in _get_interpreters_pyzo()])
    
    # Remove Pyzo interpreters from pythons
    pythons = pythons.difference(pyzos)
    
    # Almost done
    interpreters = list(pyzos) + list(pythons)
    if minimumVersion:
        return _select_interpreters(interpreters, minimumVersion)
    else:
        return interpreters


def _select_interpreters(interpreters, minimumVersion):
    """ Given a list of PythonInterpreter instances, return a list with
    the interpreters selected that are valid and have their version equal 
    or larger than the given minimimVersion. The returned list is sorted
    by version number.
    """ 
    if not isinstance(minimumVersion, str):
        raise ValueError('minimumVersion in get_interpreters must be a string.')
    # Remove invalid interpreters
    interpreters = [i for i in interpreters if i.version]
    # Remove the ones below the reference version
    if minimumVersion is not None:
        refTuple = _versionStringToTuple(minimumVersion)
        interpreters = [i for i in interpreters if (i.version_info >= refTuple)]
    # Return, sorted by version
    return sorted(interpreters, key=lambda x:x.version_info)


def _get_interpreters_win():
    found = []
    
    # Query from registry
    for v in get_interpreters_in_reg():
        found.append(v.installPath() )
    
    # Check common locations
    for rootname in ['c:/', 'C:/program files/', 'C:/program files (x86)/']:
        if not os.path.isdir(rootname):
            continue
        for dname in os.listdir(rootname):
            if dname.lower().startswith('python'):
                try: 
                    version = float(dname[len('python'):])
                except ValueError:
                    continue
                else:
                    found.append(os.path.join(rootname, dname))
    
    # Normalize all paths, and remove trailing backslashes
    found = [os.path.normcase(os.path.abspath(v)).strip('\\') for v in found]
    
    # Append "python.exe" and check if that file exists
    found2 = []
    for dname in found:
        exename = os.path.join(dname, 'python.exe')
        if os.path.isfile(exename):
            found2.append(exename)
    
    # Returnas set (remove duplicates)
    return set(found2)


def _get_interpreters_posix():
    found=[]
    for searchpath in ['/usr/bin','/usr/local/bin','/opt/local/bin']: 
        # Get files
        try:
            files = os.listdir(searchpath)
        except Exception:
            continue
        
        # Search for python executables
        for fname in files:
            if fname.startswith('python') and not fname.count('config'):
                found.append( os.path.join(searchpath, fname) )
    
    # Resolve simlinks
    found = [os.path.realpath(v) for v in found]
    
    # Return as set (remove duplicates)
    return set(found)


def _get_interpreters_pyzo():
    """ Get a list of known Pyzo interpreters.
    """
    pythonname = 'python' + '.exe' * sys.platform.startswith('win')
    return [os.path.join(d, pythonname) for d in paths.pyzo_dirs()]
    

if __name__ == '__main__':
    for pi in getPythonInterpreters():
        print(pi)

