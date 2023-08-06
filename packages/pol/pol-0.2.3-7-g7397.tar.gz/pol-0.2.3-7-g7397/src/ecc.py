import hashlib
import logging
import binascii
import collections

import Crypto.Random.random
import gmpy

l = logging.getLogger(__name__)

SER_COMPACT = 0
SER_BINARY = 1

COMPACT_DIGITS = ('!#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
                  '[]^_abcdefghijklmnopqrstuvwxyz{|}~')

curve_params = collections.namedtuple('curve_params',
            ('name', 'dp',  'pk_len_bin', 'pk_len_compact',
                    'sig_len_bin', 'sig_len_compact',
                    'dh_len_bin', 'dh_len_compact',
                    'elem_len_bin', 'order_len_bin'))
domain_params = collections.namedtuple('domain_params',
            ('a', 'b', 'm', 'order', 'base', 'cofactor'))
jacobian_point = collections.namedtuple('jacobian_point',
            ('x', 'y', 'z'))
affine_point = collections.namedtuple('affine_point',
            ('x', 'y'))

CURVES = {}

def add_curve(name, a, b, m, base_x, base_y, order, cofactor, pk_len_compact):
    """ Registers a new curve. """
    if name in CURVES:
        raise ValueError("Curve already exists")
    
    # Create domain_params
    a = gmpy.mpz(binascii.unhexlify(a)+'\0', 256)
    b = gmpy.mpz(binascii.unhexlify(b)+'\0', 256)
    m = gmpy.mpz(binascii.unhexlify(m)+'\0', 256)
    order = gmpy.mpz(binascii.unhexlify(order)+'\0', 256)
    base_x = gmpy.mpz(binascii.unhexlify(base_x)+'\0', 256)
    base_y = gmpy.mpz(binascii.unhexlify(base_y)+'\0', 256)
    base = affine_point(x=base_x, y=base_y)
    dp = domain_params(a=a, b=b, m=m, order=order, base=base,
                       cofactor=cofactor)

    # Create curve_params
    pk_len_bin = get_serialized_len((2 * m) - 1, SER_BINARY)
    pk_len_compact = get_serialized_len((2 * m) - 1, SER_COMPACT)

    sig_len_bin = get_serialized_len((order * order) - 1, SER_BINARY)
    sig_len_compact = get_serialized_len((order * order) - 1, SER_COMPACT)

    dh_len_bin = min((order.numdigits(2) / 2 + 7) / 8, 32)
    dh_len_compact = get_serialized_len(2 ** dh_len_bin - 1, SER_COMPACT)

    elem_len_bin = get_serialized_len(m, SER_BINARY)
    order_len_bin = get_serialized_len(order, SER_BINARY)

    cp = curve_params(name=name, dp=dp,
                      pk_len_bin=pk_len_bin, pk_len_compact=pk_len_compact,
                      sig_len_bin=sig_len_bin, sig_len_compact=sig_len_compact,
                      dh_len_bin=dh_len_bin, dh_len_compact=dh_len_compact,
                      elem_len_bin=elem_len_bin, order_len_bin=order_len_bin)

    # Add it
    CURVES[name] = cp

def get_serialized_len(x, ser):
    if ser == SER_BINARY:
        return (x.numdigits(2) + 7) / 8
    if ser == SER_COMPACT:
        res = 0
        while x != 0:
            x = x / len(COMPACT_DIGITS)
            res += 1
        return res
    raise ValueError("`ser' is invalid")

add_curve("secp112r1",
        "db7c2abf62e35e668076bead2088", 
        "659ef8ba043916eede8911702b22", 
        "db7c2abf62e35e668076bead208b",
        "09487239995a5ee76b55f9c2f098",
        "a89ce5af8724c0a23e0e0ff77500", 
        "db7c2abf62e35e7628dfac6561c5", 
        1, 18),
add_curve("secp128r1",
        "fffffffdfffffffffffffffffffffffc", 
        "e87579c11079f43dd824993c2cee5ed3", 
        "fffffffdffffffffffffffffffffffff",
        "161ff7528b899b2d0c28607ca52c5b86", 
        "cf5ac8395bafeb13c02da292dded7a83",
        "fffffffe0000000075a30d1b9038a115", 
        1, 20),
