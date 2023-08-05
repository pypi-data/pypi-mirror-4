# -*- coding: utf-8 -*-
from distutils.core import setup
    
setup(
    name = "ipget",
    # 階層があるプロジェクトはこれ
    # packages = ["debify"], 
    # フラットなプロジェクトはこれ
    py_modules = ["ipget"], 
    # コマンド。 ディフォルトで/usr/local/bin/に入る
    scripts = ["ipget.py"], 
    version = "0.0.1",
    # ここのから選ぶ？ http://pypi.python.org/pypi?:action=list_classifiers 「License ::」を検索。
    license = "LGPL",        
    # これも同上
    platforms = ['Linux', 'Mac'],
    # このモジュールは何をするか一言
    description = "This package is for those that know the local ip in linux.",
    author = "Yuta Kitagami",
    author_email = "hokusin02@gmail.com",
    url = "http://kitagami.org",
    keywords = ["Linux", "ip", "ifconfig"],
    # できるだけ該当するクラシファイアお入れておくといい。
    # このクラシファイアは勝手に入力しないで該当するものをここから見付けてくる http://pypi.python.org/pypi?:action=browse
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
	# 対象とするOS。「Operating System :: POSIX」など
        "Operating System :: MacOS", 
		"Operating System :: Unix", 
		"Operating System :: POSIX", 
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
	# プロジェクトのステータス。本番で磨き抜かれたものでなければ'3 - Alpha'、'4 -Beta'などとしておくのが無難だ。
        "Development Status :: 4 - Beta",
	# 稼動環境： 端末、ウェブ、デーモン、X11など
        "Environment :: Console",
	# 対象ユーザ
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development",
        ],
    # 複数行の説明
    long_description = """\
This package is for those that know the local ip in linux.

>>> import ipget
>>> a = ipget.ipget()
>>> print a.ipaddr("eth0")
192.168.0.2/24
>>> print a.ipaddr6("eth0")
240f:f:3872:1:709d:3141:873a:f5c3/64
>>> print a.mac("eth0")
3c:d9:2b:7a:24:47

Thank you.
...
"""
    )
