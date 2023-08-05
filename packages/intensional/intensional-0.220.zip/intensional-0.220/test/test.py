 
from intensional import *

def test_Re():
    tests = 'some string with things in it ok?'
    testpat = Re(r'\b(s\w*)\b')
    testpat1 = Re(r'\b(s\w*)\b')
    assert testpat is testpat1   # test memoization
    if tests in testpat:
        assert Re._[1] == 'some'
        assert Re._.end(1) == 4
        assert Re._._match.group(1) == Re._[1]
    else:
        raise ValueError('yes it is!!!')
    
    found = testpat.findall(tests)
    assert found == ['some', 'string']
    
    person = 'John Smith 48'
    if person in Re(r'(?P<name>[\w\s]*)\s+(?P<age>\d+)'):
        assert Re._.name == 'John Smith'
        assert int(Re._.age) == 48
        assert Re._.name == Re._._match.group('name')
        assert Re._.age  == Re._._match.group('age')
    else:
        raise ValueError('yes it is!!!')

def in_out(s, includes, excludes):
    """
    Testing shortcut. Assert s includes everything in includes and
    excludes everything in excludes. Encourages compact in/out testing
    and therefore better coverage.
    """
    for item in includes:
        assert item in s
    for item in excludes:
        assert item not in s
    
def test_Set():
    s = Set([1,2,44], exclude=44)
    in_out(s, [1, 2],
              [44, 3, 100, "string"])
    
    t = s.union([77, "other"])
    in_out(t, [1, 2, 77, "other"],
              [44, 3, 100, "string"])
    
    u = t.difference(Any(2, 99))
    in_out(t, [1, 77, "other"],
              [44, 2, 99, 3, 100, "string"])
    
def test_Any():
    ext = Any(1,2,3)
    assert 2 in ext
    assert 33 not in ext
    a2 = Any(12, Test('x.startswith("k")'))
    assert 12 in a2
    assert "kaboom" in a2
    assert "laboom" not in a2
    assert 33 not in a2
    
    any2 = Any(1,2,3, "this", "that")
    in_out(any2,
          [1,2,3, "this", "that"],
          [44, 45, 'lovely', 'bones'])
    
    assert Any(1,2,3,"this") is Any(1,2,3,"this")

    
def test_Every():
    e = Every(1)
    assert 1 in e
    assert 4 not in e
    e2 = Every(Test('x > 12'), Test('x > 33'))
    assert 44 in e2
    assert 55 in e2
    assert 0 not in e2
    assert 18 not in e2

    e3 = Every(Test('x.startswith("r")'), Test('len(x) <= 5'))
    
    assert 'roger' in e3
    assert 'roof'  in e3
    assert 'roofer' not in e3
    
    # diffent way of stating e3
    e3a = Every(Test('x.startswith("r") and len(x) <= 5'))

    assert 'roger' in e3a
    assert 'roof'  in e3a
    assert 'roofer' not in e3a

    # yet another way of stating e3
    e3b = Test('x.startswith("r") and len(x) <= 5')

    assert 'roger' in e3b
    assert 'roof'  in e3b
    assert 'roofer' not in e3b
    
    assert Every(1,2,3,"this") is Every(1,2,3,"this")
    
    # any way to link to Python all and any?

def test_ButNot():

    a2 = Any(12, Test('x.startswith("k")'))
    assert 12 in a2
    assert "kaboom" in a2
    assert "laboom" not in a2
    assert 33 not in a2
    
    bn = ButNot(a2, Any(12, 'kookoo'))
    assert 'kookoo' in a2
    assert 'kookoo' not in bn
    assert 'kaboom' in bn
    assert 'laboom' not in bn
    assert 12 in a2
    assert 12 not in bn
    
    assert ButNot(Any(12, Test('x.startswith("k")')), Any(12, 'kookoo')) is \
           ButNot(Any(12, Test('x.startswith("k")')), Any(12, 'kookoo'))
    
    
