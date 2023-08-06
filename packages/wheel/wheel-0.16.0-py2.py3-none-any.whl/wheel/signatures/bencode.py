#!/usr/bin/env python
# bencode (canonical representation) for simple dicts
# used to generate a key fingerprint

def bencode(structure):
    if isinstance(structure, int):
        return "i%de" % (structure,)
    elif isinstance(structure, str):
        return "%d:%s" % (len(structure), structure)
    elif isinstance(structure, dict):
        return 'd%se' % ''.join(''.join((bencode(k), bencode(v))) for k, v in sorted(structure.items()))
    raise ValueError("not a general-purpose bencode; cannot encode {}".format(type(structure)))

