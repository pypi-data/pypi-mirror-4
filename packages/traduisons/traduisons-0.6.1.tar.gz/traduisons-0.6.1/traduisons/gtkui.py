#! /usr/bin/env python
# coding: utf-8

# Copyright 2013 John E Tyree <johntyree@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
    Traduisons!
    http://traduisons.googlecode.com

    Python bindings to Bing! Translate RESTful API
"""

import base64
import sys
import threading

import traduisons

msg_USAGE = """Usage: %s [OPTION]...
Translate a string between languages using Bing! Translate.

OPTIONS
  -h, --help            Show help and basic usage.
  -n, --no-gui          Run at command line only.
  -v, --version         Print version information and exit.
""" % (sys.argv[0],)

msg_HELP = """Type the name or code for the desired language.
Format:  <Input Language> | <Target Language>
fi|French    Finnish to French:
auto|en      Auto detect to English:
|ar          Change target Language to Arabic:
es|          Change starting Language to Spanish:

Please visit <http://code.google.com/p/traduisons/wiki> for help."""

start_text = ""
from_lang = "auto"
to_lang = "en"
b64_images = {
'png': {
    'google_logo': r'''
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''',
    'bing_logo':r'''
iVBORw0KGgoAAAANSUhEUgAAAC0AAAAUCAYAAAAZb7T/AAAABmJLR0QAAAAAAAD5Q7t/AAAACXBI
WXMAAABIAAAASABGyWs+AAAACXZwQWcAAAAtAAAAFACATny0AAAEBUlEQVRIx+3WW4iVVRQH8N8+
c85kOiil5KUwKi+J3SAiIcQaKyyxG1L5UBAFRWpQzohFJBLdHJXsAtEFiiALCvMlzXQmsYsUWWHq
g0oWGOVtysZpnDnn2z18++iMjlrZ5aU/HL6Pc/Za67/W+q+1D//j30EAs1uggKIYK0KomH/FMQ3L
S8ZAiEEdYswKbUJUO23TP066AGIkxkliXIqpYjyuYQzEYByWY1koZOeHcHy7vwPFbu9n4VqsAw3N
hFR9AaFLyKL59Xm2IRKdFELsjwNZDLWhu+cZa5mykeWjKRWoRBZd3juLB1flz65CMRWyrBIyNRkh
1GEgfsVeTfU9SFdRg7GCybgAA4iIO0WfaWxeSdh+0cYdsRTK6y7su+OerliTfb7/zA2/ZSUaB9YQ
R9M13qpRY5XiKVQqauzW2PwV1uJ7RAFRX2WX4SrB2SihTTF+TSjhaozEc3j88EpXcQvuwB604OOU
yHl4ALOIT29oH/ayYND69jMXo404FZ3EBtyFMtZju7xVY3A7WvEk8TUxDMUTuB7fYAV2YUTyMTKd
/wjf9iaPKkakrJ70yeCfjNtJIeZ1Cc5J2S4U1GIpcQh+TsTuxUN4B/NEW8SsrBAQajEBz2MR4cck
x9vwLOYKWmWoqSXrfA2vYhReEcOyNIG9kv4Uj2Kvj8fmdYaG1ZGwNZG6GNPxJbJ0og5TsBvzsNmC
+kNeG1s6iR/gJczHzRiXOvoiWqvz4v4WijZgCZpwDV3LxNp8nrqR7UjPbYTWI1JZMLH6tiO1agiG
JtIxFaAf9qeW9kTTwRX6Q7fZacXJGJYKk0oZyULAaensXqGYwvQkvRn7MJY46IigVYe5zkbhlxQ0
OBK9fXc49shl2IWnMFkIAzU298MZCnGmfLbW4/XcJDtCHl/INXQ3HsYT5rz/o6yYloeQJ2RhqkwT
th6W+J9BUPGmGu24T67rn1KnhuBcbMMMbBYPdTsn3dFBnz4H8Ehq350Yr1L6NEmhLBiNK1PAOXgB
p6qmlKPikFyOhnjwUyNT9q6i1fJ7YrhcLhXciBswE1sFu3pvY2OzVLmzMVG+pvonIruxQT6a36XA
/eR7tBNr5INVIragQ9NEvfgfjkuxRfRVj2Htea5OPqDTUrWfB031x9Be4xoMpppgltGnwmP1ThgN
H+Y5h1hAVCjknXnq8vT7akKAWVgg1/7MKuniUR03TThxckdDiIQKsXArrpNl7wneMLu5LEjzFgcS
Jsql8kVul5sX/1LQEyadEQvkt+B0PCMahxWidowgTMUlWIy3obrH/8hq+meQ/yEj3xQ3YRJOR638
ztiEt9CMDk2HZPnfka5i1kpK/cgO1IoGJNLtQtwnhoq6NuZe91+zPHH8Dm+QWR0lVuQ3AAAAJXRF
WHRkYXRlOmNyZWF0ZQAyMDExLTExLTI1VDEyOjE2OjI0KzAxOjAwTqRycQAAACV0RVh0ZGF0ZTpt
b2RpZnkAMjAxMS0xMS0yNVQxMjoxNjoyNCswMTowMD/5ys0AAAAASUVORK5CYII=''',
    'mymemory_logo' : r'''
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
'''},
'ico': {
    'traduisons_icon': r'''
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
/QD///8AAAAAAAAAAAD4/fxS8/379qKm2v8REZv/BQWS/woKpv8MC6r/DAym/woLo/8MDK3/DAyw
/wwMsv8NDLP/Cwqq/wkJrf8uMtX/bXbn/yw11/8YHMH/JzDW/0RT8v9FVfP/QVHy/0JT8/9BU/T/
Sl32/0ha9v9JWvb/UmT3/1hp9/9ZaPb/TF73/0VW9f9FVvX/SFr2/0db9v86Sej/HiPG/xwgvv8S
FKP/DQ2F/4yUz//w/vz/9P78o////wX+//8AAAAAAAAAAAD3//yK4+n1/0NDq/8CAoz/DAyo/xIT
uv8ODrX/EhOz/xAQrv8QELD/EBC0/w8Ps/8PELb/Dw+z/w0NtP8oLM//mKDu/0RR4/8gKMj/HSPH
/zI/5P9DVfT/SFr1/0ZZ9f9MXfb/V2b2/01e9/9IWvb/UWD2/0la9P9CU/P/Pk3z/z9O8v9BUfT/
RVb1/0VW9v9FWfX/MDvd/xcZu/8YG7j/Dg6O/zY4oP/S3fD/8//85Pj+/Sv4/v0AAAAAAAAAAAD4
//3Mubzi/xISjf8HB5b/ERK4/xQXwP8cIMr/HyTL/xcaw/8XG8H/Fhm8/xQWu/8VGLr/FRe5/xQW
vf8YG8T/foji/3+J7P80QeD/ISfK/yky2v9EVvT/S1r2/0hb9f9RYvb/Vmb2/0tc9f9EVPP/QFD0
/0FR8v88TPD/OEfv/zZF7/84SO//O0ry/0NT9f9GWvb/QVPw/yEoy/8cIcH/ExWj/xIRi/+dpdn/
8//9//b+/XS69+8A////AAAAAAD1+vv/eXnE/wQDif8RE6//GBzI/yoz3v9CUPL/Pkzx/y856v8u
N+n/Ji7d/x0iyf8XG8L/GBzB/xUYwP8WGsX/MznQ/5Sf6v9jcOv/Okjn/y886P86Se//R1j0/0Zc
9f9NX/f/TF72/0NT8/9AUPL/QlP0/0FS9P88TPH/NkXv/zM/7v83Ru//Oknx/0FQ9P9KWvX/SVz2
/zI93P8XGrr/ERKt/wkJjf9fYrv/6PX5//T+/ND///8Y/f//AAAAAADo7vf/TEuw/wYGmv8VGMD/
HiTQ/z9N8P9DU/b/O0n0/ztJ8/81QPH/OETw/zQ+6v8jKtj/ISfQ/yYu1/8cIcn/FRnE/0pS1/+Z
ofD/SFbu/zVD7f80Qu3/Q1Tz/0xg9/9PYfb/Sl71/0NU8/9CVPT/QFHy/09g8/9RYfH/Qk/w/zpI
7v86SfD/NULw/zpJ8f9MXfX/UmL1/zlG5/8dIsL/Fxm4/xITpf8pKZ7/vMbn//T//fj7/v5N+v79
AAAAAADl6/b/Tk22/wsMqP8dIsr/KDDe/zlG8/8/TvT/Pk30/zxK8/83QvL/QVD0/ztI8/81QvD/
PEnx/ztH8f8rNeP/GBzG/xofy/9kbOD/govu/z1M7P82RO3/NUPt/0la9P9WZfb/RFTx/0JV8/9F
VfH/hJTx/8vW9//R2vf/u8L0/5af8f94g/H/XGjv/2Ft8f9JW/X/QVDs/yky0v8cIsT/FRe7/xIU
sf8MC5H/ZWm8/+v3+v/5/v2Y////Af7//wDs8Pj5V1a//w0Prv8dIsv/KjLk/zdD8v89S/P/OETy
/zdC8f85RPH/RlP1/z1K9P82QvH/MDrw/y007/8tNe//IijY/xYZwv8kKsz/i5bs/2Zz7v81Quz/
OUft/zlH7v9PYvb/SFr0/0RW8/+LmfP/6PP5//T8+v/x+vn/8fv5//D7+f/s8vj/5Oz4/9rf9/90
fOz/JCzS/yEoy/8kK8z/Fxq6/xITsf8KCp//ISGb/7/H5//4//3Y/P7+JPz+/gD3/v3vgoPQ/woK
pf8VF7//JCvg/zVB8v83Q/L/NkLy/zZB8f85RfL/O0fz/zQ/8v8tNe//Jy3s/yIo6v8kKuv/Ji3q
/xoezf8WGcX/KzHL/3yF5/9TYPD/NkPu/zhG7/8+TvH/R1n1/1Zq8//S3vf/9P36//H7+v/w+vn/
8fv6//H6+f/w9/n/7vj4//H5+f+eouP/HCDF/yEo0P8qM9f/Jy7O/xMVsf8SE63/CAiS/2xxw//t
+vv/9/79de79+wD7//25vb/m/x4dqv8RErj/HSLS/zZB8P85RfL/ND7w/zU/8f85RfP/Okfz/zA5
8P8rM+7/ISfp/x0i5/8dIuj/HyTp/yIp5P8ZHcr/EhTA/0hP0/+QmvD/SVfw/zdF8P80Qu3/P0/z
/26A9f/l8vn/8fv6//D6+v/x+vr/8Pr5/+34+P/p9fj/7Pn5/8TM6f88P8T/Gh/K/xkeyf8pMt//
O0jq/x0iwf8UFbP/CAiX/ycpp//O1vD/+P/9w////xT3//yH5+/3/2Njxv8VFrX/GyDL/ygv5P83
QvH/ND/x/z5L9P9ATvT/NkPx/zA57/8nLuz/HiTm/xwg4/8cIeL/JCnk/yku6P8eJN//FhrH/xYZ
xv9nbuP/jZjy/0lZ8P83Ru7/QE3w/36P9f/n8/j/8Pn6/+z2+P/r+fj/6/n4/+n29//p9ff/3eb0
/1pawf8JCaz/FRe//xkdyv8lLOT/N0Tw/zE83/8WGLv/FBey/wcHj/+GjdL/9//99v3//mv7/v1S
9f389Li75/80NLj/FBe+/xsgz/8pMef/N0Ty/zxJ8/84RPL/ND/x/yoz7f9ASev/hY7u/6Sq7v+n
ru//s7rx/6+08P92fO//Tlfq/ykw3/8rM+j/sLz0/6av8/9CT+3/SFby/3mJ8//j8Pj/7vj4/+z5
+f/p+fj/7Pj4/+ny9//r8vj/lJbS/w4No/8ODq7/FRi//yEn1/8pMuv/Mz/v/0JQ8/8oL9L/Fxu7
/wYHkv9ARLL/4+34//j//dD///8M+v/9fPL2+veho9//MTK7/xUZvf8eJNb/MTrv/zlF8v83Q/L/
Mz3x/0NN7v++yfX/7PH4/+3w9//t8ff/7fL3/+3z+P/r7/j/1Nj3/6er8/+LkvD/1Nv3/+72+f+A
iPD/OEXt/5en9P/s9/n/6Pb4/+v0+P/o9Pf/6fT4/+nw+P+rrt7/KSmo/wsKp/8RErP/Gh/I/y45
6f82ROv/SFbp/0lX8/82P+P/Fxq9/w4Pnv8TFZH/u8Tp//j//dv+//4A//7/Cfr//Wzy+vvlxcnr
/0NEvv8XG83/KzLs/y847/81QPL/MTvw/3aD8f/t9vn/6/L4/+3x+P/w9Pj/7PL4/+zy+P/t8vj/
8PT5//D0+P/L0PL/vcT0/9/q+P/FyvX/c37v/9Pf+P/0/vr/7Pj5/+33+P/q9Pj/0tvw/4WG1P8r
K7H/Cwuk/xITsP8WGb3/JS7a/zJA7v9NWun/cHvb/05a5v8+Se3/Gh7G/wwNnP8DA4b/i5LS//r/
/tsAAAAA/f7+ANv+8wD5/v1h+f/86M7U7v9KTc//N0Dm/ykx7f8qMu7/KjPu/5qk8//x9/j/7PT4
/+3z+P/v9fj/7/T4/+7y+P/v8/j/4OT1/5KY4f81Ocj/Jy7Z/3WB7/+YnfD/dn7w/4mR5/+osef/
ucLr/73E6/+KkNz/QkbC/xYYsP8UFrP/ExW0/xkdwf8mMNn/OUbt/0FQ8P+Un+//d4LV/ztGz/8q
Mtr/HiTS/xARn/8BAYX/YGa8/+76+9sAAAAAAAAAAP7//gD///8C/P79RPr//d3Dx+v/PUDP/yEo
4/8eI+j/HCHn/2t07P/n7/j/8Pb4//D0+P/w8/n/8PH4/+7y+P/g5fX/bW/W/xgbwP8WGcT/FhrJ
/zc/5/+Fjuv/P0fe/yInxv8bHrj/Jiq9/ysvwf8WGLP/DxCv/xITsP8VF7j/IinO/zNA5v9BUfP/
Tl/3/4aS9P+yuOn/ZW/O/zM7w/8WGbz/Gh7W/xASr/8AAIH/W2C6/+z3+9sAAAAAAAAAAAAAAAD/
//8A////APr+/Tj4/vzKtbrn/zAyyP8XGtz/Gh7n/yYr5P+2wfL/9Pf5//H0+P/x9fn/8fX5/9rd
9v9nadj/Fhi8/xcaxP8YHMb/GBvQ/zI45v+FjeH/OD7D/xsgvf8ZHb//GBvC/xQWvv8UF7z/Fhm8
/x8kx/8qMtj/P0/u/0pd9f9RYff/ZXH1/7fB9f+lrOX/ZG3L/0JLwf8WF7X/FxrU/xETtP8DA4v/
dHvN//L9/NsAAAAAAAAAAAAAAAAAAAAA////APr//gD9//8p+P79ubW55v80Nsb/HB/Y/0BJ6P+/
yPP/4uj3/+bq9//g5vf/vcPw/2104v8jKcz/FhnE/xcawf8dItL/HyXk/3J87P+iqOP/X2PK/y0x
wP8cIcL/JCzY/ys15P8yP+r/NULp/0BP8P9LW/X/Tl71/0RT8/87SOn/ipPs/7K47P+orun/Zm7M
/1hhyP8yNLr/ERK2/wwNo/8MDaP/gozd//T+/NsAAAAAAAAAAAAAAAAAAAAAAAAAAP///wD8//4A
/v//Ifv//bevsuP/PD/C/09a4f99hvP/f4fz/4+U8v+DiPT/SlPj/yUu0v8iKNL/HybU/ykx3/8p
Mer/R1Dp/9DZ9f/Izu//eX/U/1ley/8gJb3/IivQ/zVE7v87SvL/Sln2/1Ni9v9XZfT/VmLv/zlE
3v8wOdH/d3/X/4KI1/+Jkdv/ZW7N/1pjyP9iZsv/Gxyk/wgIlv8bH7L/oavn//b++9sAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAA9P37AP3//lnS1e76QEHA/zA64f9KWfb/UF72/1Zi9f9LWPX/
Okfv/zE86P8tNuj/MDvt/y027f8wOOr/k53t/9bd8v/d4/b/n6bm/290z/9VWsr/Nz/K/1Bb5v9x
ePL/gojy/4WO8f+Biuf/fIbd/0ZQ0v8yPc//Y23P/2Jryv9pb8z/bHLO/3uB1v9dYMX/Ghqa/xIT
oP8zOsD/ytby//j//NIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+f39AP///y3j5/XtTlHK
/zM+5/9CUfb/QlH1/z1K9P85RvP/NkLx/zpG8P85RvH/NkLx/zZC6/9ca93/gY3a/32J3v/W3vX/
xczx/3J70v9tcs7/cHbR/4yT3/+3vO7/pKft/3WA4v+Ql97/g47Y/1dj1v87SND/X2nL/2txzP9t
cs7/ZGjN/05Rv/8fIKD/Gxyj/xocsP9mb9T/6vT58/v//WIAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAA/f/+AP///xvz+fvWi4zb/y433P89SvT/PUv0/ztJ8/86R/P/QE30/zpI8v84RfH/O0fp
/1dn3P9whdf/YHHU/0ZU3/+tt/P/ytDx/2930P9XYcX/XGXH/0NJxP9IUt3/naTu/1Nf2f9hbNf/
dIHX/1Fe0/9JVtD/YGjK/1Vcx/84P8X/GRyu/wYGi/8ICI//GBuq/2Ns1P/R2vP/9v37r////w0A
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/v//AP///wH7//6Zysvr/zw/yv84Re//Pkz1/z1L
9P85R/P/O0jz/0ZS8v99he//fore/3WI1/9yhdb/WGXV/zRA4f9VYeH/ho3a/2Bpyv9WYMX/WGLF
/0tRxv8qMd//UFjg/3uC2v9dZ9j/RFPU/zdD1v8+Stn/SlbV/yQqwP8NDar/BASL/wwMmv8lJ7H/
e4HW/+Do9v/3/fvh+f39OPb8/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPT9/AD4
//1G7vb58pCR2/8yOtn/NUHp/ztF3/8zO9f/g43x/7S69P/GyfD/kJnd/3mK1/96idf/YWvZ/ztH
6f9FUtr/c33T/2Vty/9XYsf/WGLG/2NpzP83Otv/EBO4/xwdp/9eYsn/UVfL/ztE0f8xOtT/JSzA
/xkarP8WF6L/ICGh/0dKvP+nquL/5uz2//X8+tb4/PxQ//z/AP7+/gAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAPz+/gD9/v4K9//9iOnx+Pecn+H/XmLP/4OG1/+nrOL/rq/o/3V95f96
heP/hpDc/3+N2P9/jtj/Z3Hf/0BO6/9KWNj/dYLV/3F40P9cZsj/WmLG/4mN2f9XWND/Bgag/yIl
rv+us+b/rK3i/3t70P9bW8T/UE+6/1pZwP91dc7/oKHg/8fN7f/y9fnp9vv7l/v+/S/3/PsA////
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD7//4A/P//CPr//mn0+/vd
4un29+/2+vvw9/r8k5XY/zM2v/8tN83/UmPY/3iJ2f+Fkdn/ZnPl/0dU7/9VY9v/fYrY/3Z+0/9o
b8v/XGTK/2Rp2v8tLa3/EBCX/3x+0f/j6Pj77/P52unq9+Xg4fTu2t3z+d3e8/zl6fb87vL56/f6
/KT3+fs++f/8A/b7+wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAA/v//AP7//wL5//0g+//+RPv//k35//1y6/L47J+i3P80Nrr/LTfK/1ho2/+Djtv/
anTp/1Vf7v9yfOL/iJPb/3uF1f9nbtD/O0LP/xcbtP8HB5D/OTqw/7/E6//p7vnO9/n7JPHz+SXw
9fkv8/j6Sfb6+lL1+fpR9fj6Mfn7/Af2+fsA////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP7//wD///8D+//9
VvT8/NbFyur/VlfC/ykwwv9SXtr/Xmns/1dh7/9ze+X/gYnb/2Vy2f9BStX/HCK+/wsLlP8fH5v/
hIjT/97j9fPy9fpZvc3pAP///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAD///8A9v/8APv//jT7//6y5On1+4eK1/8wNsv/Lznh/zI+6f85RN7/RlLb
/yw0yf8YG7X/Fxmu/0BCtv+EiNT/09jz++/z+pf5+vwJ9/j7AAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////APv//gD9//4Q+//+h/D4
+vK1uuj/TlDK/x4iwv8hJsf/MDXF/ywvuf83Obv/cnTP/8LG7P/i6Pf77fH5rfP3+hPw9foAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAD+//8A//7/Bfv//VH4/vy+4Ob0+K605v+Zn+H/o6Xg/6Wn4f+7ven/4ef19+zy
+cfv9Pla+vz8EfT4+gD///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////APn+/AD7/v0R+//9UPb9+6Hz
+/qv8/b6rvD0+a/u9fqV8/f6Tfb6+xT///8B/f/+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAD///8A//7/APP/+gLv+/sD8/f6A/3+/AP9//4B/v/9AAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///+H//8AAP//+AA/
/wAA///gAA//AAD//8AAB/8AAP//gAAD/wAA//8AAAH/AAD//wAAAP8AAP/+AAAAfwAA/AAAAAB/
AADgAAAAAD8AAOAAAAAAPwAAwAAAAAAfAACAAAAAAA8AAAAAAAAADwAAAAAAAAAHAAAAAAAAAAcA
AAAAAAAABwAAAAAAAAADAAAAAAAAAAMAAAAAAAAAAQAAAAAAAAABAAAAAAAAAAEAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAADgAAAAAAAAAOAAAAAAAAAA8AAAAAAAAAD8
AAAAAAAAAP4AAAAAAAAA/wAAAAAAAAD/AAAAAAAAAP8AAAAAAAAA/wAAAAABAAD/gAAAAAEAAP+A
AAAABwAA/8AAAAAPAAD/4AAAAD8AAP/+AAA//wAA//+AAD//AAD//8AAf/8AAP//4AD//wAA///4
Af//AAD///wP//8AAP///////wAA////////AAA=''',
    },
}

