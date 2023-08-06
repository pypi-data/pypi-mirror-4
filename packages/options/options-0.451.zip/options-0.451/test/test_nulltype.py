
from options.nulltype import *

### Setup

Prohibited = NullType("Prohibited")
Transient  = NullType("Transient")
Nothing    = NullType("Nothing")

nulls = [Prohibited, Transient, Nothing] 

### Tests

def test_bool():
    for n in nulls:
        assert not bool(n)

def test_if():
    for n in nulls:
        if n:
            assert False
