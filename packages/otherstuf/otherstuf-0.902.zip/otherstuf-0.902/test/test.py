
from otherstuf import *
import sys
from stuf import stuf

def test_chainstuf():
    """Test chainstuf class"""
    
    # make some base dicts
    d1 = dict(this=1, that=2)
    d2 = dict(roger=99, that=100)
    
    # test simple attribute equivalence
    dd = chainstuf(d1, d2)
    assert dd.this == 1
    assert dd.roger == 99
    assert dd.this == dd['this']
    assert dd.that == dd['that']
    assert dd.roger == dd['roger']
    
    # set value on chainstuf, ensure properly set, in top dict
    dd.roger = 'wilco'
    assert dd.roger == 'wilco'
    assert dd.roger == d1['roger']
    
    # test new_child
    dd2 = dd.new_child()
    dd2.smorg = 44
    assert dd2.smorg == 44
    dd.roger = 'roger'
    assert dd2.roger == 'roger'
    
def test_files():
    # stuf (<0.9.9) had a problem with files being assigned in a stuf()
    # constructor. It was fixed in 0.9.10, though not for PyPy. This test
    # demonstrates that otherstuf.chainstuf does not manifest this bug. To be
    # fair, the bug was in stuf's base collections (stuf and orderedstuf), not
    # stuf.chainstuf. So this test is included out of an abundance of caution.
    
    # Get names of files that won't be munged by py.test's capturing mechanism
    # (sys.stdout and sys.stderr definitely will be overtaken by py.test, but
    # their primitive double-underscore names won't be). This doesn't seem to
    # be an issue with Python 2.x, but spuriously screws up the test otherwise
    # in Python 3.x (gives false negative, saying module not working when it is)
    
    f1 = sys.__stdout__
    f2 = sys.__stderr__
    f3 = sys.__stdin__
    
    d1 = dict(a=44, b=f2, c=[f2, f3])
    d2 = dict(a=f1)
    o = chainstuf(d2, d1)

    assert o.a is f1
    assert o.b is f2
    assert len(o.c) == 2
    assert o.c[0] is f2
    assert o.c[1] is f3
    
    # first push
    oo = o.new_child()
    oo.b = f1
    oo.c = 12
    assert oo.a is f1
    assert oo.b is f1
    assert oo.c == 12
    
    # now try it with an update
    d3 = dict(b=f1, c=12)
    oo2 = oo.new_child()
    oo2.update(d3)
    assert oo2.a is f1
    assert oo2.b is f1
    assert oo2.c == 12
    
    # second push
    ooo = oo.new_child()
    ooo.update(dict(a=f2, b=f3))
    assert ooo.a is f2
    assert ooo.b is f3
    assert ooo.c == 12
    
    
def test_counterstuf():
    """Test counterstuf class"""
    c = counterstuf()
    c.update("this and this is this but that isn't this".split())
    c.total = sum(c.values())
    assert c.total == 9
    assert c.this == 4
    assert c.but == 1
    assert c.bozo == 0
    c2 = counterstuf().update_self("big big small big medium xlarge".split())
    assert c2.medium == 1
    assert dict(c2.most_common()) == dict([('big', 3), ('small', 1), ('medium', 1), ('xlarge', 1)])