# decorator
def echo(f):
    def newfunc(*args, **kwargs):
        print f.__name__, "BEGIN"
        f(*args, **kwargs)
        print f.__name__, "END"
    return newfunc

# decorator
def backgroundThread(f):
    echo = False
    if echo: print "backgroundThread definition start"
    def newfunc(*args, **kwargs):
        if echo: print "newfunc definition start"
        class bgThread(threading.Thread):
            def __init__(self, f, *args, **kwargs):
                if echo: print "bgThread Init Start"
                self.f = f
                threading.Thread.__init__(self)
                if echo: print "bgThread Init End"
                return
            def __call__(self, *args, **kwargs):
                if echo: print "__call__ start"
                resp = self.start()
                if echo: print "__call__ end"
                return resp
            def run(self):
                if echo: print "Thead start"
                result = self.f(*args, **kwargs)
                if echo: print "Thead end"
                if echo: print "newfunc definition end"
        #return bgThread(target = f, args = args, kwargs = kwargs).start()
        return bgThread(f).start()
    if echo: print "backgroundThread definition end"
    return newfunc

def clipboard_get():
    '''Return a gtk.Clipboard object or False if gtk is unavailable'''
    try:
        import gtk
        class clipboard(gtk.Clipboard):
            def __init__(self, text = None):
                gtk.Clipboard.__init__(self)

            def set_text(self, text, len=-1):
                targets = [ ("STRING", 0, 0),
                            ("TEXT", 0, 1),
                            ("COMPOUND_TEXT", 0, 2),
                            ("UTF8_STRING", 0, 3) ]
                def text_get_func(clipboard, selectiondata, info, data):
                    selectiondata.set_text(data)
                    return
                def text_clear_func(clipboard, data):
                    del data
                    return
                self.set_with_data(targets, text_get_func, text_clear_func, text)
                return
