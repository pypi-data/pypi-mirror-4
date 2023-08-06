# coding: utf-8

import os
import sys
import math
import numbers
import warnings
import gettext

from .constants import *

def get_default_languages():
    languages = []
    for language in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
        env = os.environ.get(language)
        if not env:
            continue
        sp = env.split(':')
        languages.extend(sp)
    if not languages:
        languages.append('C')
    return languages

def decide_languages_order(hope=[]):
    # first is overwrited by second.
    # so should be hope=['lower-important', 'higher-important']
    languages = get_default_languages()
    if 'ja' not in languages:
        languages.insert(0, 'zannenenglish')
    languages.extend(hope)

    return languages

def gettext_install(domain,
                    localedir=None,
                    languages=[],
                    codeset=None,
                    names=None):
    t = gettext.translation(domain, localedir,
                            languages=languages,
                            fallback=True,
                            codeset=codeset)
    t.install(names)

path_ = os.path.join(os.path.dirname(__file__), 'locale')
# print('path_ =', path_)
gettext_install('engineer_number',
                 path_,
                 languages=decide_languages_order())


class EngineerNumber(numbers.Real):
    """EngineerNumber class は、SI接頭辞の変換・異なるSI接頭辞同士の
    計算を容易にします。使用可能なSI接頭辞は、最後に説明します。

    EngineerNumber instance(インスタンス) に対し、
    任意のSI接頭辞を KEY にすることで、
    任意のSI接頭辞に換算した値を知ることが出来ます。
    SI 接頭辞変換結果として返される文字列を EngineerNumber() に渡し、
    新たな EngineerNumber instance を生成出来ます。

    EngineerNumber.num 属性は、数値型 object です。
    EngineerNumber class に、__add__() 等の method を定義し、
    演算の対象を EngineerNumber.num とすることで、
    EngineerNumber instance は、数値型 object 互換になっています。
    数値型 object 互換にする方法は、
    PEP 3141, numbers class 等をご覧下さい。

    以下、使うための手順を簡単に紹介します。
    >>> from engineer_number import EngineerNumber

    KILO, MEGA, ...等々の SI 接頭辞名を使わない場合、
    以下の行は必要ありません。
    >>> from engineer_number.constants import *

    以下の、No.1, 2, 3 では、 10 * 1000 の値を得る方法と、
    SI 接頭辞変換の方法を説明します。

    No.1: 有効値の文字列と、SI 接頭辞を連結し、
    10 kilo の値を得る方法です。
    >>> r1 = EngineerNumber('10k')       # No.1
    >>> r1
    10.000k

    10 kilo を Mega で計算し、SI 接頭辞変換を行います。
    >>> r1['M']
    '0.010M'

    No.2: 有効値と、SI 接頭辞名で 10 kilo の値を得る方法です。
    >>> r2 = EngineerNumber(10, KILO)    # No.2
    >>> r2 = EngineerNumber('10', KILO)  # No.2
    >>> r2
    10.000k

    10 kilo に SI 接頭辞変換を行い、数値に変換します。
    10 の乗数が 0 の場合、
    空文字列を SI 接頭辞としていることに注意して下さい。
    >>> r2['']
    '10000.000'

    No.3: 有効値と 10 の乗数で 10 kilo の値を得る方法です。
    抵抗のカラーコードから抵抗値を求める事を想定しています。
    >>> r3 = EngineerNumber(10, 3)       # No.3
    >>> r3 = EngineerNumber('10', 3)     # No.3
    >>> r3
    10.000k

    10 kilo を kilo で計算する、なんちゃって SI 接頭辞変換を行います。
    自分でも必要ないとは思うんですけれど、流れ上、書きました。
    >>> r3['k']
    '10.000k'

    以下の、No.4, 5 では、コンデンサ上の表示から、
    コンデンサの容量値を求める方法を紹介します。
    "p" を有効数値の後に付けていることに注意して下さい。

    No.4: コンデンサの表示 "104" から容量値を求めます。
    >>> c4 = EngineerNumber('10p', 4)    # No.4
    >>> c4
    100.000n

    マイクロ・ナノ・ピコを計算する時など、
    よく頭がこんがらがりますよね。
    >>> c4['u']
    '0.100u'

    No.5: コンデンサの表示 "202" から容量値を求めます。
    >>> c5 = EngineerNumber('20p', 2)    # No.5
    >>> c5
    2.000n

    マイクロ・ナノ・ピコを計算する時など、
    よく頭がこんがらがりますよね。
    >>> c5['p']
    '2000.000p'

    ここだけの話：
    マイクロ・ナノ・ピコの変換が大変でややこしくて、
    よく間違えて困るので、この EngineerNumber を作成しました。
    抵抗のカラーコードにも使えると分かった時には、
    本当に便利だなー。と自分でも思いました

    使用例を、もう少し知りたい方は "README.txt" をご覧下さい。

    SI 接頭辞として用意しているのは、以下の通りです。
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
    """

    # I18N
    __doc__ = _(__doc__)

    # EngineerNumber instance を __str__() にて
    # 文字列表現した時の、小数点以下の有効桁数。
    round_ndigits = 3

    @classmethod
    def _parse_string(cls, ss):
        "有効数字の数値と 10 の乗数値を、tuple に詰めて返します。"
        if ss[-1].isalpha():
            si = ss[-1]
        else:
            si = ''
        if si == 'K':
          # message = ('cannot accept "K" as SI prefix symbol. '
          #            'please use "k" as prefix if you hope to describe kilo.'
          #            'Because "K" means Kelbin celcius.')
            message = _(''
                       '"K" を SI 接頭辞の記号として'
                       '使用することは出来ません。\n'
                       'kilo を表現したい場合、 "K" ではなく、小文字の "k" を'
                       'お使い下さい。\n'
                       'なぜならば、"K" は、Kelvin 温度を表現するための'
                       '単位記号だからです。')
            raise KeyError(message)

        value = float(ss.replace(si, ''))
      # print('si =', si, 'value =', value)
        exponent10 = cls._si2exponent10(si)

        return (value, exponent10)

    @classmethod
    def _si2exponent10(cls, si):
        """SI 接頭辞に対応する、10 の乗数値を返します。"""
        try:
            exponent10 = d_SYMBOL_EXPONENT[si]
        except KeyError as raiz:
          # message = \
          #     ('SI prefix symbol must be in '
          #      '{}'.format(tuple(d_SYMBOL_EXPONENT)))
            message = \
               _('SI 接頭辞の記号は、次のいずれかでなければなりません。'
                 '{}').format(tuple(d_SYMBOL_EXPONENT))
            raise KeyError(message)
        return exponent10

    def __init__(self, value, exponent10=0):
        """有効数値と 10 の乗数値を指定します。
        value を、二つの方法により指定できます。
        一つ目は、有効数値を整数値、浮動小数値として指定する方法です。
        二つ目は、有効数値の文字列と SI 接頭辞を連結し、文字列として
        指定する方法です。

        exponent10 は、無指定であれば、0 として取り扱います。
        以下の計算式により、value, exponent10 の値から、
        EngineerNumber.num 属性の値を計算します。
        num = value * 10 ** exponent10

        つまり、exponent10 を指定しなければ、
        num 属性の値として、value の値を、そのまま代入することになります。
        num = value * 10 ** 0 = value * 1 = value
        num 属性の値の範囲は、 -24 <= num <= 24 であり、かつ、
        num 属性の値は、3 の整数倍となります。

        詳しい使い方は、EngineerNumber class の docstring をご覧下さい。
        例 1 〜 5 等が分かりやすいかと思います。
        更なる情報は、少しだけ、"README.txt" に書いています。
        """
        if isinstance(value, str):
            value, parsed_exponent10 = EngineerNumber._parse_string(value)
            exponent10 += parsed_exponent10
        self.num = value * (10 ** exponent10)
        # >>> 10 ** 0
        # 1
        self._normalize()

    def __getitem__(self, si_prefix):
        """self[si_prefix] として、SI 接頭辞変換を行う。"""
        return self._force(si_prefix)

    def _force(self, si=''):
        """SI 接頭辞により有効数字を変換。"""
        exponent10 = EngineerNumber._si2exponent10(si)
        value = self.num / (10 ** exponent10)
        fmt = ':.{}f'.format(EngineerNumber.round_ndigits)
        fmt = '{' + fmt + '}{}'
        s = fmt.format(round(value, EngineerNumber.round_ndigits), si)
        return s

    def _normalize(self):
        """EngineerNumber.num の値から、_value, _exponent10 を正規化する。
        num, _value, _exponent10 の計算方法は、簡単に以下の通り。

        _exponent10 = log10(num) // 3
        _value = num // (10 ** _exponent10)
        num =(大体同じ、approximately equal to) _value * 10 ** _exponent10

        _exponent10 は SI 接頭辞と連動するため、
        3 の整数倍になっていることに注意。"""

        num = self.num
        while isinstance(num, EngineerNumber):
            num = num.num
        if num == 0:
            self._value = 0
            self._exponent10 = 0
            return
        elif num > 0:
            sign_num = 1
        else:
            sign_num = -1
        num *= sign_num
      # print('num={}'.format(num))
        exponent = math.log10(num)
        if exponent >= 0:
            sign_exponent = 1
        else:
            sign_exponent = -1
        div, mod = divmod(exponent, 3)
        div = int(div)
        exponent *= sign_exponent
        exponent10 = div * 3
        factor = 10 ** exponent10
        value = num / factor
        value *= sign_num

        self._value = value
        self._exponent10 = exponent10
        return self

    def sqrt(self):
        """math.sqrt() の help を読んで。"""
        root = math.sqrt(self)
        return EngineerNumber(root)

    def detail(self):
        """主に debug 用。
        本当は非公開にしたかったが、公開としてしまった為、
        今更、非公開に出来なくて困っている。
        出来ることなら、今からでも非公開にしたい。。。"""
        print(self)
        print('        num =', self.num)
        print('     _value =', self._value)
        print('_exponent10 =', self._exponent10)

    def __add__(self, other):
        """object.__add__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = self.num + other.num
        return EngineerNumber(n)

    def __sub__(self, other):
        """object.__sub__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = self.num - other.num
        return EngineerNumber(n)

    def __mul__(self, other):
        """object.__mul__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = self.num * other.num
        return EngineerNumber(n)

    def __floordiv__(self, other):
        """object.__floordiv__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = self.num // other.num
        return EngineerNumber(n)

    def __truediv__(self, other):
        """object.__truediv__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = self.num / other.num
        return EngineerNumber(n)

    def __mod__(self, other):
        """object.__mod__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = self.num % other.num
        return EngineerNumber(n)

    def __divmod__(self, other):
        """object.__divmod__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        div, mod = divmod(self.num, other.num)
        return (EngineerNumber(div), EngineerNumber(mod))

    def __pow__(self, other):
        """object.__pow__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other)
        n = pow(self.num, other.num)
        return EngineerNumber(n)

    def __int__(self):
        """object.__int__() の help を読んで。"""
        if self._exponent10 < 0:
          # message = 'abs(number(={})) in range(0, 1) convert to int.'.format(self)
            message = _('0 < abs(number(={})) < 1 を満たす数字を '
                        'int に変換しようとしました。').format(self)
            warnings.warn('{}'.format(message), UserWarning)
        return int(self.num)

    def __float__(self):
        """object.__float__() の help を読んで。"""
        return float(self.num)

    def __radd__(self, other):
        """object.__radd__() の help を読んで。"""
        n = other + self.num
        return EngineerNumber(n)

    def __rsub__(self, other):
        """object.__rsub__() の help を読んで。"""
        n = other - self.num
        return EngineerNumber(n)

    def __rmul__(self, other):
        """object.__rmul__() の help を読んで。"""
      # print('self=', type(self))
      # print('other=', type(other))
        n = other * self.num
        return EngineerNumber(n)

    def __rfloordiv__(self, other):
        """object.__rfloordiv__() の help を読んで。"""
        n = other // self.num
      # print('self.num={} // other={}, n={}'.format(self.num, other, n))
        return EngineerNumber(n)

    def __rtruediv__(self, other):
        """object.__rtruediv__() の help を読んで。"""
      # print('self=', type(self))
      # print('other=', type(other))
        n = other / self.num
        return EngineerNumber(n)

    def __rmod__(self, other):
        """object.__rmod__() の help を読んで。"""
        n = other % self.num
        return EngineerNumber(n)

    def __rdivmod__(self, other):
        """object.__rdivmod__() の help を読んで。"""
        div, mod = divmod(other, self.num)
        return (EngineerNumber(div), EngineerNumber(mod))

    def __rpow__(self, other):
        """object.__rpow__() の help を読んで。"""
        n = pow(other, self.num)
        return EngineerNumber(n)

    def __eq__(self, other):
        """object.__eq__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other, ONE)
        return self._exponent10 == other._exponent10 and \
               round(self) == round(other)

    def __ne__(self, other):
        """object.__ne__() の help を読んで。"""
        return not self == other

    def __gt__(self, other):
        """object.__gt__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other, ONE)
        return round(self) > round(other)

    def __ge__(self, other):
        """object.__ge__() の help を読んで。"""
        return self > other or self == other

    def __lt__(self, other):
        """object.__lt__() の help を読んで。"""
        if not isinstance(other, EngineerNumber):
            other = EngineerNumber(other, ONE)
        return round(self) < round(other)

    def __le__(self, other):
        """object.__le__() の help を読んで。"""
        return self < other or self == other

    def __repr__(self):
        """object.__repr__() の help を読んで。"""
        # for EngineerNumber in tuple.
        return str(self)

    def __str__(self):
        """object.__str__() の help を読んで。"""
        symbol = ''
        if self._exponent10 in d_EXPONENT_SYMBOL:
            symbol = d_EXPONENT_SYMBOL[self._exponent10]
