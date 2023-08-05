import os
import sys
import unittest
from test import support

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engineer_number import *
from engineer_number.constants import *

class TestEngineerNumber(unittest.TestCase):
    def test_simple_but_too_long(self):
        M3_3 = EngineerNumber(3.3, MEGA)
        # kilo must be 'k'. K means kelbin.
        k47 = EngineerNumber(47, KILO)
        mili47 = EngineerNumber(47, MILLI)
        mcr3_3 = EngineerNumber(3.3, MICRO)

        # __str__()
        self.assertEqual('3.300M', str(M3_3))
        self.assertEqual('47.000k', str(k47))
        self.assertEqual('47.000m', str(mili47))
        self.assertEqual('3.300u', str(mcr3_3))

        # mul
        self.assertEqual('155.100G', str(k47 * M3_3))
        self.assertEqual('155.100n', str(mili47 * mcr3_3))
        self.assertEqual('2.209k', str(k47 * mili47))
        self.assertEqual('10.890', str(M3_3 * mcr3_3))
        self.assertEqual('155.100m', str(k47 * mcr3_3))
        self.assertEqual('155.100k', str(M3_3 * mili47))

        self.assertEqual('100.000n', EngineerNumber('10p') * 10 ** 4)
        self.assertEqual('100.000n', EngineerNumber('10p', 10 ** 4))

        # add, sub
        self.assertEqual('3.347M', str(M3_3 + k47))
        self.assertEqual('3.253M', str(M3_3 - k47))
        self.assertEqual('47.003m', str(mili47 + mcr3_3))
        self.assertEqual('46.997m', str(mili47 - mcr3_3))
        # big and small, ignored small
        self.assertEqual('3.300M', str(M3_3 + mili47))

        # TOO BIG
        T10 = EngineerNumber(10, TERA)
        G40 = EngineerNumber(40, GIGA)
        self.assertEqual('10.000T', str(T10))
        self.assertEqual('40.000G', str(G40))
        BIG400 = T10 * G40
        self.assertEqual('400000000000000000000000', str(BIG400))

        # too small
        u1 = EngineerNumber(1, MICRO)
        n4 = EngineerNumber(4, NANO)
        self.assertEqual('1.000u', str(u1))
        self.assertEqual('4.000n', str(n4))
        small4 = u1 * n4
        self.assertEqual('4e-15', str(small4))

        self.assertEqual('987.000m', str(EngineerNumber(0.987)))
        self.assertEqual('1.000k', str(EngineerNumber(1000, ONE)))
        self.assertEqual('1.040k', str(EngineerNumber(1040, ONE)))
        self.assertEqual('999.000', str(EngineerNumber(999, ONE)))
        self.assertEqual('999.200', str(EngineerNumber(999.2, ONE)))
        self.assertEqual('2.000', str(EngineerNumber(2, ONE)))
        self.assertEqual('1.001', str(EngineerNumber(1.001, ONE)))
        self.assertEqual('1.000', str(EngineerNumber(1, ONE)))

        # same result
        self.assertEqual('1.000m', str(EngineerNumber(0.001, ONE)))
        self.assertEqual('1.000m', str(EngineerNumber(1, MILLI)))
        self.assertEqual('1.000m', str(EngineerNumber(1000, MICRO)))

        self.assertRaises
        self.assertEqual('1.004u', str(u1 + n4))
        self.assertEqual('996.000n', str(u1 - n4))
        self.assertEqual('250.000', str(u1 / n4))
        self.assertEqual('249.000', str(u1 // n4))
        self.assertEqual('4.000n', str(u1 % n4))
        div, mod = divmod(u1, n4)
        self.assertEqual('249.000', str(div))
        self.assertEqual('4.000n', str(mod))

        self.assertEqual('1000.000m', str(pow(u1, n4))) # 0.9999999447379593
        self.assertEqual('999.981m', str(pow(n4, u1))) # 0.9999806632154822
        self.assertEqual(0.9999999447379593, pow(u1, n4.num))
        neg1 = EngineerNumber(-1, ONE)
        self.assertEqual('-1.000', str(neg1))

        self.assertEqual('0.000', str(EngineerNumber(0)))
        self.assertEqual(-0.000001, -u1)
        self.assertEqual(0.000001, math.fabs(-u1))

        self.assertEqual('2.000', str(EngineerNumber(16) % EngineerNumber(7)))
        self.assertEqual('2.000', str(16 % EngineerNumber(7)))
        self.assertEqual('2.000', str(EngineerNumber(16) % 7))

        self.assertEqual('9.000', str(EngineerNumber(16) - EngineerNumber(7)))
        self.assertEqual('9.000', str(16 - EngineerNumber(7)))
        self.assertEqual('9.000', str(EngineerNumber(16) - 7))

        self.assertEqual('128.000', str(EngineerNumber(2) ** EngineerNumber(7)))
        self.assertEqual('128.000', str(2 ** EngineerNumber(7)))
        self.assertEqual('128.000', str(EngineerNumber(2) ** 7))

        self.assertEqual('2.286', str(EngineerNumber(16) / EngineerNumber(7)))
        self.assertEqual('2.286', str(16 / EngineerNumber(7)))
        self.assertEqual('2.286', str(EngineerNumber(16) / 7))

        self.assertEqual('2.000', str(EngineerNumber(16) // EngineerNumber(7)))
        self.assertEqual('2.000', str(16 // EngineerNumber(7)))
        self.assertEqual('2.000', str(EngineerNumber(16) // 7))

        self.assertEqual('2.286M', str(EngineerNumber(16, MEGA) / EngineerNumber(7)))
        self.assertEqual('2.286M', str(16 / EngineerNumber(7, MICRO)))
        self.assertEqual('2.286M', str(EngineerNumber(16, MEGA) / 7))

        self.assertEqual('1.000u', str(EngineerNumber(u1)))

        self.assertEqual('121.484m', str(EngineerNumber('121.484m')))
        self.assertEqual(121.484, EngineerNumber('121.484').num)
        self.assertEqual(121.484, EngineerNumber('121.484'))
        self.assertEqual(EngineerNumber('121.484'), 121.484)
        self.assertEqual('121.484', str(EngineerNumber('121.484')))
        self.assertEqual('121.484E', str(EngineerNumber('121.484E')))

        self.assertEqual('121.488p', str(EngineerNumber(121.488, PICO)))
        self.assertEqual('121.488p', str(EngineerNumber(0.121488, NANO)))

    def test_equal_different_value_and_factor(self):
        self.assertEqual(EngineerNumber(121.484, KILO), EngineerNumber(0.121484, MEGA))
        self.assertEqual(EngineerNumber(121.484, MILLI), EngineerNumber(0.121484, ONE))
        self.assertEqual(EngineerNumber(121.484, PICO), EngineerNumber(0.121484, NANO))
      # print(str(EngineerNumber(121.488, PICO)), str(EngineerNumber(0.121486, NANO)))
        self.assertEqual(str(EngineerNumber(121.488, PICO)), str(EngineerNumber(0.121488, NANO)))

    def test_equal_with_number(self):
        self.assertEqual(121484000000000000000, EngineerNumber('121.484E').num)
        self.assertEqual(121484000000000000000, EngineerNumber('121.484E'))

    def test_compare_with_same_instance(self):
        self.assertGreater(EngineerNumber('1.000'), EngineerNumber('0.999'))
        self.assertGreaterEqual(EngineerNumber('1.000'), EngineerNumber('0.999'))
        self.assertGreaterEqual(EngineerNumber('1.000'), EngineerNumber('1.000'))

        self.assertLess(EngineerNumber('0.999'), EngineerNumber('1.000'))
        self.assertLessEqual(EngineerNumber('0.999'), EngineerNumber('0.999'))
        self.assertLessEqual(EngineerNumber('1'), EngineerNumber('1.000'))

    def test_around_exa(self):
        exa999999 = EngineerNumber('999.999E')
      # print('e999999 =')
      # exa999999.detail()
      # print()
        self.assertEqual('999.999E', str(exa999999))

        # over exa a little
        exa = EngineerNumber(1, EXA)
        self.assertEqual('1.000E', str(exa))
        exa1 = exa + 1
        self.assertEqual('1.000E', str(exa1))
        self.assertEqual('1000000000000000001', str(exa1.num))

        # in zetta
        zetta = exa * 1000
        self.assertEqual('1000000000000000000000', str(zetta))
        zetta1 = zetta + 1
        self.assertEqual('1000000000000000000001', str(zetta1))

      # zetta_1 = zetta - 1
      # print('zetta - 1 =')
      # zetta_1.detail()
      # print()

    def test_compare_with_number(self):
        # swap
        self.assertGreater(EngineerNumber('1.000'), 0.999)
        self.assertGreaterEqual(EngineerNumber('1.000'), 0.999)
        self.assertGreaterEqual(EngineerNumber('1.000'), 1.000)
        self.assertGreater(1.0, EngineerNumber('0.999'))
        self.assertGreaterEqual(1.0, EngineerNumber('0.999'))
        self.assertGreaterEqual(1.0, EngineerNumber('1.000'))
        self.assertGreater(EngineerNumber('1.000'), 0)
        self.assertGreaterEqual(EngineerNumber('1.000'), 0)
        self.assertGreaterEqual(EngineerNumber('1.000'), 1)
        self.assertGreater(1, EngineerNumber('0.999'))
        self.assertGreaterEqual(1, EngineerNumber('0.999'))
        self.assertGreaterEqual(1, EngineerNumber('1.000'))

        self.assertLess(0.999, EngineerNumber('1.000'))
        self.assertLessEqual(0.999, EngineerNumber('0.999'))
        self.assertLessEqual(1, EngineerNumber('1.000'))

    def test_bool(self):
        self.assertTrue(EngineerNumber('1.000'))
        self.assertTrue(EngineerNumber('1.000p'))
        self.assertTrue(EngineerNumber(1, PICO))
        self.assertFalse(EngineerNumber('0.000'))

    def test_si_prefix_symbol_error(self):
        with self.assertRaises(ValueError) as raiz:
            EngineerNumber('100K')
      # message = ('cannot accept "K" as SI prefix symbol. '
      #            'please use "k" as prefix if you hope to describe kilo.'
      #            'Because "K" means Kelbin celcius.')
        message = ('"K" を SI 接頭辞の記号として使用することは出来ません。'
                   'kilo を表現したい場合、 "K" ではなく、小文字の "k" を'
                   'お使い下さい。'
                   'なぜならば、"K" は、Kelvin 温度を表現するための'
                   '単位記号だからです。')
        self.assertEqual(message, raiz.exception.args[0])

    def test_force(self):
        one = EngineerNumber('1')
        self.assertEqual('1.000', str(one))
        self.assertEqual('1000.000m', one._force('m'))
        self.assertEqual('0.001k', one._force('k'))
        self.assertEqual('1000.000m', one['m'])
        self.assertEqual('0.001k', one['k'])
        self.assertEqual('1.000', one[''])

        m1 = EngineerNumber('1m')
        self.assertEqual('1.000m', str(m1))
        self.assertEqual('1000.000u', m1._force('u'))
        self.assertEqual('1000.000u', m1['u'])
        self.assertEqual('0.001', m1[''])
        self.assertEqual('1000000.000n', m1['n'])

        k1 = EngineerNumber('123.456k')
        self.assertEqual('123.456k', k1['k'])
        self.assertEqual('123456.000', k1[''])
        self.assertEqual('123456000000000000.000p', k1['p'])

        m1234567 = EngineerNumber('1.234567m')
        self.assertEqual('1.235m', str(m1234567))
        self.assertEqual('1234.567u', m1234567._force('u'))
        self.assertEqual('1234.567u', m1234567['u'])
        self.assertEqual('0.001', m1234567[''])

        m1534567 = EngineerNumber('1.534567m')
        self.assertEqual('0.002', m1534567[''])
      # self.assertEqual('1.535m', str(m1534567))
      # self.assertEqual('1534.567u', m1534567._force('u'))
      # self.assertEqual('1534.567u', m1534567['u'])

    def test_warning(self):
        n1 = EngineerNumber('0.1m')
      # message = 'number\(={}\) in range\(0, 1\) convert to int.'.format(n1)
        message = (r'0 < number\(={}\) < 1 を満たす数字を '
                    'int に変換しようとしました。'.format(n1))

        with self.assertWarnsRegex(UserWarning, message) as warn:
            int(n1)

        n2 = EngineerNumber('-0.1m')
      # message = 'number\(={}\) in range\(0, 1\) convert to int.'.format(n2)
        message = (r'0 < number\(={}\) < 1 を満たす数字を '
                    'int に変換しようとしました。'.format(n2))
        with self.assertWarnsRegex(UserWarning, message) as warn:
            int(n2)

      # with support.captured_stderr() as stderr_:
      #     int(n2)
      # self.assertEqual(message, stderr_.getvalue())

    def test_math(self):
        two = EngineerNumber('2')
        root2 = math.sqrt(2)

        sqrt2 = two.sqrt()
        self.assertEqual(2, two)
        self.assertEqual(root2, sqrt2)
        self.assertIsInstance(sqrt2, EngineerNumber)

if __name__ == '__main__':
  # gc.set_debug(gc.DEBUG_LEAK)
    unittest.main()
