
from mementos import memento_factory, with_metaclass
                                        # to memoize IntensionalSet
import re                               # for Re
import fnmatch                          # for Glob
# import six
import sys, copy
import collections
from intensional.superhash import superhash

if sys.version_info[0] > 2:
    unicode = str
    basestring = str

SuperHashMeta = memento_factory('SuperHashMeta',
                            lambda cls, args, kwargs: (cls, superhash(args)) )

class IntensionalSet(object):
    """
    An intensional set (actually, an intensionally defined set) is a set
    defined by a rule rather than an explicit listing of members
    (which would be an extensional set).
    
    Like other Python sets, IntensionalSet objects can include explicit
    items--but it also admits the possibility of rule-based membership.
    """
    
    def union(self, other):
        return Any(self, other)
    
    def intersection(self, other):
        return Every(self, other)
    
    def difference(self, other):
        return ButNot(self, other)
    
    def symmetric_difference(self, other):
        return EitherOr(self, other)
    
    def __or__(self, other):
        # |, equivalent to union
        return Any(self, other)
    
    def __and__(self, other):
        # &, equivalent to intersection
        return Every(self, other)
    
    def __sub__(self, other):
        # -, equivalent to difference
        return ButNot(self, other)
    
    def __xor__(self, other):
        # ^, equivalent to symmetric_difference
        return EitherOr(self, other)
    
    def __contains__(self, item):
        raise TypeError('Should have been implemented by subclass')
    
    def __len__(self):
        raise TypeError('Impossible to compute the cardinality of an intensional set.')
    
    def issubset(self, other):
        raise TypeError('Impossible to test subset relation between intensional sets.')
    
    def __le__(self, other):
        # <=, equivalent to issubset
        raise TypeError('Impossible to test subset relation between intensional sets.')

    def issuperset(self, other):
        raise TypeError('Impossible to test superset relation between intensional sets.')
    
    def __le__(self, other):
        # >=, equivalent to issuperset
        raise TypeError('Impossible to test superset relation between intensional sets.')
    
    def copy(self):
        return copy.copy(self)

    def pop(self):
        raise TypeError('Impractical to pop() an item from an intensional set.')
        # and impossible in the general case
    
    ### remaining to be implemented
    
    # Many of these are self-modifying methods, which are harder to implement in the
    # scheme we currenly have. If we had a top-level Set object with inclusions and
    # exclusions components, could probably jigger these up. 
    
    def update(self, others):
        raise NotImplementedError()
    
    union_update = update # backwards compatibility
    
    def __ior__(self, other):
        # |=, similar to update but takes only one item, not an iterable
        raise NotImplementedError()
        
    def intersection_update(self, others):
        raise NotImplementedError()

    def __iand__(self, other):
        # &=, similar to intersection_update but takes only one item, not an iterable
        raise NotImplementedError()
    
    def difference_update(self, others):
        raise NotImplementedError()

    def __isub__(self, other):
        # -=, similar to difference_update but takes only one item, not an iterable
        raise NotImplementedError()
    
    def symmetric_difference_update(self, others):
        raise NotImplementedError()

    def __ixor__(self, other):
        # ^=, similar to symmetric_difference_update but takes only one item, not an iterable
        raise NotImplementedError()
    
    def add(self, x):
        raise NotImplementedError()
    
    def remove(self, x):
        raise NotImplementedError()
    
    def discard(self, x):
        raise NotImplementedError()
    
    def clear(self):
        raise NotImplementedError()
    
# Any = Union, Every = Intersection, ButNot = Difference, EitherOr = Xor / Symmetric Difference
# might want to complete more of the set functions like symmetric difference, discard, etc
   
class ReMatch(object):
    """
    An easier-to-use proxy for regular expression match objects. Ideally this would be
    a subclass of the re module's match object, but their type ``_sre.SRE_Match``
    `appears to be unsubclassable
    <http://stackoverflow.com/questions/4835352/subclassing-matchobject-in-python>`_.
    Thus, ReMatch is a proxy exposes the match object's numeric (positional) and
    named groups through indices and attributes. If a named group has the same
    name as a match object method or property, it takes precedence. Either
    change the name of the match group or access the underlying property thus:
    ``x._match.property``
    """
     
    def __init__(self, match):
        self._match = match
        self._groupdict = match.groupdict()
        
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self._groupdict:
            return self._groupdict[name]
        try:
            return getattr(self._match, name)
        except AttributeError:
            return AttributeError("no such attribute '{}'".format(name))
        
    def __getitem__(self, index):
        return self._match.group(index)

