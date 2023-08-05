
from testharness import import_from_parent, test_run

import_from_parent()

from otherstuf import *

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
    assert c2.most_common() == [('big', 3), ('small', 1), ('medium', 1), ('xlarge', 1)]
    
if __name__ == '__main__':
    test_run()
