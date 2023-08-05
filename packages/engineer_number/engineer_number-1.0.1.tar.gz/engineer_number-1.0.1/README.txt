本 module では、工学的な数値の計算を容易に行うことを目的としています。
例えば、 以下のような場合に役に立ちます。

1. 470 nano って 何 micro だっけ？
2. このコンデンサーには、 "104" って書いてあるけど、容量は何マイクロFだっけ？
3. 1GB のHDDに 103MB の、このファイル何個入れれる？
4. VCCは 5V で 47k の抵抗を使って、
   Ibeo が、、、hfeは 140だから、
   Iceoは、、、で、結局 Io は、、、mA で、
   Aで考えると絶対最大定格を下回るから。。。
5. 抵抗のカラーコードが、黄紫赤金で、数字にすると472xだから、、、
   47 * (10 ** 2) でえっと、、、

ええーい、ややこしいんじゃーいっ！

などなど、工学的な数値計算にお悩みのあなた。
そこで、EngineerNumber class の出番です。
簡単に計算しちゃいましょう。

0.
>>> from engineer_number import EngineerNumber

1.
>>> nano470 = EngineerNumber('470n')
>>> nano470
470.000n
>>> nano470['u']
'0.470u'

2.
>>> c104 = EngineerNumber('10p') * 10 ** 4
>>> c104 = EngineerNumber('10p', 4) # equal to above line
>>> c104['u']
'0.100u'
>>> c104['n']
'100.000n'

3.
>>> G1 = EngineerNumber('1G')
>>> M103 = EngineerNumber('103M')
>>> G1 / M103
9.709

4.
>>> Vcc = 5
>>> k47 = EngineerNumber('47k')
>>> Ibeo = Vcc / k47
>>> Ibeo
106.383u
>>> Ibeo['m']
'0.106m'
>>> Iceo = Ibeo * 140
>>> Iceo['m']
'14.894m'
>>> Io = Ibeo + Iceo
>>> Io
15.000m
>>> Io['']
'0.015'

5.
>>> kx = EngineerNumber('47', 2)
>>> kx
4.700k
>>> kx['']
'4700.000'

ほーら？どうです？
EngineerNumber() 使いたくなっちゃった〜♪
