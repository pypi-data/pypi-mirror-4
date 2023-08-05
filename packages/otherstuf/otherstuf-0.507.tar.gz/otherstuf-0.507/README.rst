Attribute-accesible collections inspired by `stuf
<http://pypi.python.org/pypi/stuf>`_. Implements ``chainstuf`` and
``counterstuf``: versions of ``ChainMap`` and ``Counter`` that expose their keys as
attributes.

The ultimate goal of this module is to have these functions available in the
``stuf`` module, and this sidecar to be retired.

Usage
=====

Use these just like you would ``ChainMap`` and ``Counter``, except that
you get attribute-style access as well.

For ``chainstuf``::

    from chainstuf import chainstuf
    
    d1 = dict(this=1, that=2)
    d2 = dict(roger=99, that=100)
    
    # test simple attribute equivalence
    c = chainstuf(d1, d2)
    
    assert c.this == 1
    assert c.roger == 99
    
    c.roger = 'wilco'
    assert c.roger
    print "roger", c.roger
    
    d1.update(feeling='fancypants!')
    print "i'm feeling", c.feeling     # passed through, since d2 lacks 'feeling'

For ``counterstuf``::

    from counterstuf import counterstuf
    
    c = counterstuf()
    c.update("this and this is this but that isn't this".split())
    c.total = sum(c.values())
    
    print "everything:", c.total
    print "'this' mentioned", c.this, "times"
    print "'bozo' mentioned", c.bozo, "times"
    print c
    
Installation
============

::

    pip install otherstuf
    
(You may need to prefix this with "sudo " to authorize installation.)