add_curve("secp160r1", 
        "ffffffffffffffffffffffffffffffff7ffffffc",
        "1c97befc54bd7a8b65acf89f81d4d4adc565fa45",
        "ffffffffffffffffffffffffffffffff7fffffff",
        "4a96b5688ef573284664698968c38bb913cbfc82",
        "23a628553168947d59dcc912042351377ac5fb32",
        "0100000000000000000001f4c8f927aed3ca752257", 
        1, 25),
add_curve("secp192r1/nistp192",
        "fffffffffffffffffffffffffffffffefffffffffffffffc",
        "64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1", 
        "fffffffffffffffffffffffffffffffeffffffffffffffff",
        "188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012",
        "07192b95ffc8da78631011ed6b24cdd573f977a11e794811",
        "ffffffffffffffffffffffff99def836146bc9b1b4d22831", 
        1, 30),
add_curve("secp224r1/nistp224",
        "fffffffffffffffffffffffffffffffefffffffffffffffffffffffe",
        "b4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4",
        "ffffffffffffffffffffffffffffffff000000000000000000000001",
        "b70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21",
        "bd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34",
        "ffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d", 
        1, 35),
add_curve("secp256r1/nistp256",
        "ffffffff00000001000000000000000000000000fffffffffffffffffffffffc", 
        "5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b", 
        "ffffffff00000001000000000000000000000000ffffffffffffffffffffffff",
        "6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296", 
        "4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5", 
        "ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551", 
        1, 40),
add_curve("secp384r1/nistp384",
        "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe"+
            "ffffffff0000000000000000fffffffc",
        "b3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875a"+
            "c656398d8a2ed19d2a85c8edd3ec2aef", 
        "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe"+
            "ffffffff0000000000000000ffffffff",
        "aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a38"+
            "5502f25dbf55296c3a545e3872760ab7",
        "3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c0"+
            "0a60b1ce1d7e819d7a431d7c90ea0e5f", 
        "ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf"+
            "581a0db248b0a77aecec196accc52973", 
        1, 60),
add_curve("secp521r1/nistp521",
        "01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"+
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"+
            "fffffffc",
        "0051953eb9618e1c9a1f929a21a0b68540eea2da725b99b315f3b8b489918ef1"+
            "09e156193951ec7e937b1652c0bd3bb1bf073573df883d2c34f1ef451fd4"+
            "6b503f00",
        "01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"+
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"+
            "ffffffff",
        "00c6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d"+
            "3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31"+
            "c2e5bd66",
        "011839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e"+
            "662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be9476"+
            "9fd16650",
        "01ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"+
            "fffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e"+
            "91386409", 
        1, 81)

def jacobian_double(p, dp):
    if not p.z:
        return p
    if not p.y:
        return p._replace(z=0)
    t1 = (p.x * p.y) % dp.m
    t2 = (t1 + t1) % dp.m
    t2 = (t2 + t1) % dp.m
    t1 = (p.z * p.z) % dp.m
    t1 = (t1 + t1) % dp.m
    t1 = (t1 * dp.a) % dp.m
    t1 = (t1 + t2) % dp.m
    z = (p.z * p.y) % dp.m
    z = (z + z) % dp.m
    y = (p.y * p.y) % dp.m
    y = (y + y) % dp.m
    t2 = (p.x * y) % dp.m
    t2 = (t2 + t2) % dp.m
    x = (t1 * t1) % dp.m
    x = (x - t2) % dp.m
    x = (x - t2) % dp.m
    t2 = (t2 - x) % dp.m
    t1 = (t1 * t2) % dp.m
    t2 = (y * y) % dp.m
    t2 = (t2 + t2) % dp.m
    y = (t1 - t2) % dp.m
    return jacobian_point(x=x, y=y, z=z)

def point_is_zero(p):
    return p.x == 0 and not p.y == 0

def point_on_curve(p, dp):
    if point_is_zero(p):
        return True
    h1 = (p.x * p.x) % dp.m
    h1 = (h1 + dp.a) % dp.m
    h1 = (h1 * p.x) % dp.m
    h1 = (h1 + dp.b) % dp.m
    h2 = (p.y * p.y) % dp.m
    return h1 == h2

