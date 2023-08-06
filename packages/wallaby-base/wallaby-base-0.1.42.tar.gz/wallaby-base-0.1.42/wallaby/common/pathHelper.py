# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX
import sys, re

class SelectionNotSpecified(Exception):
    pass

class SelectionOutOfRange(SelectionNotSpecified): #TODO: Change inheritance
    pass

class PathHelper:
    @staticmethod
    def getSelection(path, selection=None):
        resPath = selectionPath = ""

        if path != None and re.search("__root__", path):
            path = path.replace("__root__.", "").replace("__root__", "")

        rest = str(path)

        while rest != None and len(rest) > 0:
            lst = rest.split('.', 1)
            if len(lst) == 2:
                part, rest = lst
            else:
                part, rest = lst[0], None

            selectionPath = selectionPath+part+'.'

            if part == '*':
                part = PathHelper.getValue(selection, selectionPath+'_selection')

                if part == None:
                    raise SelectionNotSpecified()

            resPath = resPath + unicode(part) + "."

        return re.sub("\.$", "", resPath)

    @staticmethod
    def getValue(base, path, selection=None, asList=False, asDict=False, wrap=False):
        if base != None:
            if path != None:
                grp = re.match(r"\"(.*)\"", path)
                if grp:
                    return grp.group(1)

            pos = base
            selectionPath = ""

            if path != None and re.search("__root__", path):
                path = path.replace("__root__.", "").replace("__root__", "")

            rest = str(path)

            while rest != None and len(rest) > 0:
                lst = rest.split('.', 1)
                if len(lst) == 2:
                    part, rest = lst
                else:
                    part, rest = lst[0], None

                selectionPath = selectionPath+part+'.'

                if isinstance(pos,dict):
                    if part in pos:
                        pos = pos[part]
                    elif selection != None and part == '*':
                        part = PathHelper.getValue(selection, selectionPath+'_selection')

                        if part == None:
                            raise SelectionNotSpecified()
                        elif part not in pos:
                            raise SelectionOutOfRange()

                        if rest == '__key__':
                            return part

                        pos = pos[part]
                    else:
                        if rest != None and '*' in rest and '_selection' not in rest:
                            raise SelectionNotSpecified()
                        else:
                            return None
                elif isinstance(pos,list):
                    if part == '*':
                        part = PathHelper.getValue(selection, selectionPath+'_selection')
                    else:
                        try:
                            part = int(part)
                        except:
                            raise SelectionNotSpecified()

                    if part == None:
                        raise SelectionNotSpecified()
                    elif part >= len(pos) or part == -1:
                        raise SelectionOutOfRange()

                    pos = pos[part]
                elif rest != None and '*' in rest:
                    raise SelectionNotSpecified()
                else:
                    return None

            if asList == True and not isinstance(pos, list):
                #if isinstance(pos, dict):
                #    keys = sorted(pos)
                #    values = []
                #    for key in keys:
                #        values.append(pos[key])
                #    pos = values
                #else:
                #    pos = [pos]

                if wrap:
                    pos = [pos]
                else:
                    return None

            if asDict == True and not isinstance(pos, dict):
                #if isinstance(pos, list):
                #    values = {}
                #    for i in range(len(pos)):
                #        values[i] = pos[i]
                #    pos = values
                #else:
                #    pos = {"_undef_":pos}
                if wrap:
                    pos = {"_undef_":pos}
                else:
                    return None

            return pos
        return None

    @staticmethod
    def setValue(base, path, value, selection=None, merge=False, isSub=False, recurse=False):
        if base == None: return

        if path != None and re.search("__root__", path):
            path = path.replace("__root__.", "").replace("__root__", "")

        if value != None and (merge or recurse):
            if isinstance(value, dict):
                for k, v in value.items():
                    if not isSub and k != None and len(k) > 0 and k[0] == '_': continue 
                    subpath = k
                    if path != None: subpath = path + "." + subpath 

                    PathHelper.setValue(base, subpath, v, selection, merge=merge, isSub=True, recurse=recurse)

                return
            elif isinstance(value, (list, tuple)):
                for k in range(len(value)):
                    v = value[k]

                    subpath = unicode(k)
                    if path != None: subpath = path + "." + subpath

                    PathHelper.setValue(base, subpath, v, selection, merge=merge, isSub=True, recurse=recurse)

                return

        pos = base
        lastpos = None
        part = None
        lastpart = None
        selectionPath = ""

        parts = str(path).split('.')
        if len(parts) > 0:
            for i in range(len(parts)):
                lastpart = part
                part = parts[i]
                selectionPath = selectionPath+part+'.'

                if part == '*' and selection != None:
                    part = PathHelper.getValue(selection, selectionPath+'_selection')

                    if part == None:
                        raise SelectionNotSpecified()

                    if isinstance(pos,dict):
                        if part not in pos:
                            raise SelectionOutOfRange()
                    else:
                        if pos == None:
                            lastpos[lastpart] = [] 
                            pos = lastpos[lastpart]

                        elif part >= len(pos) or part == -1:
                            raise SelectionOutOfRange()

                        elif not isinstance(pos,list):
                            lastpos[lastpart] = [] 
                            pos = lastpos[lastpart]
                elif not isinstance(pos, (dict, list, tuple) ):
                    lastpos[lastpart] = {}
                    pos = lastpos[lastpart]

                if isinstance(pos, (list, tuple)):
                    part = int(part)

                if i == len(parts)-1:
                    if not merge or (part not in pos or pos[part] == None):
                        pos[part] = value
                    elif value != None and merge and (part in pos):
                        if isinstance(pos[part], (str, unicode)) and isinstance(value, (float, int)):
                            try:
                                pos[part] = int(pos[part])
                            except:
                                try:
                                    pos[part] = float(pos[part])
                                except:
                                    pos["_old_" + part] = pos[part]
                                    pos[part] = value
                        
                else:
                    if isinstance(pos, dict) and part not in pos:
                        pos[part] = None
                    
                    lastpos = pos
                    pos = pos[part]