class Re(with_metaclass(SuperHashMeta, IntensionalSet)):
    
    # convenience copy of re flag constants
    
    DEBUG      = re.DEBUG
    I          = re.I
    IGNORECASE = re.IGNORECASE
    L          = re.L
    LOCALE     = re.LOCALE
    M          = re.M
    MULTILINE  = re.MULTILINE
    S          = re.S
    DOTALL     = re.DOTALL
    U          = re.U
    UNICODE    = re.UNICODE
    X          = re.X
    VERBOSE    = re.VERBOSE
    
    _ = None
    
    def __init__(self, pattern, flags=0):
        self.pattern = pattern
        self.flags   = flags
        self.re = re.compile(pattern, flags)
        self.groups     = self.re.groups
        self.groupindex = self.re.groupindex
        
    def _regroup(self, m):
        """
        Given an _sre.SRE_Match object, create and return a corresponding
        ReMatch object. Also, set the en passant variable to it.
        """

        result = ReMatch(m) if m else m
        Re._ = result
        return result

    def __contains__(self, item):
        if not isinstance(item, (str, unicode)):
             item = str(item)
        return self._regroup(self.re.search(item))
    
    ### methods that return ReMatch objects
    
    def search(self, *args, **kwargs):
        return self._regroup(self.re.search(*args, **kwargs))

    def match(self, *args, **kwargs):
        return self._regroup(self.re.match(*args, **kwargs))
    
    def finditer(self, *args, **kwargs):
        return self.re.finditer(*args, **kwargs)
 
    ### methods that don't need ReMatch objects
      
    def findall(self, *args, **kwargs):
        return self.re.findall(*args, **kwargs)
    
    def split(self, *args, **kwargs):
        return self.re.split(*args, **kwargs)
    
    def sub(self, *args, **kwargs):
        return self.re.sub(*args, **kwargs)
    
    def subn(self, *args, **kwargs):
        return self.re.subn(*args, **kwargs)
    
    def escape(self, *args, **kwargs):
        return self.re.escape(*args, **kwargs)

class Glob(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    An item matches a Glob via Unix filesystem glob semantics.
    
    E.g. 'alpha' matches 'a*' and 'a????' but not 'b*'
    """
        
    def __init__(self, pattern):
        self.pattern = pattern
        
    def __contains__(self, item):
        return fnmatch.fnmatch(str(item), self.pattern)

class Instances(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    An object is in an IsInstance if it is an instance of the given types.
    """
    def __init__(self, *args):
        self.types = tuple(args)
        
    def __contains__(self, item):
        return isinstance(item, self.types)
    
Type = Instances
IsInstance = Instances
    
def boxed(item):
    """
    Return item in a container if it is a scalar, else the item itself.
    Aka box it up, unless it's already boxed.
    """
    return item if isinstance(item, (list, set)) else [ item ]

class Set(IntensionalSet):
    """
    Set that has both inclusions and exclusions. An item is in a Aset if it is, or
    is in, any of the inclusions--as long as it is not equal to or included in
    any of the exclusions. A convenient hybrid of the Any and ButNot set types.
    Some set operations like union can be performed without requiring returning
    a different subclass of IntensionalSet. Provides more opporunity also for
    in-place mutations.
    
    NB NOT YET OPERATIONAL OR TESTED
    """
    def __init__(self, include, exclude=[]):
        self.include = boxed(include)
        self.exclude = boxed(exclude)
    
    def _included(self, item):
        for i in self.include:
            if item == i:
                return True
            elif hasattr(i, '__contains__'):
                if item in i:
                    return True
        return False
    
    def _excluded(self, item):
        for i in self.exclude:
            if item == i:
                return True
            elif hasattr(i, '__contains__'):
                if item in i:
                    return True
        return False
        
    def __contains__(self, item):    
        return self._included(item) and not self._excluded(item)
    
    def union(self, other):
        clone = self.copy()
        if other not in clone.include:
            clone.include.append(other)
        return clone
        
    def difference(self, other):
        clone = self.copy()
        if other not in clone.exclude:
            clone.exclude.append(other)
        return clone
    
def equals_or_in(item, collection):
    """
    Return true if the item is the collection, or is in the collection.
    Guard against possible TypeError exceptions (ie, testing if `int` is
    in `str` can raise this).
    """
    if item == collection:
        return True
    if hasattr(collection, '__contains__'):
        try:
            if item in collection:
                return True
        except TypeError:
            pass
    return False

    
class Any(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    An item is in an Any if it is or is in any member of the set.
    """
    def __init__(self, *args):
        self.items = set(args)
        
    def __contains__(self, item):
        if item in self.items:
            return True
        for i in self.items:
            if equals_or_in(item, i):
                return True
        return False
    
class Every(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    An item is in an Every if it is or is in every member of the set.
    """
    def __init__(self, *args):
        self.items = set(args)

    def __contains__(self, item):
        for i in self.items:
            if not equals_or_in(item, i):
                return False
        return True

class ButNot(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    An item is in a ButNot if it's in the primary set and not the exclusion.
    """
    def __init__(self, items, exclusion):
        self.items = items
        self.exclusion = exclusion

    def __contains__(self, item):        # why the == self.items?
        if item == self.items or item in self.items:
            if item != self.exclusion and item not in self.exclusion:
                return True
        return False
    
    # probably need to guard against type errors here
    
class EitherOr(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    An item is in an EitherOr if it's in subseta or subset b, but not both.
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __contains__(self, item):
        if item in self.a:
            return not item in self.b
        elif item in self.b:
            return not item in self.a
        else:
            return False
        
class Test(with_metaclass(SuperHashMeta, IntensionalSet)):
    """
    Test is a generic wrapper around lambda expressions.
    Provides special support for compact, neat expressions by not
    auto-adding a 'lambda x:' prefix if test provided as a string.
    """
    def __init__(self, expr, *args, **kwargs):
        IntensionalSet.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.expr = expr
        if isinstance(expr, basestring): 
            if not expr.startswith('lambda'):
                expr = 'lambda x: ' + expr
            self.func = eval(expr)
        elif hasattr(expr, '__call__'):
            self.func = expr
        else:
            raise ValueError('expr needs to be string or callable')
        
    def __contains__(self, item):
        try:
            return self.func(item, *self.args, **self.kwargs)
        except Exception:
            return False
        
    # NB failure to run test => fails test
    # might silently hide syntax errors and such
    # do we want a mode or mechanism to make such errors into Warnings?