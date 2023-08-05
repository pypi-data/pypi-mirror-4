

# from show import show
import sys

_PY3 = (sys.version_info[0] > 2)

HASH       = 1    # hash ALWAYS considered for primitive types
ID         = 2
TYPE       = 4
CODE       = 8
ATTRIBUTES = 16
ITEMS      = 32

DEFAULT_CONSIDER = CODE | ATTRIBUTES | ITEMS

STRING_TYPES = [str, bytes] if _PY3 else [str, unicode]
PRIMITIVE_TYPES = tuple(STRING_TYPES + [int, float, complex])

FUNC_ATTR = '__code__' if _PY3 else 'func_code'

def chash(obj, considering=DEFAULT_CONSIDER, seen=None):
    """
    Return a content hash of the given object.
    """
    
    # show(obj)
    
    if seen is None:
        seen = set()
        
    if isinstance(obj, PRIMITIVE_TYPES):
        return hash(obj)
    
    if isinstance(obj, tuple):
        try:
            return hash(obj)
        except TypeError:
            return hash(tuple([chash(item, considering, seen) for item in obj]))
        # if tuple is unhashable (ie, contains unhashable things), treat it as
        # a collection/list
        
    # general cyclic item detection
    _id = id(obj)
    if _id in seen:
        return 0
    seen.add(_id)
        
    hashval = 0
    
    if considering & HASH:
        hashval ^= hash(obj)
        
    if considering & TYPE:
        hashval ^= hash(type(obj))
        
    if considering & ID:
        hashval ^= _id    

    if considering & CODE:                    # CODE is the most important attribute, overriding all others
        code = getattr(obj, FUNC_ATTR, None)
        if code:
            hashval ^= hash(code)
    elif considering & ATTRIBUTES: 
        try:
            hashval ^= chash(obj.__dict__, considering, seen)
        except AttributeError:
            pass
    
    if considering & ITEMS and hasattr(obj, '__iter__'):
        if hasattr(obj, 'items'):
            for item in obj.items():
                hashval ^= chash(item, considering, seen)
        else:
            for itemtup in enumerate(obj):
                hashval ^= chash(itemtup, considering, seen)
    
    return hashval
    # should we use a bit-spreading hash here as a final salting operation?
    
    # ideally would use enumerate any time order is important, such as OrderedDict and such,
    # even if it has an items() attribute
    # hasattr(o, '__reversed__') may => ordered
    
    # for sets and other non-ordered types, we depend on the property that
    # however constructed and in whatver order, will iterate in a given order
    # tested - seems to work
    
def _demo_chash():
    from collections import OrderedDict, Counter
    from show import show
    
    class O(object):
        one = 1
        two = 2
            
    testitems = [
        1,
        2.3,
        2.3+5.6j,
        'this is a string',
        (1, 4),
        ('this', 'that'),
        O,
        O(),
        [1, 2, 3, 4],
        [1, 2, 3, 4],
        range(3),
        xrange(3),
        xrange(4), 
        xrange(4),
        eval('xrange(4)'),
        lambda x: x + 1,
        lambda x: x + 1,
        eval('lambda x: x + 1'),
        lambda x: x + 2,
        {'a':1, 'b':12, 'c':99},
        {'a':1, 'b':12, 'c':99},
        OrderedDict([('a', 1), ('b', 12), ('c', 99)]),
        Counter({'a':1, 'b':12, 'c':99}),
        [1,[2,3,[4,5]]],
        {'a':1, 'b':12, 'c':99,
         'od': OrderedDict([('a', 1), ('b', 12), ('c', 99)]),
         'l': [1,[2,3,[4,5]]],
         'cc': Counter({'a':1, 'b':12, 'c':99})
        },
    ]
    
    
    for item in testitems:
        try:
            h = hash(item)
        except:
            h = None
        show(item, chash(item), h)
    
# _demo_chash()
    