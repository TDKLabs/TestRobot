#!C:\tdk\TDKAutoTest\src\win\python\python.exe 

"""
    winpdb

    A wrapper for winpdb.py

    Copyright (C) 2005-2009 Nir Aides

    This program is free software; you can redistribute it and/or modify it 
    under the terms of the GNU General Public License as published by the 
    Free Software Foundation; either version 2 of the License, or any later 
    version.

    This program is distributed in the hope that it will be useful, 
    but WITHOUT ANY WARRANTY; without even the implied warranty of 
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along 
    with this program; if not, write to the Free Software Foundation, Inc., 
    59 Temple Place, Suite 330, Boston, MA 02111-1307 USA    
"""



import sys
import os



STR_VERSIONS_ERROR_TITLE = 'Warning'
STR_VERSIONS_ERROR_MSG = """Winpdb is being run with the wrong version of Python.
Winpdb path: %s
Python path: %s""" % (os.path.abspath(__file__), os.path.abspath(sys.executable))



def expandPath(p):
    if not '~' in p:
        return p

    d, b = os.path.split(p)

    if '~' in d:
        d = expandPath(d)

    if not '~' in b:
        return os.path.join(d, b)

    _prefix, _index = b.split('~', 1)
    prefix = _prefix.lower()
    index = int(_index)

    for f in os.listdir(d):
        if not f.replace(' ', '').lower().startswith(prefix):
            continue

        index -= 1
        if index == 0:
            return os.path.join(d, f)
            


if os.name == 'nt':
    path1 = expandPath(os.path.abspath(os.path.dirname(sys.executable))).lower()
    path2 = expandPath(os.path.abspath(os.path.dirname(__file__))).lower()

    if not path2.startswith(path1):
        sys.__stderr__.write(STR_VERSIONS_ERROR_MSG)
        
        try:
            import Tkinter
            import tkMessageBox

            Tkinter.Tk().wm_withdraw()
            tkMessageBox.showwarning(STR_VERSIONS_ERROR_TITLE, STR_VERSIONS_ERROR_MSG)

        except:
            pass



import winpdb



winpdb.main()




