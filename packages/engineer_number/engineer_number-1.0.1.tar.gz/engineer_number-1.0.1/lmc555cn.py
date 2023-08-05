import os
import sys
import math
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), 'engineer_number'))
from engineer_number import *
from engineer_number.constants import *

# >>> math.log(2)
# 0.6931471805599453
# >>> math.log(2, math.e)
# 0.6931471805599453
# >>> math.log(8, 2) # swaped math logarithm
# 3.0 # 2 ** 3 = 8, pow(2, 3)
CONST = math.log(2, math.e)

# c = 0.1 * MICRO

# tH = 0.693 * (ra + rb) * c
# tL = 0.693 * rb * c
# t = tH + tL
#   = 0.693 * (ra + 2 * rb) * c
# t = 0.693 * 3 * r * c if r = ra = rb

# t = 0.001 # 1 kHz
# = 0.693 * (ra + 2 * rb) * c
# = 0.693 * (ra + 2 * rb) * c = 0.001
# c = 0.001 / (0.693 * (ra + 2 * rb))

# if r = ra = rb = 1 kR
# c = 0.001 / (0.693 * (1k + 2 * 1k))
#   = 0.001 / (0.693 * 3k )
# >>> 0.001 / (0.693 * 3000 )
# 4.81000481000481e-07
# 0.481000481000481e-06
# 0.481 * 10 ** -6
# 0.481 * MICRO

def lmc555(Ra, Rb, C=EngineerNumber(0.1*MICRO)):
    _c2gnd = 0.1 * MICRO
    tH = CONST * (Ra + Rb) * C
    tL = CONST * Rb * C
    t = tL + tH
    f = 1 / t

    return (tL, tH, t, f)

'''
手持ちの抵抗は最大で 10M R
手持ちの抵抗は最小で 1 R
t = 0.693 * (ra + 2 * rb) * c
ここで、抵抗部分を rx として、
t = 0.693 * rx * c
制限があるのは、cの値なので、まずcの値を適当に決める。
"・０．１μＦ５０Ｖ
積層セラミックコンデンサ
（ムラタ製または各社相当品）"

積セラ 50V 0.1uF 2.54ピッチ[R指]
積セラ 50V 0.1uF 5.08ピッチ[R指]
積セラ 50V 1uF[R指]

LMC555 CMOS タイマ
■ 5V 電源で1mW 以下の消費電力
■ 3MHzまでの無安定周波数
■ 1.5V 動作電源電圧の保証
■ 出力は5V 電源で、TTL、CMOS ロジックと完全互換
'''

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
    condition = False
    for r2 in Rs:
        for r1 in Rs:
            rb = EngineerNumber(r2, ONE)
            ra = EngineerNumber(r1, ONE)
            tL, tH, t, f = lmc555(ra, rb, c)
            condition = 1 or t == f and t == 1
            tup = (tL, tH, t, f, ra, rb, c) # sort() x index refer here.
            tf.append(tup)
          # if condition:
          #     print('--')
          #     print('ra = {:.3e}'.format(ra))
          #     print('rb = {:.3e}'.format(rb))
          #     print('c = {:.3e}'.format(c))
          #     print()

          #     print('tL = {:.3e}'.format(tL))
          #     print('tH = {:.3e}'.format(tH))
          #     print('t = {:.3e}'.format(t))
          #     print('f = {:.3e}'.format(f))

    # Hz を優先して sort。
    tf.sort(key=lambda x: math.fabs(Hz - x[3]))
    return tf

def parse_args():
    parser = argparse.ArgumentParser(description='look for optimized Hz.')

    parser.add_argument('--Hz', metavar='N', dest='Hz',
                       type=int, nargs='?', default=1000,
                       help='frequency')
    parser.add_argument('--capacita', metavar='N', dest='c_str',
                       nargs='?', default='0.100m',
                       help='capacita')
    parser.add_argument('--top', metavar='N', dest='top',
                       type=int, nargs='?', default=10,
                       help='ranking')
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