def test_union():
    a = Any(44, Test('x < 12'))
    b = Test('x > 100')
    u = a.union(b)
    assert 44 in u
    assert 45 not in u
    assert 101 in u
    assert 100 not in u
    assert -44 in u
    
    uu = a | b
    assert 44 in uu
    assert 45 not in uu
    assert 101 in uu
    assert 100 not in uu
    assert -44 in uu
    
def test_intersection():
    a = Any(44, Test('x < 12'))
    b = Test('x >= 6')
    i = a.intersection(b)
    assert 6 in i
    assert 11 in i
    assert 12 not in i
    assert 101 not in i
    assert 100 not in i
    assert -44 not in i
    
    ii = a & b
    assert 6 in ii
    assert 11 in ii
    assert 12 not in ii
    assert 101 not in ii
    assert 100 not in ii
    assert -44 not in ii
    
    
def test_difference():
    a = Test('x < 12')
    b = Test('x >= 6')
    d = a.difference(b)
    assert 6 not in d
    assert 5 in d
    assert -100 in d
    assert 11 not in d
    assert 100 not in d
    
    dd = a - b
    assert 6 not in dd
    assert 5 in dd
    assert -100 in dd
    assert 11 not in dd
    assert 100 not in dd
    
def test_symmetric_difference():
    a = Test('x <= 10')
    b = Test('x >= 5')
    s = a.symmetric_difference(b)
    assert 1 in s
    assert 2 in s
    assert 4 in s
    assert 20 in s
    assert 100 in s
    assert 5 not in s
    assert 10 not in s
    assert 11 in s
    
    ss = a ^ b
    assert 1 in ss
    assert 2 in ss
    assert 4 in ss
    assert 20 in ss
    assert 100 in ss
    assert 5 not in ss
    assert 10 not in ss
    assert 11 in ss
    
def test_Glob():
    assert "alpha" in Glob("a*")
    assert "beta" not in Glob("a*")
    
def test_Test():
    mytest = Test('x.startswith("a")')
    assert 'a' in mytest
    assert 'alpha' in mytest
    assert 'sljd' not in mytest
    
def test_IsInstance():
    assert 1 in IsInstance(int)
    assert 'yo' in IsInstance(str)
    assert 333 not in IsInstance(str)
    assert {} in IsInstance(dict)
    
def test_Instances():
    assert 1 in Instances(int)
    assert 'yo' in Instances(str)
    assert 333 not in Instances(str)
    assert {} in Instances(dict)
    
def test_Type():
    assert 1 in Type(int)
    assert 'yo' in Type(str)
    assert 333 not in Type(str)
    assert {} in Type(dict)
    
def test_examples():
        
    in_out(Any('Steve', 'Steven', 'Stephen'),
           ['Steve', 'Steven', 'Stephen'],
           ['Joe', 'Frank', 'Bill', 'Sally', 'Stan'])
    
    in_out(Test("x.startswith('S')"),
           ['Steve', 'Steven', 'Stephen', 'Sally', 'Stan'],
           ['Joe', 'Frank', 'Bill'])


    starts_with_S =  Test("x.startswith('S')")
    ends_with_n   =  Test("x.endswith('n')")
    
    in_out(Every(starts_with_S, ends_with_n),
           ['Steven', 'Stephen', 'Stan'],
           ['Joe', 'Frank', 'Bill', 'Steve', 'Sally'])
    
    in_out(Test("x.startswith('S') and x.endswith('n',)"),
           ['Steven', 'Stephen', 'Stan'],
           ['Joe', 'Frank', 'Bill', 'Steve', 'Sally'])

    S_something_n = starts_with_S & ends_with_n
    
    in_out(S_something_n,
           ['Steven', 'Stephen', 'Stan'],
           ['Joe', 'Frank', 'Bill', 'Steve', 'Sally'])

    integers = Instances(int)
    in_out(integers,
           [1,3,4,5,-33, 0, 137423],
           [0.4, 4+9j, "string", object, object(), KeyError, KeyError() ])
    
    in_out(Instances(int),
           [1,3,4,5,-33, 0, 137423],
           [0.4, 4+9j, "string", object, object(), KeyError, KeyError() ])
    
    assert integers is Instances(int)