# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

class Pillow(type):
    Out        = "WLBY_API_OUT"
    OutState   = "WLBY_API_OUT_STATE"
    In         = "WLBY_API_IN"
    InState    = "WLBY_API_IN_STATE"
    InOut      = "WLBY_API_IN_OUT"
    InOutState = "WLBY_API_IN_OUT_STATE"

    Runtime = "WLBY_API_RUNTIME"
    Startup = "WLBY_API_STARTUP"

    def __new__(mcs, name, bases, dict):
        in_dict = {}
        out_dict = {}

        inPillows = []
        outPillows = []

        import copy
        dct = copy.copy(dict)

        for key, val in dct.items():
            if val == Pillow.InOut: 
                in_dict[key] = name + ".In." + key 
                out_dict[key] = name + ".Out." + key 
                inPillows.append(key)
                outPillows.append(key)
            elif val == Pillow.InOutState: 
                in_dict[key] = name + ".In." + key + "!"
                out_dict[key] = name + ".Out." + key + "!"
                inPillows.append(key)
                outPillows.append(key)
            elif val == Pillow.In: 
                in_dict[key] = name + ".In." + key 
                inPillows.append(key)
            elif val == Pillow.InState: 
                in_dict[key] = name + ".In." + key  + "!"
                inPillows.append(key)
            elif val == Pillow.Out: 
                out_dict[key] = name + ".Out." + key 
                outPillows.append(key)
            elif val == Pillow.OutState: 
                out_dict[key] = name + ".Out." + key  + "!"
                outPillows.append(key)
            else:
                continue

            del dict[key]

        if len(in_dict)+len(out_dict) > 0:
            if '__doc__' not in dict:
                dict['__doc__'] = ''
            if len(in_dict) > 0:
                dict['__doc__'] += '\nIngoing Pillows:'
                for key in in_dict:
                    dict['__doc__'] += '\n\t* '+in_dict[key]
            if len(out_dict) > 0:
                dict['__doc__'] += '\nOutgoing Pillows:'
                for key in out_dict:
                    dict['__doc__'] += '\n\t* '+out_dict[key]
            dict['__doc__'] += '\n'

        if not 'Sending' in dict:
            dict['Sending'] = set()
        else:
            dict['Sending'] = set(dict['Sending'])

        if not 'Receiving' in dict:
            dict['Receiving'] = set()
        else:
            dict['Receiving'] = set(dict['Receiving'])

        if 'Routings' in dict:
            for f, t in dict['Routings']:
                dict['Sending'].add(t)
                dict['Receiving'].add(f)
        else:
            dict['Routings'] = set()

        dict['In'] = type(name + 'InPillows', (object,), in_dict)
        dict['Out'] = type(name + 'OutPillows', (object,), out_dict)

        dict['InPillows'] = inPillows 
        dict['OutPillows'] = outPillows 

        if not 'ObjectType' in dict:
            dict['ObjectType'] = Pillow.Startup

        return type.__new__(mcs, name, bases, dict)