#           s = '{:.3f}{}'
            fmt = ':.{}f'.format(EngineerNumber.round_ndigits)
            fmt = '{' + fmt + '}{}'
            round_value = \
                round(self._value, EngineerNumber.round_ndigits)
            s = fmt.format(round_value, symbol)
        else:
            s = str(self.num)
        return s

    def __abs__(self):
        """object.__abs__() の help を読んで。"""
        return abs(self.num)

    def __pos__(self):
        """object.__pos__() の help を読んで。"""
        return +self.num

    def __neg__(self):
        """object.__neg__() の help を読んで。"""
        return -self.num

    def __round__(self, ndigits=None):
        """object.__round__() の help を読んで。"""
        if ndigits is None:
            ndigits = EngineerNumber.round_ndigits
        if self._exponent10 < 0:
            ndigits += abs(self._exponent10)
        return round(self.num, ndigits)

    def __ceil__(self):
        """math.__ceil__() の help を読んで。"""
        return math.ceil(self.num)

    def __floor__(self):
        """math.floor() の help を読んで。"""
        return math.floor(self.num)

    def __trunc__(self):
        """math.trunc() の help を読んで。"""
        return math.trunc(self.num)

def I18N(attr):
    """attr.__doc__ を gettext() にて翻訳する。

    attr() として attr を呼び出し可能であれば、
    attr に結び付く __doc__ 属性を msgid とし、
    以下を実行する。
    msgstr = gettext(msgid)
    実行後、attr に結びつく __doc__ 属性の値を、msgstr で上書きする。

    attr() として attr を呼び出し可能でない場合、何も実行しない。
    """

    if callable(attr):
        msgid = getattr(attr, '__doc__')
        msgstr = _(msgid)
        setattr(attr, '__doc__', msgstr)

I18N(I18N)
for attr in EngineerNumber.__dict__.values():
    I18N(attr)

del attr, path_
