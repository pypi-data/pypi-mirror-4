# -*- coding: utf-8 -*-
'''
    Copyright (C) 2013  Rodrigo Pinheiro Matias <rodrigopmatias@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import zlib

configuration = {
    'menu.json': '''
eNrtVkFPgzAUvu9XND140cB9NzM1nuaWGT0sy9LBG6srfaQtoiH77wJOMgY4Z6jZEnsgoe/r9328
0vc67ZFspMUzH9TAm6F9Qi/uuAB6RXYi7xHkkRBkXAkUE30yLWeqlCVOr1AZLza6Bi4hA6PE5ZDW
grMdvZrVISS0Ka4FFlpps5ZRPAhAgd8KKWBMBYXhJgslaL1FpZvvUEuZ29Uglo6EZA4+N6hoI35T
m900pmC7J8wzHGWVan9B2p7BhwgktcxPuCTZV5NnLn1MbKpN2CvY5idME8dx7MsIYUVju1xDxBSr
/YVHuBygXPIgVkAixaUBZTMlo1yCRCwA5zSz8tMSNz6yxI1jbs6uxnkCNdgrb+XbrLdL0NTLbv1q
+g73ssOcExDwaatj4ide7WddcI4UvmRuu6Z9RBS6a9J7EFG3F48v6hv04myNYfvbZuk4tSIK1MqY
SPddN+BmFS8cD0NXoZ8pYBRmDpl219xvOT9tBeP3hxWzFj3X3MAp3EfuMYSizP9v0gluUmd3h+sF
xufX1rIen8xZYf3Peltv9gELN7GV
''',
    'editor.json': '''
eNpdjrsOwjAMRfd+RZQZMcEA/8DIHDmNQyOCU9W2SkH8OymPJR7vucf2szN1rFKigCTOQ3/lEXq0
RyOT4sZ8Cz88pyBDRbt/HktNOT3W/mG7b+rK6AQ8Vxghc7vtoikgN5cCRtAsLuMdp8rsuMhQyDYu
qJTG/PwS4ZbysnpnryRqToWK7V5vwqtGOg==
'''
}

compress = lambda text: zlib.compress(text, 9).encode('base64')

decompress = lambda text: zlib.decompress(text.decode('base64'))
