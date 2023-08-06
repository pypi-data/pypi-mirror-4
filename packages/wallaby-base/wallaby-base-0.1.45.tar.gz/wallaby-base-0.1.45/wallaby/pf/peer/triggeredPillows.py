# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class TriggeredPillows(Peer):
    def __init__(self, room, pillows):
        Peer.__init__(self, room)

        self._triggers = {}

        for config in pillows:
            if config == None: continue
            trigger  = config.get("trigger", None)
            args     = config.get("trigger-args", None)
            pillow   = config.get("pillow", None)
            feathers = config.get("feathers", None)
            isJson   = config.get("isJson", False)

            if None in (trigger, pillow): continue

            if trigger not in self._triggers:
                self._triggers[trigger] = []

            self._triggers[trigger].append({
                "args": args,
                "pillow": pillow,
                "feathers": feathers,
                "isJson": isJson
            })

    def __translate(self, feathers, doc, path, value):
        if feathers != None:
            from wallaby.common.pathHelper import PathHelper
            import re
            if isinstance(feathers, (str, unicode)):
                if '%VALUE' in feathers:
                    match = re.match('(.*?)%VALUE:?(.*?)%(.*)', feathers)
                    if match.group(2):
                        try:
                            if match.group(1) or match.group(3):
                                if doc is not None:
                                    feathers = match.group(1) + unicode(doc.get(".".join( (path, match.group(2)) ))) + match.group(3)
                                else:
                                    feathers = match.group(1) + unicode(PathHelper.getValue(value, match.group(2))) + match.group(3)
                            else:
                                if doc is not None:
                                    feathers = doc.get(".".join( (path, match.group(2)) ))
                                else:
                                    feathers = PathHelper.getValue(value, match.group(2))
                        except:
                            feathers = None
            
                    else:
                        if match.group(1) or match.group(3):
                            feathers = match.group(1) + unicode(value) + match.group(3)
                        else:
                            feathers = value

                if '%path%' in feathers:
                    feathers = re.sub('%path%', path, feathers)

            if isinstance(feathers, dict):
                import copy
                feathers = copy.deepcopy(feathers)
                for k, v in feathers.items():
                    if isinstance(v, (str, unicode)) and '%VALUE' in v:
                        match = re.match('(.*?)%VALUE:?(.*?)%(.*)', v)

                        if match.group(2):
                            try:
                                if match.group(1) or match.group(3):
                                    if doc is not None:
                                        v = match.group(1) + unicode(doc.get(".".join( (path, match.group(2)) ))) + match.group(3)
                                    else:
                                        v = match.group(1) + unicode(PathHelper.getValue(value, match.group(2))) + match.group(3)
                                else:
                                    if doc is not None:
                                        v = doc.get(".".join( (path, match.group(2)) ))
                                    else:
                                        v = PathHelper.getValue(value, match.group(2))
                            except Exception as e:
                                v = None

                        else:
                            if match.group(1) or match.group(3):
                                v = match.group(1) + unicode(value) + match.group(3)
                            else:
                                v = value

                    if isinstance(v, (str, unicode)) and '%PATH%' in v:
                        v = re.sub('%PATH%', path, v)

                    feathers[k] = v
            
        return feathers 

    def trigger(self, trigger, args=None, doc=None, path=None, value=None, *ignore):
        if trigger not in self._triggers: 
            return False

        found = False

        for t in self._triggers[trigger]:    
            if args != None and args != t['args']: continue
            found = True

            feathers = t['feathers']            

            if t['isJson']:
                jsonString = '{"object":' + feathers + '}'
                try: 
                    import json
                    feathers = json.loads(jsonString)
                    feathers = feathers["object"]
                except Exception as e:
                    print "Error while parsing json", jsonString, e
                    feathers = None

            feathers = self.__translate(feathers, doc, path, value)
          
            if isinstance(t['args'], (str, unicode)):
                import re 
                match = re.match('^delay:(.*)$', t['args'])
                if match is not None:
                    try:
                        delay = float(match.group(1))
                        from twisted.internet import reactor
                        reactor.callLater(delay, self._throw, t['pillow'], feathers)
                        return
                    except: pass

            self._throw(t['pillow'], feathers)

        return found
