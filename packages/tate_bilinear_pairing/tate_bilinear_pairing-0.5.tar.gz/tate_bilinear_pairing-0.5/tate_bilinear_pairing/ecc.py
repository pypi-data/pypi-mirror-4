"""
This module is about point addition and point scalar multiplication on the elliptic curve $y^2=x^3-x+1$ over $GF(3^m)$.
Each element in the elliptic curve is expressed by a list of $[(bool)b, (list)x, (list)y]$.
If the value of $b$ is "True", it will mean the element is the point at infinity.
Otherwise, the value of $x$ and $y$ must obey $y^2=x^3-x+1$.
"""

from . import f3m
import random as _r

_order = None
_x = None
_y = None

def inf():
    'the point at infinity'
    return [True, f3m.zero(), f3m.zero()]

def _clone(p):
    '_clone an elliptic curve group element'
    return [p[0], f3m._clone(p[1]), f3m._clone(p[2])]

def gen():
    'generator in the elliptic curve group'
    return _clone([False, _x, _y])

def order():
    'the least number $k$ such that $k\cdot gen$ is inf in the elliptic curve group'
    return _order

def random():
    'a random point in the elliptic curve group'
    a = _r.randint(1, order())
    return scalar_mult(a, gen())

def add(p1, p2):
    'adding two elements in the elliptic curve group'
    inf1, x1, y1 = p1
    inf2, x2, y2 = p2
    if inf1:
        return _clone(p2)
    if inf2:
        return _clone(p1)
    if x1 == x2:
        ny2 = f3m.zero()
        f3m.neg(y2, ny2) # ny2 == -y2
        if y1 == ny2:
            return inf()
        if y1 == y2:
            v0 = f3m.inverse(y1) # v0 == y1^{-1}
            v1 = f3m.mult(v0, v0) # v1 == [y1^{-1}]^2
            f3m.add(v1, x1, v1) # v1 == [y1^{-1}]^2 + x1
            v2 = f3m.cubic(v0) # v2 == [y1^{-1}]^3
            f3m.add(v2, y1, v2) # v2 == [y1^{-1}]^3 + y1
            f3m.neg(v2, v2) # v2 == -([y1^{-1}]^3 + y1)
            return [False, v1, v2]
    # P1 != \pm P2
    v0 = f3m.zero()
    f3m.sub(x2, x1, v0) # v0 == x2-x1
    v1 = f3m.inverse(v0) # v1 == (x2-x1)^{-1}
    f3m.sub(y2, y1, v0) # v0 == y2-y1
    v2 = f3m.mult(v0, v1) # v2 == (y2-y1)/(x2-x1)
    v3 = f3m.mult(v2, v2) # v3 == [(y2-y1)/(x2-x1)]^2
    v4 = f3m.cubic(v2) # v4 == [(y2-y1)/(x2-x1)]^3
    f3m.add(x1, x2, v0) # v0 == x1+x2
    f3m.sub(v3, v0, v3) # v3 == [(y2-y1)/(x2-x1)]^2 - (x1+x2)
    f3m.add(y1, y2, v0) # v0 == y1+y2
    f3m.sub(v0, v4, v4) # v4 == (y1+y2) - [(y2-y1)/(x2-x1)]^3
    return [False, v3, v4]

def scalar_mult(n, p):
    '''computing the scalar multiplication $n*p$, where $p$ is a point on the elliptic curve,
    and $n$ is an integer scalar value.'''
    a = inf()
    x = _clone(p)
    while n > 0:
        if (n & 1):
            a = add(a, x)
        n = n // 2
        x = add(x, x)
    return a
