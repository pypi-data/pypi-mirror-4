
from enpassant import *

def test_one():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]
    
    for v in values:
        if passer / v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v


def test_alt_operations():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]
    
    for v in values:
        if passer < v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v
            
    for v in values:
        if passer <= v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v

def test_call_delivery():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]

    for v in values:
        if passer <= v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v