## ------*------ End CLASS ------*------
        return clipboard()
    except ImportError:
        return False
## ------*------ End CLIPBOARD ------*------


## -----v----- BEGIN GUI -----v-----
class TranslateWindow(traduisons.translator):
    '''Gui frontend to translate function.'''
    ## If gtk or pygtk fails to import, warn user and run at cli.
    try:
        import gtk, gobject; global gtk; global gobject
        gobject.threads_init()
    except ImportError:
        print """  Import module GTK: FAIL"""
        guiflagfail = False
    try:
        import pygtk
        pygtk.require('2.0')
    except ImportError:
        guiflagfail = False
        print """  Import module pyGTK: FAIL"""
    try:
        import pango
    except ImportError:
        print """  Import modules pango: FAIL"""
    try:
        guiflagfail
        print """
        Install modules or try:
            python "%s" --no-gui
            """ % (sys.argv[0],)
        sys.exit()
    except NameError:
        pass

    def __init__(self, from_lang = 'auto', to_lang = 'en'):
        self.pixbufs = {}
        for form, name in (('ico', 'traduisons_icon'),
                           ('png', 'bing_logo'),
                           ('png', 'google_logo'),
                           ('png', 'mymemory_logo')):
            loader = gtk.gdk.PixbufLoader(form)
            loader.write(base64.b64decode(b64_images[form][name]))
            loader.close()
            self.pixbufs[name] = loader.get_pixbuf()

        ## localize variables
        traduisons.translator.__init__(self, from_lang, to_lang)

        ## Generate user messages
        self.msg_LANGTIP  = self.pretty_print_languages(0)
        self.msg_MODAL = ''

        ## Set window properties
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(250, 95)
        self.window.set_title("Traduisons!")
        self.window.set_role("translator")

        ## Try to load icon or skip
        try:
            self.window.set_icon(self.pixbufs["traduisons_icon"])
        except Exception, e:
            pass
        self.window.connect("delete_event", lambda w, e: sys.exit())

        ## Keyboard Accelerators
        self.AccelGroup = gtk.AccelGroup()
        #self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK,
                                      #gtk.ACCEL_LOCKED,
                                      #lambda w, x, y, z: gtk.main_quit())
        self.AccelGroup.connect_group(ord('Q'), gtk.gdk.CONTROL_MASK,
                                      gtk.ACCEL_LOCKED,
                                      lambda w, x, y, z: sys.exit())
        self.AccelGroup.connect_group(ord('N'), gtk.gdk.CONTROL_MASK,
                                      gtk.ACCEL_LOCKED,
                                      lambda w, x, y, z:
                                          self.resultbuffer1.set_text(''))
        self.window.add_accel_group(self.AccelGroup)

        self.vbox1 = gtk.VBox(False, 0)
        self.window.add(self.vbox1)

