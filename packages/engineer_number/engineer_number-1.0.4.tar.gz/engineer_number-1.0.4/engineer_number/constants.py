import collections

# 見れば分かると思われる為、特に説明はない。
# xxxEXPONENTxxx は非公開の方が良かったかも。。。
# もう、今となってはどうしようもないんですぅ〜〜〜。。。
__all__ = [
    'YOTTA', 'ZETTA', 'EXA', 'PETA', 'TERA', 'GIGA', 'MEGA', 'KILO',
    'ONE',
    'MILLI', 'MICRO', 'NANO', 'PICO', 'FEMTO', 'ATTO', 'ZEPTO', 'YOCTO',
    'd_EXPONENT_SYMBOL', 'd_SYMBOL_EXPONENT', 'EXPONENTS',
    'E6', 'E12', 'E24',
]

YOTTA = 24
ZETTA = 21
EXA = 18 # means 10 ** 18
PETA = 15
TERA = 12
GIGA = 9
MEGA = 6
KILO = 3
ONE = 0
MILLI = -3
MICRO = -6
NANO = -9
PICO = -12
FEMTO = -15
ATTO = -18
ZEPTO = -21
YOCTO = -24

EXPONENT_BIG = (YOTTA, ZETTA, EXA, PETA, TERA, GIGA, MEGA, KILO)
EXPONENT_SMALL = (MILLI, MICRO, NANO, PICO, FEMTO, ATTO, ZEPTO, YOCTO)
EXPONENTS = EXPONENT_BIG + (ONE,) + EXPONENT_SMALL

d_SYMBOL_EXPONENT = collections.OrderedDict((
    ('Y', YOTTA),
    ('Z', ZETTA),
    ('E', EXA),
    ('P', PETA),
    ('T', TERA),
    ('G', GIGA),
    ('M', MEGA),
    ('k', KILO),
     ('', ONE),
    ('m', MILLI),
    ('u', MICRO),
    ('n', NANO),
    ('p', PICO),
    ('f', FEMTO),
    ('a', ATTO),
    ('z', ZEPTO),
    ('y', YOCTO),
))

d_EXPONENT_SYMBOL = \
    dict(zip(d_SYMBOL_EXPONENT.values(), d_SYMBOL_EXPONENT.keys()))

# E6, E12, E24 系列。
E6 =  (1.0,                1.5,                2.2,
            3.3,                4.7,                6.8)
E12 = (1.0,      1.2,      1.5,      1.8,      2.2,      2.7,
            3.3,      3.9,      4.7,      5.6,      6.8,
       8.2)
E24 = (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7,
       3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5,
       8.2, 9.1)

# len(E12) = 13
# >>> 13 * 2
# 26
# >>> 13 * 4
# 52
# >>> 13 * 6
# 78

# combination
# for EXPONENT_SMALL
# >>> (13 * 2) ** 2
# 676

# for EXPONENT_BIG
# >>> (13 * 4) ** 2
# 2704

# for EXPONENTS
# >>> (13 * 6) ** 2
# 6084
