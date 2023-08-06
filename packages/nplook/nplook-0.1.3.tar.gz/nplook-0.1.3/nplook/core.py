
from __future__ import print_function
import sys
import numpy as np

def represent(obj, indent=0):
    if isinstance(obj, np.ndarray):
        if obj.shape == ():
            robj = obj[()]
            if isinstance(robj, dict):
                return represent(robj, indent+2)
            else:
                return '{2}{0} [{1}]'.format(repr(robj), obj.dtype, " "*indent)
        else:
            return "ndarray {0} [{1}]".format(obj.shape, obj.dtype)
    elif isinstance(obj, str):
        l = len(obj)
        if l > 60: 
            pr = '"' + obj[:60] + '..."' + " [string:{0}]".format(l)
        else:
            pr = '"' + obj + '"'
        return pr
    elif isinstance(obj, dict):
        s = [] 
        for key, value in obj.items():
            s.append("{2}| {0} : {1}".format(key, represent(value, indent+2), " "*indent))
        num = len(obj)
        return "dict ({0} entr{1})\n".format(num, ('ies', 'y')[num==1])+" "*indent + ("\n"+" "*indent).join(s) 
    else:
        lines = repr(obj).split("\n")
        if len(lines) > 5:
            lines = lines[:5] + ["..."]
        return ("\n"+" "*indent).join(lines)

def summarize(filename):
    s = ""
    try:
        data = np.load(filename)
    except IOError:
        data = None

    status = ''
    if data is None:
        return None#status = 'FILE NOT FOUND!'

    s += "-> {0} {1}\n".format(filename, status)
    
    if isinstance(data, np.lib.npyio.NpzFile):
        N = max(map(lambda x: len(x), data.keys()))
        indent = 3
        for k in data.keys():
            x = represent(data[k])
            x = x.replace('\n', '\n'+' '*(N+2 + indent + 1))
            s += " "*indent + "{0} : {1}\n".format(k.rjust(N), x)
    else:
        indent = 3
        x = represent(data)
        x = x.replace('\n', '\n'+' '*(indent))
        s += " "*indent + x

    # Remove the last newline
    if s[-1] == '\n':
        s = s[:-1]
    return s