##  ----v---- Upper half of window ----v----
        self.hbox1 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox1, False, False, 3)

        ## language label
        self.langbox = gtk.Label()
        self.langbox.set_markup(str(self.from_lang()) + ' | ' + \
                                str(self.to_lang()) + ':  ')
        self.hbox1.pack_start(self.langbox, False, False, 1)
        self.langbox.set_tooltip_text(self.msg_LANGTIP)

        ## Entry box
        self.entry = gtk.Entry()
        self.entry.set_max_length(0)
        self.entry.connect('activate', self.enter_callback)
        self.entry.set_tooltip_text(msg_HELP)
        self.hbox1.pack_start(self.entry, True, True, 1)
##  ----^---- Upper half of window ----^----

##  ----v---- Lower Half of window ----v----
        self.hbox2 = gtk.HBox(False, 0)
        self.vbox1.pack_start(self.hbox2)

        ## Result window
        self.result1 = gtk.TextView()
        self.result1.set_cursor_visible(False)
        self.result1.set_editable(False)
        self.result1.set_wrap_mode(gtk.WRAP_WORD)
        self.result1.set_indent(-12)
        self.resultbuffer1 = self.result1.get_buffer()
        self.resultbuffer1.create_tag('from_lang', foreground = "dark red")
        self.resultbuffer1.create_tag('to_lang',foreground = "dark blue")
        self.resultbuffer1.create_mark('end',
                                       self.resultbuffer1.get_end_iter(),
                                       False)

        ## Scroll Bar
        self.resultscroll = gtk.ScrolledWindow()
        self.resultscroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.resultscroll.add(self.result1)
        self.hbox2.pack_start(self.resultscroll, True, True, 1)

        ## Custom status bar
        self.hbox3 = gtk.HBox(False, 0)
        self.statusBar1 = gtk.Label()
        self.statusBar1.set_alignment(0, 0.5)
        self.statusBar2 = gtk.Label()
        self.vbox1.pack_start(self.hbox3, False)
        self.hbox3.pack_start(self.statusBar1)
        self.hbox3.pack_start(self.statusBar2, False)
        try:
            serviceLogo = gtk.Image()
            serviceLogo.set_from_pixbuf(self.pixbufs['mymemory_logo'])
            self.statusBar2.set_text("powered by ")
            self.hbox3.pack_start(serviceLogo, False)
        except Exception, e:
            print e
            self.statusBar2.set_text("powered by MyMemory")
        self.statusBar2.set_alignment(1, 0.5)