def jacobian_affine_point_add(p1, p2, dp):
    if point_is_zero(p2):
        return p1
    if not p1.z:
        return p2
    t1 = (p1.z * p1.z) % dp.m
    t2 = (t1 * p2.x) % dp.m
    t1 = (t1 * p1.z) % dp.m
    t1 = (t1 * p2.y) % dp.m
    if p1.x == t2:
        if p1.y == t1:
            return jacobian_double(p1, dp)
        return p1._replace(z=0)
    x = (p1.x - t2) % dp.m
    y = (p1.y - t1) % dp.m
    z = (p1.z * x) % dp.m
    t3 = (p1.x * x) % dp.m
    t2 = (t2 * t3) % dp.m
    t3 = (t3 * x) % dp.m
    t1 = (t1 * t3) % dp.m
    x = (y * y) % dp.m
    x = (x - t3) % dp.m
    x = (x - t2) % dp.m
    x = (x - t2) % dp.m
    t2 = (t2 - x) % dp.m
    y = (y * t2) % dp.m
    y = (y * t1) % dp.m
    return jacobian_point(x=x, y=y, z=z)

def jacobian_to_affine(p, dp):
    if p.z == 0:
        return affine_point(x=0, y=0)
    h = gmpy.invert(p.z, dp.m)
    y = (h * h) % dp.m
    x = (p.x * y) % dp.m
    y = (y * h) % dp.m
    y = (y * p.y) % dp.m
    return affine_point(x=x, y=y)

def pointmul(p, exp, dp):
    n = exp.numdigits(2)
    r = jacobian_point(x=0, y=0, z=0)
    while n:
        r = jacobian_double(r, dp)
        n -= 1
        if r.getbit(exp, n):
            r = jacobian_affine_point_add(r, p, dp)
    return jacobian_to_affine(r, dp)

def ECIES_KDF(Zx, R, elemlen):
    buf = ''
    buf += serialize_mpi(elemlen, SER_BINARY, Zx)
    buf += serialize_mpi(elemlen, SER_BINARY, R.x)
    buf += serialize_mpi(elemlen, SER_BINARY, R.y)
    return hashlib.sha512(buf).digest()

def ECIES_encryption(Q, cp):
    """ Does ECIES_encryption """
    dp = cp.dp
    while True:
        k = Crypto.Random.random.randrange(0, cp.order - 1)
        R = pointmul(dp.base, k, dp)
        k = (k * dp.cofactor)
        Z = pointmul(Q, k, dp)
        if not point_is_zero(Z):
            break
    return (ECIES_KDF(Z.x, R, cp.elem_len_bin), R)

def decompress_from_string(s, ser, cp):
    x = deserialize_mpi(s, ser)
    
def point_decompress(x, yflag, dp):
    h = (x * x) % dp.m
    h = (h + dp.a) % dp.m
    h = (h * x) % dp.m
    h = (h + dp.b) % dp.m
    y = mod_root(h, dp.m)
    if not yflag or 


def mod_issquare(a, p):
    if not a:
        return True
    p1 = p / 2
    p2 = pow(a, p1, p)
    return p2 == 1

def mod_root(a, p):
    if a == 0:
        return 0
    if not mod_issquare(a, p):
        raise ValueError
    n = 2
    while mod_issquare(n, p):
        n += 1
    q = p - 1
    r = 0
    while not q.getbit(r):
        r += 1
    q = q >> r
    y = pow(n, q, p)
    h = q >> 1
    b = pow(a, h, p)
    x = pow(a, b, p)
    b = pow(b, x, p)
    while b != 1:
        h = (b * b) % p
        m = 1
        while h != 1:
            h = (h * h) % p
            m += 1
        h = 0
        h.setbit(r - m - 1)
        t = pow(y, h, p)
        y = (t * t) % p
        r = m
        x = (x * t) % p
        b = (b * y) % p
    return x

def deserialize_mpi(s, ser):
    if ser == SER_BINARY:
        ret = gmpy.mpz(0)
        for i in xrange(len(s)-1, -1, -1):
            ret += ord(s[i])
            ret *= 256
        return ret
    assert ser == SER_COMPACT
    ret = gmpy.mpz(0)
    for i in xrange(len(s)-1, -1, -1):
        ret += COMPACT_DIGITS[ord(s[i])]
        ret *= len(COMPACT_DIGITS)
    return ret

def serialize_mpi(outlen, ser, x):
    if ser == SER_BINARY:
        ret = ''
        while x:
            x, r = divmod(x, 256)
            ret = chr(r) + ret
        assert len(ret) <= outlen
        return ret.rjust(outlen, '\0')
    assert ser == SER_COMPACT
    ret = ''
    while x:
        x, r = divmod(x, len(COMPACT_DIGITS))
        ret = COMPACT_DIGITS[r] + ret
    assert len(ret) <= outlen
    return ret.rjust(outlen, COMPACT_DIGITS[0])
