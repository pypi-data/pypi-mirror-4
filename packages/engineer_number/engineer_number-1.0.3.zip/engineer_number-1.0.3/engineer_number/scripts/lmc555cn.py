import os
import sys
import math
import argparse

from engineer_number import *
from engineer_number.constants import *

# >>> math.log(2)
# 0.6931471805599453
# >>> math.log(2, math.e)
# 0.6931471805599453
# >>> math.log(8, 2) # swaped math logarithm
# 3.0 # 2 ** 3 = 8, pow(2, 3)
CONST = math.log(2, math.e)

def lmc555(Ra, Rb, C=EngineerNumber(0.1*MICRO)):
    _c2gnd = 0.1 * MICRO
    tH = CONST * (Ra + Rb) * C
    tL = CONST * Rb * C
    t = tL + tH
    f = 1 / t

    return (tL, tH, t, f)

def _make_all_combination(series='E12'):
    if series != 'E12':
        raise ValueError('series must be "E12".')
    #                         k                    M
    factor_big = (1, 10, 100, 1000, 10000, 100000, 1000000)
    combination = []
    for factor in factor_big:
        for n in E12:
            r = factor * n
            combination.append(r)
    return combination

def check_Hz_in_range(r_min, r_max, c):
    tf = []
    ra = EngineerNumber(r_min)
    rb = EngineerNumber(r_max)

    tL, tH, t, f = lmc555(ra, rb, c)
    tup = (tL, tH, t, f, ra, rb, c)
    tf.append(tup)

    ra, rb = rb, ra
    tL, tH, t, f = lmc555(ra, rb, c)
    tup = (tL, tH, t, f, ra, rb, c)
    tf.append(tup)

    return tf

def look_for_optimized_Hz(Hz, c=EngineerNumber(0.1, MICRO)):
    Rs = _make_all_combination('E12')
    Rs.append(10 * MEGA)
    len_combination = len(Rs) ** 2
    print('len_combination =', len_combination)

    tf = []
    for r2 in Rs:
        for r1 in Rs:
            rb = EngineerNumber(r2, ONE)
            ra = EngineerNumber(r1, ONE)
            tL, tH, t, f = lmc555(ra, rb, c)
            tup = (tL, tH, t, f, ra, rb, c) # sort() x index refer here.
            tf.append(tup)

    # Hz を優先して sort。
    tf.sort(key=lambda x: math.fabs(Hz - x[3]))
    return tf

def parse_args():
    parser = argparse.ArgumentParser(description='look for optimized Hz.')

    parser.add_argument('--Hz', metavar='N', dest='Hz',
                       type=int, nargs='?', default=1000,
                       help='frequency default: 1000')
    parser.add_argument('--capacita', metavar='N', dest='c_str',
                       nargs='?', default='0.1u',
                       help='capacita default: 0.1u')
    parser.add_argument('--top', metavar='N', dest='top',
                       type=int, nargs='?', default=10,
                       help='ranking default: 10')
    args = parser.parse_args()
    return args

def view_tf(tf, top=-1):
    for tL, tH, t, f, ra, rb, c in tf[:top]:
        print('tL={}, tH={}, t={}, f={}, ra={}, rb={}, c={}'.format(tL, tH, t, f, ra, rb, c))

if __name__ == '__main__':
    args = parse_args()

    c = EngineerNumber(args.c_str)
    Hz = args.Hz
    tf = look_for_optimized_Hz(Hz, c)

    print('len(tf)=', len(tf))
    print()
    top = args.top
    view_tf(tf, top)
    print()