##  ----^---- Lower Half of window ----^----

        self.window.show_all()
        self.check_for_update()

## ------*------ START CALLBACKS ------*------

    def modal_message(self, msg = None):
        if msg is None:
            msg = self.msg_MODAL
        gobject.idle_add(self.statusBar1.set_text, msg)

    @backgroundThread
    def check_for_update(self):
        '''
        Update language list. Check the server for a new version of
        Traduisons and notify the user.
        '''
        chgs = self.update_languages(True)
        if chgs is False:
            print 'Unable to update_languages'
        else:
            for change in chgs:
                print change

        self.msg_LANGTIP = self.pretty_print_languages(0)
        gobject.idle_add(self.langbox.set_tooltip_text, self.msg_LANGTIP)
        if not self.is_latest():
            self.msg_MODAL = 'Update Available!'
            print self.msg_MODAL
            self.modal_message(self.msg_MODAL)
            tooltip = 'Get Traduisons! %s\n%s' % (self.msg_LATEST,
                                                  traduisons.msg_DOWNLOAD)
            gobject.idle_add(self.statusBar1.set_tooltip_text, tooltip)
        return

    def enter_callback(self, widget, data = None):
        '''Submit entrybox text for translation.'''
        buf = self.resultbuffer1
        if self.entry.get_text() in ('.clear', 'clear()'):
            buf.set_text('')
            self.entry.set_text('')
            return
        result = self.text(self.entry.get_text())
        if result is None:
            return

        if 'HELP' in result:
            help_text = '\nPlease visit:\nhttp://code.google.com/p/traduisons/wiki'
            buf.insert(buf.get_end_iter(), help_text)
            self.result1.scroll_mark_onscreen(buf.get_mark('end'))
            self.entry.set_text('')
            return
        elif 'SWAP' in result or 'CHANGE' in result:
            self.langbox.set_markup(self.from_lang() + ' | ' +
                                    self.to_lang() + ':  ')
            if 'SWAP' in result:
                self.entry.set_text(self.text())
            elif 'CHANGE' in result:
                self.entry.set_text('')
                return
        elif 'VERSION' in result:
            ver_text = '\nTraduisons! - %s' % (traduisons.msg_VERSION,)
            buf.insert(buf.get_end_iter(), ver_text)
            self.result1.scroll_mark_onscreen(buf.get_mark('end'))
            self.entry.set_text('')
            return

        elif 'EXIT' in result:
            gtk.main_quit()
            return

        self.modal_message('translating...')
        self.entry.select_region(0, -1)

        ## If it's not blank, stick a newline on the end.
        if buf.get_text(buf.get_start_iter(), buf.get_end_iter()) != '':
            buf.insert(buf.get_end_iter(), '\n')

        # Sending out text for translation
        if not self.translate():
            print 'Error:', repr(self._error)
            if str(self._error[1]) == 'invalid translation language pair':
                buf.insert(buf.get_end_iter(),
                           str(self._error[1]).capitalize())
                self.from_lang('auto')
        from_langTemp = self.from_lang()
        if from_langTemp == 'auto':
            from_langTemp = self.detect_lang()
        translation = self.result
        self.modal_message()
        self.langbox.set_markup(self.from_lang() + ' | ' +
                                self.to_lang() + ':  ')
        if translation == '':
            return

        # Setting marks to apply from_lang and to_lang color tags
        buf.insert(buf.get_end_iter(), '%s:' % (from_langTemp,))
        front = buf.get_iter_at_mark(buf.get_insert())
        front.backward_word_start()
        back = buf.get_iter_at_mark(buf.get_insert())
        buf.apply_tag_by_name('from_lang', front, back)
        self.result1.scroll_mark_onscreen(buf.get_mark('end'))

        buf.insert(buf.get_end_iter(), ' %s\n  %s:' % (self.entry.get_text(),
                                                       self.to_lang()))
        front = buf.get_iter_at_mark(buf.get_insert())
        front.backward_word_start()
        back = buf.get_iter_at_mark(buf.get_insert())
        buf.apply_tag_by_name('to_lang', front, back)
        buf.insert(buf.get_end_iter(), ' %s' % (translation,))
        self.result1.scroll_mark_onscreen(buf.get_mark('end'))
        print "%s: %s\n  %s: %s" % (from_langTemp, self.entry.get_text(),
                                    self.to_lang(), translation)

        try:
            self.clipboard
        except AttributeError:
            self.clipboard = clipboard_get()
        self.clipboard.set_text(translation)
        self.clipboard.store()

## ------*------ End CALLBACKS ------*------
## ------*------ End CLASS ------*------
## ------*------ END GUI ------*------


def main():
    guiflag = True
    for arg in sys.argv[1:]:
        if arg in ('--help', '-h', "/?"):
            print msg_USAGE, "\n", msg_HELP
            sys.exit()
        elif arg in ('--no-gui', '-n', "/n"):
            guiflag = False
        elif arg in ("--version", "-v", "/v"):
            print traduisons.msg_LICENSE
            sys.exit()
        else:
            print msg_USAGE, "\n", traduisons.msg_BUGS
            sys.exit()


    ## Start traduisons!
    if guiflag:
        TranslateWindow()
        gtk.main()
    else:
        print "\nTraduisons! - %s\npowered by Bing! ..." % (traduisons.msg_VERSION,)
        t = traduisons.translator()
        if not t.is_latest():
            print "Version %s now available! %s" % (t.msg_LATEST,
                                                    traduisons.msg_DOWNLOAD)

        # This thread doesn't return until after main dies
        # Perhaps there is a better to avoid the blocking behavior
        #@backgroundThread
        #def update_languages():
            #t.update_languages()
            #update_languages()
        while True:
            t.text('')
            while t.text() == '':
                stringLang = t.from_lang() + "|" + t.to_lang() + ": "
                try:
                    result = t.text(raw_input(stringLang))
                    if None == result:
                       break
                    elif 'HELP' == result[1]:
                        print msg_HELP
                        print t.pretty_print_languages()
                except EOFError:
                    print
                    sys.exit()
            if t.translate():
                if t.result != '':
                    if t.from_lang() == 'auto':
                        l = t.detect_lang()[0]
                        for k, v in t.dictLang.items():
                            if v == l:
                                print k, '-', v
                    print t.result
            else:
                raise t.result[1]

if __name__ == '__main__': main()
